# -*- coding: utf-8 -*-
from odoo import models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_send_whatsapp(self):
        """Open WhatsApp composer with pre-filled SO info."""
        self.ensure_one()
        partner = self.partner_id
        body = _(
            "Dear %(name)s,\n\n"
            "Your order *%(order)s* for *%(currency)s %(amount)s* "
            "has been confirmed.\n\n"
            "Thank you for your business!",
            name=partner.name,
            order=self.name,
            currency=self.currency_id.symbol,
            amount=f"{self.amount_total:,.2f}",
        )
        return {
            'type': 'ir.actions.act_window',
            'name': 'Send WhatsApp',
            'res_model': 'whatsapp.composer',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_partner_id': partner.id,
                'default_phone': partner.whatsapp_number or partner.mobile or partner.phone or '',
                'default_body': body,
                'default_res_model': 'sale.order',
                'default_res_id': self.id,
            },
        }
