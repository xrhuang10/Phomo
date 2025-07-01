import json
import boto3
from datetime import datetime, timezone
from utils.response import success, error

dynamodb = boto3.resource('dynamodb')
events_table = dynamodb.Table('Events')

def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        user_id = body.get('user_id')
        event_id = body.get('event_id')

        if not user_id or not event_id:
            return error("Missing user_id or event_id.")

        # Fetch event to confirm host
        event_item = events_table.get_item(Key={"event_id": event_id}).get("Item")
        if not event_item:
            return error("Event not found.")
        if event_item.get("created_by") != user_id:
            return error("User is not the host of this event.")

        # Update end_time to now
        now = datetime.now(timezone.utc).isoformat()
        events_table.update_item(
            Key={"event_id": event_id},
            UpdateExpression="SET end_time = :e",
            ExpressionAttributeValues={":e": now}
        )

        return success({"message": "Event ended immediately.", "new_end_time": now})

    except Exception as e:
        print(f"Error in end_event_now_phomo: {str(e)}")
        return error("Failed to end event.")
