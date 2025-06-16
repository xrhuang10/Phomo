import json
import boto3
from datetime import datetime, timezone
from boto3.dynamodb.conditions import Key
from utils.response import success, error

# DynamoDB table setup
dynamodb = boto3.resource("dynamodb")
users_table = dynamodb.Table("Users")
events_table = dynamodb.Table("Events")

def lambda_handler(event, context):
    try:
        # Simulated Cognito ID (replace with real one from context later)
        user_id = "test-user-1"

        # Parse incoming request
        body = json.loads(event["body"])
        event_code = body.get("event_code")

        if not event_code:
            return error("Event code is required.")

        # ✅ Query Events table by event_code using the GSI
        response = events_table.query(
            IndexName="event_code-index",
            KeyConditionExpression=Key("event_code").eq(event_code)
        )

        items = response.get("Items", [])
        if not items:
            return error("Invalid event code.")

        event = items[0]

        # ✅ Check if event is expired
        expires_at = datetime.fromisoformat(event["expires_at"].replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        if now > expires_at:
            return error("Event expired.")

        # ✅ Save event_id in Users table as active_event_id
        users_table.put_item(Item={
            "user_id": user_id,
            "active_event_id": event["event_id"],
            "joined_at": now.isoformat()
        })

        return success({
            "message": "Successfully joined event!",
            "event_id": event["event_id"],
            "event_name": event.get("name", "Untitled Event")
        })

    except Exception as e:
        return error(str(e))


# For testing locally
if __name__ == "__main__":
    test_event = {
        "body": json.dumps({
            "event_code": "ABC123"
        })
    }
    print(lambda_handler(test_event, None))
