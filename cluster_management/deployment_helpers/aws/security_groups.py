def find_sec_group(sec_group_name, tag_dict=None):
    ec2_client = create_ec2_client()
    sec_grps = ec2_client.describe_security_groups()['SecurityGroups']
    if tag_dict is None:
        return sec_grps
    for sec_grp in sec_grps:
        pass

def create_sec_groups():
    pass
    """
    celery workers need to connect to rabbitmq, postgres
    postgres needs to allow rabbitmq server, celery workers, eb servers
    rabbitmq needs to allow workers
    """


