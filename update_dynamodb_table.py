#!/usr/bin/python3
import os
import json
import send_messages
import boto3

INTERVIEWERS_LIST = os.environ["INTERVIEWERS_LIST"]
SHADOWERS_LIST = os.environ["SHADOWERS_LIST"]

dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')

def update_dynamodb_table(dynamodb_client, USER_BASE, table_name):

    slack_user_list = send_messages.get_user_list('',[])

    USER_BASE_LIST = USER_BASE.split(",")

    for item in slack_user_list:

        if "email" in item["profile"] and item["profile"]["email"] in USER_BASE_LIST:

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


update_dynamodb_table(dynamodb_client, INTERVIEWERS_LIST, 'interviewers')

update_dynamodb_table(dynamodb_client, SHADOWERS_LIST, 'shadowers')
