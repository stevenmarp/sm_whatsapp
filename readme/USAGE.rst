Sending Messages
~~~~~~~~~~~~~~~~~

1. Open any document with a WhatsApp button (Contact, Sale Order, Invoice).
2. Click the **Send WhatsApp** button.
3. In the composer wizard:

   - Select **recipients** (partners with WhatsApp number).
   - Write your **message** or select a **template**.
   - Choose **text** or **template** message type.

4. Click **Send** — the message is delivered via Meta Cloud API.

Using Templates
~~~~~~~~~~~~~~~~

1. Go to **WhatsApp → Templates**.
2. Click **Sync Templates from Meta** to import approved templates.
3. Templates support **Marketing**, **Utility**, and **Authentication** categories.
4. Select a template in the composer wizard when sending messages.

Bulk Messaging
~~~~~~~~~~~~~~~

- In the send wizard, add **multiple recipients** to send the same message to all at once.
- Each recipient gets an individual message via WhatsApp.

wa.me Fallback
~~~~~~~~~~~~~~~

- If the API is not configured, the composer offers an **"Open in WhatsApp"** button.
- This opens a ``wa.me`` link directly in the browser — no API token needed.

Message Tracking
~~~~~~~~~~~~~~~~~

- Every sent message is logged in **WhatsApp → Messages**.
- Track delivery **status**: Draft → Sent → Delivered → Read → Failed.
- View the full **message content**, recipient, timestamp, and error details.
- Messages are also logged as **chatter notes** on the source document.

Technical Flow
~~~~~~~~~~~~~~~

1. Configuration stored in ``ir.config_parameter`` system parameters.
2. ``Test Connection`` calls ``GET /v25.0/{phone_number_id}`` to verify credentials.
3. ``Sync Templates`` calls ``GET /v25.0/{waba_id}/message_templates``.
4. Text messages sent via ``POST /v25.0/{phone_number_id}/messages`` with type ``text``.
5. Template messages sent via same endpoint with type ``template``.
6. Webhook endpoint at ``/whatsapp/webhook`` handles incoming messages & status updates.
7. HMAC-SHA256 signature verification secures all incoming webhook payloads.
8. Incoming messages auto-create contacts for unknown WhatsApp numbers.
9. Full audit trail via chatter notes + dedicated message log records.
