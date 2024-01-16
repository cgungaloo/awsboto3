import json
from unittest import TestCase
from unittest.mock import MagicMock, patch
import boto3
from botocore.stub import Stubber
import pytest
from lambda_helpers import LambdaManage

class Test(TestCase):

    def test_create_deployment_package(self):
        test_filename = 'awsboto3/lambdas/lambda_function.py'
        destination_file = 'awsboto3/lambdas/lambdafunction-gl.zip'
        lambda_client = boto3.client("lambda")
        lambda_resource = boto3.resource("iam")

        lambda_manager = LambdaManage(lambda_client, lambda_resource)
        lambda_manager.create_deployment_package(test_filename, destination_file)

    @patch("boto3.resource")
    def test_iam_role(self, mock_resource):

        lambda_client = boto3.client("lambda")

        lambda_manager = LambdaManage(lambda_client, mock_resource)
        lambda_manager.get_iam_role('some_role_name')
        
        mock_resource.Role.assert_called_with('some_role_name')
        mock_resource.Role().load.assert_called()
    

    @patch("boto3.resource")
    def test_create_iam_role(self, mock_resource):
        role_name = "test_iam_role_cg"

        lambda_role_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "lambda.amazonaws.com"},
                    "Action": "sts:AssumeRole",
                }
            ],
        }

        policy_arn = 'arn:aws:iam::443231674046:policy/gl-policies'
        json_dumped_lambda_role_policy = json.dumps(lambda_role_policy)

        lambda_client = boto3.client("lambda")
        lambda_manager = LambdaManage(lambda_client, mock_resource)
        lambda_manager.get_iam_role= MagicMock()
        lambda_manager.get_iam_role.return_value = None
        lambda_manager.create_iam_role(role_name)
        mock_resource.create_role.assert_called_with(RoleName=role_name, 
                                                AssumeRolePolicyDocument=json_dumped_lambda_role_policy)
        
        mock_resource.create_role().attach_policy.assert_called_with(PolicyArn=policy_arn)

    def test_create_role_error(self):
        role_name = "test_iam_role_cg"
        lambda_client = boto3.client("lambda")
        resource_client = boto3.resource('iam')

        resource_stubber = Stubber(resource_client.meta.client)

        resource_stubber.add_client_error('create_role','EntityAlredyExists')
        resource_stubber.activate()
        lambda_manager = LambdaManage(lambda_client, resource_client)

        lambda_manager.get_iam_role= MagicMock()
        lambda_manager.get_iam_role.return_value = None

        with pytest.raises(SystemError) as clientexcp:
            lambda_manager.create_iam_role(role_name)
        
        assert str(clientexcp.value) == 'Entity already exists'
        


    def test_check_function_exists_false(self):

        lambda_client = boto3.client("lambda")

        lambda_stubber = Stubber(lambda_client)

        functions_response = {
            'NextMarker':'my-marker-gl',
            'Functions': [

            ]
        }
        lambda_stubber.add_response('list_functions',functions_response)
        lambda_stubber.activate()

        lambda_resource = boto3.resource("iam")
        lambda_manager = LambdaManage(lambda_client, lambda_resource)

        exists = lambda_manager.check_if_function_exists('myfunction')
        self.assertFalse(exists)


    def test_check_function_exists_true(self):

        lambda_client = boto3.client("lambda")

        lambda_stubber = Stubber(lambda_client)

        functions_response = {
            'NextMarker':'my-marker-gl',
            'Functions': [
                {
                    'FunctionName': 'myfunction'
                },
                {
                    'FunctionName': 'otherfunction'
                }
            ]
        }
        lambda_stubber.add_response('list_functions',functions_response)
        lambda_stubber.activate()

        lambda_resource = boto3.resource("iam")
        lambda_manager = LambdaManage(lambda_client, lambda_resource)

        exists = lambda_manager.check_if_function_exists('myfunction')
        self.assertTrue(exists)