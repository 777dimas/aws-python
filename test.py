import boto3
import ipaddress

ec2_client = boto3.client("ec2")

def get_cidr(subnet_id: str) -> str:
    """
    Get Subnet CIDR
    :param subnet_id:VPC subnet-id
    :return: The IPv4 CIDR block
    """
    paginator = ec2_client.get_paginator('describe_subnets')
    for subnets in paginator.paginate(SubnetIds=[subnet_id]):
        for subnet in subnets["Subnets"]:
            return subnet['CidrBlock']
    raise Exception(f"{subnet_id=} has no CidrBlock.")

#def get_free_ip_on_subnet():
subnet_id = 'subnet-017e874c922279fdf'
cidr = get_cidr(subnet_id)
cidr_ips = [str(ip) for ip in ipaddress.IPv4Network(cidr)]
cidr_ips.sort(key=ipaddress.IPv4Address)