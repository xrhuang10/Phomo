from handler import lambda_handler as lambda_function

# Mock event payload
mock_event = {
    "version": "1",
    "region": "us-east-1",
    "userPoolId": "test_pool_id",
    "userName": "testuser",
    "callerContext": {
        "awsSdkVersion": "aws-sdk-unknown-unknown",
        "clientId": "testclientid"
    },
    "triggerSource": "PostConfirmation_ConfirmSignUp",
    "request": {
        "userAttributes": {
            "sub": "12345678-1234-1234-1234-123456789012",
            "email": "testuser@example.com"
        }
    },
    "response": {}
}

# Mock context
class Context:
    def __init__(self):
        self.function_name = "phomo_create_user_on_signup"
        self.memory_limit_in_mb = 128
        self.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:phomo_create_user_on_signup"
        self.aws_request_id = "test-invoke-request"

mock_context = Context()

# Invoke the Lambda function
response = lambda_function(mock_event, mock_context)

print(response)
