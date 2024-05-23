import boto3

class EC2Utils:
    def __init__(self, region_name, account_num):
        client = boto3.client("sts")
        roleArn="arn:aws:iam::" + account_num + ":role/"+account_num+"-crossAccountRoleForEC2Utils"
        roleSessionName=f"{account_num}-crossaccount-role"
        response = client.assume_role(RoleArn=roleArn, RoleSessionName=roleSessionName,DurationSeconds=900)
        another_account_client = boto3.Session(
            aws_access_key_id=response["Credentials"]["AccessKeyId"],
            aws_secret_access_key=response["Credentials"]["SecretAccessKey"],
            aws_session_token=response["Credentials"]["SessionToken"]
            )
        self.ec2_client = another_account_client.client('ec2', region_name=region_name)
        

    def get_vpc_subnets_and_security_group(self, environment):
        response = self.ec2_client.describe_vpcs(
            Filters=[
                {
                    'Name': 'tag:env',
                    'Values': [environment]
                }
            ]
        )

        vpc_id = ""
        if response['Vpcs']:
            vpc_id = response['Vpcs'][0]['VpcId']

        subnet_ids = []
        response = self.ec2_client.describe_subnets(
            Filters=[
                {
                    'Name': 'vpc-id',
                    'Values': [vpc_id]
                }
            ]
        )
        if response:
            subnets = response['Subnets']
            subnet_ids = [subnet['SubnetId'] for subnet in subnets]

        route_table_ids = []
        response = self.ec2_client.describe_route_tables(
            Filters=[
                {
                    'Name': 'vpc-id',
                    'Values': [vpc_id]
                }
            ]
        )
        if response['RouteTables']:
            route_table_id = response['RouteTables'][0]['RouteTableId']
            route_table_ids.extend([route_table_id] * 4)
        sg_group_id = ""
        sg_group_name = ""
        response = self.ec2_client.describe_security_groups(
            Filters=[
                {
                    'Name': 'tag:env',
                    'Values': [environment]
                }
            ]
        )
        if response['SecurityGroups']:
            sg = response['SecurityGroups'][0]
            sg_group_id = sg['GroupId']
            sg_group_name = sg['GroupName']

        return vpc_id, subnet_ids, route_table_ids, sg_group_id, sg_group_name


