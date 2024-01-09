import json
import boto3
def lambda_handler(event, context):
    client = boto3.resource('dynamodb')
    table = client.Table('articles')
    response = table.get_item(
        Key={
        'id': event['queryStringParameters']['id']
    }
    )
    
    http_res = {}
    http_res['headers'] = {}
    http_res['headers']['Content-Type'] = 'application/json'
    
    if 'Item' in response:
        
        http_res['statusCode'] = 200
        http_res['body'] = json.dumps(response['Item'])
        
        
        return http_res
    else:
        
        http_res['statusCode'] = 400
        http_res['body'] = json.dumps(f'Not item {event['queryStringParameters']['id']}')
        
        return http_res