import sys
import json
import numpy as np
import matplotlib.pyplot as plt
from weasyprint import HTML
from datetime import datetime

import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import ticket_tailor

# pdfkit.from_file('report.html', 'out.pdf')

def tr_1(event_name, event_total_tickets, event_tickets_issued, event_tickets_remaining):
    return f"""
        <tr>
            <td class="la_text">{event_name}</td>
            <td>{event_total_tickets}</td>
            <td>{event_tickets_issued}</td>
            <td>{event_tickets_remaining}</td>
        </tr>
    """

def slot_tr(slots):
    slot_trs = ""
    for s in slots:
        slot_trs += f"""
            <tr>
                <td>{s['start_time']}</td>
                <td>{s['total_issued_tickets']}</td>
                <td>{s['remaining_tickets']}</td>
            </tr>
        """
    return slot_trs

# detailed table rows
def dtrs(slots, event_name, summary):
    num_slots = len(slots)
    return f"""
    <table style="break-inside: avoid">
        <tbody>
            <tr style="border-top: 1px solid var(--border);">
                <td rowspan="{num_slots + 2}" class="la_text"><strong>{event_name}</strong></td>
                <td colspan="3">
            </tr>
            {slot_tr(slots)}
            <tr style="border-bottom: 1px solid var(--border);">
                <td><strong>Totals</strong></td>
                <td><strong>{summary['total_issued_tickets']}</strong></td>
                <td><strong>{summary['remaining_tickets']}</strong></td>
            </tr>
        </tbody>
    </table>
    """

def get_detailed_tables(events):
    details_tables = []
    for event in events:
        event_summ = events[event]['summary']
        event_slots = events[event]['time_slots']
        event_name = event.replace('Car Parking - ', '')

        details_tables.append(
            dtrs(event_slots, event_name, event_summ)
        )
    return "\n".join(details_tables)

def make_graph(venue_name, events):
    x = []
    yi = []
    yr = []
    for event in events:
        x.append(event.replace('Car Parking - ', ''))
        summary = events[event]['summary']
        yi.append(summary['total_issued_tickets'])
        yr.append(summary['remaining_tickets'])

    barWidth = 0.2
    fig = plt.subplots(facecolor='#ede6ff')
    br1 = np.arange(len(yi))
    br2 = [x + barWidth for x in br1]

    plt.title('Car Parking Sales Report')

    #5f01ee   purple
    #00e4ad   green
    #ede6ff   pink

    #70777f   text

    plt.bar(br1, yi, color ='#00e4ad', width=barWidth, edgecolor ='#f1f1f1', label ='Sold')
    plt.bar(br2, yr, color ='#5f01ee', width=barWidth, edgecolor ='#f1f1f1', label ='Available')

    plt.xlabel('Event')
    plt.ylabel('Tickets')
    plt.xticks(
        [r + (barWidth/2) for r in range(len(yi))],
        x,
        rotation=35,
        ha='right',
        rotation_mode='anchor'
    )
    plt.tight_layout()
    plt.legend()
    # plt.show()
    fig_location = f"images/{venue_name.replace(' ', '_')}.svg"
    plt.savefig(fig_location)

    return fig_location


def get_summary_trs(events):
    summary_trs = []
    for event in events:
        event_summ = events[event]['summary']
        event_name = event.replace('Car Parking - ', '')
        summary_trs.append(
            tr_1(
                event_name,
                event_summ['total_tickets'],
                event_summ['total_issued_tickets'],
                event_summ['remaining_tickets']
            )
        )
    return "\n".join(summary_trs)

def gen_report_html(venue, events):
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Car Parking Sales Report</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/water.css@2/out/light.min.css">
        <link rel="stylesheet" href="styles/evntz_reports.css">
    </head>
    <header style="display:flex;">
        <div style="flex-basis: 65%">
            <h1 style="margin-top: 0px;">{venue}</h1>
            Date: {datetime.now().strftime("%d/%m/%Y")}<br/>
            Time: {datetime.now().strftime("%H:%M")}
        </div>
        <div style="flex-basis: 35%; border-left: 1px solid var(--border); padding-left: 10px;">
            <h2 style="margin-top: 0px; margin-bottom: 8px;">Car Parking<br/>Ticket Sales Report</h2>
            <img style="height: 44px; width: 160px;" src="https://uploads.tickettailor.com/c_limit,w_630/v1/production/userfiles/event_description_image_136857_1750111853_10ec2.png?_a=BAAAV6DQ">
        </div>
    </header>
    <body>
        <hr>
        <h4 style="text-align: center;">All Events Summary</h4>
        <table>
            <thead>
                <th style="width:30%">Event</th>
                <th>Total Tickets</th>
                <th>Tickets Issued</th>
                <th>Tickets Remaining</th>
            </thead>
            <tbody>
                {get_summary_trs(events)}
            </tbody>
        </table>

        <img src="{make_graph(venue, events)}" width="90%" style="break-after: page; display: block; margin-left: auto; margin-right: auto; width: 95%;">

        <h3 style="text-align: center;">Event Details</h3>
        <table>
            <thead>
                <tr>
                    <th>Event</th>
                    <th>Start Time</th>
                    <th>Tickets Issued</th>
                    <th>Ticket Remaining</th>
                </tr>
            </thead>
        </table>
        {get_detailed_tables(events)}
    </body>
    </html>
    """

# with open('all.json', 'r') as sjson:
#     venues = json.load(sjson)

def send_email(venue, filename):
    sender_email = "bryanoneill10@gmail.com"
    sender_password = "mtoe eadz suol rwrj"
    receiver_email = "killian.martin@gmail.com"
    cc = "bryanoneill10@gmail.com"

    # Email content
    subject = f"{venue} - Car Parking Sales Report"
    body = (
        "Hi,\n\n"
        f"Please see latest sales report for {venue} attached.\n\n"
        "Many thanks,\n"
        "Evntz Team"
    )
    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Cc"] = cc
    # Add body to email
    message.attach(MIMEText(body, "plain"))
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
        # server.sendmail(sender_email, receiver_email, message.as_string())
        server.send_message(message)

venues = ticket_tailor.get_all_upcoming_venues_dict()

for venue in venues:
    filename = f"{venue.replace(' ', '_')}"
    html_report = gen_report_html(venue, venues[venue])
    with open(f"{filename}.html", 'w') as html_out:
        html_out.writelines(html_report)

    # html = HTML(string=html_report)
    html = HTML(filename=f"{filename}.html")
    html.write_pdf(
        f"{filename}.pdf",
        presentational_hints=True,
        optimize_images=True
    )
    send_email(venue, f"{filename}.pdf")