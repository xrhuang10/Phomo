import json
import boto3
from datetime import datetime, timezone
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

        # Check if event exists
        event = events_table.get_item(Key={"event_code": event_code}).get("Item")
        if not event:
            return error("Invalid event code.")

        # Check if event expired
        expires_at = datetime.fromisoformat(event["expires_at"])
        if datetime.now(timezone.utc) > expires_at:
            return error("Event expired.")

        # Add to user table
        users_table.put_item(Item={
            "user_id": user_id,
            "active_event_id": event["event_id"],
            "joined_at": datetime.now(timezone.utc).isoformat()
        })

        return success({"message": "Successfully joined event!"})

    except Exception as e:
        return error(str(e))


if __name__ == "__main__":
    test_event = {
        "body": json.dumps({
            "event_code": "551150"
        })
    }
    print(lambda_handler(test_event, None))

