from Modules import credentials
import smtplib
import imaplib
import email
import datetime


def send_notification(
    subject: str,
    body: str,
    passwords: credentials.PasswordManager,
    receivers: list = None,
    carbonCopy: list = None,
    hiddenCarbonCopy: list = None,
):
    """
    Send a notification email.

    Args:
        - subject (str): The subject of the email.
        - body (str): The body of the email.
        - passwords (credentials.PasswordManager): The password manager to get credentials.
        - receivers (list): List of email addresses to send the email to.
        - carbonCopy (list): List of email addresses to send a carbon copy to.
        - hiddenCarbonCopy (list): List of email addresses to send a blind carbon copy to.

    Returns:
        - None
    """
    msg = email.message.EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject

    if receivers:
        msg["To"] = ", ".join(receivers)

    if carbonCopy:
        msg["CC"] = ", ".join(carbonCopy)

    if hiddenCarbonCopy:
        hiddenCarbonCopy.append(passwords.getValue("reciever"))
        msg["BCC"] = ", ".join(hiddenCarbonCopy)
    else:
        msg["BCC"] = passwords.getValue("reciever")

    if not (receivers or carbonCopy or hiddenCarbonCopy):
        msg["To"] = passwords.getValue("reciever")

    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    msg["From"] = passwords.getValue("username")

    if notCheckIfAlready(msg, passwords):
        sendMail(smtp_server, smtp_port, passwords, msg)


def sendMail(smtpServer, smtpPort, passwords: credentials.PasswordManager, message):
    with smtplib.SMTP(smtpServer, smtpPort) as server:
        server.ehlo()
        server.starttls()
        server.login(passwords.getValue("username"), passwords.getValue("password"))
        server.send_message(message)
        print("Mail sent")


def notCheckIfAlready(
    message: email.message.EmailMessage, passwords: credentials.PasswordManager
) -> bool:
    """
    Check if the email has already been sent today.

    Args:
        - message (email.message.EmailMessage): The email message to check.
        - passwords (credentials.PasswordManager): The password manager to get credentials.

    Returns:
        - bool: True if the email has not been sent, False otherwise.
    """  # Set your email and password
    email_address = passwords.getValue("username")
    password = passwords.getValue("password")

    # Connect to the IMAP server
    with imaplib.IMAP4_SSL("imap.gmail.com") as mail:
        # Login to your email account
        mail.login(email_address, password)

        # Select the mailbox you want to read emails from (e.g., "inbox")
        mail.select('"[Gmail]/Sent Mail"')

        currentDate = datetime.date.today()

        # Search for all emails sent today
        status, messages = mail.search(
            None, f'SINCE "{currentDate.strftime("%d-%b-%Y")}"'
        )

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

            if subject == message["Subject"] and to_ == message["To"]:
                return False

        return True


def decodePartMessage(message, part):
    parts = email.header.decode_header(message.get(part))
    decodedMessage = ""
    for part, encoding in parts:
        if isinstance(part, bytes):
            decodedMessage += part.decode(encoding or "utf-8")
        else:
            decodedMessage += part
    return decodedMessage
