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

account_id = PeerOwnerId
tag_key = TagKey
tag_value = TagValue

client = boto3.client('ec2', config=my_config)

accepter_vpc_id = PeerVpcId
requester_vpc_id = VpcId

#def create_route_tables_in_accepter_vpc_vpc(client):
response = client.create_route_table(VpcId=accepter_vpc_id)
if 'RouteTable' not in response:
    raise Exception(f"Bad response {response}")
route_table_id = response['RouteTable']['RouteTableId']

if 'ResponseMetadata' not in response:
    raise Exception(f'Bad response {response}')
client.create_route(
    RouteTableId=route_table_id,
    DestinationCidrBlock='10.0.0.0/16',
    VpcPeeringConnectionId='pcx-0d34e5ef6cca1cc99'
)

print(f'Route table {route_table_id} created with routes in accepter vpc')

