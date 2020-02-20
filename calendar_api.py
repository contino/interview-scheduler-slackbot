#!/usr/local/bin/python3
from __future__ import print_function
import datetime
import dateutil.parser
from pytz import timezone
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import json

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
# INTERVIEW_AVAIL_CAL='contino.io_eepahmdv2bb1tvhbvv0ictha3g@group.calendar.google.com'
INTERVIEW_AVAIL_CAL = 'ashok.gadepalli@contino.io'
# calendar_timezone = 'America/New_York'

def get_service():

    creds = None

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    return service

def get_events_for_next_week(service,next_weekday,last_weekday,calendar):

    events_result = service.events().list(  calendarId=calendar,
                                            timeMin=next_weekday.isoformat() + 'Z',
                                            timeMax=last_weekday.isoformat() + 'Z',
                                            singleEvents=True,
                                            orderBy='startTime').execute()

    events = events_result.get('items', [])

    return events

def get_free_slots_for_week(service,calendar,next_weekday,last_weekday):

    calendar_timezone = get_calendar_tz(service,calendar)

    next_weekday = timezone(calendar_timezone).localize(next_weekday)
    last_weekday = timezone(calendar_timezone).localize(last_weekday)

    day_start_hour = 8 # 8am
    day_end_hour = 18 # 5pm
    duration = datetime.timedelta(hours=1) #interview length

    current_day = next_weekday

    slots_for_week = []

    while current_day < last_weekday:

        next_day = current_day + datetime.timedelta(days=1)
        
####

        body = {
            "timeMin": current_day.isoformat(),
            "timeMax": next_day.isoformat(),
            "timeZone": get_calendar_tz(service,calendar),
            "items": [{"id": calendar}]
        }
        
        eventsResult = service.freebusy().query(body=body).execute()
        
####

        current_day_busy_events = eventsResult["calendars"][calendar]["busy"]

        day_start_time = datetime.datetime.combine(current_day.date(), datetime.time(day_start_hour))
        day_end_time = datetime.datetime.combine(current_day.date(), datetime.time(day_end_hour))

        hours = (timezone(calendar_timezone).localize(day_start_time), timezone(calendar_timezone).localize(day_end_time))

        appointments = []

        if current_day_busy_events:

            for busy_event in current_day_busy_events:

                busy_event_start = (dateutil.parser.parse(busy_event["start"]))
                busy_event_end = (dateutil.parser.parse(busy_event["end"]))
                appointments.append((busy_event_start,busy_event_end))

        slots_for_day = get_free_slots_for_day(hours, appointments, duration, current_day.date(), calendar_timezone)

        # for slot in slots_for_day:

        slots_for_week.append(slots_for_day)

        current_day += datetime.timedelta(days=1)

    return slots_for_week

def get_free_slots_for_day(hours, appointments, duration, date, timezone):

    slots = sorted([(hours[0], hours[0])] + appointments + [(hours[1], hours[1])])

    slots_for_day = []

    for start, end in ((slots[i][1], slots[i+1][0]) for i in range(len(slots)-1)):

        while start + duration <= end:

            slot = {}
            event = {}

            slot['date'] = str(date)
            slot['weekday'] = date.strftime('%A')
            slot['timezone'] = timezone

            event['start'] = start.isoformat()
            event['end'] = (start + duration).isoformat()
            
            slot['event'] = event

            slots_for_day.append(slot)

            start += duration

    return slots_for_day

def get_calendar_tz(service,calendar):

    calendar_json = service.calendars().get(calendarId=calendar).execute()

    return calendar_json["timeZone"]

def get_calendars_list(service):

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time

    print('Getting the list of calendars')

    calendars_list = service.calendarList().list(maxResults=10).execute()

    calendars = calendars_list.get('items', [])

    if not calendars:
        print('No calendars found.')
    for calendar in calendars:
        # calid = calendar['id']
        # print(calid, calendar['summary'])
        get_calendar_tz(service,calendar['id'])
        # print(json_pretty(calendar))

# def get_working_days_for_next_week(holiday_calendar):

def json_pretty(json_block):
    json_formatted_str = json.dumps(json_block, indent=2)
    print(json_formatted_str)

def next_weekday(weekday):
    today = datetime.datetime.today()
    days_ahead = weekday - today.weekday()
    days_ahead += 7
    next_weekday = today + datetime.timedelta(days_ahead)
    return datetime.datetime.combine(next_weekday.date(), datetime.time(0,0,0,0))

# def get_workingdays():

if __name__ == '__main__':
    main()