import json
import boto3
from datetime import datetime, timezone
from boto3.dynamodb.conditions import Key
from utils.response import success, error

dynamodb = boto3.resource("dynamodb")
users_table = dynamodb.Table("Users")
events_table = dynamodb.Table("Events")

def lambda_handler(event, context):
    try:
        user_id = "test-user-1"  # Replace with Cognito later
        body = json.loads(event["body"])
        event_code = body.get("event_code")

        if not event_code:
            return error("Event code is required.")

        # Step 1: Look up the event by event_code using GSI
        response = events_table.query(
            IndexName="event_code-index",  # ✅ make sure this index exists
            KeyConditionExpression=Key("event_code").eq(event_code)
        )
        if not response["Items"]:
            return error("Invalid event code.")

        event = response["Items"][0]

        # Step 2: Check if event is expired
        end_time = datetime.fromisoformat(event["end_time"])
        if datetime.now(timezone.utc) > end_time:
            return error("Event expired.")

        # Step 3: Add to Users table
        users_table.put_item(Item={
            "user_id": user_id,
            "active_event_id": event["event_id"],
            "joined_at": datetime.now(timezone.utc).isoformat()
        })

        return success({
            "message": "Successfully joined event!",
            "event_id": event["event_id"],
            "event_name": event["event_name"],
            "start_time": event["start_time"],
            "end_time": event["end_time"],
            "cover_photo": event.get("cover_photo", ""),
            "created_by": event["created_by"]
        })

    except Exception as e:
        return error(str(e))


if __name__ == "__main__":
    test_event = {
        "body": json.dumps({
            "event_code": "551150"
        })
    }
    print(lambda_handler(test_event, None))
