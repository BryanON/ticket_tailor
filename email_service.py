"""Email service for sending reports via SMTP."""
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import EMAIL_CONFIG


def send_report_email(venue_name, pdf_filename, recipients=None, cc_recipients=None):
    """
    Send an email with the PDF report attached.
    
    Args:
        venue_name: Name of the venue for the subject line
        pdf_filename: Path to the PDF file to attach
        recipients: List of email addresses to send to. If None, uses EMAIL_CONFIG defaults
        cc_recipients: List of CC email addresses. If None, uses EMAIL_CONFIG defaults
        
    Raises:
        smtplib.SMTPAuthenticationError: If email credentials are invalid
        FileNotFoundError: If the PDF file doesn't exist
        ValueError: If no valid recipients are provided
    """
    sender_email = EMAIL_CONFIG['sender_email']
    sender_password = EMAIL_CONFIG['sender_password']
    
    # Use provided recipients or fall back to config defaults
    if recipients is None:
        to_emails = [EMAIL_CONFIG['receiver_email']]
    else:
        to_emails = recipients if isinstance(recipients, list) else [recipients]
    
    # Use provided CC recipients or fall back to config defaults
    if cc_recipients is None:
        cc_emails = [EMAIL_CONFIG['cc']] if EMAIL_CONFIG['cc'] else []
    else:
        cc_emails = cc_recipients if isinstance(cc_recipients, list) else [cc_recipients]
    
    if not to_emails:
        raise ValueError(f"No valid recipients configured for venue: {venue_name}")

    # Email content
    subject = f"{venue_name} - Car Parking Sales Report"
    body = (
        "Hi,\n\n"
        f"Please see latest sales report for {venue_name} attached.\n\n"
        "Many thanks,\n"
        "Evntz Team"
    )

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = ", ".join(to_emails)
    message["Subject"] = subject
    if cc_emails:
        message["Cc"] = ", ".join(cc_emails)

    # Add body to email
    message.attach(MIMEText(body, "plain"))

    # Open the file in binary mode and attach
    with open(pdf_filename, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    # Encode file in ASCII characters to send by email
    encoders.encode_base64(part)

    # Add header as key/value pair to attachment part
    part.add_header("Content-Disposition", f"attachment; filename= {pdf_filename}")

    # Add attachment to message
    message.attach(part)

    # Send the email
    try:
        with smtplib.SMTP_SSL(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port']) as server:
            server.login(sender_email, sender_password)
            # Send to all recipients (to + cc)
            all_recipients = to_emails + cc_emails
            server.sendmail(sender_email, all_recipients, message.as_string())
            print(f"Email sent successfully for {venue_name} to {', '.join(to_emails)}")
    except smtplib.SMTPAuthenticationError:
        print(f"Error: Failed to authenticate with email service for {venue_name}")
        raise
    except Exception as e:
        print(f"Error sending email for {venue_name}: {e}")
        raise
