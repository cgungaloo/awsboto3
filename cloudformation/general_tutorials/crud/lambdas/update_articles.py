import json
import boto3
from datetime import datetime

def lambda_handler(event, context):
    print("Event json %s" % json.dumps(event))
    print("Context %s" % context)
       
    client = boto3.resource('dynamodb')
    table = client.Table('articles')
    eventDateTime = (datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
    published = False
    
    body = json.loads(event['body'])
    response = table.put_item(
        Item={
                'id':  body['id'],
                'title': body['title'],
                'description': body['description'],
                'published': body['published'],
                'updatedAt': eventDateTime,
                'createdAt': eventDateTime
           }
       )
       
    http_res = {}
    http_res['headers'] = {}
    http_res['headers']['Content-Type'] = 'application/json'
    http_res['statusCode'] = response['ResponseMetadata']['HTTPStatusCode']
    http_res['body'] = 'Record ' + context.aws_request_id + ' added'
    return http_res