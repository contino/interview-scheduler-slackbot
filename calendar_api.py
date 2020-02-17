#!/usr/local/bin/python3

from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import json

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

INTERVIEW_AVAIL_CAL='contino.io_eepahmdv2bb1tvhbvv0ictha3g@group.calendar.google.com'
DEFAULT_TIMEZONE = 'America/New_York'

def next_weekday(weekday):
    
    today = datetime.datetime.today()

    days_ahead = weekday - today.weekday()

    if days_ahead <= 0:
        days_ahead += 7

    next_weekday = today + datetime.timedelta(days_ahead)
    
    return datetime.datetime.combine(next_weekday.date(), datetime.time(0,0,0,0))

def main():

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

    # print(next_weekday(5).isoformat())

    # events = get_events_for_next_week(service,next_weekday(0).isoformat(),next_weekday(5).isoformat(),INTERVIEW_AVAIL_CAL)
    
    # get_free_slots_for_calendar(events)

    # get_calendars_list(service)

    # now = datetime.datetime.utcnow().isoformat() + 'Z'

    # print(next_weekday().date() + 'T18:00:10.00000Z')

def get_events_for_next_week(service,next_weekday,last_weekday,calendar):

    events_result = service.events().list(  calendarId=calendar,
                                            timeMin=next_weekday + 'Z',
                                            timeMax=last_weekday + 'Z', 
                                            singleEvents=True,
                                            orderBy='startTime').execute()

    events = events_result.get('items', [])

    return events

def get_free_slots_for_calendar(events):

    if not events:
        print('No upcoming events found.')
    for event in events:

        #if tz is not set, defaults to DEFAULT_TIMEZONE
        if "timeZone" not in event["start"]:
            event["start"]["timeZone"] = DEFAULT_TIMEZONE

        print( event["start"]["dateTime"].strip('\"') + " " + event["start"]["timeZone"].strip('\"') + " " + event["creator"]["email"].strip('\"'))

def get_calendar_tz(service,calendar):

    calendar_json = service.calendars().get(calendarId=calendar).execute()

    print(calendar_json["timeZone"])

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

def json_pretty(json_block):
    json_formatted_str = json.dumps(json_block, indent=2)
    return json_formatted_str

if __name__ == '__main__':
    main()