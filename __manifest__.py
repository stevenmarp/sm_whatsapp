# -*- coding: utf-8 -*-
{
    'name': 'WhatsApp Cloud API Connector',
    'version': '19.0.1.0.0',
    'summary': 'Connect Odoo to Meta WhatsApp Cloud API — send & receive messages from Contacts, Sales Orders, Invoices. No middleware, no monthly fees.',
    'description': """
WhatsApp Cloud API Connector for Odoo 19
==========================================

Direct connector to Meta WhatsApp Cloud API — no middleware, no monthly subscription:
- Send text & template messages from Contacts, Sales Orders, Invoices
- Receive incoming messages via webhook
- Track delivery status (sent, delivered, read)
- Message history & chat log per contact
- Bulk messaging to multiple contacts
- Sync & manage Meta-approved message templates
- Role-based access control (User / Manager)
- HMAC-SHA256 webhook security
- wa.me fallback when API is not configured
    """,
    'author': 'Steven Marp',
    'website': 'https://apps.odoo.com/apps/browse?repo_maintainer_id=512936',
    'category': 'Productivity/Discuss',
    'license': 'OPL-1',

    'depends': [
        'base',
        'mail',
        'contacts',
        'sale_management',
        'account',
    ],

    'data': [
        # Security
        'security/security.xml',
        'security/ir.model.access.csv',

        # Views
        'wizard/whatsapp_composer_views.xml',
        'views/res_config_settings_views.xml',
        'views/whatsapp_template_views.xml',
        'views/whatsapp_message_views.xml',
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
        'views/account_move_views.xml',
        'views/menu.xml',
    ],

    'assets': {},

    'images': ['static/description/banner.gif'],
    'price': 39.0,
    'currency': 'USD',
    'installable': True,
    'application': True,
    'auto_install': False,
}
