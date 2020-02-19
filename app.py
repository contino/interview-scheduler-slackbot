#!/usr/bin/python3
import importlib
from flask import Flask, request, make_response, Response
import os
import json
import ssl
from slack import WebClient
import calendar_api

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_VERIFICATION_TOKEN = os.environ["SLACK_VERIFICATION_TOKEN"]
INTERVIEW_AVAIL_CAL = 'ashok.gadepalli@contino.io'

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

    payload = slack_client.api_call("users.list")
    # print json_pretty(payload)

    for item in payload["members"]:
        if "email" in item["profile"]:

            # print(item["id"] + " " + item["profile"]["real_name_normalized"] + " " + item["profile"]["email"])

            response = post_message(item["id"])

            print("Message delivered:" + " " + str(response["ok"]))


def post_message(channel_id):

    blocks = []

    welcome_block = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "Hello Contini! I checked your Interview availability calendar for next week and it looks like you have not scheduled a slot. I already checked your calendar for next week and have them ready in the drop-downs below. You can choose one from each day!"
        }
    }

    blocks.append(welcome_block)

    service = calendar_api.get_service()
    events = calendar_api.get_events_for_next_week(service,calendar_api.next_weekday(0),calendar_api.next_weekday(5),INTERVIEW_AVAIL_CAL)
    slots = calendar_api.get_free_slots_for_week(service,INTERVIEW_AVAIL_CAL,events,calendar_api.next_weekday(0),calendar_api.next_weekday(5))

    #replace above functions with function to get working days for next week

    accessory_sections = []

    for day in slots: #each day's events are encased in their own array

        weekday = day[0]["weekday"]
        event_date = day[0]["date"]

        drop_down = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Pick a slot for " + weekday + " " + event_date
            },
            "accessory": {
                "type": "external_select",
                "action_id": channel_id + "_" + weekday + "_" + event_date,
                "placeholder": {
                    "type": "plain_text",
                    "text": "Pick a slot"
                },
                "min_query_length": 0
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

    # Parse the request payload
    form_json = json.loads(request.form["payload"])

    json_formatted_str = json.dumps(form_json, indent=2)
    print(json_formatted_str)

    # Verify that the request came from Slack
    verify_slack_token(form_json["token"])

    # Check to see what the user's selection was and update the message accordingly
    selection = form_json["actions"][0]["selected_option"]["value"]

    print(selection)

    # response = slack_client.api_call(
    #   "chat.update",
    #   channel=form_json["channel"]["id"],
    #   ts=form_json["message_ts"],
    #   text="One {}, right coming up! :coffee:".format(message_text),
    #   attachments=[] # empty `attachments` to clear the existing massage attachments
    # )

    # Send an HTTP 200 response with empty body so Slack knows we're done here
    return make_response("", 200)

@app.route("/slack/options", methods=["POST"])
def message_options():

    form_json = json.loads(request.form["payload"])


    verify_slack_token(form_json["token"])

    menu_options = {
          "options": [
            {
              "text": {
                "type": "plain_text",
                "text": "10am to 11am"
              },
              "value": "10to11"
            },
            {
              "text": {
                "type": "plain_text",
                "text": "11am to 12pm"
              },
              "value": "11to12"
            },
            {
              "text": {
                "type": "plain_text",
                "text": "1pm to 2pm"
              },
              "value": "1to2"
            }
          ]
    }

    return Response(json.dumps(menu_options), mimetype='application/json')

get_user_list()

if __name__ == "__main__":
    app.run()
