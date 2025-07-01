import boto3
import os
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('USERS_TABLE', 'Users')
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    print("Received event:", event)

    try:
        user_attributes = event['request']['userAttributes']
        user_id = user_attributes['sub']
        username = event['userName']
        email = user_attributes.get('email', '')

        joined_at = datetime.utcnow().isoformat()

        table.put_item(
            Item={
                'user_id': user_id,
                'username': username,
                'email': email,
                'joined_at': joined_at,
                'active_event_id': None,
            }
        )
        print(f"✅ User {username} inserted into DynamoDB with sub {user_id}.")

    except Exception as e:
        print(f"❌ Error inserting user into DynamoDB: {e}")
        raise e

    return event
