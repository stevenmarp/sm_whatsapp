# -*- coding: utf-8 -*-
from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    whatsapp_api_token = fields.Char(
        string='API Token',
        config_parameter='sm_whatsapp.api_token',
        help='Permanent token from Meta Developer Console → WhatsApp → API Setup',
    )
    whatsapp_phone_number_id = fields.Char(
        string='Phone Number ID',
        config_parameter='sm_whatsapp.phone_number_id',
        help='Phone Number ID from Meta Developer Console → WhatsApp → API Setup',
    )
    whatsapp_business_account_id = fields.Char(
        string='Business Account ID',
        config_parameter='sm_whatsapp.business_account_id',
        help='WhatsApp Business Account ID from Meta Business Suite',
    )
    whatsapp_webhook_verify_token = fields.Char(
        string='Webhook Verify Token',
        config_parameter='sm_whatsapp.webhook_verify_token',
        help='Custom token for webhook verification (you choose this)',
    )
    whatsapp_app_secret = fields.Char(
        string='App Secret',
        config_parameter='sm_whatsapp.app_secret',
        help='App Secret from Meta Developer Console → App Settings → Basic',
    )
    whatsapp_api_version = fields.Char(
        string='API Version',
        config_parameter='sm_whatsapp.api_version',
        default='v25.0',
    )

    def action_test_whatsapp_connection(self):
        """Test the WhatsApp API connection."""
        return self.env['whatsapp.message']._test_connection()

    def action_sync_whatsapp_templates(self):
        """Sync WhatsApp templates from Meta."""
        self.env['whatsapp.message']._sync_templates()
