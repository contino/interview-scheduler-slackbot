#!/usr/bin/python3
import os
import json
import send_messages
import boto3

AWS_REGION = os.environ['REGION']

# reads list of users from the environment and adds them to their specific table

dynamodb_client = boto3.client('dynamodb', region_name=AWS_REGION)


def update_dynamodb_table(dynamodb_client, user_base, table_name):

    slack_user_list = send_messages.get_user_list('', [])  # recursive

    user_list = user_base.split(",")

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


update_dynamodb_table(dynamodb_client, os.environ["INTERVIEWERS_LIST"], 'interviewers')

update_dynamodb_table(dynamodb_client, os.environ["SHADOWERS_LIST"], 'shadowers')
