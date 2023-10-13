
### create_vpc_peering_connection.py
```create_vpc_peering_connection.py``` - script for creating peering connection between local networks EKS and RDS with creating route tables and routes.

### Usage
```
export AWS_DEFAULT_PROFILE=my_aws_account
python create_vpc_peering_connection.py
```
### Output
```
Peering connections {peering_connection_id} created'
Status peering connection is: {accept_connection['Status']}
Route table {route_table_id} created with routes in requester vpc
Route table {route_table_id} created with routes in accepter vpc
```