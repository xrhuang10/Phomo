import json
from home.create_event import handler as create_event
from home.join_event import handler as join_event
from camera.upload_photo import handler as upload_photo
from home.get_my_event_photos import handler as get_my_photos
from home.get_photos_after_event import handler as get_all_photos
from datetime import datetime, timezone
import base64
import time

# Fake test user
USER_ID = "test-user-1"

def simulate_flow():
    print("\n🔧 Step 1: Create Event")
    create_response = create_event.lambda_handler({
        "body": json.dumps({"name": "Phomo Test Event"})
    }, None)
    print(create_response)

    data = json.loads(create_response["body"])["data"]
    event_code = data["event_code"]
    event_id = data["event_id"]

    print("\n🚪 Step 2: Join Event")
    join_response = join_event.lambda_handler({
        "body": json.dumps({"event_code": event_code})
    }, None)
    print(join_response)

    print("\n📸 Step 3: Upload Photo(s)")
    # Read a sample image
    with open("sample.jpg", "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")

    for i in range(3):
        upload_response = upload_photo.lambda_handler({
            "body": json.dumps({
                "image_data": image_data,
                "event_id": event_id
            })
        }, None)
        print(f"Uploaded photo {i+1}: {upload_response}")

    print("\n🖼️ Step 4: View My Photos During Event")
    my_photos = get_my_photos.lambda_handler({
        "body": "{}"
    }, None)
    print(my_photos)

    print("\n⏱️ Step 5: Simulate Event Expiry")
    print("Manually update event's expires_at in DynamoDB to be in the past (or wait)...")
    input("Press Enter when ready to test get_photos_after_event...")

    print("\n🔓 Step 6: View All Photos After Expiry")
    all_photos = get_all_photos.lambda_handler({
        "body": "{}"
    }, None)
    print(all_photos)


if __name__ == "__main__":
    simulate_flow()
