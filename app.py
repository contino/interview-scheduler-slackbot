#!/usr/bin/python3
import importlib
from flask import Flask, request, make_response, Response
import os
import json
import ssl
from slack import WebClient
from slack.errors import SlackApiError
import calendar_api
import time

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_VERIFICATION_TOKEN = os.environ["SLACK_VERIFICATION_TOKEN"]
INTERVIEW_AVAIL_CAL = os.environ["INTERVIEW_AVAIL_CAL"]

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

slack_client = WebClient(token=SLACK_BOT_TOKEN, ssl=ssl_context)
app = Flask(__name__)


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

    json_pretty(form_json["actions"])

    verify_slack_token(form_json["token"])

    event_start = form_json["actions"][0]["selected_option"]["value"].split("_")[0]
    event_end = form_json["actions"][0]["selected_option"]["value"].split("_")[1]

    user_email = form_json["actions"][0]["action_id"].split(";")[0]
    user_tz = form_json["actions"][0]["action_id"].split(";")[1]
    user_real_name = form_json["actions"][0]["action_id"].split(";")[2].replace("%", " ")

    service = calendar_api.get_service_delegated(user_email)

    insert_response = calendar_api.create_event(service,
                                                INTERVIEW_AVAIL_CAL,
                                                user_email, user_tz,
                                                event_start, event_end, user_real_name)

    json_pretty(insert_response)

    if insert_response["status"] == 'confirmed':

        try:
            slack_client.chat_postMessage(
                channel=form_json["channel"]["id"],
                thread_ts=form_json["message"]["ts"],
                text=form_json["actions"][0]["selected_option"]["value"].split("T")[0] + " "
                + form_json["actions"][0]["selected_option"]["text"]["text"] + " scheduled ✅"
            )
        except SlackApiError as e:
            if e.response["error"] == 'user_not_found':
                print(user_email + " channel_id:" + form_json["channel"]["id"] + " " + e.response["error"])
                print("Possible incorrect channel_id or deleted account.")
            else:
                print(e.response["error"] + " " + user_email)

    return make_response("", 200)

def json_pretty(json_block):

    json_formatted_str = json.dumps(json_block, indent=2)
    print(json_formatted_str)


if __name__ == "__main__":
    app.run()
