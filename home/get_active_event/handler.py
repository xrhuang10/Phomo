import json
import boto3
from datetime import datetime, timedelta, timezone
from utils.response import success, error

dynamodb = boto3.resource("dynamodb")
users_table = dynamodb.Table("Users")
events_table = dynamodb.Table("Events")

def lambda_handler(event, context):
    try:
        user_id = "test-user-123"  # Replace with Cognito user ID

        # Step 1: Fetch user
        user = users_table.get_item(Key={"user_id": user_id}).get("Item")
        if not user or "active_event_id" not in user:
            return success({"state": "not_in_event"})

        active_event_id = user["active_event_id"]

        # Step 2: Fetch event
        event = events_table.get_item(Key={"event_code": active_event_id}).get("Item")
        if not event:
            return success({"state": "not_in_event"})



        # Step 3: Determine state
        expires_at_str = event["expires_at"]
        expires_at = datetime.fromisoformat(expires_at_str.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        
        if now < expires_at:
            state = "in_event"
        elif now < expires_at + timedelta(hours=24):
            state = "grace_period"
        else:
            # Optional cleanup: remove active_event_id from user
            users_table.update_item(
                Key={"user_id": user_id},
                UpdateExpression="REMOVE active_event_id"
            )
            return success({"state": "not_in_event"})

        return success({
            "state": state,
            "event": {
                "event_id": event["event_id"],
                "event_code": event["event_code"],
                "name": event.get("name"),
                "expires_at": event["expires_at"]
            }
        })

    except Exception as e:
        return error(str(e))


if __name__ == "__main__":
    fake_event = {
        "body": "{}"
    }
    print(lambda_handler(fake_event, None))
