# eks-school

In order to deploy this EKS Enviroment:

1. Ensure you have nodejs 10 or greater and python 3 or greater installed
1. Install the CDK with a `sudo npm install -g --upgrade aws-cdk`
1. Install the Python CDK dependencies with a `pip install --upgrade -r requirements.txt`
1. Set the environment variable CDK_DEFAULT_ACCOUNT to your account number with a `export CDK_DEFAULT_ACCOUNT=$(aws sts get-caller-identity --query 'Account' --output text)`
1. Set the environment variable CDK_DEFAULT_REGION to the region you want with a `export CDK_DEFAULT_REGION=ap-southeast-2`
1. Run `cdk deploy`
1. Find the ALB and go to it on http://
1. The password is the instance id of EKSEnvironmentStack/CodeServerInstance
1. Open a new Terminal and run the command `aws eks update-kubeconfig --name cluster`
1. Run a `kubectl get nodes` to confirm everything is working

And then you're ready go go!

Note that because we are accessing VS Code through a insecure HTTP you need to insert into this by going Shift+Insert instead of Ctrl-V. On the Macbook Insert is Fn+Return so it is Shift+Fn+Return.

Alternatively, the stack has an output with an `aws eks update-kubeconfig` command that inclues a `--role-arn` in it. If you run that on your laptop where the AWS CLI is working with an administrative role then that will set up your ~/.kube/config in a way that kubectl will work that way too (as this EKS is Public and Private).