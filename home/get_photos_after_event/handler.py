import json
import boto3
from datetime import datetime, timezone, timedelta
from utils.response import success, error
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")

users_table = dynamodb.Table("Users")
events_table = dynamodb.Table("Events")
photos_table = dynamodb.Table("Photos")

BUCKET_NAME = "phomo-photos-storage"

def lambda_handler(event, context):
    try:
        user_id = "test-user-1"

        # Step 1: Get user's active event
        user = users_table.get_item(Key={"user_id": user_id}).get("Item")
        if not user or "active_event_id" not in user:
            return error("User is not in an event.")

        event_id = user["active_event_id"]
        print("Looking for event_id:", event_id)

        # Step 2: Fetch event using event_id (no scan needed!)
        event = events_table.get_item(Key={"event_id": event_id}).get("Item")
        if not event:
            return error("Event not found.")

        # Step 3: Time checks (based on end_time)
        end_time = datetime.fromisoformat(event["end_time"].replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)

        if now < end_time:
            return error("Event has not ended yet.")
        if now > (end_time + timedelta(hours=24)):
            return error("24h viewing window has expired.")

        # Step 4: Get all photos from this event (scan is okay here if no GSI)
        response = photos_table.scan(
            FilterExpression=Key("event_id").eq(event_id)
        )
        photos = response.get("Items", [])

        # Step 5: Add signed S3 download URLs
        for photo in photos:
            photo["download_url"] = s3.generate_presigned_url(
                ClientMethod="get_object",
                Params={
                    "Bucket": BUCKET_NAME,
                    "Key": f"photos/{event_id}/{photo['photo_id']}.jpg"
                },
                ExpiresIn=3600
            )

        return success({"photos": photos})

    except Exception as e:
        print("Error:", str(e))
        return error(str(e))


if __name__ == "__main__":
    fake_event = {
        "body": "{}"
    }
    print(lambda_handler(fake_event, None))
