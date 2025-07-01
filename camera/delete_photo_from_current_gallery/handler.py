import json
import boto3
from datetime import datetime, timezone
from utils.response import success, error

dynamodb = boto3.resource('dynamodb')
photos_table = dynamodb.Table('Photos')
events_table = dynamodb.Table('Events')
s3 = boto3.client('s3')

BUCKET_NAME = "phomo-photos-storage"  # adjust if your bucket is different

def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))
        user_id = body.get("user_id")
        photo_id = body.get("photo_id")

        if not user_id or not photo_id:
            return error("Missing user_id or photo_id.")

        # Step 1: Fetch photo to confirm uploader and get event_id and image_url
        photo_item = photos_table.get_item(Key={"photo_id": photo_id}).get("Item")
        if not photo_item:
            return error("Photo not found.")

        if photo_item.get("uploader_id") != user_id:
            return error("User is not the uploader of this photo.")

        event_id = photo_item.get("event_id")
        image_url = photo_item.get("image_url")

        # Step 2: Fetch event to confirm it is still active
        event_item = events_table.get_item(Key={"event_id": event_id}).get("Item")
        if not event_item:
            return error("Event not found.")

        now = datetime.now(timezone.utc).isoformat()
        start_time = event_item.get("start_time")
        end_time = event_item.get("end_time")

        if not (start_time <= now <= end_time):
            return error("Event is not active. Photos can only be deleted during the event.")

        # Step 3: Delete photo from Photos table
        photos_table.delete_item(Key={"photo_id": photo_id})

        # Step 4: Delete photo from S3
        # Parse S3 key from image_url
        # e.g., "https://phomo-photos-storage.s3.amazonaws.com/event123/photo456.jpg"
        s3_key = image_url.split(f"{BUCKET_NAME}.s3.amazonaws.com/")[-1]
        s3.delete_object(Bucket=BUCKET_NAME, Key=s3_key)

        return success({"message": "Photo deleted successfully from gallery and S3."})

    except Exception as e:
        print(f"Error in delete_photo_from_current_gallery: {str(e)}")
        return error("Failed to delete photo from gallery.")

# For local testing
if __name__ == "__main__":
    test_event = {
        "body": json.dumps({
            "user_id": "test-user-uuid",
            "photo_id": "test-photo-uuid"
        })
    }
    print(lambda_handler(test_event, None))
