1. Place ``sm_whatsapp`` folder in your Odoo addons path.
2. Restart Odoo server.
3. Go to **Apps**, update the Apps List, search for *WhatsApp Cloud API Connector* and click **Install**.

Prerequisites
~~~~~~~~~~~~~

- A **Meta Developer Account** with a registered Business app.
- A **WhatsApp Business Account** linked to your Meta app.
- A permanent **System User token** with ``whatsapp_business_management`` and ``whatsapp_business_messaging`` permissions.
- For incoming messages: your Odoo instance must be accessible via a **public HTTPS** domain.

.. important::
   Meta requires a **payment method** and **completed business profile** (Legal Name, Country, Website)
   before messages will actually be delivered. Without these, the API will accept messages but NOT deliver them.
