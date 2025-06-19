import json
import boto3
import uuid
from datetime import datetime, timedelta, timezone
from utils.response import success, error



dynamodb = boto3.resource("dynamodb")
events_table = dynamodb.Table("Events")

def lambda_handler(event, context):
    print("lambda_triggered")
    try:
        # Step 1: Simulate creator
        user_id = "test-user-1"  # eventually from Cognito
        # Step 2: Parse input
        body = json.loads(event["body"])
        event_name = body.get("name")
        if not event_name:
            return error("Event name is required.")

        # Step 3: Generate event fields
        event_id = str(uuid.uuid4())
        event_code = generate_event_code()
        start_time = (datetime.now(timezone.utc)).isoformat() #dynamically change
        end_time = (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()
        cover_photo = "https://fastly.picsum.photos/id/557/200/300.jpg?hmac=eC86bsSOhqQjoHHnj3yzH5wMTIY9S3ys6cQjU1_QLGc"  # Placeholder, can be updated later

        # Step 4: Save to Events table
        events_table.put_item(Item={
            "event_code": event_code,
            "event_id": event_id,
            "start_time": start_time,
            "end_time": end_time,
            "created_by": user_id,
            "event_name": event_name,
            "cover_photo": cover_photo
        })

        return success({
            "message": "Event created",
            "event_code": event_code,
            "event_id": event_id,
            "start_time": start_time,
            "end_time": end_time,
            "created_by": user_id,
            "event_name": event_name,
            "cover_photo": cover_photo
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
            "event_name": "Phomo Launch Party!"
        })
    }
    print(lambda_handler(fake_event, None))
