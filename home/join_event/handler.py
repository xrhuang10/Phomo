import boto3
from datetime import datetime, timezone

dynamodb = boto3.resource("dynamodb")
users_table = dynamodb.Table("Users")
events_table = dynamodb.Table("Events")

def test_join_event():
    user_id = "test-user-123"
    event_code = "551150"

    # Check if event exists
    event = events_table.get_item(Key={"event_code": event_code}).get("Item")
    if not event:
        print("❌ Invalid event code")
        return

    # Check if event expired
    expires_at = datetime.fromisoformat(event["expires_at"])
    if datetime.now(timezone.utc) > expires_at:
        print("❌ Event expired")
        return

    # Add to user table
    users_table.put_item(Item={
        "user_id": user_id,
        "active_event_id": event["event_id"],
        "joined_at": datetime.now(timezone.utc).isoformat()
    })

    print("✅ Successfully joined event!")

if __name__ == "__main__":
    test_join_event()
