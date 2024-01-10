import boto3

def lambda_handler(event, context):
    client = boto3.resource('dynamodb')
    table = client.Table('articles')
    response = table.delete_item(
        Key={
        'id': event['queryStringParameters']['id']
        }
    )
    
    http_res = {}
    http_res['headers'] = {}
    http_res['headers']['Content-Type'] = 'application/json'
    http_res['statusCode'] = response['ResponseMetadata']['HTTPStatusCode']
    http_res['body'] = 'Article ' + event['queryStringParameters']['id']+ ' deleted successfully'
    
    return http_res