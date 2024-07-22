import smtplib
import imaplib
import email
from Modules import FileHandling
import datetime
import os


def send_notification(subject, body, receivers = None, carbonCopy = None, hiddenCarbonCopy = None):
    msg = email.message.EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    data = FileHandling.openJson(os.path.join(os.path.dirname((os.path.dirname(os.path.abspath(__file__)))), "Password.json"))

    if receivers:
        msg["To"] = ", ".join(receivers)

    if carbonCopy:
        msg["CC"] = ", ".join(carbonCopy)

    if hiddenCarbonCopy:
        msg["BCC"] = ", ".join(hiddenCarbonCopy)
        
    elif not(receivers or carbonCopy or hiddenCarbonCopy):
        msg["To"] = data["reciever"]

    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    
    username = data["username"]
    msg["From"] = username
    password = data["password"]

    if notCheckIfAlready(msg):
        sendMail(smtp_server, smtp_port, username, password, msg)


def sendMail(smtpServer, smtpPort, username, password, message):
    with smtplib.SMTP(smtpServer, smtpPort) as server:
        server.ehlo()
        server.starttls()
        server.login(username, password)
        server.send_message(message)
        print("Mail sent")

def notCheckIfAlready(message):

    # Set your email and password
    data = FileHandling.openJson(os.path.join(os.path.dirname((os.path.dirname(os.path.abspath(__file__)))), "Password.json"))
    email_address = data["username"]
    password = data["password"]

    # Connect to the IMAP server
    with imaplib.IMAP4_SSL("imap.gmail.com") as mail:
        # Login to your email account
        mail.login(email_address, password)

        # Select the mailbox you want to read emails from (e.g., "inbox")
        mail.select('"[Gmail]/Sent Mail"')

        currentDate = datetime.date.today()

        # Search for all emails sent today
        status, messages = mail.search(None, f'SINCE "{currentDate.strftime("%d-%b-%Y")}"')

        message_ids = messages[0].split()

        # Loop through the message IDs and fetch the emails
        for message_id in message_ids:
            # Fetch the email by ID
            status, msg_data = mail.fetch(message_id, "(RFC822)")
            raw_email = msg_data[0][1]

            # Parse the raw email using the email library
            msg = email.message_from_bytes(raw_email)

            # Print the email subject and sender
            subject = decodePartMessage(msg, "Subject")

            to_ = decodePartMessage(msg, "To")

            if subject == message["Subject"] and to_== message["To"]:
                return False

        return True

def decodePartMessage(message, part):
    parts = email.header.decode_header(message.get(part))
    decodedMessage = ''
    for part, encoding in parts:
        if isinstance(part, bytes):
            decodedMessage += part.decode(encoding or 'utf-8')
        else:
            decodedMessage += part
    return decodedMessage
