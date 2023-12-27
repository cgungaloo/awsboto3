
from time import sleep
from unittest import TestCase
import boto3
from botocore.stub import Stubber
from awsboto3.lambda_helpers import LambdaManage
import logging

class Test(TestCase):
    

    def test_list_functions(self):
        lambda_client = boto3.client("lambda")

        functions = lambda_client.list_functions()
        print('-',100)
        print(functions)
        functionfound = ''
        for function in functions['Functions']:
            if function['FunctionName'] == 'getItem':
                functionfound = function
                break

        functionfound

    def test_run_e2e(self):
        logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

        lambda_role_name = "gl-lambda-role"
        lambda_function_name = "gl-lambda-rest"
        lambda_handler_name = "lambda_handler_rest.lambda_handler"
        lambda_filename = "awsboto3/lambdas/lambda_function.py"
        destination_file = 'awsboto3/lambdas/lambdafunction-gl.zip'

        iam_resource = boto3.resource("iam")
        lambda_client = boto3.client("lambda")
        wrapper = LambdaManage(lambda_client, iam_resource)

        iam_role, should_wait = wrapper.create_iam_role(lambda_role_name)

        # Replace with proper checking
        if should_wait:
            logger.info("Giving AWS time to create resources...")
            sleep(10)

        logger.info(
            f"Creating AWS Lambda function {lambda_function_name} from "
            f"{lambda_handler_name}...")
        
        lambda_pck_bytes = wrapper.create_deployment_package(lambda_filename,
                                                             destination_file)

        wrapper.deploy_lambda_function(lambda_function_name,
                                       iam_role,
                                       lambda_handler_name,
                                        lambda_pck_bytes)

