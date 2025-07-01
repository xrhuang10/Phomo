import json
import boto3
from utils.response import success, error

dynamodb = boto3.resource('dynamodb')
users_table = dynamodb.Table('Users')

def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        user_id = body.get('user_id')
        event_id = body.get('event_id')

        if not user_id or not event_id:
            return error("Missing user_id or event_id.")

        # Get user to confirm they are in the event
        user = users_table.get_item(Key={"user_id": user_id}).get("Item")
        if not user:
            return error("User not found.")
        if user.get("active_event_id") != event_id:
            return error("User is not in this event.")

        # Set active_event_id to null
        users_table.update_item(
            Key={"user_id": user_id},
            UpdateExpression="SET active_event_id = :n",
            ExpressionAttributeValues={":n": None}
        )

        return success({"message": "User has left the event."})

    except Exception as e:
        print(f"Error in leave_event_phomo: {str(e)}")
        return error("Failed to leave event.")
