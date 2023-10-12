import boto3
from botocore.config import Config

from vars import *

NatGWID = NatGWID_var

def wait_for_release(client, eip):
    found = True
    while found:
        response_ip = client.describe_nat_gateways()
        found = False
        if 'NatGateways' in response_ip:
            for nat_gateway in response_ip['NatGateways']:
                for address in nat_gateway['NatGatewayAddresses']:
                    public_ip = address.get('PublicIp')
                    if public_ip == eip['PublicIp']:
                        found = True

def main():
    my_config = Config(
        region_name = 'eu-central-1',
        signature_version = 'v4',
        retries = {
            'max_attempts': 10,
            'mode': 'standard'
        }
    )

    TagKey = TagKey_var
    TagValue = TagValue_var


    client = boto3.client('ec2', config=my_config)

    response = client.describe_addresses()

    for eip in response['Addresses']:
        for tag in eip['Tags']:
            if tag['Key'] == TagKey and tag['Value'] == TagValue:
                print(f"Elastic IP with tag '{TagKey}:{TagValue}' found: {eip['PublicIp']}")

                response_ip = client.describe_nat_gateways()
                if 'NatGateways' not in response_ip:
                    raise Exception(f" Bad response {response}")
                for nat_gateway in response_ip['NatGateways']:
                    for address in nat_gateway['NatGatewayAddresses']:
                        public_ip = address.get('PublicIp')
                        if public_ip == eip['PublicIp']:
                            print(address.get('AssociationId'))
                            response = client.disassociate_nat_gateway_address(
                            NatGatewayId=NatGWID,
                            AssociationIds=[address.get('AssociationId')],
                            MaxDrainDurationSeconds=5,
                            )
                            wait_for_release(client, eip)
                            response = client.release_address(
                            AllocationId=eip['AllocationId'],
                            )
                            if 'ResponseMetadata' not in response:
                                raise Exception(f'Bad response {response}')


    eip = client.allocate_address(Domain='vpc')
    response = client.create_tags(
        Resources=[
            eip['AllocationId'],
        ],
        Tags=[
            {
                'Key': TagKey,
                'Value': TagValue,
            },
        ],
    )

    print(f"Secondary IP for NatGateway is: {eip['PublicIp']}")

    eip = client.associate_nat_gateway_address(
    NatGatewayId=NatGWID,
    AllocationIds=[eip['AllocationId']],
    PrivateIpAddresses=['10.0.4.141'],
    )

if __name__ == "__main__":
    main()
