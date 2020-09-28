# eks-school

In order to deploy this EKS Enviroment:

1. Ensure you have nodejs 10 or greater and python 3 or greater installed
1. Install the CDK with a `sudo npm install -g --upgrade aws-cdk`
1. Install the Python CDK dependencies with a `pip install --upgrade -r requirements.txt`
1. Set the environment variable CDK_DEFAULT_ACCOUNT to your account number with a `export CDK_DEFAULT_ACCOUNT=$(aws sts get-caller-identity --query 'Account' --output text)`
1. Set the environment variable CDK_DEFAULT_REGION to the region you want with a `export CDK_DEFAULT_REGION=ap-southeast-2`
1. Run `cdk deploy`