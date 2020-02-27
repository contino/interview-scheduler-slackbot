![CI](https://github.com/contino/interview-scheduler-slackbot/workflows/CI/badge.svg?branch=master)
# interview-scheduler-slackbot 🤖

## What does this bot do?

Makes scheduling interview slots for the coming week super easy. Pull out your phone, look at the client calendar and pick a slot, the bot will create the event on the Interview Availability calendar 🤯. The bot will make sure the suggested slots are from your free time.

# Installation

There are four things that you need to setup to run and test the slackbot locally

1) Google Calendar API setup + credentials

2) Your own Slack Workspace for bot development

3) A Slack app in the workspace above

4) ngrok

## Setup local google calendar dev environment

Follow below guide and install required tools for python dev environment

https://developers.google.com/calendar/quickstart/python

Interview availability calendar id
`contino.io_eepahmdv2bb1tvhbvv0ictha3g@group.calendar.google.com`

Unlike the example above, this project uses a service account with delegated credentials to interact with the Google API. Individual users can however setup their own credentials and use the example in the link above to get familiar with the Google Calendar API.

## Create a Slack workspace

Click on the link below and use a personal email (not Contino!) to create a development workspace. Setting up the workspace should be super straight-forward.

https://slack.com/create#email

1) Once you are done setting up the workspace, head over to https://api.slack.com/apps and click on create a new app.

## Configure Slack App on the Slack API page

1) Next, enable interactive components. This feature lets our bot respond to user actions like button clicks.

2) Do not worry about the `Request URL`. Leave it empty for now, we will get back to that later.

3) Click on OAuth & Permissions and scroll down to Scopes (Bot Token Scopes). Click on `Add an Oauth Scope` and add the scopes from the image below.

Insert bot scopes image

4) Click on `Install App` button on the sidebar and install app to the workspace you created.

## Setup local development environment

1) Click on `Basic Information` button and scroll down to the credentials, we will need to set these up as env vars on our dev environment.

```
export SLACK_BOT_TOKEN='xoxb-blah-blah'
export SLACK_VERIFICATION_TOKEN='bluph-blurph'
export INTERVIEW_AVAIL_CAL='you@email.com'
```

2) Install Python 3.7 (figure it out)

3) Install and start ngrok