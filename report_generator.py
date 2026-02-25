"""Report generation utilities including graphs and data aggregation."""
import textwrap
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from config import COLORS, VENUE_PREFIX, OUTPUT_DIR


def generate_chart(venue_name, events, base_dir=None):
    """
    Generate a bar chart showing ticket sales data and save as SVG.
    
    Args:
        venue_name: Name of the venue
        events: Dictionary of events with their ticket data
        base_dir: Base directory for output. If None, uses current directory
        
    Returns:
        Path to the saved SVG file (relative to base_dir if provided, otherwise relative to cwd)
    """
    # Determine output directory
    if base_dir:
        output_dir = Path(base_dir) / OUTPUT_DIR
    else:
        output_dir = Path(OUTPUT_DIR)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    event_names = []
    issued_tickets = []
    remaining_tickets = []

    for event in events:
        event_names.append(event.replace(VENUE_PREFIX, ''))
        summary = events[event]['summary']
        issued_tickets.append(summary['total_issued_tickets'])
        remaining_tickets.append(summary['remaining_tickets'])

    bar_width = 0.2
    fig = plt.subplots(facecolor=COLORS['background'])
    bar_positions_1 = np.arange(len(issued_tickets))
    bar_positions_2 = [x + bar_width for x in bar_positions_1]

    plt.title('Car Parking Sales Report')
    plt.bar(bar_positions_1, issued_tickets, color=COLORS['sold'], 
            width=bar_width, edgecolor=COLORS['border'], label='Sold')
    plt.bar(bar_positions_2, remaining_tickets, color=COLORS['available'], 
            width=bar_width, edgecolor=COLORS['border'], label='Available')

    plt.xlabel('Event')
    plt.ylabel('Tickets')
    wrapped_names = [textwrap.fill(name, width=25) for name in event_names]
    plt.xticks(
        [r + (bar_width / 2) for r in range(len(issued_tickets))],
        wrapped_names,
        rotation=35,
        ha='right',
        rotation_mode='anchor',
    )
    plt.tight_layout()
    plt.legend()

    fig_location = output_dir / f"{venue_name.replace(' ', '_')}.svg"
    plt.savefig(str(fig_location))
    plt.close()

    # Return relative path for use in HTML
    return str(fig_location.relative_to(output_dir.parent))
