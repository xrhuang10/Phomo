import boto3
from datetime import datetime, timezone, timedelta

dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")

events_table = dynamodb.Table("Events")
photos_table = dynamodb.Table("Photos")

BUCKET_NAME = "phomo-photos-storage"

def delete_expired_photos():
    now = datetime.now(timezone.utc)
    print("🧼 Running cleanup at", now.isoformat())

    # Step 1: Scan all events
    events = events_table.scan().get("Items", [])
    for event in events:
        try:
            expires_at = datetime.fromisoformat(event["expires_at"])
        except Exception as e:
            print(f"⚠️ Skipping event (bad date): {event.get('event_code')}")
            continue

        # Step 2: Check if event expired + 24h ago
        if now > (expires_at + timedelta(hours=24)):
            event_id = event["event_id"]
            print(f"🗑️ Cleaning photos from expired event: {event_id}")

            # Step 3: Scan photos by event_id
            photos = photos_table.scan(
                FilterExpression=boto3.dynamodb.conditions.Attr("event_id").eq(event_id)
            ).get("Items", [])

            for photo in photos:
                photo_id = photo["photo_id"]
                s3_key = f"photos/{event_id}/{photo_id}.jpg"

                # Delete from S3
                try:
                    s3.delete_object(Bucket=BUCKET_NAME, Key=s3_key)
                    print(f"   ✅ Deleted from S3: {s3_key}")
                except Exception as e:
                    print(f"   ❌ Failed to delete from S3: {s3_key} — {str(e)}")

                # Delete from DynamoDB
                try:
                    photos_table.delete_item(Key={"photo_id": photo_id})
                    print(f"   ✅ Deleted from DynamoDB: {photo_id}")
                except Exception as e:
                    print(f"   ❌ Failed to delete from DynamoDB: {photo_id} — {str(e)}")

if __name__ == "__main__":
    delete_expired_photos()
