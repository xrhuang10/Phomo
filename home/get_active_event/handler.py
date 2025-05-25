import json
import boto3
from utils.response import success, error

dynamodb = boto3.resource("dynamodb")
users_table = dynamodb.Table("Users")
events_table = dynamodb.Table("Events")

def lambda_handler(event, context):
    try:
        user_id = "test-user-123"  # Replace with Cognito later

        # Step 1: Look up the user
        user = users_table.get_item(Key={"user_id": user_id}).get("Item")
        if not user or "active_event_id" not in user:
            print('User not found or no active event')
            return success({"active_event": None})


        active_event_id = user["active_event_id"]

        # Step 2: Look up the event by scanning Events table for that event_id
        result = events_table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr("event_id").eq(active_event_id)
        )
        items = result.get("Items", [])
        if not items:
            return success({"active_event": None})

        event = items[0]

        return success({
            "active_event": {
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
