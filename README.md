Assignment 7 WebApp and Infrastructure
This is a simple python based API that takes user details from user in Json format and stores it in the MySql database when called.

The API Allows to Add User, Updated User Details and View User Details.

This API Uses Basic Auth for authenticating the user identyty for retieve and update functions.

The application dependency and infrastructure setup is automatically don with the creation of custom AMI

The application starts running as soon as the instance is launched. To launch the ec2 instanc and create infra conponenst run following command with your cloud formation template.

aws cloudformation create-stack --stack-name assignment6 --template-body file://infrastructure.yaml --parameters ParameterKey=amiId,ParameterValue=ami-03bfd684634fdd769 ParameterKey=HostedZoneName,ParameterValue=prod.sagarmalhotra.me. --region us-east-1 --profile demo --capabilities CAPABILITY_NAMED_IAM

API END POINTS

authenticated
Operations available only to authenticated users

GET
/v1/account/{accountId}
Get User Account Information

PUT
/v1/account/{accountId}
Update User's account information

GET
/v1/documents
Get List of All Documents Uploaded

POST
/v1/documents
Upload a document

GET
/v1/documents/{doc_id}
Get Document Details

DELETE
/v1/documents/{doc_id}
Delete the document

Unauthenticated
Operations available to all users without authentication

GET
/healthz
Health endpoint

POST
/v1/account
Create a user account


