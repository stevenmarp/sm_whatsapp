# -*- coding: utf-8 -*-
from odoo import models, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_send_whatsapp(self):
        """Open WhatsApp composer with pre-filled invoice info."""
        self.ensure_one()
        partner = self.partner_id
        due_date = self.invoice_date_due or ''
        body = _(
            "Dear %(name)s,\n\n"
            "Your invoice *%(invoice)s* for *%(currency)s %(amount)s* is ready.\n"
            "Payment due: *%(due)s*\n\n"
            "Thank you!",
            name=partner.name,
            invoice=self.name or 'Draft',
            currency=self.currency_id.symbol,
            amount=f"{self.amount_total:,.2f}",
            due=due_date,
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
                'default_res_model': 'account.move',
                'default_res_id': self.id,
            },
        }
