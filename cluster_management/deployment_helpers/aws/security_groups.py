"""
celery workers need to connect to rabbitmq, postgres
postgres needs to allow rabbitmq server, celery workers, eb servers
rabbitmq needs to allow workers
"""
from botocore.exceptions import ClientError

from deployment_helpers.aws.boto_helpers import create_ec2_resource, create_ec2_client
from deployment_helpers.aws.elastic_beanstalk_configuration import get_global_config

GLOBAL_CONFIGURATION = get_global_config()

def find_sec_group(sec_group_name, tag_dict=None):
    ec2_client = create_ec2_client()
    sec_grps = ec2_client.describe_security_groups()['SecurityGroups']
    if tag_dict is None:
        return sec_grps
    for sec_grp in sec_grps:
        pass

class InvalidSecurityGroupIdException(Exception): pass

def get_security_group_by_id(sec_grp_id):
    try:
        return create_ec2_client().describe_security_groups(GroupIds=[sec_grp_id])['SecurityGroups'][0]
    except ClientError as e:
        # Boto3 throws unimportable errors.
        if "Invalid id:" in e.message:
            raise InvalidSecurityGroupIdException(sec_grp_id)
        raise


def get_security_group_by_name(sec_grp_name):
    return create_ec2_client().describe_security_groups(GroupNames=[sec_grp_name])['SecurityGroups'][0]


def create_sec_grp_rule_parameters_allowing_traffic_from_another_security_group(
        tcp_port, sec_grp_id, protocol="TCP"):
    # Do not even try to construct an inline declaration of security group rules.  They are simply
    # unpythonic, bloated, and really hard to read.  In addition errors are displayed like this:
    #   Unknown parameter in IpPermissions[0].UserIdGroupPairs[0]: "ToPort", must be one of:
    #   Description, GroupId, GroupName, PeeringStatus, UserId, VpcId, VpcPeeringConnectionId
    # The "mutation style" declaration is easier to read, harder to screw up the various [] and {}
    # nestings, easier to parse when looking at the boto error messages in development,
    # has significantly reduced line count,
    ingress_rule = {}
    ingress_rule["IpPermissions"] = [{}]
    ingress_rule["IpPermissions"][0]["FromPort"] = tcp_port
    ingress_rule["IpPermissions"][0]["ToPort"] = tcp_port
    ingress_rule["IpPermissions"][0]["IpProtocol"] = protocol
    ingress_rule["IpPermissions"][0]['UserIdGroupPairs'] = [{}]
    ingress_rule["IpPermissions"][0]['UserIdGroupPairs'][0]['GroupId'] = sec_grp_id
    return ingress_rule


def create_security_group(group_name, description,
                          list_of_dicts_of_ingress_kwargs=None, list_of_dicts_of_egress_kwargs=None):
    """
    mostly kwargs should look like this: ToPort=22, IpProtocol="TCP", SourceSecurityGroupName="thing"
    """
    if list_of_dicts_of_ingress_kwargs is None:
        list_of_dicts_of_ingress_kwargs = []
    if list_of_dicts_of_egress_kwargs is None:
        list_of_dicts_of_egress_kwargs = []

    if not isinstance(list_of_dicts_of_ingress_kwargs, list):
        raise Exception("list_of_dicts_of_ingress_kwargs was not a list, it was a %s" % type(list_of_dicts_of_ingress_kwargs))
    if not isinstance(list_of_dicts_of_egress_kwargs, list):
        raise Exception("list_of_dicts_of_egress_kwargs was not a list, it was a %s" % type(list_of_dicts_of_egress_kwargs))
    
    ec2_client = create_ec2_client()
    ec2_resource = create_ec2_resource()
    
    sec_grp = ec2_client.create_security_group(
            VpcId=GLOBAL_CONFIGURATION["VPC_ID"],
            GroupName=group_name,
            Description=description,
    )
    sec_grp_resource = ec2_resource.SecurityGroup(sec_grp["GroupId"])
    
    for ingress_params in list_of_dicts_of_ingress_kwargs:
        sec_grp_resource.authorize_ingress(**ingress_params)
        
    for egress_params in list_of_dicts_of_egress_kwargs:
        sec_grp_resource.authorize_egress(**egress_params)

    return get_security_group_by_id(sec_grp["GroupId"])