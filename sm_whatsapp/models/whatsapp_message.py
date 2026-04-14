# -*- coding: utf-8 -*-
import json
import logging
import re

import requests

from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

GRAPH_API_URL = 'https://graph.facebook.com'


class WhatsAppMessage(models.Model):
    _name = 'whatsapp.message'
    _description = 'WhatsApp Message'
    _order = 'create_date desc'
    _rec_name = 'display_name'

    partner_id = fields.Many2one('res.partner', string='Contact', required=True, index=True)
    phone = fields.Char(string='Phone Number', required=True)
    direction = fields.Selection([
        ('outgoing', 'Outgoing'),
        ('incoming', 'Incoming'),
    ], string='Direction', default='outgoing', required=True)
    message_type = fields.Selection([
        ('text', 'Text'),
        ('template', 'Template'),
    ], string='Type', default='text', required=True)
    body = fields.Text(string='Message')
    template_id = fields.Many2one('whatsapp.template', string='Template')
    wa_message_id = fields.Char(string='WA Message ID', index=True)
    status = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
        ('failed', 'Failed'),
    ], string='Status', default='draft', required=True)
    error_message = fields.Text(string='Error')
    res_model = fields.Char(string='Related Model')
    res_id = fields.Many2oneReference(
        string='Related Record', model_field='res_model',
    )
    display_name = fields.Char(compute='_compute_display_name', store=True)

    @api.depends('partner_id.name', 'direction', 'create_date')
    def _compute_display_name(self):
        for rec in self:
            direction = '→' if rec.direction == 'outgoing' else '←'
            name = rec.partner_id.name or 'Unknown'
            rec.display_name = f"{direction} {name}"

    # ------------------------------------------------------------------
    # API helpers
    # ------------------------------------------------------------------

    def _get_api_config(self):
        """Get WhatsApp API configuration."""
        ICP = self.env['ir.config_parameter'].sudo()
        token = ICP.get_param('sm_whatsapp.api_token', '')
        phone_id = ICP.get_param('sm_whatsapp.phone_number_id', '')
        version = ICP.get_param('sm_whatsapp.api_version', 'v21.0')
        if not token or not phone_id:
            raise UserError(_(
                'WhatsApp API is not configured. '
                'Go to Settings → WhatsApp to set your API Token and Phone Number ID.'
            ))
        return {
            'token': token,
            'phone_number_id': phone_id,
            'api_version': version,
            'base_url': f'{GRAPH_API_URL}/{version}/{phone_id}',
        }

    @staticmethod
    def _sanitize_phone(phone):
        """Remove non-digit characters from phone number."""
        if not phone:
            return ''
        return re.sub(r'[^\d]', '', phone.strip())

    # ------------------------------------------------------------------
    # Send message
    # ------------------------------------------------------------------

    def action_send(self):
        """Send message(s) via WhatsApp Cloud API."""
        for msg in self:
            try:
                if msg.message_type == 'template':
                    msg._send_template_message()
                else:
                    msg._send_text_message()
                msg._post_chatter_note()
            except requests.exceptions.RequestException as e:
                msg.write({
                    'status': 'failed',
                    'error_message': str(e),
                })
                _logger.exception('WhatsApp send failed for message %s', msg.id)

    def _send_text_message(self):
        config = self._get_api_config()
        phone = self._sanitize_phone(self.phone)
        if not phone:
            raise UserError(_('No valid phone number.'))

        payload = {
            'messaging_product': 'whatsapp',
            'to': phone,
            'type': 'text',
            'text': {'body': self.body or ''},
        }
        result = self._call_api(config, '/messages', payload)
        self._handle_send_result(result)

    def _send_template_message(self):
        config = self._get_api_config()
        phone = self._sanitize_phone(self.phone)
        if not phone:
            raise UserError(_('No valid phone number.'))
        if not self.template_id:
            raise UserError(_('Select a template to send.'))

        payload = {
            'messaging_product': 'whatsapp',
            'to': phone,
            'type': 'template',
            'template': {
                'name': self.template_id.template_name,
                'language': {
                    'code': self.template_id.language or 'en_US',
                },
            },
        }
        result = self._call_api(config, '/messages', payload)
        self._handle_send_result(result)

    def _call_api(self, config, endpoint, payload):
        """Make a POST request to the WhatsApp Cloud API."""
        url = config['base_url'] + endpoint
        headers = {
            'Authorization': f"Bearer {config['token']}",
            'Content-Type': 'application/json',
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        return resp.json()

    def _handle_send_result(self, result):
        """Process the API response after sending."""
        if 'messages' in result:
            self.write({
                'wa_message_id': result['messages'][0].get('id', ''),
                'status': 'sent',
                'error_message': False,
            })
        else:
            error = result.get('error', {})
            self.write({
                'status': 'failed',
                'error_message': error.get('message', json.dumps(result)),
            })

    def _post_chatter_note(self):
        """Post a note in the related record's chatter."""
        if not self.res_model or not self.res_id:
            return
        try:
            record = self.env[self.res_model].browse(self.res_id)
            if hasattr(record, 'message_post'):
                status_icon = '✅' if self.status == 'sent' else '❌'
                body_preview = (self.body or '')[:200]
                record.message_post(
                    body=f"{status_icon} <b>WhatsApp</b> to {self.phone}<br/>{body_preview}",
                    message_type='notification',
                    subtype_xmlid='mail.mt_note',
                )
        except Exception:
            _logger.warning('Could not post chatter note for %s,%s', self.res_model, self.res_id)

    # ------------------------------------------------------------------
    # Status update (called from webhook)
    # ------------------------------------------------------------------

    def _update_status_from_webhook(self, wa_message_id, new_status):
        """Update message status from webhook callback."""
        status_map = {
            'sent': 'sent',
            'delivered': 'delivered',
            'read': 'read',
            'failed': 'failed',
        }
        mapped = status_map.get(new_status)
        if not mapped:
            return
        msg = self.sudo().search([('wa_message_id', '=', wa_message_id)], limit=1)
        if msg:
            msg.write({'status': mapped})

    # ------------------------------------------------------------------
    # Test connection
    # ------------------------------------------------------------------

    def _test_connection(self):
        """Test API connection by fetching the phone number info."""
        config = self._get_api_config()
        url = config['base_url']
        headers = {
            'Authorization': f"Bearer {config['token']}",
        }
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            data = resp.json()
            if 'error' in data:
                raise UserError(_(
                    'Connection failed: %s', data['error'].get('message', 'Unknown error')
                ))
            phone_display = data.get('display_phone_number', 'Unknown')
            verified = data.get('verified_name', 'Unknown')
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Connection Successful'),
                    'message': _(
                        'Phone: %(phone)s\nBusiness Name: %(name)s',
                        phone=phone_display,
                        name=verified,
                    ),
                    'type': 'success',
                    'sticky': True,
                },
            }
        except requests.exceptions.RequestException as e:
            raise UserError(_('Connection failed: %s', str(e)))

    # ------------------------------------------------------------------
    # Sync templates from Meta
    # ------------------------------------------------------------------

    def _sync_templates(self):
        """Fetch templates from WhatsApp Business API and sync locally."""
        ICP = self.env['ir.config_parameter'].sudo()
        token = ICP.get_param('sm_whatsapp.api_token', '')
        ba_id = ICP.get_param('sm_whatsapp.business_account_id', '')
        version = ICP.get_param('sm_whatsapp.api_version', 'v21.0')
        if not token or not ba_id:
            raise UserError(_(
                'Set your API Token and Business Account ID in Settings → WhatsApp first.'
            ))

        url = f'{GRAPH_API_URL}/{version}/{ba_id}/message_templates'
        headers = {'Authorization': f'Bearer {token}'}
        try:
            resp = requests.get(url, headers=headers, timeout=30)
            data = resp.json()
        except requests.exceptions.RequestException as e:
            raise UserError(_('Failed to fetch templates: %s', str(e)))

        if 'error' in data:
            raise UserError(_(
                'API error: %s', data['error'].get('message', 'Unknown')
            ))

        Template = self.env['whatsapp.template']
        count = 0
        for tpl in data.get('data', []):
            existing = Template.search([
                ('template_name', '=', tpl['name']),
                ('language', '=', tpl.get('language', 'en_US')),
            ], limit=1)

            body = ''
            for comp in tpl.get('components', []):
                if comp.get('type') == 'BODY':
                    body = comp.get('text', '')

            status_map = {
                'APPROVED': 'approved',
                'REJECTED': 'rejected',
            }

            vals = {
                'name': tpl['name'].replace('_', ' ').title(),
                'template_name': tpl['name'],
                'language': tpl.get('language', 'en_US'),
                'category': tpl.get('category', 'UTILITY').lower(),
                'body': body,
                'status': status_map.get(tpl.get('status'), 'draft'),
            }
            if existing:
                existing.write(vals)
            else:
                Template.create(vals)
            count += 1

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Sync Complete'),
                'message': _(
                    '%(count)s template(s) synced from Meta.',
                    count=count,
                ),
                'type': 'success',
                'sticky': False,
            },
        }
