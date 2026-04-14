# -*- coding: utf-8 -*-
import json
import logging

import requests

from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

GRAPH_API_URL = 'https://graph.facebook.com'


class WhatsAppTemplate(models.Model):
    _name = 'whatsapp.template'
    _description = 'WhatsApp Message Template'
    _order = 'name'

    name = fields.Char(string='Name', required=True)
    template_name = fields.Char(
        string='Meta Template Name', required=True,
        help='Exact template name as registered in Meta Business Manager',
    )
    language = fields.Char(string='Language Code', default='en_US')
    category = fields.Selection([
        ('marketing', 'Marketing'),
        ('utility', 'Utility'),
        ('authentication', 'Authentication'),
    ], string='Category', default='utility', required=True)
    body = fields.Text(
        string='Body Preview',
        help='Preview of template body. Use {{1}}, {{2}} for variables.',
    )
    header_type = fields.Selection([
        ('none', 'None'),
        ('text', 'Text'),
    ], string='Header Type', default='none')
    header_text = fields.Char(string='Header Text')
    footer_text = fields.Char(string='Footer Text')
    active = fields.Boolean(default=True)
    model_id = fields.Many2one(
        'ir.model', string='Applies To',
        help='If set, this template will be available only for this model',
    )
    status = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='Status', default='draft')

    def action_sync_templates(self):
        """Sync templates from Meta WhatsApp Business API."""
        self.env['whatsapp.message']._sync_templates()

    def action_submit_to_meta(self):
        """Submit this template to Meta Business Manager via API."""
        self.ensure_one()
        ICP = self.env['ir.config_parameter'].sudo()
        token = ICP.get_param('sm_whatsapp.api_token', '')
        ba_id = ICP.get_param('sm_whatsapp.business_account_id', '')
        version = ICP.get_param('sm_whatsapp.api_version', 'v21.0')

        if not token or not ba_id:
            raise UserError(_(
                'Set your API Token and Business Account ID in Settings → WhatsApp first.'
            ))

        url = f'{GRAPH_API_URL}/{version}/{ba_id}/message_templates'
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        }

        # Build components
        components = []
        if self.header_type == 'text' and self.header_text:
            components.append({
                'type': 'HEADER',
                'format': 'TEXT',
                'text': self.header_text,
            })
        if self.body:
            components.append({
                'type': 'BODY',
                'text': self.body,
            })
        if self.footer_text:
            components.append({
                'type': 'FOOTER',
                'text': self.footer_text,
            })

        payload = {
            'name': self.template_name,
            'language': self.language or 'en_US',
            'category': (self.category or 'utility').upper(),
            'components': components,
        }

        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=30)
            data = resp.json()
        except requests.exceptions.RequestException as e:
            raise UserError(_('Failed to submit template: %s', str(e)))

        if 'error' in data:
            raise UserError(_(
                'Meta API error: %s', data['error'].get('message', json.dumps(data))
            ))

        # Meta returns the template with status
        meta_status = data.get('status', '').upper()
        status_map = {'APPROVED': 'approved', 'REJECTED': 'rejected'}
        new_status = status_map.get(meta_status, 'draft')
        self.write({'status': new_status})

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Template Submitted'),
                'message': _(
                    'Template "%(name)s" submitted to Meta. Status: %(status)s. '
                    'Utility templates are usually auto-approved.',
                    name=self.template_name,
                    status=meta_status or 'PENDING',
                ),
                'type': 'success',
                'sticky': True,
            },
        }

    def action_sync_status(self):
        """Check the current status of this template on Meta."""
        self.ensure_one()
        ICP = self.env['ir.config_parameter'].sudo()
        token = ICP.get_param('sm_whatsapp.api_token', '')
        ba_id = ICP.get_param('sm_whatsapp.business_account_id', '')
        version = ICP.get_param('sm_whatsapp.api_version', 'v21.0')

        if not token or not ba_id:
            raise UserError(_(
                'Set your API Token and Business Account ID in Settings → WhatsApp first.'
            ))

        url = (
            f'{GRAPH_API_URL}/{version}/{ba_id}/message_templates'
            f'?name={self.template_name}'
        )
        headers = {'Authorization': f'Bearer {token}'}

        try:
            resp = requests.get(url, headers=headers, timeout=30)
            data = resp.json()
        except requests.exceptions.RequestException as e:
            raise UserError(_('Failed to check template status: %s', str(e)))

        if 'error' in data:
            raise UserError(_(
                'Meta API error: %s', data['error'].get('message', json.dumps(data))
            ))

        templates = data.get('data', [])
        if not templates:
            raise UserError(_(
                'Template "%(name)s" not found on Meta. '
                'Please submit it first using "Submit to Meta".',
                name=self.template_name,
            ))

        tpl = templates[0]
        meta_status = tpl.get('status', '').upper()
        status_map = {'APPROVED': 'approved', 'REJECTED': 'rejected'}
        new_status = status_map.get(meta_status, 'draft')
        self.write({'status': new_status})

        # Also update body if available
        for comp in tpl.get('components', []):
            if comp.get('type') == 'BODY':
                self.write({'body': comp.get('text', '')})

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Status Updated'),
                'message': _(
                    'Template "%(name)s" status: %(status)s',
                    name=self.template_name,
                    status=meta_status,
                ),
                'type': 'success' if new_status == 'approved' else 'warning',
                'sticky': False,
            },
        }
