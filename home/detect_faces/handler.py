# import boto3

# rekognition = boto3.client('rekognition')

# response = rekognition.create_collection(CollectionId='phomo-user-faces')
# print(response)

import boto3
import json
from boto3.dynamodb.conditions import Attr

# AWS clients
dynamodb = boto3.resource("dynamodb")
rekognition = boto3.client("rekognition")

# Config
USERS_TABLE = "Users"
PHOTOS_TABLE = "Photos"
REKOGNITION_COLLECTION = "phomo-user-faces"
BUCKET = "phomo-photos-storage"
PHOTO_PREFIX = "photos/"
PROFILE_PREFIX = "profile-pictures/"

def lambda_handler(event, context):
    user_id = event.get("user_id")
    event_id = event.get("event_id")
    profile_picture_key = event.get("profile_picture_key")  # new param

    if not user_id or not event_id or not profile_picture_key:
        return {"statusCode": 400, "body": "Missing user_id, event_id, or profile_picture_key"}

    # 1. Check if user's face_id is already stored
    users_table = dynamodb.Table(USERS_TABLE)
    user = users_table.get_item(Key={"user_id": user_id}).get("Item")
    face_id = None

    if user and "face_id" in user:
        face_id = user["face_id"]
        print(f"✅ Using existing face_id: {face_id}")
    else:
        # 2. Index the user's profile picture in Rekognition
        try:
            index_response = rekognition.index_faces(
                CollectionId=REKOGNITION_COLLECTION,
                Image={"S3Object": {"Bucket": BUCKET, "Name": profile_picture_key}},
                ExternalImageId=user_id,
                DetectionAttributes=["DEFAULT"]
            )

            face_records = index_response.get("FaceRecords", [])
            if not face_records:
                return {"statusCode": 422, "body": "No face detected in profile picture."}

            face_id = face_records[0]["Face"]["FaceId"]
            print(f"✅ Face indexed. FaceId: {face_id}")

            # Save face_id to Users table
            users_table.update_item(
                Key={"user_id": user_id},
                UpdateExpression="SET face_id = :f, profile_picture = :p",
                ExpressionAttributeValues={
                    ":f": face_id,
                    ":p": profile_picture_key
                }
            )
            print("✅ face_id saved to Users table.")

        except Exception as e:
            return {"statusCode": 500, "body": f"Error indexing face: {str(e)}"}

    # 3. Scan Photos table for this event
    photos_table = dynamodb.Table(PHOTOS_TABLE)
    try:
        response = photos_table.scan(
            FilterExpression=Attr("event_id").eq(event_id)
        )
        photos = response.get("Items", [])
    except Exception as e:
        return {"statusCode": 500, "body": f"Error scanning Photos table: {str(e)}"}

    # 4. Compare each photo in the event with the user’s face
    matched_photos = []
    for photo in photos:
        photo_key = photo.get("photo_key") or photo.get("s3_key")
        expected_prefix = f"{PHOTO_PREFIX}{event_id}/"
        if not photo_key or not photo_key.startswith(expected_prefix):
            continue

        try:
            rek_response = rekognition.search_faces_by_image(
                CollectionId=REKOGNITION_COLLECTION,
                Image={"S3Object": {"Bucket": BUCKET, "Name": photo_key}},
                FaceMatchThreshold=80,
                MaxFaces=3
            )
            matches = rek_response.get("FaceMatches", [])
            if any(match["Face"]["FaceId"] == face_id for match in matches):
                matched_photos.append(photo)

        except Exception as e:
            print(f"Rekognition failed for {photo_key}: {e}")

    return {
        "statusCode": 200,
        "body": json.dumps(matched_photos)
    }

# === LOCAL TESTING ENTRY POINT ===
if __name__ == "__main__":
    test_event = {
        "user_id": "test-user-123",
        "event_id": "b71b19be-9f28-4199-b972-2f417f58d867",
        "profile_picture_key": "profile-pictures/Headshot.jpg"  # Replace with your actual key
    }

    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))
