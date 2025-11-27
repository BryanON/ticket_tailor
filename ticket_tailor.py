#!/usr/bin/env python3

"""

API Docs: https://developers.tickettailor.com/#ticket-tailor-api

"""
import csv
import sys
import argparse
import requests
import json
from pprint import pprint
from datetime import datetime


API_BASE_URL='https://api.tickettailor.com'
AUTH_KEY='sk_5352_136857_520aa3bd8625edc9704ee9f570a20cf6'
P_NUM=0

def rest_get(endpoint, params={}):
    response = requests.get(
        url=API_BASE_URL + endpoint,
        headers={'Accept': 'application/json'},
        auth=(AUTH_KEY, ''),
        params=params
    )
    return response.json()

def get_event_series(past_events=False):
    print('Fetching event series list...')
    event_series_list = []
    next_link = '/v1/event_series'

    while next_link:
        events = rest_get(next_link)
        for event in events['data']:
            if not past_events and not event['upcoming_occurrences']:
                continue
            event['occurrences'] = get_occurrences(event['id'])
            event['date'] = event['occurrences'][0]['start']['date']
            event_series_list.append(event)

        next_link = events['links']['next']

    return sorted(event_series_list, key=lambda d: d['date'])

# def get_event_date(event):
#     # TODO: avoid fetching occurrences here and again in main.
#     occurrence = get_occurrences(event['id'])[0]
#     return occurrence['start']['date']

def get_occurrences(event_series_id):
    #print(f'Fetching occurrences list for event series {event_series_id} ...')
    return rest_get(f"/v1/event_series/{event_series_id}/events")['data']

def get_issued_tickets(event_series_id):
    print(f'Fetching tickets for event series {event_series_id} ...')
    ticket_list = []
    next_link = ('/v1/issued_tickets', {'event_series_id': event_series_id})

    while next_link:
        tickets = rest_get(*next_link)
        ticket_list.extend(tickets['data'])

        next_link = tickets['links']['next']
        if next_link:
            next_link = (f"/v1{tickets['links']['next']}", {})

    return ticket_list

def get_check_in_times(event_series_id):
    print(f'Fetching check ins for event series {event_series_id} ...')
    check_in_dict = {}
    next_link = ('/v1/check_ins', {'event_series_id': event_series_id})

    while next_link:
        check_ins = rest_get(*next_link)
        for check_in in check_ins['data']:
            cid = check_in['issued_ticket_id']
            if 'check_in_at' in check_in:
                check_in_dict[cid] = datetime.fromtimestamp(
                        check_in['check_in_at']
                    ).strftime('%H:%M')

        next_link = check_ins['links']['next']
        if next_link:
            next_link = (f"/v1{check_ins['links']['next']}", {})

    return check_in_dict

def selector(event_series):
    '''Print enumerated list event_series'''

    event_series = sorted(event_series, key=lambda e: e['date'])

    for index, event in enumerate(event_series):
        print(f"{index:2d} - {event['date']} -- {event['name']}")

    event_index = int(input('Enter the number for the event you want: '))

    return event_series[event_index]

# Usage
#
# python3 ticket_tailor.py
#       - Generate a csv file listing upcoming events and ticket numbers
#
# python3 ticket_tailor.py --tickets
#       - Show list of upcoming event series to select
#       - Generate a csv of issued tickets for the selected event
#
# python3 ticket_tailor.py --sales YYYY-MM-DD
#       - Show list of event series from the date provided to select
#       - Generate a csv file listing ticket numbers for the selected event

def parse_args():
    parser = argparse.ArgumentParser(
        description="""Ticket Tailor API Helper Script"""
    )
    parser.add_argument(
        "--past_events",
        required=False,
        action='store_true',
        help="Show events from the past"
    )
    parser.add_argument(
        "--all",
        required=False,
        action='store_true',
        help="Show occurrences for all events, don't show selector"
    )
    option = parser.add_mutually_exclusive_group(required=True)
    option.add_argument(
        "--tickets",
        required=False,
        action='store_true',
        help="Generate a csv of issued tickets for the selected event"
    )
    option.add_argument(
        "--sales",
        required=False,
        action='store_true',
        help="Generate a csv file listing ticket numbers for the selected event"
    )

    return parser.parse_args()

