====================================================
WhatsApp Cloud API Connector — Documentation
====================================================

.. contents:: Table of Contents
   :depth: 2
   :local:

----

1. Getting Started
==================

Prerequisites
-------------

Before installing, make sure your environment meets these requirements:

.. warning::
   Meta requires a **payment method**, **completed business profile**, and optionally
   **business verification** before WhatsApp messages will actually be delivered.
   The API will accept messages without these, but they will NOT arrive.

+----------------------------+----------------------------------------------------------------+
| Requirement                | Description                                                    |
+============================+================================================================+
| Meta Developer Account     | Register at ``developers.facebook.com``                        |
+----------------------------+----------------------------------------------------------------+
| WhatsApp Business Account  | Linked to your Meta app with the WhatsApp product added        |
+----------------------------+----------------------------------------------------------------+
| System User Token          | Permanent token with ``whatsapp_business_management`` and      |
|                            | ``whatsapp_business_messaging`` permissions                    |
+----------------------------+----------------------------------------------------------------+
| Payment Method             | Credit/debit card in Meta Business Suite → Billing             |
+----------------------------+----------------------------------------------------------------+
| Business Profile           | Legal Name, Country, Website filled in Business Settings       |
+----------------------------+----------------------------------------------------------------+
| Public HTTPS Domain        | Required only for webhook (incoming messages)                  |
+----------------------------+----------------------------------------------------------------+

.. tip::
   If you are developing locally, use `ngrok <https://ngrok.com>`_ to create
   a temporary HTTPS tunnel to your local Odoo instance for webhook testing.


Installation
------------

1. Upload the ``sm_whatsapp`` module folder to your server's **custom addons directory**.
2. **Restart** the Odoo service to detect the new module.
3. Navigate to **Apps** menu, click **Update Apps List**.
4. Search for **"WhatsApp Connector"** and click **Install**.

.. note::
   After installation, a new **WhatsApp** top-level menu will appear in the main menu bar.
   All message management, templates, and configuration are accessible from there.

----

2. Meta Developer Setup
=======================

To get started, you need to create a Meta Developer App with the WhatsApp product.

Step 1: Create App
------------------

1. Go to **developers.facebook.com** and log in.
2. Click **My Apps** → **Create App**.
3. Select app type: **Business**.
4. Give your app a name (e.g. "Odoo WhatsApp").
5. Add the **WhatsApp** product to your app.

Step 2: Get API Credentials
----------------------------

1. In Meta Developer Console, go to **WhatsApp → API Setup**.
2. Copy the following values:

   :Phone Number ID:
       The unique ID of your WhatsApp phone number.

   :WhatsApp Business Account ID:
       Found on the same API Setup page.

   :App Secret:
       Found in **App Settings → Basic**.

Step 3: Create System User & Permanent Token
----------------------------------------------

1. Go to **Meta Business Suite → Settings → System Users**.
2. Click **Add** to create a new System User (e.g. "odoo_bot").
3. Set role to **Admin**.
4. Click **Add Assets** → select your WhatsApp app → grant **Full Control**.
5. Click **Generate Token** → select the app.
6. Add permissions:

   - ``whatsapp_business_management``
   - ``whatsapp_business_messaging``

7. Copy the generated token — this is your **permanent API token**.

.. important::
   **Keep your token secure!** Anyone with access to this token can send messages
   from your WhatsApp Business Account. Never share it publicly.

----

3. Phone Number Registration
=============================

Meta provides a **test phone number** for development. You can also add your own
business phone number.

Test Phone Number
-----------------

- The test phone number is available immediately in **WhatsApp → API Setup**.
- In **Development mode**, you must add recipient numbers as **test recipients**.
- Go to API Setup → scroll to "To" field → **Manage phone number list** → add numbers.

Own Business Number
-------------------

- To use your own phone number, register it in **WhatsApp → Phone Numbers → Add Phone Number**.
- The number must NOT be currently registered with any WhatsApp account (personal or business).
- Follow Meta's verification process (SMS or voice call OTP).

----

4. Business Requirements
========================

.. warning::
   These requirements are **mandatory** for actual message delivery.

Payment Method
--------------

1. Go to **Meta Business Suite → Billing → Payment Methods**.
2. Add a valid credit or debit card.
3. Without this, Meta will accept API calls but **block delivery** (error 141006).

Business Profile
-----------------

1. Go to **Meta Business Suite → Settings → Business Info**.
2. Fill in:

   - **Legal Business Name**
   - **Country**
   - **Website URL**

3. Incomplete profile causes error 131000 and delivery blocks.

Business Verification (Recommended)
-------------------------------------

1. Go to **Meta Business Suite → Settings → Security Center → Start Verification**.
2. Submit required documents.
3. Verification removes messaging limits and enables full production access.

----

5. Odoo Configuration
=====================

Step 1: Module Settings
-----------------------

1. After installing, go to **Settings → WhatsApp** section.
2. Fill in the following fields:

+----------------------------+--------------------------------------------------------------+
| Setting                    | Where to find it                                             |
+============================+==============================================================+
| **API Token**              | The permanent token from your System User                    |
+----------------------------+--------------------------------------------------------------+
| **Phone Number ID**        | Meta Developer Console → WhatsApp → API Setup                |
+----------------------------+--------------------------------------------------------------+
| **Business Account ID**    | Meta Developer Console → WhatsApp → API Setup                |
+----------------------------+--------------------------------------------------------------+
| **API Version**            | Default: ``v25.0`` (leave as-is unless you know a newer one) |
+----------------------------+--------------------------------------------------------------+
| **Webhook Verify Token**   | Any random string; must match what you set in Meta Console   |
+----------------------------+--------------------------------------------------------------+
| **App Secret**             | From App Settings → Basic in Meta Developer Console          |
+----------------------------+--------------------------------------------------------------+

