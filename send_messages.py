#!/usr/bin/python3
import importlib
import os
import json
import ssl
from slack import WebClient
import calendar_api
import schedule
import time

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_VERIFICATION_TOKEN = os.environ["SLACK_VERIFICATION_TOKEN"]
INTERVIEW_AVAIL_CAL = os.environ["INTERVIEW_AVAIL_CAL"]
TEST_EMAIL = os.environ["TEST_EMAIL_LIST"]

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

slack_client = WebClient(token=SLACK_BOT_TOKEN, ssl=ssl_context)

# response = post_message(service, item["id"], DEMO_USER_CAL, item["profile"]["real_name_normalized"].replace(" ", "%"))

def lambda_handler(event, context):

    service = calendar_api.get_service_delegated()  # use this if you are using a Google Cloud API service account
    # service = calendar_api.get_service_local_creds()  # use this if you are using local credentials

    cursor = ''

    user_list = []

    user_list = get_user_list(service,cursor,user_list)

    # already_signed_up_users = get_already_signed_up_users(service)

    TEST_EMAIL_LIST = TEST_EMAIL.split(",")

    for item in user_list:

        # if "email" in item["profile"] and item["profile"]["email"] not in already_signed_up_users:

        if "email" in item["profile"] and item["profile"]["email"] and item["profile"]["email"] in TEST_EMAIL_LIST:

            print(item["id"] + " " + item["profile"]["real_name_normalized"] + " " + item["profile"]["email"]) # + " " + str(response["ok"]))


def get_already_signed_up_users(service):

    interview_calendar_events = calendar_api.get_events_for_next_week(service,
                                                                      calendar_api.next_weekday(0),
                                                                      calendar_api.next_weekday(5),
                                                                      INTERVIEW_AVAIL_CAL)

    already_signed_up_users = []

    for event in interview_calendar_events:
        already_signed_up_users.append(event["creator"]["email"])

    return already_signed_up_users


def get_user_list(service,cursor,user_list):

    payload = slack_client.users_list(cursor=cursor)

    for user in payload["members"]:
        user_list.append(user)

    if payload["response_metadata"]["next_cursor"]:
        # print(payload["response_metadata"]["next_cursor"])
        user_list = get_user_list(service,payload["response_metadata"]["next_cursor"],user_list)

    return user_list

def post_message(service, channel_id, user_email, user_real_name):

    blocks = []

    welcome_block = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "Hello Contini! Signup for an interview slot for next week. I have some free slots below!"
        }
    }

    blocks.append(welcome_block)

    weekdays = calendar_api.get_free_slots_for_week(service,
                                                    user_email,
                                                    calendar_api.next_weekday(0),
                                                    calendar_api.next_weekday(5))

    for day in weekdays:
        options = []
        for free_slot in day:

            option = {
                "text": {
                    "type": "plain_text",
                    "text": free_slot["event"]["start"] + " - " + free_slot["event"]["end"]
                },
                "value": free_slot["event"]["isostart"] + "_" + free_slot["event"]["isoend"]
            }

            options.append(option)

        drop_down = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Pick a slot for " + day[0]["weekday"] + " " + day[0]["date"]
            },
            "accessory": {
                "type": "static_select",
                "action_id": user_email + "_" + day[0]["timezone"] + "_" + user_real_name,
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select a slot"
                },
                "options": options
            }
        }

        blocks.append(drop_down)

    initial_message = [{"blocks": blocks}]

    response = slack_client.chat_postMessage(
      channel=channel_id,
      attachments=json.dumps(initial_message)
    )

    return response


def json_pretty(json_block):

    json_formatted_str = json.dumps(json_block, indent=2)
    print(json_formatted_str)

lambda_handler('','')
