import json
import boto3
from botocore.exceptions import ClientError
import datetime
import logging

def lambda_handler(event, context):
    logger = logging.getLogger(__name__)

    logger.info(type(event))
    logger.info(event)
    logger.info("Event json %s" % json.dumps(event))
    logger.info("Context %s" % context)

    client = boto3.resource('dynamodb')
    table = client.Table('articles')

    http_res = {}
    http_res['headers'] = {}
    http_res['headers']['Content-Type'] = 'application/json'

    eventDateTime = (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
    published = False
    try:
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
    except ClientError as ce:
        logger.info(f'Got ClientError: {str(ce)}')
        logger.info(f'Exception : {str(ce)}')
        logger.info(f'Returning 500 error')
        http_res['statusCode'] = 500
        http_res['body'] = json.dumps(f'Got ClientError: {str(ce)}')
        return http_res


    http_res['statusCode'] = response['ResponseMetadata']['HTTPStatusCode']
    http_res['body'] = 'Record ' + context.aws_request_id + ' added'
    
    return http_res