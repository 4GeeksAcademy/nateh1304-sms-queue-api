import os
from twilio.rest import Client

def send_SMS(body, to):
    account_sid = os.environ["TWILIO_ACCOUNT_SID"]
    auth_token = os.environ["TWILIO_AUTH_TOKEN"]

    twilio_client = Client(account_sid, auth_token)
    message = twilio_client.messages.create(
        body= body,
        from_= "+18444120247",
        to= to,
    )

    print(message.body)
