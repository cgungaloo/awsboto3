import json
from unittest import TestCase
from unittest.mock import MagicMock, patch
import boto3
from botocore.stub import Stubber
from awsboto3.lambda_helpers import LambdaManage

class Test(TestCase):

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

        policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
        json_dumped_lambda_role_policy = json.dumps(lambda_role_policy)

        lambda_client = boto3.client("lambda")
        lambda_manager = LambdaManage(lambda_client, mock_resource)
        lambda_manager.get_iam_role= MagicMock()
        lambda_manager.get_iam_role.return_value = None
        lambda_manager.create_iam_role(role_name)
        mock_resource.create_role.assert_called_with(RoleName=role_name, 
                                                AssumeRolePolicyDocument=json_dumped_lambda_role_policy)
        mock_resource.create_role().attach_policy.assert_called_with(PolicyArn=policy_arn)

