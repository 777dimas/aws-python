import boto3
from botocore.config import Config

from vars import *

accepter_vpc_id = PeerVpcId
requester_vpc_id = VpcId

def create_route_tables_in_requester_vpc(client):

    nat_gateway = NatGatewayId

    response = client.create_route_table(VpcId=requester_vpc_id)
    route_table_id = response['RouteTable']['RouteTableId']

    client.create_route(
        RouteTableId=route_table_id,
        DestinationCidrBlock='172.20.0.0/16',
        VpcPeeringConnectionId=response['VpcPeeringConnection']['VpcPeeringConnectionId']
    )

    client.create_route(
        RouteTableId=route_table_id,
        DestinationCidrBlock='0.0.0.0/0',
        NatGatewayId=nat_gateway
    )

    result_msg = f'Route table {route_table_id} created with routes in requester vpc'
    return result_msg

def create_route_tables_in_accepter_vpc_vpc(client):
    response = client.create_route_table(VpcId=accepter_vpc_id)
    route_table_id = response['RouteTable']['RouteTableId']

    client.create_route(
        RouteTableId=route_table_id,
        DestinationCidrBlock='10.0.0.0/16',
        VpcPeeringConnectionId=response['VpcPeeringConnection']['VpcPeeringConnectionId']
    )

    result_msg = f'Route table {route_table_id} created with routes in accepter vpc'
    return result_msg

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

    peering_connection_id = response['VpcPeeringConnection']['VpcPeeringConnectionId']
    print(f'Peering connections {peering_connection_id} created')

    accept_connection = client.accept_vpc_peering_connection(
    VpcPeeringConnectionId=peering_connection_id
    )
    print(f"Status peering connection is: {accept_connection['Status']}")
    print(create_route_tables_in_requester_vpc(client))
    print(create_route_tables_in_accepter_vpc_vpc(client))

if __name__ == "__main__":
    main()