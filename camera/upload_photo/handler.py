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
    print("upload_photo_phomo triggered by:", json.dumps(event))

    try:
        user_id = "test-user-1"  # Replace with Cognito integration later
        body = json.loads(event["body"])

        image_data = body.get("image_data")
        event_id = body.get("event_id")

        if not image_data or not event_id:
            return error("Missing image data or event_id.")

        photo_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()
        s3_key = f"photos/{event_id}/{photo_id}.jpg"

        # Decode base64 image
        image_bytes = base64.b64decode(image_data)

        # Upload to S3
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=s3_key,
            Body=image_bytes,
            ContentType='image/jpeg'
        )

        # Generate signed download URL (valid for 24h)
        download_url = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': s3_key},
            ExpiresIn=86400
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

        print("Photo uploaded to event:", event_id)

        return success({
            "message": "Photo uploaded!",
            "photo_id": photo_id,
            "image_url": image_url,
            "download_url": download_url
        })

    except Exception as e:
        print("Error occurred:", str(e))
        return error(str(e))


if __name__ == "__main__":
    with open("sample.jpg", "rb") as image_file:
        image_data = base64.b64encode(image_file.read()).decode("utf-8")

    fake_event = {
        "body": json.dumps({
            "image_data": image_data,
            "event_id": "717dcbec-b252-42fa-8a6a-19623b9b8c56"
        })
    }

    print(lambda_handler(fake_event, None))
