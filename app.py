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

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE
slack_client=WebClient(token=SLACK_BOT_TOKEN,ssl=ssl_context)

# Flask webserver for incoming traffic from Slack
app = Flask(__name__)

def json_pretty(json_block):
    json_formatted_str = json.dumps(json_block, indent=2)
    print(json_formatted_str)

# def get_user_calendar_events():

def get_user_list():

    with open('botkit_message.json') as msg_file:
        intro_msg = json.load(msg_file)

    payload = slack_client.api_call("users.list")
    # print json_pretty(payload)

    for item in payload["members"]:
        if "email" in item["profile"]:

            # print(item["id"] + " " + item["profile"]["real_name_normalized"] + " " + item["profile"]["email"])

            print(json_pretty(intro_msg))

            response = slack_client.chat_postMessage(
              channel=item["id"],
              attachments=intro_msg
            )

            print("Message delivered:" + " " + str(response["ok"]))

            print(response)

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
    selection = form_json["actions"][0]["value"]

    print(selection)

    # if selection == "cappuccino":
    #     message_text = "cappuccino"
    # else:
    #     message_text = "latte"

    # response = slack_client.api_call(
    #   "chat.update",
    #   channel=form_json["channel"]["id"],
    #   ts=form_json["message_ts"],
    #   text="One {}, right coming up! :coffee:".format(message_text),
    #   attachments=[] # empty `attachments` to clear the existing massage attachments
    # )

    # Send an HTTP 200 response with empty body so Slack knows we're done here
    return make_response("", 200)


INTERVIEW_AVAIL_CAL = 'ashok.gadepalli@contino.io'

service = calendar_api.get_service()
events = calendar_api.get_events_for_next_week(service,calendar_api.next_weekday(0),calendar_api.next_weekday(5),INTERVIEW_AVAIL_CAL)
slots = calendar_api.get_free_slots_for_week(service,INTERVIEW_AVAIL_CAL,events,calendar_api.next_weekday(0),calendar_api.next_weekday(5))

json_pretty(slots)

# importlib.import_module(calendar_api)

# if __name__ == "__main__":
#     app.run()
