# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class WhatsAppComposer(models.TransientModel):
    _name = 'whatsapp.composer'
    _description = 'WhatsApp Message Composer'

    partner_id = fields.Many2one('res.partner', string='Contact', required=True)
    phone = fields.Char(string='Phone Number', required=True)
    message_type = fields.Selection([
        ('text', 'Text Message'),
        ('template', 'Template Message'),
    ], string='Message Type', default='text', required=True)
    body = fields.Text(string='Message')
    template_id = fields.Many2one('whatsapp.template', string='Template',
                                  domain=[('status', '=', 'approved')])
    res_model = fields.Char(string='Related Model')
    res_id = fields.Integer(string='Related Record ID')

    # Multi-send
    partner_ids = fields.Many2many(
        'res.partner', string='Recipients',
        help='For bulk send — leave empty for single send',
    )

    @api.onchange('template_id')
    def _onchange_template_id(self):
        if self.template_id and self.template_id.body:
            self.body = self.template_id.body

    def action_send(self):
        """Create and send WhatsApp message."""
        self.ensure_one()

        if self.message_type == 'text' and not self.body:
            raise UserError(_('Please enter a message.'))
        if self.message_type == 'template' and not self.template_id:
            raise UserError(_('Please select a template.'))

        # Bulk send
        partners = self.partner_ids or self.partner_id
        messages = self.env['whatsapp.message']

        for partner in partners:
            phone = partner.whatsapp_number or partner.mobile or partner.phone or self.phone
            msg = self.env['whatsapp.message'].create({
                'partner_id': partner.id,
                'phone': phone,
                'message_type': self.message_type,
                'body': self.body,
                'template_id': self.template_id.id if self.template_id else False,
                'res_model': self.res_model or False,
                'res_id': self.res_id or 0,
            })
            messages |= msg

        messages.action_send()

        sent = messages.filtered(lambda m: m.status == 'sent')
        failed = messages.filtered(lambda m: m.status == 'failed')

        if failed and not sent:
            error = failed[0].error_message or 'Unknown error'
            raise UserError(_('Send failed: %s', error))

        return {'type': 'ir.actions.act_window_close'}

    def action_open_wa_link(self):
        """Fallback: open wa.me link in browser (no API needed)."""
        self.ensure_one()
        phone = self.env['whatsapp.message']._sanitize_phone(self.phone)
        body = self.body or ''
        import urllib.parse
        encoded = urllib.parse.quote(body)
        url = f'https://wa.me/{phone}?text={encoded}'
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }
