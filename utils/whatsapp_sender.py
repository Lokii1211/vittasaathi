from utils.twilio_client import client, WHATSAPP_FROM

def send_whatsapp_message(to_number, message):
    client.messages.create(
        from_=WHATSAPP_FROM,
        body=message,
        to=f"whatsapp:{to_number}"
    )
