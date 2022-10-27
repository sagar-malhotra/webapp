# Assignment 5 WebApp and Infrastructure
This is a simple python based API that takes user details from user in Json format and stores it in the MySql database when called.

The API Allows to Add User, Updated User Details and View User Details.

This API Uses Basic Auth for authenticating the user identyty for retieve and update functions.


The application dependency and infrastructure setup is automatically don with the creation of custom AMI

The application starts running as soon as the instance is launched.
 To launch the ec2 instanc and create infra conponenst run following command with your cloud formation template.
 
 
aws cloudformation create-stack --stack-name Stac Name --template-body file://infrastructure.yaml --parameters ParameterKey=amiId,ParameterValue= ami id --region us-east-1 --profile demo

