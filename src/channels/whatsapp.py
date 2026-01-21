import os
from twilio.rest import Client


class WhatsAppChannel:
    def __init__(self):
        """
        Initializes the WhatsAppChannel with Twilio client.
        """
        self.client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))

    def send_message(self, to_number, body):
        """
        Sends a WhatsApp message.
        """
        # Ensure environment variables exist
        from_number = os.getenv('FROM_WHATSAPP_NUMBER')
        if not from_number:
            raise RuntimeError("Missing FROM_WHATSAPP_NUMBER environment variable (should include 'whatsapp:+...')")

        # Normalize number formats
        if not str(to_number).startswith("whatsapp:"):
            to_number = f"whatsapp:{to_number}"

        try:
            message = self.client.messages.create(
                body=body,
                from_=from_number,
                to=to_number,
            )
            result = {"ok": True, "sid": getattr(message, "sid", None)}
            print(f"Twilio: message sent to {to_number}, SID={result['sid']}")
            return result
        except Exception as e:
            # Re-raise after logging so callers can handle/report errors
            print(f"Twilio send failed to {to_number}: {e}")
            raise

    def receive_messages(self):
        """
        Receiving messages is handled via webhooks.

        This method is not implemented because incoming WhatsApp messages are typically received through a webhook configured in the Twilio account. 
        The webhook sends an HTTP request to our server when a message is received.
        """
        pass 