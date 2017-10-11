import boto3





##
## Boto3 clients
##

def create_ec2_client():
    """ connect to a boto3 ec2 CLIENT in the appropriate region. """
    return boto3.client(
            "ec2",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
    )


def create_eb_client():
    return boto3.client(
           'elasticbeanstalk',
           aws_access_key_id=AWS_ACCESS_KEY_ID,
           aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
           region_name=AWS_REGION
    )

def create_iam_client():
    return boto3.client(
           'iam',
           aws_access_key_id=AWS_ACCESS_KEY_ID,
           aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
           region_name=AWS_REGION
    )


def create_rds_client():
    return boto3.client(
           'rds',
           aws_access_key_id=AWS_ACCESS_KEY_ID,
           aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
           region_name=AWS_REGION
    )



## Not a client.
def create_ec2_resource():
    return boto3.resource(
        "ec2",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
    )


