#!/usr/bin/python3
import importlib
from flask import Flask, request, make_response, Response
import os
import json
import ssl
from slack import WebClient
import calendar_api
import dateutil.parser

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_VERIFICATION_TOKEN = os.environ["SLACK_VERIFICATION_TOKEN"]

DEMO_USER_CAL = 'ashok.gadepalli@contino.io'
INTERVIEW_AVAIL_CAL = 'contino.io_eepahmdv2bb1tvhbvv0ictha3g@group.calendar.google.com'

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

slack_client=WebClient(token=SLACK_BOT_TOKEN,ssl=ssl_context)



# Flask webserver for incoming traffic from Slack
app = Flask(__name__)

def json_pretty(json_block):
    json_formatted_str = json.dumps(json_block, indent=2)
    print(json_formatted_str)

def get_user_list():

    service = calendar_api.get_service()

    interview_calendar_events = calendar_api.get_events_for_next_week(service,calendar_api.next_weekday(0),calendar_api.next_weekday(5),INTERVIEW_AVAIL_CAL)
    weekdays = calendar_api.get_free_slots_for_week(service,INTERVIEW_AVAIL_CAL,calendar_api.next_weekday(0),calendar_api.next_weekday(5))

    already_signed_up_users = []

    for event in interview_calendar_events:
        already_signed_up_users.append(event["creator"]["email"])

    payload = slack_client.api_call("users.list")

    for item in payload["members"]:
        if "email" in item["profile"] and item["profile"]["email"] not in already_signed_up_users:

            print(item["id"] + " " + item["profile"]["real_name_normalized"] + " " + item["profile"]["email"])

            response = post_message(service,item["id"],DEMO_USER_CAL) #testing only use above line for prod
            
            print("Message delivered:" + " " + str(response["ok"]))



def post_message(service,channel_id,user_email):

    blocks = []

    welcome_block = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "Hello Contini! I checked your Interview availability calendar for next week and it looks like you have not scheduled a slot. I checked your calendar and have some options below, pick one and I will set it up for you on the interview availability calendar."
        }
    }

    blocks.append(welcome_block)

    weekdays = calendar_api.get_free_slots_for_week(service,user_email,calendar_api.next_weekday(0),calendar_api.next_weekday(5))

    for day in weekdays: #each day's events are encased in their own array

        options = []
        
        for free_slot in day:

            option = {
                "text": {
                    "type": "plain_text",
                    "text": free_slot["event"]["start"] + " - " + free_slot["event"]["end"]
                },
                "value": free_slot["event"]["isostart"]
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
                "action_id": user_email + "_" + channel_id,
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select a slot"
                },
                "options": options
            }
        }

        blocks.append(drop_down)

    initial_message = [{ "blocks": blocks }]

    response = slack_client.chat_postMessage(
      channel=channel_id,
      attachments=json.dumps(initial_message)
    )

    return response

# Helper for verifying that requests came from Slack
def verify_slack_token(request_token):
    if SLACK_VERIFICATION_TOKEN != request_token:
        print("Error: invalid verification token!")
        print("Received {} but was expecting {}".format(request_token, SLACK_VERIFICATION_TOKEN))
        return make_response("Request contains invalid Slack verification token", 403)

# # The endpoint Slack will send the user's menu selection to
@app.route("/slack/message_actions", methods=["POST"])
def message_actions():

    form_json = json.loads(request.form["payload"])
    verify_slack_token(form_json["token"])

    
    json_pretty(form_json)


    selection = form_json["actions"][0]["selected_option"]["value"]
    print(selection)

    return make_response("", 200)

# @app.route("/slack/options", methods=["POST"])
# def message_options():

#     form_json = json.loads(request.form["payload"])

#     # json_pretty(form_json)
#     # user_id = form_json["user"]["username"]

#     action_id = form_json["action_id"]

#     print(form_json["action_id"])

#     user_data = form_json["action_id"].split("_")

#     # print(user_data[0])

#     # free_slots = calendar_api.get_free_slots_for_week(service,user_data[0],calendar_api.next_weekday(0),calendar_api.next_weekday(5))
#     # json_pretty(free_slots)

#     verify_slack_token(form_json["token"])

#     menu_options = {
#           "options": [
#             {
#               "text": {
#                 "type": "plain_text",
#                 "text": "10am to 11am"
#               },
#               "value": "10to11"
#             },
#             {
#               "text": {
#                 "type": "plain_text",
#                 "text": "11am to 12pm"
#               },
#               "value": "11to12"
#             },
#             {
#               "text": {
#                 "type": "plain_text",
#                 "text": "1pm to 2pm"
#               },
#               "value": "1to2"
#             }
#           ]
#     }

#     return Response(json.dumps(menu_options), mimetype='application/json')

get_user_list()

if __name__ == "__main__":
    app.run()
