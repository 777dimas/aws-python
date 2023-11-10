import boto3
import argparse
from botocore.config import Config

from vars import *

parser = argparse.ArgumentParser()
parser.add_argument('ip_var', type=str, help='First parameter == "IP address"')
parser.add_argument('description_var', type=str, help='Second parameter == "Description for IP address"')
args = parser.parse_args()

def main():
    my_config = Config(
        region_name = 'eu-central-1',
        signature_version = 'v4',
        retries = {
            'max_attempts': 10,
            'mode': 'standard'
        }
    )

    sg_var = Security_GroupID
    sg_rule_id_var = Security_GroupRuleID

    client = boto3.client('ec2', config=my_config)

    response_sg = client.describe_security_groups(GroupIds=[sg_var])

    if 'SecurityGroups' not in response_sg:
        raise Exception(f" Bad response {response_sg}")

    for permission in response_sg['SecurityGroups'][0]['IpPermissions']:
        for ip_range in permission['IpRanges']:
            if ip_range.get('CidrIp', 'N/A') != args.ip_var and ip_range.get('Description', 'N/A') == args.description_var:
                client.modify_security_group_rules(
                    GroupId=sg_var,
                    SecurityGroupRules=[
                        {
                            'SecurityGroupRuleId': sg_rule_id_var,
                            'SecurityGroupRule': {
                                'IpProtocol': 'tcp',
                                'FromPort': 443,
                                'ToPort': 443,
                                'CidrIpv4': args.ip_var,
                                'Description': args.description_var
                            }
                        },
                    ],
                )
                response_check_ip = client.describe_security_groups(GroupIds=[sg_var])

                if 'SecurityGroups' not in response_check_ip:
                    raise Exception(f" Bad response {response_check_ip}")
                
                for permission in response_check_ip['SecurityGroups'][0]['IpPermissions']:
                    for ip_range_check in permission['IpRanges']:
                        if ip_range_check.get('Description', 'N/A') == args.description_var:
                            print(f"IP {ip_range.get('CidrIp', 'N/A')} has been changed to IP {ip_range_check.get('CidrIp', 'N/A')}")
            else: 
                response_add_new_ip = client.describe_security_groups(GroupIds=[sg_var])
            #     existing_permissions = response_add_new_ip['SecurityGroups'][0]['IpPermissions']
            #     for permission in existing_permissions:
            #         if permission['FromPort'] == 443 and permission['ToPort'] == 443:
            #             permission['IpRanges'].append({'CidrIp': args.ip_var})
            #             break
            #     client.authorize_security_group_ingress(
            #     GroupId=sg_var,
            #     IpPermissions=existing_permissions
            # )
            print(response_add_new_ip)

if __name__ == "__main__":
    main()