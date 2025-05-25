import json
import boto3
from utils.response import success, error
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource("dynamodb")
photos_table = dynamodb.Table("Photos")
users_table = dynamodb.Table("Users")

def lambda_handler(event, context):
    try:
        user_id = "test-user-123"  # Replace with Cognito later

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

        # Optional: include image URLs only
        for photo in photos:
            photo["image_url"] = photo.get("image_url")

        return success({"photos": photos})

    except Exception as e:
        return error(str(e))
