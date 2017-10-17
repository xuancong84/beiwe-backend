from deployment_helpers.aws.boto_helpers import *
from deployment_helpers.aws.elastic_beanstalk import *
from deployment_helpers.aws.elastic_compute_cloud import *
from deployment_helpers.aws.iam import *
from deployment_helpers.aws.rds import *
from deployment_helpers.aws.route_53 import *
from deployment_helpers.aws.security_groups import *
eb_client = create_eb_client()
ec2_client = create_ec2_client()
ec2_resource = create_ec2_resource()
iam_client = create_iam_client()
rds_client = create_rds_client()


prod_eb_client = boto3.client(
        'elasticbeanstalk',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name="us-east-1"
)

prod_ec2_client = boto3.client(
        'ec2',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name="us-east-1"
)

prod_ec2_resource = boto3.resource(
    "ec2",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name="us-east-1",
)


prod_rds_client = boto3.client(
       'rds',
       aws_access_key_id=AWS_ACCESS_KEY_ID,
       aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
       region_name="us-east-1",
)