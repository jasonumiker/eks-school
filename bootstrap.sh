#!/bin/bash
LOCAL_ACCOUNT=$(aws sts get-caller-identity --query 'Account' --output text)
CDK_DEFAULT_ACCOUNT=${CDK_DEFAULT_ACCOUNT:=LOCAL_ACCOUNT}
CDK_DEFAULT_REGION=${CDK_DEFAULT_REGION:="ap-southeast-2"}
pip install -r requirements.txt --upgrade
cdk bootstrap $@

