#!/usr/bin/env python
import argparse
import requests
import time
from datetime import datetime, timedelta


def get_people(location_id):
    people = {}
    r = requests.get('http://hapk.digitaal-inschrijven.com/persons.json')
    for d in r.json()['data']:
        for l in d['items']:
            if location_id in l['locations']:
                people[l['name']['en']] = l['external']
    return people


def get_practices():
    practices = {}
    r = requests.get('http://hapk.digitaal-inschrijven.com/locations.json')
    for d in r.json()['data']:
        for l in d['items']:
            practices[l['name']['en']] = l
    return practices


def get_slots(calendar_ids, consult_blocks, date):
    slots = []
    r = requests.post('http://hapk.digitaal-inschrijven.com/scripts/getPeriods.php',
                      {
                          'calendar_id': ','.join([str(x) for x in calendar_ids]),
                          'consult_blocks': ','.join([str(x) for x in consult_blocks]),
                          'date': date
                      })
    data = r.json()
    if data['result']:
        for slot in data['slots']:
            slots.append('%s %s:%s' % (date, slot['hour'], slot['minute']))
    return slots


def list_practices():
    print('Practices:')
    for name, _ in get_practices().items():
        print('* %s' % name)


def find_next(practice_name, days):
    p = get_practices().get(practice_name, None)
    if not p:
        print('Could not find practice')
        return False

    print('Appointments:')
    for x in range(1, days):
        date = (datetime.today() + timedelta(days=x)).strftime('%Y-%m-%d')

        print('%s:' % date)
        entries = {}
        for name, eids in get_people(p['id']).items():
            for slot in get_slots(eids, p['external'], date):
                if slot not in entries:
                    entries[slot] = []
                entries[slot].append(name)

        if len(entries) == 0:
            print('  None')
        else:
            for date in sorted(
                entries,
                key=lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M")
            ):
                print('  %s: %s' % (date, ', '.join(entries[date])))
        print('')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--practice', '-p',
                        action='store',
                        default='City Centre, Westermarkt 2. 1016 DK')
    parser.add_argument('--list-practices', action='store_true')
    parser.add_argument('--days', '-d', action='store', default=3)
    args = parser.parse_args()

    if args.list_practices:
        list_practices()
    else:
        find_next(args.practice, args.days)
