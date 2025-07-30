import json
import boto3
from boto3.dynamodb.conditions import Key
from utils.response import success, error

dynamodb = boto3.resource('dynamodb')
participation_table = dynamodb.Table('UserEventParticipation')

def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))
        user_id = body.get("user_id")

        if not user_id:
            return error("Missing user_id")

        # Step 1: Query UserEventParticipation table for all events user has joined
        response = participation_table.query(
            KeyConditionExpression=Key('user_id').eq(user_id)
        )
        
        participation_items = response.get('Items', [])

        if not participation_items:
            return success({"events": []})

        # Step 2: Construct events list
        events = []
        for item in participation_items:
            events.append({
                "event_id": item["event_id"],
                "event_timeline_photo": item.get("event_timeline_photo", ""),  # user-chosen timeline photo
                "host": item.get("host", False),
                "joined_at": item.get("joined_at", "")
            })

        # Step 3: Sort events by joined_at descending
        events.sort(key=lambda x: x["joined_at"], reverse=True)

        return success({"events": events})

    except Exception as e:
        print(f"Error in list_past_events: {str(e)}")
        return error("Failed to list past events.")


if __name__ == "__main__":
    fake_event = {
        "body": json.dumps({
            "user_id": "testuser"
        })
    }
    print(lambda_handler(fake_event, None))
