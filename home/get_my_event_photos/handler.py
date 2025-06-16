import json
import boto3
from utils.response import success, error
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource("dynamodb")
photos_table = dynamodb.Table("Photos")
users_table = dynamodb.Table("Users")

def lambda_handler(event, context):
    try:
        user_id = "test-user-1"  # Replace with Cognito later

        # Get user's active event
        user = users_table.get_item(Key={"user_id": user_id}).get("Item")
        if not user or "active_event_id" not in user:
            return success({"photos": []})

        event_id = user["active_event_id"]

        # Query photos uploaded by this user in this event
        result = photos_table.scan(
            FilterExpression=Attr("event_id").eq(event_id) & Attr("uploader_id").eq(user_id)
        )

        photos = result.get("Items", [])

        cleaned_photos = []

        for photo in photos:
            if "image_url" in photo and isinstance(photo["image_url"], str):
                cleaned_photos.append({
                    "photo_id": photo.get("photo_id"),
                    "event_id": photo.get("event_id"),
                    "uploader_id": photo.get("uploader_id"),
                    "image_url": photo["image_url"],
                    "timestamp": photo.get("timestamp")
                })

        # Optional: log for debugging
        print("Returning cleaned photos:", cleaned_photos)

        return success({"photos": cleaned_photos})

    except Exception as e:
        return error(str(e))
    


if __name__ == "__main__":
    fake_event = {
        "body": "{}"
    }
    print(lambda_handler(fake_event, None))

