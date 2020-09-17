from aws_cdk import (
    aws_iam as iam,
    aws_ec2 as ec2,
    aws_eks as eks,
    core
)
import os

class EKSEnvironmentStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        eks_vpc = ec2.Vpc(
            self, "VPC",
            cidr="10.0.0.0/16"
        )
        self.eks_vpc = eks_vpc

        # Create IAM Role For code-server bastion
        bastion_role = iam.Role(
            self, "BastionRole",
            assumed_by=iam.CompositePrincipal(
                iam.ServicePrincipal("ec2.amazonaws.com")
            ),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AdministratorAccess")
            ]
        )
        self.bastion_role = bastion_role
        # Create EC2 Instance Profile for that Role
        instance_profile = iam.CfnInstanceProfile(
            self, "InstanceProfile",
            roles=[bastion_role.role_name]            
        )

        # Create SecurityGroup for the Control Plane ENIs
        eks_security_group = ec2.SecurityGroup(
            self, "EKSSecurityGroup",
            vpc=eks_vpc,
            allow_all_outbound=True
        )
        
        eks_security_group.add_ingress_rule(
            ec2.Peer.ipv4('10.0.0.0/16'),
            ec2.Port.all_traffic()
        )    

        # Create an EKS Cluster
        eks_cluster = eks.Cluster(
            self, "cluster",
            cluster_name="cluster",
            vpc=eks_vpc,
            masters_role=bastion_role,
            default_capacity_type=eks.DefaultCapacityType.NODEGROUP,
            default_capacity_instance=ec2.InstanceType("m5.large"),
            default_capacity=2,
            security_group=eks_security_group,
            endpoint_access=eks.EndpointAccess.PRIVATE,
            version=eks.KubernetesVersion.V1_17
        )
        self.cluster_cert = eks_cluster.cluster_certificate_authority_data

class CodeServerStack(core.NestedStack):

    def __init__(self, scope: core.Construct, id: str, vpc: ec2.Vpc, role: iam.Role, cluster_cert: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
    
        # Create code-server bastion
        # Get Latest Amazon Linux AMI
        amzn_linux = ec2.MachineImage.latest_amazon_linux(
            generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
            edition=ec2.AmazonLinuxEdition.STANDARD,
            virtualization=ec2.AmazonLinuxVirt.HVM,
            storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE
            )

        # Create SecurityGroup for code-server
        security_group = ec2.SecurityGroup(
            self, "SecurityGroup",
            vpc=vpc,
            allow_all_outbound=True
        )
        
        security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(8080)
        )

        # Create our EC2 instance running CodeServer
        code_server_instance = ec2.Instance(
            self, "CodeServerInstance",
            instance_type=ec2.InstanceType("t3.large"),
            machine_image=amzn_linux,
            role=role,
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            security_group=security_group,
            block_devices=[ec2.BlockDevice(device_name="/dev/xvda", volume=ec2.BlockDeviceVolume.ebs(20))]
        )

        # Add UserData
        code_server_instance.user_data.add_commands("mkdir -p ~/.local/lib ~/.local/bin ~/.config/code-server")
        code_server_instance.user_data.add_commands("curl -fL https://github.com/cdr/code-server/releases/download/v3.5.0/code-server-3.5.0-linux-amd64.tar.gz | tar -C ~/.local/lib -xz")
        code_server_instance.user_data.add_commands("mv ~/.local/lib/code-server-3.5.0-linux-amd64 ~/.local/lib/code-server-3.5.0")
        code_server_instance.user_data.add_commands("ln -s ~/.local/lib/code-server-3.5.0/bin/code-server ~/.local/bin/code-server")
        code_server_instance.user_data.add_commands("echo \"bind-addr: 0.0.0.0:8080\" > ~/.config/code-server/config.yaml")
        code_server_instance.user_data.add_commands("echo \"auth: password\" >> ~/.config/code-server/config.yaml")
        code_server_instance.user_data.add_commands("echo \"password: $(curl -s http://169.254.169.254/latest/meta-data/instance-id)\" >> ~/.config/code-server/config.yaml")
        code_server_instance.user_data.add_commands("echo \"cert: false\" >> ~/.config/code-server/config.yaml")
        code_server_instance.user_data.add_commands("~/.local/bin/code-server &")
        code_server_instance.user_data.add_commands("yum -y install jq gettext bash-completion moreutils")
        code_server_instance.user_data.add_commands("sudo pip install --upgrade awscli && hash -r")
        code_server_instance.user_data.add_commands("echo 'yq() {docker run --rm -i -v \"${PWD}\":/workdir mikefarah/yq yq \"$@\"}' | tee -a ~/.bashrc && source ~/.bashrc")
        code_server_instance.user_data.add_commands("echo 'export ALB_INGRESS_VERSION=\"v1.1.8\"' >>  ~/.bash_profile")
        code_server_instance.user_data.add_commands("curl --silent --location -o /usr/local/bin/kubectl \"https://amazon-eks.s3.us-west-2.amazonaws.com/1.17.9/2020-08-04/bin/linux/amd64/kubectl\"")
        code_server_instance.user_data.add_commands("chmod +x /usr/local/bin/kubectl")
        code_server_instance.user_data.add_commands("curl -L https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash")
        code_server_instance.user_data.add_commands("export ACCOUNT_ID=$(aws sts get-caller-identity --output text --query Account)")
        code_server_instance.user_data.add_commands("export AWS_REGION=$(curl -s 169.254.169.254/latest/dynamic/instance-identity/document | jq -r '.region')")
        code_server_instance.user_data.add_commands("echo \"export ACCOUNT_ID=${ACCOUNT_ID}\" | tee -a ~/.bash_profile")
        code_server_instance.user_data.add_commands("echo \"export AWS_REGION=${AWS_REGION}\" | tee -a ~/.bash_profile")
        code_server_instance.user_data.add_commands("aws configure set default.region ${AWS_REGION}")
        code_server_instance.user_data.add_commands("aws eks update-kubeconfig --name cluster")

app = core.App()
env = core.Environment(account=os.environ["CDK_DEFAULT_ACCOUNT"], region=os.environ["CDK_DEFAULT_REGION"])
eks_environment_stack = EKSEnvironmentStack(app, "EKSEnvironmentStack", env=env)
code_server_stack = CodeServerStack(eks_environment_stack, "CodeServerStack", eks_environment_stack.eks_vpc, eks_environment_stack.bastion_role, eks_environment_stack.cluster_cert)
app.synth()