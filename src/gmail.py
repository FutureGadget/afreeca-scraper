import asyncio
from google_cred import get_cred
from googleapiclient.discovery import build
from googleapiclient import errors

from email.mime.text import MIMEText
from constants import EMAIL_RECIPIENTS

import base64


def create_message(to, subject, message_text):
    """Create a message for an email.

    Args:
      sender: Email address of the sender.
      to: Email address of the receiver.
      subject: The subject of the email message.
      message_text: The text of the email message.

    Returns:
      An object containing a base64url encoded email object.
    """
    message = MIMEText(message_text)
    message["to"] = to
    message["subject"] = subject
    return {"raw": base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")}


async def send_email_to(message):
    cred = await get_cred()
    service = build("gmail", "v1", credentials=cred, cache_discovery=False)

    try:
        message = await asyncio.to_thread(
            service.users().messages().send(userId="me", body=message).execute
        )
        print(f"Message Id: {message['id']}")
        return message
    except errors.HttpError as error:
        print(f"An error occured: {error}")


async def broadcast_to_enrolled_users(subject, message_text):
    cred = await get_cred()
    service = build("gmail", "v1", credentials=cred, cache_discovery=False)

    for recipients in EMAIL_RECIPIENTS:
        message = create_message(
            to=recipients, subject=subject, message_text=message_text
        )
        try:
            message = await asyncio.to_thread(
                service.users().messages().send(userId="me", body=message).execute
            )
            print(f"Message sent to {recipients}, messageId: {message['id']}")
        except errors.HttpError as error:
            print(f"An error occured: {error} sending email to {recipients}")


if __name__ == "__main__":
    broadcast_to_enrolled_users(subject="샤강도착", message_text="테스트")
