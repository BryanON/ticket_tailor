
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sender_email = "bryanoneill10@gmail.com"
sender_password = "mtoe eadz suol rwrj"
receiver_email = "bryanoneill10@gmail.com"

# Email content
subject = f"{venue} - Car Parking Sales Report"
body = f"""Hi,

Please see latest sales report for {venue} attached.

Many thanks,
Evntz Team
"""

# Create a multipart message and set headers
message = MIMEMultipart()
message["From"] = sender_email
message["To"] = receiver_email
message["Subject"] = subject

# Add body to email
message.attach(MIMEText(body, "plain"))

# Specify the attachment file path

# Open the file in binary mode
with open(filename, "rb") as attachment:
    part = MIMEBase("application", "octet-stream")
    part.set_payload(attachment.read())

# Encode file in ASCII characters to send by email
encoders.encode_base64(part)

# Add header as key/value pair to attachment part
part.add_header("Content-Disposition", f"attachment; filename= {filename}")

# Add attachment to message
message.attach(part)



# Send the email
with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, receiver_email, message.as_string())

print('Sent')




# filename = "NEW_Malahide_Castle.html"
# # filename = "example.html"
# with open(filename, 'r') as html_out:
#     html_body = html_out.read()


# # html_message = MIMEText(body, 'html')
# html_message = EmailMessage()
# html_message['Subject'] = subject
# html_message['From'] = sender_email
# html_message['To'] = recipient_email
# html_message['']
# html_message.add_alternative(html_body, subtype='html')

# with open("NEW_Malahide_Castle.pdf", "rb") as pdf:
#   html_message.add_attachment(pdf.read())

# with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
#    server.login(sender_email, sender_password)
#    server.sendmail(sender_email, recipient_email, html_message.as_string())




