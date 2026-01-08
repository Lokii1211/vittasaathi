from utils.twilio_client import client, WHATSAPP_FROM

def send_whatsapp_voice(to_number, audio_url):
    client.messages.create(
        from_=WHATSAPP_FROM,
        to=f"whatsapp:{to_number}",
        media_url=[audio_url]
    )
