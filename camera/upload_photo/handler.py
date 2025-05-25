import json
import boto3
import uuid
import base64
from datetime import datetime, timezone
from utils.response import success, error

dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")
photos_table = dynamodb.Table("Photos")

BUCKET_NAME = "phomo-photos-storage"

def lambda_handler(event, context):
    try:
        user_id = "test-user-1"  # replace with Cognito later
        body = json.loads(event["body"])

        # Simulate getting image (in real app, this is base64-encoded)
        image_data = body.get("image_data")
        event_id = body.get("event_id")

        if not image_data or not event_id:
            return error("Missing image data or event_id.")

        photo_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()
        s3_key = f"photos/{event_id}/{photo_id}.jpg"

        # Convert base64 string to bytes
        image_bytes = base64.b64decode(image_data)

        # Upload to S3
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=s3_key,
            Body=image_bytes,
            ContentType='image/jpeg'
        )
        
        # Generate 24-hour signed URL
        download_url = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': BUCKET_NAME,
                'Key': s3_key
            },
            ExpiresIn=86400  # 24 hours in seconds
        )

        image_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{s3_key}"

        # Store in DynamoDB
        photos_table.put_item(Item={
            "photo_id": photo_id,
            "event_id": event_id,
            "uploader_id": user_id,
            "timestamp": timestamp,
            "image_url": image_url
        })
        
        print("Uploading photo to event:", event_id)
        
        return success({
            "message": "Photo uploaded!",
            "photo_id": photo_id,
            "image_url": image_url,
            "download_url": download_url
        })

    except Exception as e:
        return error(str(e))


if __name__ == "__main__":
    with open("sample.jpg", "rb") as image_file:
        image_data = base64.b64encode(image_file.read()).decode("utf-8")

    fake_event = {
        "body": json.dumps({
            "image_data": image_data,
            "event_id": "5e4f786c-82c7-4622-ad32-776283625a76"
        })
    }

    print(lambda_handler(fake_event, None))
