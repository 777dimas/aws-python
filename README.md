
## Python scripts for AWS infrastructure

# change_ip_nat_gateway.py
```change_ip_nat_gateway.py``` - script for adding a secondary IP to NatGateway.
    - First run of the script will Allocate Elastic IP address and add it to NatGateway as a secondary IP;
    - Second run and subsequent times will be Disassociate existing secondary IPv4 address, will be released it and Associate new IPv4 address.