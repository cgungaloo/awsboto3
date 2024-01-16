
from time import sleep
from unittest import TestCase
import boto3
from api_gateway_helpers import APIGatewayManage
from lambda_helpers import LambdaManage
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


    # Entry point to run API creation and deployment
    def test_run_e2e(self):
        logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

        lambda_role_name = "gl-lambda-role"
        lambda_function_name = "gl-lambda-rest"
        lambda_handler_name = "awsboto3.lambdas.lambda_function.lambda_handler"
        lambda_filename = "awsboto3/lambdas/lambda_function.py"
        destination_file = 'awsboto3/lambdas/lambdafunction-gl.zip'

        iam_resource = boto3.resource("iam")
        lambda_client = boto3.client("lambda")
        wrapper = LambdaManage(lambda_client, iam_resource)

        api_name = "gl-demo-lambda-rest-api"

        # Deleting pre existing lambda
        wrapper.delete_lambda(lambda_function_name)

        # Creating IAM role
        iam_role, should_wait = wrapper.create_iam_role(lambda_role_name)

        if should_wait:
            logger.info("Giving AWS time to create resources...")
            sleep(10)

        logger.info(
            f"Creating AWS Lambda function {lambda_function_name} from "
            f"{lambda_handler_name}...")
        
        lambda_pck_bytes = wrapper.create_deployment_package(lambda_filename,
                                                             destination_file)

        # Deploy Lambda
        function_arn = wrapper.deploy_lambda_function(lambda_function_name,
                                       iam_role,
                                       lambda_handler_name,
                                        lambda_pck_bytes)
        
        logger.info('Creating API client gatewat')

        account_id = boto3.client("sts").get_caller_identity()['Account']
        api_base_path = "glapi"
        api_stage= 'test'

        apig_client = boto3.client("apigateway")

        api_wrapper = APIGatewayManage()

        # Deleting pre existing API
        api_wrapper.delete_api(api_name, apig_client)

        api_id = api_wrapper.create_api(apig_client,api_name)
        
        root_id = api_wrapper.get_root_id(apig_client, api_id)
        
        # create basepath
        base_id =api_wrapper.create_basepath(apig_client,api_id,root_id,api_base_path)

        api_wrapper.create_method(apig_client, api_id, base_id, function_arn)

        # x=5&y=3&op=myop

        # deploy gateway
        api_wrapper.create_deployment(apig_client,api_id,api_stage, account_id, 
                                      api_base_path,lambda_client, function_arn)
        
        api_url = api_wrapper.construct_api_url(api_id, apig_client.meta.region_name, api_stage, api_base_path)
        api_url

