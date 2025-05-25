import json
import boto3
import uuid
from datetime import datetime, timedelta, timezone
from utils.response import success, error



dynamodb = boto3.resource("dynamodb")
events_table = dynamodb.Table("Events")

def lambda_handler(event, context):
    try:
        # Step 1: Simulate creator
        user_id = "test-user-123"  # eventually from Cognito
        # Step 2: Parse input
        body = json.loads(event["body"])
        event_name = body.get("name")
        if not event_name:
            return error("Event name is required.")

        # Step 3: Generate event fields
        event_id = str(uuid.uuid4())
        event_code = generate_event_code()
        expires_at = (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()

        # Step 4: Save to Events table
        events_table.put_item(Item={
            "event_code": event_code,
            "event_id": event_id,
            "expires_at": expires_at,
            "created_by": user_id,
            "name": event_name
        })

        return success({
            "message": "Event created",
            "event_code": event_code,
            "event_id": event_id,
            "expires_at": expires_at
        })

    except Exception as e:
        return error(str(e))

def generate_event_code():
    import random
    import string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


if __name__ == "__main__":
    fake_event = {
        "body": json.dumps({
            "name": "Phomo Launch Party"
        })
    }
    print(lambda_handler(fake_event, None))
