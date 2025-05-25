import json
import boto3
from datetime import datetime, timezone, timedelta
from utils.response import success, error
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")

users_table = dynamodb.Table("Users")
events_table = dynamodb.Table("Events")
photos_table = dynamodb.Table("Photos")

BUCKET_NAME = "phomo-photos-storage"

def lambda_handler(event, context):
    try:
        user_id = "test-user-123"

        # Step 1: Get the user's active event
        user = users_table.get_item(Key={"user_id": user_id}).get("Item")
        if not user or "active_event_id" not in user:
            return error("User is not in an event.")

        event_id = user["active_event_id"]
        print("Looking for event_id:", event_id)

        # Step 2: Look up event details
        result = events_table.scan(FilterExpression=Attr("event_id").eq(event_id))
        items = result.get("Items", [])
        if not items:
            return error("Event not found.")

        event = items[0]
        expires_at = datetime.fromisoformat(event["expires_at"])
        now = datetime.now(timezone.utc)

        # Step 3: Check if event has expired
        if now < expires_at:
            return error("Event has not ended yet.")

        # Step 4: Check if within 24h of event expiry
        if now > (expires_at + timedelta(hours=24)):
            return error("24h viewing window has expired.")

        # Step 5: Query Photos table for this event
        photos = photos_table.scan(
            FilterExpression=Attr("event_id").eq(event_id)
        ).get("Items", [])
        


        # Step 6: Attach pre-signed URLs to each photo
        for photo in photos:
            photo["download_url"] = s3.generate_presigned_url(
                ClientMethod="get_object",
                Params={
                    "Bucket": BUCKET_NAME,
                    "Key": f"photos/{event_id}/{photo['photo_id']}.jpg"
                },
                ExpiresIn=3600  # valid for 1 hour from now
            )

        return success({"photos": photos})

    except Exception as e:
        return error(str(e))
    
    
if __name__ == "__main__":
    fake_event = {
        "body": "{}"
    }
    
    print(lambda_handler(fake_event, None))
