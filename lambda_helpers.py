
import json
import logging
from time import sleep
import zipfile
from botocore.exceptions import ClientError
import boto3

logger = logging.getLogger(__name__)

class LambdaManage:
    def __init__(self,lambda_client, iam_resource):
        self.lambda_client = lambda_client
        self.iam_resource = iam_resource
    
    def get_iam_role(self, iam_role_name):
        role = None

        try:
            temp_role = self.iam_resource.Role(iam_role_name)
            temp_role.load()
            role = temp_role
            logger.info("Got IAM role %s", role.name)
        except ClientError as err:
            if err.response["Error"]["Code"] == "NoSuchEntity":
                logger.info("IAM role %s does not exist.", iam_role_name)
            else:
                logger.error(
                    "Couldn't get IAM role %s. Here's why: %s: %s",
                    iam_role_name,
                    err.response["Error"]["Code"],
                    err.response["Error"]["Message"],
                )
                raise
        return role
    
    def delete_role(self, iam_role_name):
        try:
            iam_client = boto3.client('iam')
            policies = iam_client.list_attached_role_policies(RoleName=iam_role_name)['AttachedPolicies']
            for policy in policies:
                policy_arn = iam_client.get_policy(PolicyArn=policy['PolicyArn'])['Policy']['Arn']
                iam_client.detach_role_policy(RoleName=iam_role_name, PolicyArn =policy_arn)
            iam_client.delete_role(RoleName=iam_role_name)
        except Exception as e:
            logger.info(f"Cant find role {iam_role_name}")

    def create_iam_role(self, iam_role_name):
        self.delete_role(iam_role_name)

        role = self.get_iam_role(iam_role_name)

        if role is not None:
            return role, False
        
        lambda_role_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "lambda.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }
            ],
        }

        add_permission_policy_arn = 'arn:aws:iam::443231674046:policy/gl-policies'

        policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"

        try:
            role = self.iam_resource.create_role(
                RoleName= iam_role_name,
                AssumeRolePolicyDocument=json.dumps(lambda_role_policy)
            )

            logger.info(f'Created role : {role.name}')
            role.attach_policy(PolicyArn=policy_arn)
            role.attach_policy(PolicyArn=add_permission_policy_arn)
            logger.info(f'Attached execution policy to role: {role.name}')
        except ClientError as error:
            if error.response["Error"]["Code"] == "EntityAlredyExists":
                role = self.iam_resource.Role(iam_role_name)
                logger.warning(f'The Role {role.name}')
                raise SystemError('Entity already exists',)
            else:
                logger.exception(
                    f"Issue Creating role {iam_role_name} or attach policy {add_permission_policy_arn}"
                )
            raise

        return role, True

    def create_deployment_package(self,filename, destination_file):
        
        with zipfile.ZipFile(destination_file, 'w') as zip_object:
            zip_object.write(filename)

        with open(destination_file,'rb') as file_data:
            bytes_content = file_data.read()
        return bytes_content

    def deploy_lambda_function(self, function_name,
                               iam_role, handler_name,
                               deployment_package):
    
        if self.check_if_function_exists(function_name) is False:
            try:
                response = self.lambda_client.create_function(
                    FunctionName=function_name,
                    Description="GL AWS Lambda doc example",
                    Runtime="python3.12",
                    Role=iam_role.arn,
                    Handler=handler_name,
                    Code={"ZipFile": deployment_package},
                    Publish=True,
                )
                sleep(5)
            except ClientError as error:
                logger.info(f'Error {error.response["Error"]["Code"] }')


            if self.check_if_function_exists(function_name):
                logger.info(f'Created Function {function_name}!!!!')
                return response['FunctionArn']
            else:
                raise
        
    def check_if_function_exists(self,function_name):
        try:
            functions = self.lambda_client.list_functions()
            for function in functions['Functions']:
                if function['FunctionName'] == function_name:
                    return True
            return False
        except ClientError as error:
                logger.info(f'Error {error.response["Error"]["Code"] }')


    def delete_lambda(self, lambda_function_name):
        if self.check_if_function_exists(lambda_function_name):
            try:
                self.lambda_client.delete_function(FunctionName=lambda_function_name)
            except ClientError as error:
                logger.info(f'Error {error.response["Error"]["Code"] }')
            

