
import logging


logger = logging.getLogger(__name__)

class APIGatewayManage:

    def create_api(self, account_id, api_base_path,
                        api_stage, apig_client,api_name):
        
        response = apig_client.create_rest_api(name=api_name)
        api_id = response['id']
        logger.info("Create REST API %s with ID %s.", api_name, api_id)