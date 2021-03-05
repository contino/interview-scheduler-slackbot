#!/usr/bin/python3
import importlib
import os
import json
import ssl
from slack import WebClient
from slack.errors import SlackApiError
import calendar_api
import boto3
from botocore.exceptions import ClientError

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_VERIFICATION_TOKEN = os.environ["SLACK_VERIFICATION_TOKEN"]
INTERVIEW_AVAIL_CAL = os.environ["INTERVIEW_AVAIL_CAL"]
INTERVIEWERS_TABLE = os.environ["INTERVIEWERS_TABLE"]
AWS_REGION = os.environ['REGION']
READ_ONLY_EMAIL = os.environ['READ_ONLY_EMAIL']

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

slack_client = WebClient(token=SLACK_BOT_TOKEN, ssl=ssl_context)


def json_pretty(json_block):

    json_formatted_str = json.dumps(json_block, indent=2)
    print(json_formatted_str)


def get_users_from_dynamodb(dynamodb_client, table_name):

    try:
        response = dynamodb_client.scan(
            TableName=table_name,
            Select='ALL_ATTRIBUTES')
        return response["Items"]

    except ClientError as e:
        if e.response['Error']['Code'] == "ResourceNotFoundException":
            print(e.response['Error']['Message'] + ":" + table_name)
        else:
            raise


def remove_user_from_db(dynamodb_client, table_name, user_email):

    response = dynamodb_client.delete_item(
        TableName=table_name,
        Key={
            'email_id': {
                'S': user_email,
            }
        }
    )

    if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
        print(user_email + " has been removed from the database.")


def update_dynamodb_table(dynamodb_client, user_list, table_name):

    slack_user_list = get_user_list('', [])  # recursive

    for item in slack_user_list:

        if "email" in item["profile"] and item["profile"]["email"] in user_list:

            response = dynamodb_client.update_item(
                    TableName=table_name,
                    Key={
                        'email_id': {
                            'S': item["profile"]["email"],
                        }
                    },
                    AttributeUpdates={
                        'channel_id': {
                            'Value': {
                                'S': item["id"]
                            }
                        },
                        'real_name_normalized': {
                            'Value': {
                                'S': item["profile"]["real_name_normalized"]
                            }
                        },
                        'interviews_done': {
                            'Value': {
                                'N': '0'
                            }
                        }
                    })

            print(item["id"] + " " + item["profile"]["real_name_normalized"] + " " + item["profile"]["email"] + " " + str(response["ResponseMetadata"]["HTTPStatusCode"]))


def lambda_handler(event, context):

    service = calendar_api.get_service_delegated(READ_ONLY_EMAIL)  # use this if you are using a Google Cloud API service account
    # service = calendar_api.get_service_local_creds()  # use this if you are using local credentials
    already_signed_up_users = get_already_signed_up_users(service)

    dynamodb_client = boto3.client('dynamodb', region_name=AWS_REGION)

    calendar_writers_and_owners = calendar_api.get_calendar_writers_and_owners(service, INTERVIEW_AVAIL_CAL)

    update_dynamodb_table(dynamodb_client, calendar_writers_and_owners, 'interviewers')

    interviewer_list = get_users_from_dynamodb(dynamodb_client, INTERVIEWERS_TABLE)

    for interviewer in interviewer_list:

        if interviewer["email_id"]["S"] not in already_signed_up_users:

            calendar_status = calendar_api.get_user_calendar(service, interviewer["email_id"]["S"])

            if calendar_status == 404:
                print(interviewer["email_id"]["S"] + "'s calendar does not exist.")
                remove_user_from_db(dynamodb_client, INTERVIEWERS_TABLE, interviewer["email_id"]["S"])
            else:
                post_message_to_interviewer(service,
                                            interviewer["channel_id"]["S"],
                                            interviewer["email_id"]["S"],
                                            interviewer["real_name_normalized"]["S"].replace(" ", "%"))

                print('INTERVIEWER ' + interviewer["channel_id"]["S"] + " " + interviewer["real_name_normalized"]["S"] + " " + interviewer["email_id"]["S"])


def get_already_signed_up_users(service):

    interview_calendar_events = calendar_api.get_events_for_next_week(service,
                                                                      calendar_api.next_weekday(0, 'next_week'),
                                                                      calendar_api.next_weekday(5, 'next_week'),
                                                                      INTERVIEW_AVAIL_CAL)

    already_signed_up_users = []

    for event in interview_calendar_events:
        already_signed_up_users.append(event["creator"]["email"])

    return already_signed_up_users


def get_user_list(cursor, user_list):

    payload = slack_client.users_list(cursor=cursor)

    for user in payload["members"]:
        user_list.append(user)

    if payload["response_metadata"]["next_cursor"]:

        user_list = get_user_list(payload["response_metadata"]["next_cursor"], user_list)

    return user_list


def post_message_to_interviewer(service, channel_id, user_email, user_real_name):

    blocks = []

    weekdays = calendar_api.get_free_slots_for_week(service,
                                                    user_email,
                                                    calendar_api.next_weekday(0, 'next_week'),
                                                    calendar_api.next_weekday(5, 'next_week'))

    for day in weekdays:
        if day:  # empty if no free slots on given day
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
                    "action_id": user_email + ";" + day[0]["timezone"] + ";" + user_real_name,
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select a slot"
                    },
                    "options": options
                }
            }

            blocks.append(drop_down)

    initial_message = [{"blocks": blocks}]

    try:
        slack_client.chat_postMessage(
          text='Hello Contini! Signup for an interview slot for next week. I have some free slots below!',
          channel=channel_id,
          attachments=json.dumps(initial_message)
        )
    except SlackApiError as e:
        if e.response["error"] == 'user_not_found':
            print(user_email + " channel_id:" + channel_id + " " + e.response["error"])
            print("Possible incorrect channel_id or deleted account.")
        else:
            print(e.response["error"] + " " + user_email)
