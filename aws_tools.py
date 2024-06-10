import boto3
from langchain.tools import tool
from apikey import aws_key_id, aws_secret_key

s3 = boto3.client(
    's3',
    region_name='us-east-2',
    aws_access_key_id= aws_key_id,
    aws_secret_access_key=aws_secret_key
)

ec2 = boto3.client("ec2",
    region_name='us-east-2',
     aws_access_key_id= aws_key_id,
    aws_secret_access_key=aws_secret_key)

iam = boto3.client("iam",
    region_name='us-east-2',
     aws_access_key_id= aws_key_id,
    aws_secret_access_key=aws_secret_key)

@tool
def PublicS3BucketsTool(query: str) -> str:
    """
    get the number of public s3 storage buckets 
    """
    response = s3.list_buckets()
    public_buckets = []
    
    for bucket in response['Buckets']:
        bucket_name = bucket['Name']
        bucket_acl = s3.get_bucket_acl(Bucket=bucket_name)
        for grant in bucket_acl['Grants']:
            if grant['Grantee']['Type'] == 'Group' and 'AllUsers' in grant['Grantee']['URI']:
                public_buckets.append(bucket_name)
                break
    
    return f"There are {len(public_buckets)} public S3 buckets."

@tool
def GetAllS3Buckets(query: str) -> str:
    """
    List all the s3 buckets for this account.
    """
    response = s3.list_buckets()
    
    bucket_names = [bucket['Name'] for bucket in response['Buckets']]
    
    # Prepare the output
    output = f"There are {len(bucket_names)} S3 buckets:\n "
    output += "\n".join(bucket_names)
    
    return output

@tool
def S3BucketContentsTool(bucket_name: str) -> str:
    """Get the contents of the S3 storage bucket
    """
    response = s3.list_objects_v2(Bucket=bucket_name)
    if 'Contents' not in response:
        return f"The S3 bucket {bucket_name} is empty or does not exist."
    
    files = [obj['Key'] for obj in response['Contents']]
    return f"The S3 bucket {bucket_name} contains the following files: \n {'\n'.join(files)}"


@tool
def GetAllEC2InstancesTool(query: str) -> str:
    """
    Get a list of all EC2 compute instances.
    """

    response = ec2.describe_instances()
    instances = []
    
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            public_ip = instance.get('PublicIpAddress', 'No public IP')
            name = 'No Name'
            for tag in instance.get('Tags', []):
                if tag['Key'] == 'Name':
                    name = tag['Value']
            instances.append(f"{instance_id} (Name: {name}, Public IP: {public_ip})")
    return f"The following EC2 instances were found: \n {'\n '.join(instances)}" if instances else "No EC2 instances were found."

@tool
def GetAllUsersTool(query: str) -> str:
    """
    Get a list of all users.
    """
    
    response = iam.list_users()
    users = [user['UserName'] for user in response['Users']]
    response = f"The following IAM users were found: {'\n '.join(users)}" if users else "No IAM users were found."
    return response


@tool
def EC2InstanceSizeTool (instance_ip: str) -> str:
    """
    Get the size of a ec2 instance from its ip address.
    """
    
    response = ec2.describe_instances(
    Filters=[{'Name': 'ip-address', 'Values': [instance_ip]}])
    
    if not response['Reservations']:
        return f"No EC2 instance found with IP {instance_ip}"
    
    instance_type = response['Reservations'][0]['Instances'][0]['InstanceType']
    return f"The EC2 instance with IP {instance_ip} is of type {instance_type}."

@tool
def UserPermissionsTool(username: str) -> str:
    """
    Get permissions for a specific user.
    """
    
    response = iam.list_users()
    users = [user['UserName'] for user in response['Users']]
    if (username not in users):
        return f"{username} cannot be found in the list of users for this account."
    response = iam.list_attached_user_policies(UserName=username)
    policies = [policy['PolicyName'] for policy in response['AttachedPolicies']]
    
    response = iam.list_groups_for_user(UserName=username)
    groups = [group['GroupName'] for group in response['Groups']]
    for group in groups:
        response = iam.list_attached_group_policies(GroupName=group)
        for policy in response['AttachedPolicies']:
            policies.append(policy['PolicyName'])
        
    policies = list(set(policies))

    return f"The user {username} has the following attached policies: \n {'\n'.join(policies)}"


# print(UserPermissionsTool.invoke('rpopat'))

aws_tools = [
            PublicS3BucketsTool,
            S3BucketContentsTool,
            EC2InstanceSizeTool,
            UserPermissionsTool,
            GetAllEC2InstancesTool,
            GetAllUsersTool,
            GetAllS3Buckets
        ]

