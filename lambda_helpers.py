
import logging
import pytest
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class LambdaManage:
    def __init__(self,lambda_client, iam_resource):
        self.lambda_client = lambda_client
        self.iam_resource = iam_resource

    # def create_iam_role(self, iam_role_name):
        
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