3. Click **Test Connection** to verify.

Step 2: Webhook Setup (Optional)
---------------------------------

Only needed if you want to **receive** incoming WhatsApp messages in Odoo.

1. In Meta Developer Console → WhatsApp → **Configuration** → Webhook.
2. Click **Edit** and set:

   :Callback URL:
       ``https://your-odoo-domain.com/whatsapp/webhook``

   :Verify Token:
       Same value as in Odoo Settings.

3. Click **Verify and Save**.
4. Subscribe to webhook fields:

   - ``messages`` — for incoming messages
   - ``message_template_status_update`` — for template status changes

Step 3: Sync Templates
-----------------------

1. Go to **WhatsApp → Templates**.
2. Click **Sync Templates from Meta**.
3. All approved templates from your WhatsApp Business Account are imported.
4. Templates are categorized as: Marketing, Utility, or Authentication.

----

6. Sending Messages
====================

From Contacts
-------------

1. Open any **Contact** (res.partner).
2. Make sure the WhatsApp number field is filled.
3. Click the **Send WhatsApp** button in the header.
4. In the composer wizard, write your message or select a template.
5. Click **Send**.

From Sales Orders
------------------

1. Open any **Sales Order**.
2. Click the **Send WhatsApp** button.
3. The message is pre-filled with order number, total amount, and currency.
4. Edit if needed, then click **Send**.

From Invoices
--------------

1. Open any **Invoice** (Customer Invoice).
2. Click the **Send WhatsApp** button.
3. The message is pre-filled with invoice number, amount, due date, and currency.
4. Edit if needed, then click **Send**.

Bulk Messaging
--------------

1. In the composer wizard, add **multiple recipients**.
2. Each recipient receives an individual WhatsApp message.
3. Delivery status is tracked per recipient.

----

7. Message Tracking
====================

All messages are tracked in **WhatsApp → Messages** with the following statuses:

+-------------------+------------------------------------------------------------+
| Status            | Description                                                |
+===================+============================================================+
| **Draft**         | Message created but not yet sent                           |
+-------------------+------------------------------------------------------------+
| **Sent**          | Successfully sent via API (accepted by Meta)               |
+-------------------+------------------------------------------------------------+
| **Delivered**     | WhatsApp confirmed delivery to recipient's device          |
+-------------------+------------------------------------------------------------+
| **Read**          | Recipient has read the message (blue ticks)                |
+-------------------+------------------------------------------------------------+
| **Failed**        | Error occurred — details shown in error message field      |
+-------------------+------------------------------------------------------------+

Failed messages can be **retried** with the Retry button.

----

8. Troubleshooting
===================

+----------------------------------------------+--------------------------------------------------------------+
| Problem                                      | Solution                                                     |
+==============================================+==============================================================+
| Messages accepted but not delivered          | Add a **payment method** in Meta Business Suite. Complete     |
|                                              | business profile (Legal Name, Country, Website).             |
+----------------------------------------------+--------------------------------------------------------------+
| Error: Account not registered (#133010)      | Recipient doesn't have WhatsApp, or not added as test        |
|                                              | recipient in Development mode.                               |
+----------------------------------------------+--------------------------------------------------------------+
| Error: Token could not be decrypted          | API token is invalid or expired. Generate a new permanent    |
|                                              | token from System User.                                      |
+----------------------------------------------+--------------------------------------------------------------+
| Webhook verification failed                  | Verify Token in Odoo must match exactly with Meta Console.   |
|                                              | Odoo server must be publicly accessible via HTTPS.           |
+----------------------------------------------+--------------------------------------------------------------+
| Test Connection failed                       | Check API Token and Phone Number ID. Ensure network          |
|                                              | connectivity from Odoo server to graph.facebook.com.         |
+----------------------------------------------+--------------------------------------------------------------+
| Template sync returns empty                  | Make sure Business Account ID is correct and you have        |
|                                              | approved templates in Meta Business Manager.                 |
+----------------------------------------------+--------------------------------------------------------------+

----

9. Security
===========

- All API calls use **Bearer token** authentication over HTTPS.
- Incoming webhooks are verified using **HMAC-SHA256** signature (using App Secret).
- Webhook endpoint validates the **verify token** during initial handshake.
- Access control: **WhatsApp User** (send/view) and **WhatsApp Manager** (full access).
- API tokens are stored as ``ir.config_parameter`` system parameters.

----

10. Technical Reference
========================

Models
------

- ``whatsapp.message`` — Main message model (text, template, status tracking)
- ``whatsapp.template`` — Meta-approved message templates synced from API
- ``whatsapp.composer`` — Transient wizard for composing & sending messages

Endpoints
---------

- ``GET /whatsapp/webhook`` — Webhook verification (Meta handshake)
- ``POST /whatsapp/webhook`` — Receive incoming messages & status updates

API Calls
----------

- ``GET /v25.0/{phone_number_id}`` — Test connection / verify credentials
- ``POST /v25.0/{phone_number_id}/messages`` — Send text or template message
- ``GET /v25.0/{waba_id}/message_templates`` — Sync templates from Meta

Configuration Parameters
-------------------------

- ``sm_whatsapp.api_token`` — Permanent API token
- ``sm_whatsapp.phone_number_id`` — WhatsApp Phone Number ID
- ``sm_whatsapp.business_account_id`` — WhatsApp Business Account ID
- ``sm_whatsapp.api_version`` — Graph API version (default: v25.0)
- ``sm_whatsapp.webhook_verify_token`` — Webhook verify token
- ``sm_whatsapp.app_secret`` — Meta App Secret for HMAC verification
