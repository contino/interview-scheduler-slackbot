# interview-scheduler-slackbot

## Setup local google calendar dev environment

Follow below guide and install required tools for python dev environment

https://developers.google.com/calendar/quickstart/python

Interview availability calendar id
`contino.io_eepahmdv2bb1tvhbvv0ictha3g@group.calendar.google.com`

## Thought process / things I need

Get current date

Generate next week's dates

Read specific user's calendar for above dates

Identify free slots in their calendar that span 1 hour (avoid lunch time)

Use first 5 free slots and generate json payload

Deliver payload
