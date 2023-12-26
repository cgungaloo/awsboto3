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
        role = lambda_manager.get_iam_role('some_role_name')
        
        mock_resource.Role.assert_called_with('some_role_name')
        mock_resource.Role().load.assert_called()

    def test_create_iam_role(self):
        role_name = "test_iam_role_cg"

        lambda_client = boto3.client("lambda")
        iam_resource = boto3.resource("iam")
        lambda_manager = LambdaManage(lambda_client, iam_resource)
        lambda_manager.create_iam_role(role_name)
