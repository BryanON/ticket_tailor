"""HTML building utilities for generating report tables and components."""
from config import VENUE_PREFIX


def build_summary_row(event_name, total_tickets, issued_tickets, remaining_tickets):
    """Generate a table row for the summary table."""
    return f"""
        <tr>
            <td class="la_text">{event_name}</td>
            <td>{total_tickets}</td>
            <td>{issued_tickets}</td>
            <td>{remaining_tickets}</td>
        </tr>
    """


def build_slot_rows(slots):
    """Generate table rows for time slots."""
    slot_rows = ""
    for slot in slots:
        slot_rows += f"""
            <tr>
                <td>{slot['start_time']}</td>
                <td>{slot['total_issued_tickets']}</td>
                <td>{slot['remaining_tickets']}</td>
            </tr>
        """
    return slot_rows


def build_detailed_table(slots, event_name, summary):
    """Generate a detailed table for an event with all its time slots."""
    num_slots = len(slots)
    return f"""
    <table style="break-inside: avoid">
        <tbody>
            <tr style="border-top: 1px solid var(--border);">
                <td rowspan="{num_slots + 2}" class="la_text"><strong>{event_name}</strong></td>
                <td colspan="3">
            </tr>
            {build_slot_rows(slots)}
            <tr style="border-bottom: 1px solid var(--border);">
                <td><strong>Totals</strong></td>
                <td><strong>{summary['total_issued_tickets']}</strong></td>
                <td><strong>{summary['remaining_tickets']}</strong></td>
            </tr>
        </tbody>
    </table>
    """


def build_summary_table_rows(events):
    """Build all summary table rows from events."""
    summary_rows = []
    for event in events:
        event_summary = events[event]['summary']
        event_name = event.replace(VENUE_PREFIX, '')
        summary_rows.append(
            build_summary_row(
                event_name,
                event_summary['total_tickets'],
                event_summary['total_issued_tickets'],
                event_summary['remaining_tickets']
            )
        )
    return "\n".join(summary_rows)


def build_detailed_tables(events):
    """Build all detailed tables from events."""
    detailed_tables = []
    for event in events:
        event_summary = events[event]['summary']
        event_slots = events[event]['time_slots']
        event_name = event.replace(VENUE_PREFIX, '')

        detailed_tables.append(
            build_detailed_table(event_slots, event_name, event_summary)
        )
    return "\n".join(detailed_tables)
