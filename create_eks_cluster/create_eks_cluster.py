import boto3
import botocore.exceptions
import time
from botocore.config import Config

from vars import *

cluster_name = 'my-eks-cluster'
role_arn = 'arn:aws:iam::123456789012:role/eks-service-role'
subnets = ['subnet-0123456789abcdef0', 'subnet-0123456789abcdef1']
security_groups = ['sg-0123456789abcdef0']
kubernetes_version = '1.28'

def main():
    my_config = Config(
        region_name = 'eu-central-1',
        signature_version = 'v4',
        retries = {
            'max_attempts': 10,
            'mode': 'standard'
        }
    )

    eks_client = boto3.client('eks', config=my_config)
    
    try:
        response = eks_client.create_cluster(
            name=cluster_name,
            roleArn=role_arn,
            resourcesVpcConfig={
                'subnetIds': subnets,
                'securityGroupIds': security_groups
            },
            version=kubernetes_version
        )
        print("Cluster creation initiated. Check the EKS console for status.")
    except botocore.exceptions.ClientError as e:
        print(f"Error: {e}")

while True:
    cluster_info = eks_client.describe_cluster(name=cluster_name)
    status = cluster_info['cluster']['status']
    
    if status == 'ACTIVE':
        print(f"Cluster {cluster_name} is now active.")
        break
    elif status == 'CREATING':
        print(f"Cluster {cluster_name} is still creating...")
    else:
        print(f"Cluster {cluster_name} is in an unexpected state: {status}")
        break
    
    time.sleep(30)


if __name__ == "__main__":
    main()