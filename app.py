from flask import Flask, request, make_response, Response
import os
import json

from slackclient import SlackClient

# Your app's Slack bot user token
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_VERIFICATION_TOKEN = os.environ["SLACK_VERIFICATION_TOKEN"]

# Slack client for Web API requests
slack_client = SlackClient(SLACK_BOT_TOKEN)

# Flask webserver for incoming traffic from Slack
app = Flask(__name__)

# Helper for verifying that requests came from Slack
def verify_slack_token(request_token):
    if SLACK_VERIFICATION_TOKEN != request_token:
        print("Error: invalid verification token!")
        print("Received {} but was expecting {}".format(request_token, SLACK_VERIFICATION_TOKEN))
        return make_response("Request contains invalid Slack verification token", 403)

# The endpoint Slack will send the user's menu selection to
@app.route("/slack/message_actions", methods=["POST"])
def message_actions():

    # Parse the request payload
    form_json = json.loads(request.form["payload"])

    # json_formatted_str = json.dumps(form_json, indent=2)
    # print(json_formatted_str)

    # Verify that the request came from Slack
    verify_slack_token(form_json["token"])

    # Check to see what the user's selection was and update the message accordingly
    selection = form_json["actions"][0]["value"]

    print selection

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

with open('botkit_message.json') as msg_file:
    intro_msg = json.load(msg_file)


payload = slack_client.api_call(
  "chat.postMessage",
  channel="#trashbin",
  attachments=intro_msg
)

json_formatted_str = json.dumps(payload, indent=2)
print(json_formatted_str)

# print json.dumps(slack_client.api_call("users.list"), indent=2)

# payload = slack_client.api_call("users.list")
# json_formatted_str = json.dumps(payload, indent=2)
# # print(json_formatted_str)

# for item in payload["members"]:
#   print item["id"] + " " + item["profile"]["real_name_normalized"]

# Start the Flask server
# if __name__ == "__main__":
#     app.run()
