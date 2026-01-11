from utils.twilio_client import client

def make_fraud_call(to_number, message):
    twiml = f"""
    <Response>
        <Say language="en">{message}</Say>
    </Response>
    """

    client.calls.create(
        to=to_number,
        from_="+14155238886",  # Twilio voice number
        twiml=twiml
    )

