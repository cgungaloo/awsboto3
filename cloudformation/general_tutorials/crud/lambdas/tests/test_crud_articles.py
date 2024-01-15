from unittest import TestCase
from unittest import mock
from awsboto3.cloudformation.general_tutorials.crud.lambdas.get_all_articles import lambda_handler as get_all_lambda
from awsboto3.cloudformation.general_tutorials.crud.lambdas.create_articles import lambda_handler as create_lambda
from awsboto3.cloudformation.general_tutorials.crud.lambdas.get_single_article import lambda_handler as single_lambda
from unittest.mock import patch, Mock
from boto3.dynamodb.conditions import Attr
from botocore.stub import Stubber
import boto3

from awsboto3.cloudformation.general_tutorials.crud.lambdas.tests.test_helpers.lambda_context import LambdaContext

class Test(TestCase):
    
    @patch("boto3.resource")
    def test_get_all_articles(self, mock_resource):
        event = {"queryStringParameters": 
                    {"title":"mytitle"}}
        context = "context_test"

        mock_table = Mock()
        mock_table.scan.return_value = {'Items':'responseval'}
        mock_resource.return_value.Table.return_value = mock_table
        response = get_all_lambda(event,context)

        mock_resource.return_value.Table.assert_called_with('articles')
        mock_table.scan.assert_called_with(
            FilterExpression= Attr('title').begins_with("mytitle")
        )

        assert response['statusCode'] == 200
        assert response['headers']['Content-Type'] == 'application/json'
        assert response['body'] == '"responseval"'
    
    @patch("boto3.resource")
    def test_get_all_key_error(self, mock_resource):
        event = {"queryStringParameters": 
                    {"badkey":"mytitle"}}
        context = "context_test"

        response = get_all_lambda(event, context)

        assert response['statusCode'] == 400
        assert response['headers']['Content-Type'] == 'application/json'
        assert response['body'] == '"Got Key Error: \'title\'"'
    
    @patch("boto3.resource")
    def test_create_key_error(self, mock_resource):
        event = {"queryStringParameters": 
                    {"badkey":"mytitle"}}
        context = "context_test"

        response = get_all_lambda(event, context)

        assert response['statusCode'] == 400
        assert response['headers']['Content-Type'] == 'application/json'
        assert response['body'] == '"Got Key Error: \'title\'"'

    @patch("boto3.resource")
    def test_create_article(self, mock_resource):
        event = {"queryStringParameters": 
                    {"title":"mytitle",
                     "description":"mydescription"}}
        context = LambdaContext()

        mock_table = Mock()
        mock_table.put_item.return_value = {'ResponseMetadata':
                                            {'HTTPStatusCode':200}
                                            }
        mock_resource.return_value.Table.return_value = mock_table

        response = create_lambda(event, context)

        mock_table.put_item.assert_called_with(
            Item ={
                'id':context.aws_request_id,
                'title': event['queryStringParameters']['title'],
                'description': event['queryStringParameters']['description'],
                'published': False,
                'createdAt': mock.ANY,
                'updatedAt': mock.ANY
            }
        )

        assert response['statusCode'] == 200
        assert response['body'] == 'Record abc123 added'
    
    @patch("boto3.resource")
    def test_single_item(self, mock_resource):
        event = {"queryStringParameters": 
                    {"id":"abc123"}}
        context = LambdaContext()

        mock_table = Mock()
        mock_table.get_item.return_value = {'statusCode': 200, 'Item':'item creaed'}
        mock_resource.return_value.Table.return_value = mock_table
        response = single_lambda(event, context)

        mock_table.get_item_assert_called_with(
            Key={
            'id': event['queryStringParameters']['id']
        }
        )
        

    def test_create_client_error(self):
        event = {"queryStringParameters": 
                    {"title":"mytitle",
                     "description":"mydescription"}}
        context = LambdaContext()

        db_resource = boto3.resource('dynamodb')
        resource_stubber = Stubber(db_resource.meta.client)

        resource_stubber.add_client_error('put_item','LimitExceededException')
        resource_stubber.activate()

        with mock.patch('boto3.resource', mock.MagicMock(return_value=db_resource)):
            response = create_lambda(event, context)
            assert response['body'] == '"Got ClientError: An error occurred (LimitExceededException) when calling the PutItem operation: "'
            assert response['statusCode'] == 500