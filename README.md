# interview-scheduler-slackbot

## Setup local google calendar dev environment

Follow below guide and install required tools for python dev environment

https://developers.google.com/calendar/quickstart/python

Interview availability calendar id
`contino.io_eepahmdv2bb1tvhbvv0ictha3g@group.calendar.google.com`

## Thought process / things I need

Get current date ✅

Generate next week's dates ✅

List Slack Users ✅

Get Slack User's name ✅

Get Slack User's email ✅

Get Slack User's DM ID ✅

DM User ✅

Read Contino interview availability calendar ✅

Read specific user's calendar for above dates 

Identify free slots in their calendar that span 1 hour (avoid lunch time)

Use first 5 free slots and generate json payload

Deliver payload to user's direct message channel

Capture user response json (button click)

Build payload for google calendar

Make api call to google calendar
