# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    whatsapp_number = fields.Char(
        string='WhatsApp',
        help='WhatsApp number with country code, e.g. 6281234567890',
    )
    whatsapp_message_ids = fields.One2many(
        'whatsapp.message', 'partner_id', string='WhatsApp Messages',
    )
    whatsapp_message_count = fields.Integer(
        string='WA Messages', compute='_compute_whatsapp_message_count',
    )

    @api.depends('whatsapp_message_ids')
    def _compute_whatsapp_message_count(self):
        data = self.env['whatsapp.message']._read_group(
            [('partner_id', 'in', self.ids)],
            ['partner_id'],
            ['__count'],
        )
        counts = {partner.id: count for partner, count in data}
        for rec in self:
            rec.whatsapp_message_count = counts.get(rec.id, 0)

    def action_send_whatsapp(self):
        """Open WhatsApp composer wizard."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Send WhatsApp',
            'res_model': 'whatsapp.composer',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_partner_id': self.id,
                'default_phone': self.whatsapp_number or self.mobile or self.phone or '',
                'default_res_model': 'res.partner',
                'default_res_id': self.id,
            },
        }

    def action_view_whatsapp_messages(self):
        """View WhatsApp message history for this contact."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'WhatsApp Messages',
            'res_model': 'whatsapp.message',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id},
        }
