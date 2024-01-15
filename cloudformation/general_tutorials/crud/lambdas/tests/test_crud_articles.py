from unittest import TestCase
from awsboto3.cloudformation.general_tutorials.crud.lambdas.get_all_articles import lambda_handler as get_all_lambda
from unittest.mock import patch, Mock
from boto3.dynamodb.conditions import Attr

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
        





        