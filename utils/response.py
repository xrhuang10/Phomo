import json

def success(data):
    return {
        "statusCode": 200,
        "body": json.dumps({"status": "success", "data": data})
    }

def error(message):
    return {
        "statusCode": 400,
        "body": json.dumps({"status": "error", "message": message})
    }