def get_all_upcoming_venues_dict():

    event_series_list = get_event_series()
    _, venues_dict, _ = process_event_series(event_series_list)

    return venues_dict


def process_event_series(event_series_list, tickets=False):
    occurrences_dict = {}
    venues_dict = {}
    tickets_list = []
    for event_series in event_series_list:
        es_id = event_series['id']
        vname = event_series['venue']['name']
        ename = event_series['name']
        if vname not in venues_dict:
            venues_dict[vname] = {}

        if ename not in venues_dict[vname]:
            venues_dict[vname][ename] = {
                'time_slots': [],
                'summary': {
                    "date": '',
                    "total_tickets": 0,
                    "total_issued_tickets": 0,
                    "remaining_tickets": 0
                }

            }

        for occurrence in event_series['occurrences']:
            venues_dict[vname][ename]['summary']['date'] = occurrence['start']['date']

            total_tickets = 0
            for t_type in occurrence['ticket_types']:
                total_tickets += t_type['quantity_total']
            occurrences_dict[occurrence['id']] = {
                'name': event_series['name'],
                'venue': event_series['venue']['name'],
                'date': occurrence['start']['date'],
                'start_time': occurrence['start']['time'],
                'end_time': occurrence['end']['time'],
                'total_tickets': total_tickets,
                'total_issued_tickets': occurrence['total_issued_tickets'],
                'remaining_tickets': total_tickets - occurrence['total_issued_tickets'],
            }
            venues_dict[vname][ename]['time_slots'].append({
                'start_time': occurrence['start']['time'],
                'end_time': occurrence['end']['time'],
                'total_tickets': total_tickets,
                'total_issued_tickets': occurrence['total_issued_tickets'],
                'remaining_tickets': total_tickets - occurrence['total_issued_tickets'],
            })
            venues_dict[vname][ename]['summary']['total_tickets'] += total_tickets
            venues_dict[vname][ename]['summary']['total_issued_tickets'] += occurrence['total_issued_tickets']
            venues_dict[vname][ename]['summary']['remaining_tickets'] += total_tickets - occurrence['total_issued_tickets']

        if tickets:
            global P_NUM
            check_in_times = get_check_in_times(es_id)

            for ticket in get_issued_tickets(es_id):
                occurrence = occurrences_dict[ticket['event_id']]

                if P_NUM or ticket['barcode'] == '????':
                    pprint(ticket)
                    P_NUM -= 1

                tickets_list.append({
                    'first_name': ticket['first_name'],
                    'last_name': ticket['last_name'],
                    'barcode': ticket['barcode'],
                    'event_name': event_series['name'],
                    'date': occurrence['date'],
                    'start_time': occurrence['start_time'],
                    'status': ticket['status'],
                    'checked_in_time': check_in_times.get(ticket['id'], 'none')
                })
    return(occurrences_dict, venues_dict, tickets_list)

def main():

    args = parse_args()

    event_series_list = get_event_series(args.past_events)
    occurrences_dict = {}
    venues_dict = {}
    tickets_list = []

    if not args.all:
        event_series_list = [selector(event_series_list)]

    occurrences_dict, _, tickets_list = process_event_series(event_series_list, args.tickets)

    occurrences_list = sorted(occurrences_dict.values(), key=lambda d: d['date'])
    csv_file_name = f'sales_{datetime.now().strftime("%Y-%m-%d_%H%M%S")}.csv'
    csv_file_headers = occurrences_list[0].keys()
    csv_file_data = occurrences_list

    if args.tickets:
        event_name = tickets_list[0]['event_name'].replace(' ', '')
        csv_file_name = f'tickets_{event_name}_{datetime.now().strftime("%Y-%m-%d_%H%M%S")}.csv'
        csv_file_headers = tickets_list[0].keys()
        csv_file_data = sorted(tickets_list, key=lambda d: d['date'])

    with open(csv_file_name, 'w') as csv_file:
        dict_writer = csv.DictWriter(csv_file, csv_file_headers)
        dict_writer.writeheader()
        dict_writer.writerows(csv_file_data)

if __name__ == "__main__":
    main()