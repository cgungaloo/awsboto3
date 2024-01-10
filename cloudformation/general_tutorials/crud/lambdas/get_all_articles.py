import json
import boto3
from boto3.dynamodb.conditions import Attr

def lambda_handler(event, context):
    print("Event json %s" % json.dumps(event))
    print("Context %s" % context)
    
    client = boto3.resource('dynamodb')
    table = client.Table('articles')
    
    title = event['queryStringParameters']['title']

    print("Getting Title Filter %s" % title)
    
    if not title:
        print("Title is empty")
        response = table.scan()
    else:
        print("Title is not empty")
        
    response = table.scan(
                     FilterExpression = Attr('title').begins_with(title)
                     )
        
    http_res = {}
    http_res['statusCode'] = 200
    http_res['headers'] = {}
    http_res['headers']['Content-Type'] = 'application/json'
    http_res['body'] = json.dumps(response['Items'])
    
    
    return http_res