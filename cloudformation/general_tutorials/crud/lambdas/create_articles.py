import json
import boto3
import datetime

def lambda_handler(event, context):
    print(type(event))
    print(event)
    print("Event json %s" % json.dumps(event))
    print("Context %s" % context)
    client = boto3.resource('dynamodb')
    table = client.Table('articles')

    eventDateTime = (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
    published = False
    response = table.put_item(
            Item = {
                'id': context.aws_request_id,
                'title': event['queryStringParameters']['title'],
                'description': event['queryStringParameters']['description'],
                'published': published,
                'createdAt': eventDateTime,
                'updatedAt': eventDateTime
            }
    )
    
    http_res = {}
    http_res['headers'] = {}
    http_res['headers']['Content-Type'] = 'application/json'
    http_res['statusCode'] = response['ResponseMetadata']['HTTPStatusCode']
    http_res['body'] = 'Record ' + context.aws_request_id + ' added'
    
    return http_res