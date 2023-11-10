import boto3
import botocore.exceptions
import time
from botocore.config import Config

from ..vars import *

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
        print("Cluster creation initiated. Check status...")
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
        
        time.sleep(5)


if __name__ == "__main__":
    main()