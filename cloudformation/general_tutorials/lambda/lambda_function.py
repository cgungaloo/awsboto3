import json
import boto3

def lambda_handler(event, context):
    
    iam_resource = boto3.resource("iam")
    lambda_client = boto3.client("iam")
    user_list = []
    for user in iam_console.users.all():
        user_list.add(user.name)
        
    http_resp = {}
    http_resp['statusCode'] = 200
    http_resp['headers'] = {}
    http_resp['headers']['Content-Type'] = 'application/json'
    http_resp['body'] = json.dumps(user_list)
    
    return http_resp