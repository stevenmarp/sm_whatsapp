Step 1: Create Meta Developer App
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Go to **developers.facebook.com** → My Apps → Create App.
2. Select app type: **Business**.
3. Add the **WhatsApp** product to your app.
4. Note your **App ID** and **App Secret** (from App Settings → Basic).

Step 2: Get API Credentials
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Go to WhatsApp → **API Setup**.
2. Copy your **Phone Number ID** and **Business Account ID**.
3. Create a **System User** in Meta Business Suite → Settings → System Users.
4. Generate a **permanent token** for the System User with permissions:
   ``whatsapp_business_management`` and ``whatsapp_business_messaging``.

Step 3: Register Phone Number
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. You can use the Meta **test phone number** or add your own business phone number.
2. Make sure the phone number is **registered** with WhatsApp Cloud API.
3. In **Development mode**, add test recipient numbers in API Setup.

Step 4: Complete Business Requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. warning::
   Meta requires the following for message delivery:

   - **Payment Method** — Add a credit/debit card in Meta Business Suite → Billing.
   - **Business Profile** — Fill in Legal Name, Country, and Website in Business Settings.
   - **Business Verification** — Start verification in Business Settings (recommended).

   Without a payment method, Meta will accept messages via API but will **NOT deliver them**.

Step 5: Configure Webhook (for incoming messages)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. In Meta Developer Console → WhatsApp → Configuration → Webhook.
2. Set Callback URL: ``https://your-odoo-domain.com/whatsapp/webhook``
3. Set Verify Token: same value as configured in Odoo Settings.
4. Subscribe to webhook fields: **messages** and **message_template_status_update**.

Step 6: Configure in Odoo
~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Install this module.
2. Go to **Settings → WhatsApp**.
3. Fill in all API credentials:

+----------------------------+--------------------------------------------------------------+
| Setting                    | Where to find it                                             |
+============================+==============================================================+
| API Token                  | Meta Business Suite → System Users → Generate Token          |
+----------------------------+--------------------------------------------------------------+
| Phone Number ID            | Meta Developer Console → WhatsApp → API Setup                |
+----------------------------+--------------------------------------------------------------+
| Business Account ID        | Meta Developer Console → WhatsApp → API Setup                |
+----------------------------+--------------------------------------------------------------+
| API Version                | Default: v25.0                                               |
+----------------------------+--------------------------------------------------------------+
| Webhook Verify Token       | You choose this — must match Meta Console                    |
+----------------------------+--------------------------------------------------------------+
| App Secret                 | Meta Developer Console → App Settings → Basic                |
+----------------------------+--------------------------------------------------------------+

4. Click **Test Connection** — should show your phone number and business name.
5. Click **Sync Templates from Meta** — imports all approved templates.
6. Done! Open any Contact and click **Send WhatsApp**.
