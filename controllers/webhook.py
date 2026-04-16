# -*- coding: utf-8 -*-
import hashlib
import hmac
import json
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class WhatsAppWebhook(http.Controller):

    @http.route('/whatsapp/webhook', type='http', auth='none', methods=['GET'], csrf=False)
    def webhook_verify(self, **kwargs):
        """Handle Meta webhook verification challenge."""
        mode = kwargs.get('hub.mode')
        token = kwargs.get('hub.verify_token')
        challenge = kwargs.get('hub.challenge')

        verify_token = request.env['ir.config_parameter'].sudo().get_param(
            'sm_whatsapp.webhook_verify_token', ''
        )

        if mode == 'subscribe' and token and token == verify_token:
            _logger.info('WhatsApp webhook verified successfully')
            return request.make_response(challenge, headers=[('Content-Type', 'text/plain')])

        _logger.warning('WhatsApp webhook verification failed')
        return request.make_response('Forbidden', status=403)

    @http.route('/whatsapp/webhook', type='http', auth='none', methods=['POST'], csrf=False)
    def webhook_receive(self, **kwargs):
        """Process incoming webhook events from Meta."""
        try:
            raw_body = request.httprequest.get_data(as_text=True)

            # Verify signature
            if not self._verify_signature(request.httprequest, raw_body):
                _logger.warning('WhatsApp webhook: invalid signature')
                return request.make_response('Unauthorized', status=401)

            data = json.loads(raw_body)
            self._process_webhook_data(data)

        except Exception:
            _logger.exception('Error processing WhatsApp webhook')

        return request.make_response('OK', headers=[('Content-Type', 'text/plain')])

    def _verify_signature(self, httprequest, raw_body):
        """Verify the X-Hub-Signature-256 header from Meta."""
        app_secret = request.env['ir.config_parameter'].sudo().get_param(
            'sm_whatsapp.app_secret', ''
        )
        if not app_secret:
            # If no secret configured, skip verification (dev mode)
            return True

        signature = httprequest.headers.get('X-Hub-Signature-256', '')
        if not signature.startswith('sha256='):
            return False

        expected = 'sha256=' + hmac.new(
            app_secret.encode(), raw_body.encode(), hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected)

    def _process_webhook_data(self, data):
        """Process the webhook payload."""
        MessageModel = request.env['whatsapp.message'].sudo()

        for entry in data.get('entry', []):
            for change in entry.get('changes', []):
                value = change.get('value', {})

                # Process status updates
                for status in value.get('statuses', []):
                    wa_id = status.get('id')
                    new_status = status.get('status')
                    if wa_id and new_status:
                        MessageModel._update_status_from_webhook(wa_id, new_status)

                # Process incoming messages
                for message in value.get('messages', []):
                    self._handle_incoming_message(value, message)

    def _handle_incoming_message(self, value, message):
        """Handle an incoming WhatsApp message."""
        MessageModel = request.env['whatsapp.message'].sudo()
        PartnerModel = request.env['res.partner'].sudo()

        from_number = message.get('from', '')
        wa_id = message.get('id', '')
        msg_type = message.get('type', 'text')

        body = ''
        if msg_type == 'text':
            body = message.get('text', {}).get('body', '')

        # Try to find contact info from metadata
        contact_name = ''
        for contact in value.get('contacts', []):
            if contact.get('wa_id') == from_number:
                contact_name = contact.get('profile', {}).get('name', '')

        # Find or create partner
        partner = PartnerModel.search([
            '|', '|',
            ('whatsapp_number', 'like', from_number),
            ('mobile', 'like', from_number),
            ('phone', 'like', from_number),
        ], limit=1)

        if not partner:
            partner = PartnerModel.create({
                'name': contact_name or f'WhatsApp {from_number}',
                'whatsapp_number': from_number,
                'phone': from_number,
            })

        # Create message record
        MessageModel.create({
            'partner_id': partner.id,
            'phone': from_number,
            'direction': 'incoming',
            'message_type': 'text',
            'body': body,
            'wa_message_id': wa_id,
            'status': 'delivered',
        })

        _logger.info('WhatsApp incoming from %s: %s', from_number, body[:100])
