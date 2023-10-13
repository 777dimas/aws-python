import boto3
from botocore.config import Config

from vars import *

my_config = Config(
        region_name = 'eu-central-1',
        signature_version = 'v4',
        retries = {
            'max_attempts': 10,
            'mode': 'standard'
        }
    )

client = boto3.client('ec2', config=my_config)

account_id = PeerOwnerId
accepter_vpc_id = PeerVpcId
requester_vpc_id = VpcId
tag_key = TagKey
tag_value = TagValue

def create_route_tables_in_requester_vpc(client):
    response = client.create_route_table(VpcId=accepter_vpc_id)
    route_table_id = response['RouteTable']['RouteTableId']

    client.create_route(
        RouteTableId=route_table_id,
        DestinationCidrBlock='10.0.0.0/16',
        VpcPeeringConnectionId='pcx-0d34e5ef6cca1cc99'
    )

    result_msg = f'Route table {route_table_id} created with routes in accepter vpc'
    return result_msg

print(create_route_tables_in_requester_vpc(client))