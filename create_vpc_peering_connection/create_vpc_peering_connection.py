import boto3
from botocore.config import Config

from vars import *

def main():
    my_config = Config(
        region_name = 'eu-central-1',
        signature_version = 'v4',
        retries = {
            'max_attempts': 10,
            'mode': 'standard'
        }
    )

    account_id = PeerOwnerId
    accepter_vpc_id = PeerVpcId
    requester_vpc_id = VpcId
    tag_key = TagKey
    tag_value = TagValue

    client = boto3.client('ec2', config=my_config)

    response = client.create_vpc_peering_connection(
        PeerOwnerId=account_id,
        PeerVpcId=accepter_vpc_id,
        VpcId=requester_vpc_id,
        TagSpecifications=[
            {
                'ResourceType': 'vpc-peering-connection',
                'Tags': [
                    {
                        'Key': tag_key,
                        'Value': tag_value,
                    },
                ]
            },
        ]
    )

    print(response['VpcPeeringConnection']['VpcPeeringConnectionId'])

    accept_connection = client.accept_vpc_peering_connection(
    VpcPeeringConnectionId=response['VpcPeeringConnection']['VpcPeeringConnectionId']
    )
    #print(accept_connection)

if __name__ == "__main__":
    main()