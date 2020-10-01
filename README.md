# eks-school

In order to deploy this EKS Enviroment:

1. Ensure you have nodejs 10 or greater and python 3 or greater installed. On a Mac this is `brew install node` and `brew install python`
1. Install the CDK with a `sudo npm install -g --upgrade aws-cdk`
1. Make sure you are cd'd into this folder and install the Python CDK dependencies with a `pip install --upgrade -r requirements.txt`
1. Set the environment variable CDK_DEFAULT_ACCOUNT to your account number with a `export CDK_DEFAULT_ACCOUNT=$(aws sts get-caller-identity --query 'Account' --output text)`
1. Set the environment variable CDK_DEFAULT_REGION to the region you want with a `export CDK_DEFAULT_REGION=ap-southeast-2`
1. Paste in the environment variables for temporary admin role access to an account from Isengard
1. Run `cdk deploy`
1. Find the ALB address and go to it on http://
1. The password is the instance id of EKSEnvironmentStack/CodeServerInstance (find in the EC2 console)
1. Open a new Terminal (click the hamburger in the upper left) and run the command `aws eks update-kubeconfig --name cluster`
1. Run a `kubectl get nodes` to confirm everything is working
1. This project should have been git cloned to the bastion - cd to `eks-school`
1. Run `kubectl apply -f nyancat.yaml` to deploy a test workload
1. Wait a couple minutes then find the ALB address with a `kubectl get ingress -A`
1. Go to that address for some nyancat fun...

And then you're ready go go!

Note that because we are accessing VS Code through a insecure HTTP you need to insert into this by going Shift+Insert instead of Ctrl-V. On the Macbook Insert is Fn+Return so it is Shift+Fn+Return.

## Direct access from your laptop
Alternatively, the stack has an output with an `aws eks update-kubeconfig` command that inclues a `--role-arn` in it. If you run that on your laptop where the AWS CLI is working with an administrative role then that will set up your ~/.kube/config in a way that kubectl will work that way too (as this EKS is Public and Private).

If you'd like to use the Lens IDE then get it from https://github.com/lensapp/lens/releases and run it from the terminal after you have gotten it to a point where kubectl works.
