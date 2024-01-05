
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class APIGatewayManage:

    def create_api(self, apig_client,api_name):
        try:
            # Create API with name
            response = apig_client.create_rest_api(name=api_name)
            # Confirm creation by getting generated ID
            api_id = response['id']
            logger.info("Create REST API %s with ID %s.", api_name, api_id)
            return api_id
    
        except ClientError as error:
            logger.info(f'Error {error.response["Error"]["Code"] }')


    def get_root_id(self,api_client,api_id):

        response = api_client.get_resources(restApiId=api_id)
        root_id = next(item["id"] for item in response["items"] if item["path"] == "/")
        logger.info("Found root resource of the REST API with ID %s.", root_id)
        return root_id
    
    def create_basepath(self, api_client,api_id,root_id, api_base_path):
        response = api_client.create_resource(
            restApiId=api_id, parentId=root_id, pathPart=api_base_path
        )

        base_id = response["id"]
        logger.info("Created base path %s with ID %s.", api_base_path, base_id)

        return base_id
    
    def create_method(self, api_client, api_id,base_id, lambda_function_arn):
        api_client.put_method(
            restApiId=api_id,
            resourceId=base_id,
            httpMethod="GET",
            authorizationType="NONE"
        )
        logger.info(
            "Created a method that accepts all HTTP verbs for the base " "resource."
        )

        lambda_uri = (
        f"arn:aws:apigateway:{api_client.meta.region_name}:"
        f"lambda:path/2015-03-31/functions/{lambda_function_arn}/invocations"
    )
        # Specify 'POST' for integrationHttpMethod
        api_client.put_integration(
            restApiId=api_id,
            resourceId= base_id,
            httpMethod="GET",
            type="AWS_PROXY",
            integrationHttpMethod='POST',
            uri=lambda_uri
        )
        logger.info(
            f"Set function {lambda_function_arn}"
        )

    def create_deployment(self,api_client,api_id,api_stage,account_id,
                          api_base_path, lambda_client, lambda_function_arn):
        
        api_client.create_deployment(restApiId=api_id, stageName=api_stage)
        print('####################### DEPLOYED ##################################')
        logger.info("Deployed REST API %s.", api_id)

        source_arn = (
        f"arn:aws:execute-api:{api_client.meta.region_name}:"
        f"{account_id}:{api_id}/*/*/{api_base_path}")

        lambda_client.add_permission(
            FunctionName=lambda_function_arn,
            StatementId=f"demo-invoke",
            Action="lambda:InvokeFunction",
            Principal="apigateway.amazonaws.com",
            SourceArn=source_arn,
        )

        logger.info(
            "Granted permission to let Amazon API Gateway invoke function %s "
            "from %s.",
            lambda_function_arn,
            source_arn,
        )

    def construct_api_url(self, api_id, region, api_stage, api_base_path):
        api_url = (
            f"https://{api_id}.execute-api.{region}.amazonaws.com/"
            f"{api_stage}/{api_base_path}"
        )
        logger.info("Constructed REST API base URL: %s.", api_url)
        # Get API url
        return api_url
    
    def delete_api(self, api_name, api_client):

        # Delete API if exists already
        response = api_client.get_rest_apis()
        response_items = response['items']
        matches = []
        response_items
        for item in response_items:
            if item['name'] == api_name:
                matches.append(item['id'])

        for id in matches:
            api_client.delete_rest_api(restApiId=id)
            logger.info(f'deleted api {id}')


    