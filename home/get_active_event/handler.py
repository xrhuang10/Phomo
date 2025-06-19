import json
import boto3
from datetime import datetime, timedelta, timezone
from utils.response import success, error

dynamodb = boto3.resource("dynamodb")
users_table = dynamodb.Table("Users")
events_table = dynamodb.Table("Events")

def lambda_handler(event, context):
    try:
        user_id = "test-user-1"  # Replace with Cognito user ID

        # Step 1: Fetch user
        user = users_table.get_item(Key={"user_id": user_id}).get("Item")
        if not user or "active_event_id" not in user:
            return success({"state": "not_in_event"})

        active_event_id = user["active_event_id"]

        # Step 2: Fetch event
        event = events_table.get_item(Key={"event_id": active_event_id}).get("Item")
        if not event:
            return success({"state": "not_in_event"})

        # Step 3: Parse end_time
        end_time_str = event["end_time"]
        end_time = datetime.fromisoformat(end_time_str.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)

        # Step 4: Determine event state
        if now < end_time:
            state = "in_event"
        elif now < end_time + timedelta(hours=24):
            state = "grace_period"
        else:
            # Clear expired event from user
            users_table.update_item(
                Key={"user_id": user_id},
                UpdateExpression="REMOVE active_event_id"
            )
            return success({"state": "not_in_event"})

        # Step 5: Return event state + metadata
        return success({
            "state": state,
            "event_id": event["event_id"],
            "event_code": event["event_code"],
            "event_name": event["event_name"],
            "start_time": event["start_time"],
            "end_time": event["end_time"],
            "cover_photo": event.get("cover_photo", ""),
            "created_by": event["created_by"]
        })

    except Exception as e:
        return error(str(e))


if __name__ == "__main__":
    fake_event = {
        "body": "{}"
    }
    print(lambda_handler(fake_event, None))
