# awsboto3 - Lab
A playground to learn aws and boto3

This repo demonstrates how to use boto3 to deploy a simple API gateway with a lambda function.
The lambda function deploys an endpoint for a GET request that either multiplies or adds numbers depending on the operation provided by the user.
This project uses aws boto3 and is reverse engineered from the AWS repo https://github.com/awsdocs/aws-doc-sdk-examples

# Entry point
Run the test_run_e2e E2E test in awsboto3/tests/test_infrarun.py. This will do the following:
Create role with lambda basic execution permissions
Zip and deploy the lambda function at awsboto3/lambdas/lambda_function.py
Create the api gateway and connect it to the lambda function.

# Testing
Testing is not comprehensive but demonstrates both unit and E2E testing. It alsso uses the botocore Stubber class to emostrate postivie and negative scenarios.

# Pre requisites
I have authenticated using the AWS client installed locally with an IAM user. The User has the following inline policy.
Named gl-inline-role (This could probably be improved to add this automatically to the role):

```
{
	"Version": "2012-10-17",
	"Statement": [
		{
			"Sid": "Statement1",
			"Effect": "Allow",
			"Action": [
				"lambda:AddPermission"
			],
			"Resource": [
				"*"
			]
		}
	]
}
```


