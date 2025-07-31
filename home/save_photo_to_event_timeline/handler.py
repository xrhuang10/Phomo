import json
import boto3
from datetime import datetime, timezone, timedelta
from utils.response import success, error

dynamodb = boto3.resource('dynamodb')
participation_table = dynamodb.Table('UserEventParticipation')
events_table = dynamodb.Table('Events')
photos_table = dynamodb.Table('Photos')

def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        user_id = body.get('user_id')
        event_id = body.get('event_id')
        photo_id = body.get('photo_id')
        event_name = body.get('event_name') 

        if not user_id or not event_id or not photo_id:
            return error("Missing user_id, event_id, or photo_id.")

        # 1️⃣ Verify participation
        participation = participation_table.get_item(
            Key={"user_id": user_id, "event_id": event_id}
        ).get("Item")
        if not participation:
            return error("User is not a participant in this event.")

        # 2️⃣ Verify grace period
        event_item = events_table.get_item(Key={"event_id": event_id}).get("Item")
        if not event_item:
            return error("Event not found.")

        now = datetime.now(timezone.utc)
        end_time = datetime.fromisoformat(event_item["end_time"])

        if now <= end_time:
            return error("Event is still active. Grace period not started.")
        if now > end_time + timedelta(hours=24):
            return error("Grace period has ended.")

        # 3️⃣ Verify photo belongs to event
        photo_item = photos_table.get_item(Key={"photo_id": photo_id}).get("Item")
        if not photo_item:
            return error("Photo not found.")
        if photo_item["event_id"] != event_id:
            return error("Photo does not belong to this event.")

        # 4️⃣ Update timeline photo and event name
        update_expression = "SET event_timeline_photo = :p"
        expression_values = {":p": photo_id}
        
        # Add event_name to update if provided
        if event_name:
            update_expression += ", event_name = :n"
            expression_values[":n"] = event_name

        participation_table.update_item(
            Key={"user_id": user_id, "event_id": event_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values
        )

        return success({"message": "Timeline photo saved successfully."})

    except Exception as e:
        print(f"Error in save_photo_to_event_timeline: {str(e)}")
        return error("Failed to save timeline photo.")

# For local testing
if __name__ == "__main__":
    fake_event = {
        "body": json.dumps({
            "user_id": "test-user-uuid",
            "event_id": "test-event-uuid",
            "photo_id": "test-photo-uuid",
            "event_name": "Test Event Name"  # Add event_name to test
        })
    }
    print(lambda_handler(fake_event, None))
