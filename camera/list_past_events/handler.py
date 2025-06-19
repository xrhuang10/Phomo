import json
import boto3
from boto3.dynamodb.conditions import Key
from utils.response import success, error

dynamodb = boto3.resource('dynamodb')
photos_table = dynamodb.Table('Photos')
events_table = dynamodb.Table('Events')

def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))
        user_id = body.get("user_id")

        if not user_id:
            return error("Missing user_id")

        # Step 1: Query Photos table to get all event_ids the user uploaded to
        response = photos_table.query(
            IndexName='user_id-index',
            KeyConditionExpression=Key('user_id').eq(user_id)
        )

        photo_items = response.get('Items', [])
        unique_event_ids = list({item['event_id'] for item in photo_items})

        if not unique_event_ids:
            return success({"events": []})

        # Step 2: Fetch each Event by event_id
        events = []
        for event_id in unique_event_ids:
            event_response = events_table.get_item(Key={"event_id": event_id})
            event_item = event_response.get('Item')

            if event_item:
                events.append({
                    "event_id": event_item["event_id"],
                    "event_name": event_item.get("event_name", ""),
                    "host": event_item.get("created_by", ""),
                    "cover_photo_url": event_item.get("cover_photo", ""),
                    "start_time": event_item.get("start_time", "")
                })

        # Step 3: Sort events by start_time descending
        events.sort(key=lambda x: x["start_time"], reverse=True)

        return success({"events": events})

    except Exception as e:
        print(f"Error in list_past_events: {str(e)}")
        return error("Failed to list past events.")
