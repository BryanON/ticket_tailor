"""Main module for generating and emailing ticket sales reports."""
import argparse
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
from weasyprint import HTML
import ticket_tailor
from config import REPORT_CONFIG, STYLES, VENUES_WHITELIST, VENUE_EMAIL_CONFIG
from html_builder import build_summary_table_rows, build_detailed_tables
from report_generator import generate_chart
from email_service import send_report_email

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).resolve().parent

# Reports directory relative to script location
REPORTS_DIR = SCRIPT_DIR / "reports"
REPORTS_DIR.mkdir(exist_ok=True)


def generate_html_report(venue, events, show_totals=False):
    """
    Generate the HTML report for a venue and its events.
    
    Args:
        venue: Name of the venue
        events: Dictionary of events with ticket data
        
    Returns:
        HTML string for the report
    """
    chart_path = generate_chart(venue, events, base_dir=REPORTS_DIR)
    
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>{REPORT_CONFIG['title']}</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/water.css@2/out/light.min.css">
        <link rel="stylesheet" href="styles/evntz_reports.css">
    </head>
    <header style="display:flex;">
        <div style="flex-basis: 65%">
            <h1 style="margin-top: 0px;">{venue}</h1>
            Date: {datetime.now(ZoneInfo("Europe/Dublin")).strftime(REPORT_CONFIG['date_format'])}<br/>
            Time: {datetime.now(ZoneInfo("Europe/Dublin")).strftime(REPORT_CONFIG['time_format'])}
        </div>
        <div style="flex-basis: 35%; border-left: 1px solid var(--border); padding-left: 10px;">
            <h2 style="margin-top: 0px; margin-bottom: 8px;">Car Parking<br/>Ticket Report</h2>
            <img style="height: 44px; width: 160px;" src="{REPORT_CONFIG['logo_url']}">
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
                {build_summary_table_rows(events, show_totals=show_totals)}
            </tbody>
        </table>

        <img src="{chart_path}" width="90%" style="break-after: page; display: block; margin-left: auto; margin-right: auto; width: 95%;">

        <h3 style="text-align: center;">Event Details</h3>
        <table>
            <thead>
                <tr>
                    <th>Event</th>
                    <th>Start Time</th>
                    <th>Tickets Issued</th>
                    <th>Tickets Remaining</th>
                </tr>
            </thead>
        </table>
        {build_detailed_tables(events)}
    </body>
    </html>
    """


def main():
    """Main function to generate reports and send emails for all venues."""
    parser = argparse.ArgumentParser(description="Generate and email ticket sales reports.")
    parser.add_argument(
        "--venue", action="append", dest="venues", metavar="VENUE",
        help="Venue name to process (can be repeated). Overrides VENUES_WHITELIST when provided.",
    )
    args = parser.parse_args()

    whitelist = args.venues if args.venues else VENUES_WHITELIST

    try:
        print(f"Running at {datetime.now(ZoneInfo('Europe/Dublin')).strftime('%Y-%m-%d %H:%M:%S')} IST")
        if not whitelist:
            print("Error: No venues specified. Pass --venue or configure VENUES_WHITELIST in config.py")
            return

        venues = ticket_tailor.get_all_upcoming_venues_dict()

        # Filter venues based on whitelist
        venues_to_process = {v: venues[v] for v in whitelist if v in venues}
        if not venues_to_process:
            print(f"Error: None of the specified venues found: {whitelist}")
            return
        
        for venue in venues_to_process:

            # Get email configuration for this venue
            venue_email_config = VENUE_EMAIL_CONFIG.get(venue)

            recipients = venue_email_config.get("recipients", [])
            cc_recipients = venue_email_config.get("cc", [])
            show_totals = venue_email_config.get("show_totals", True)

            # Generate filename with venue name and current date
            date_str = datetime.now().strftime("%Y%m%d")
            filename = f"{venue.replace(' ', '_')}_car_park_ticket_report_{date_str}"
            
            # Generate HTML report
            html_report = generate_html_report(venue, venues_to_process[venue], show_totals=show_totals)
            html_path = REPORTS_DIR / f"{filename}.html"
            with open(html_path, 'w') as html_file:
                html_file.write(html_report)
            
            # Convert HTML to PDF
            html = HTML(filename=str(html_path))
            pdf_path = REPORTS_DIR / f"{filename}.pdf"
            html.write_pdf(
                str(pdf_path),
                presentational_hints=True,
                optimize_images=True
            )
            
            if not venue_email_config:
                print(f"Warning: No email configuration found for {venue}. Skipping email.")
                continue
            
            if not recipients:
                print(f"Warning: No recipients configured for {venue}. Skipping email.")
                continue
            
            # Send email with PDF attachment
            send_report_email(venue, str(pdf_path), recipients=recipients, cc_recipients=cc_recipients)
            print(f"Report generated and sent for {venue}")
            
    except Exception as e:
        print(f"Error in main execution: {e}")
        raise


if __name__ == "__main__":
    main()