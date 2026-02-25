"""Configuration and constants for the reporting system."""
import os

# Email Configuration
EMAIL_CONFIG = {
    "sender_email": os.getenv("SENDER_EMAIL", "bryanoneill10@gmail.com"),
    "sender_password": os.getenv("SENDER_PASSWORD", "mtoe eadz suol rwrj"),
    "receiver_email": os.getenv("RECEIVER_EMAIL", "bryanoneill10@gmail.com"),
    "cc": os.getenv("CC_EMAIL", "bryanoneill10@gmail.com"),
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 465,
}

# Report Configuration
REPORT_CONFIG = {
    "title": "Car Parking Sales Report",
    "date_format": "%d/%m/%Y",
    "time_format": "%H:%M",
    "logo_url": "https://uploads.tickettailor.com/c_limit,w_630/v1/production/userfiles/event_description_image_136857_1750111853_10ec2.png?_a=BAAAV6DQ",
}

# Chart Colors
COLORS = {
    "sold": "#00e4ad",
    "available": "#5f01ee",
    "background": "#ede6ff",
    "text": "#70777f",
    "border": "#f1f1f1",
}

# String replacements
VENUE_PREFIX = "Car Parking - "

# Styling
STYLES = {
    "css_link": "https://cdn.jsdelivr.net/npm/water.css@2/out/light.min.css",
    "custom_css": "styles/evntz_reports.css",
}

# Output Configuration
OUTPUT_DIR = "images"

# Venue Whitelist - MANDATORY: Must specify venues to generate reports for
# Add venue names here, e.g., ["Venue Name 1", "Venue Name 2"]
VENUES_WHITELIST = [
    "Malahide Castle",
    "Marlay Park",
    "Slane Castle",
]

# Venue email configuration
# Maps venue names to their recipients and CC recipients
VENUE_EMAIL_CONFIG = {
    "Malahide Castle": {
        "recipients": ["killian@eventproduction.ie"],
        "cc": ["bryanoneill10@gmail.com"],
    },
    "Marlay Park": {
        "recipients": ["killian@eventproduction.ie"],
        "cc": ["bryanoneill10@gmail.com"],
    },
    "Slane Castle": {
        "recipients": ["killian@eventproduction.ie"],
        "cc": ["bryanoneill10@gmail.com"],
    },
    # Add more venues and their recipients as needed
    # "Another Venue": {
    #     "recipients": ["email1@example.com", "email2@example.com"],
    #     "cc": ["cc1@example.com"],
    # },
}
