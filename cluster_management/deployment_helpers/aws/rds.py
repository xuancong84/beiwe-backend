from deployment_helpers.aws.boto_helpers import create_rds_client
from deployment_helpers.general_utils import random_typeable_string

DB_NAME = "beiwe-database"
DB_SERVER_TYPE = "t2.medium"

# TODO: generate random username, password,


def most_recent_postgres_engine():
    rds_client = create_rds_client()
    for engine in reversed(rds_client.describe_db_engine_versions()['DBEngineVersions']):
        if 'postgres' == engine["Engine"]:
            return engine
            


def create_new_rds_instance():
    rds_client = create_rds_client()
    engine = most_recent_postgres_engine()
    
    username = random_typeable_string()
    password = random_typeable_string()
    database_name = random_typeable_string()
    
    # http://boto3.readthedocs.io/en/latest/reference/services/rds.html  --  super pedantic
    response = rds_client.create_db_instance(
            Timezone='string',
            
            DBInstanceClass=DB_SERVER_TYPE,
            AllocatedStorage=50, #gb?
            StorageType='string',
            Iops=123, # multiple between 3 and 10 times the storage...
            
            StorageEncrypted=True | False,  # buh
            KmsKeyId='string',
            TdeCredentialArn='string',
            TdeCredentialPassword='string',
            
            # buh?
            MonitoringInterval=123,
            MonitoringRoleArn='string',
            
            MultiAZ=True | False,
            AvailabilityZone='string',
            PubliclyAccessible=False,
            
            
            MasterUsername=username,
            MasterUserPassword=password,
            DBName='string',
            DBInstanceIdentifier='string',
            
            Engine=engine['DBEngineDescription'],
            EngineVersion='string',
            PreferredMaintenanceWindow='string',
            PreferredBackupWindow='string',
            AutoMinorVersionUpgrade=True,
            BackupRetentionPeriod=123,
        
            Port=123,
            DBSecurityGroups=[
                'string',
            ],
            VpcSecurityGroupIds=[
                'string',
            ],
            
            # DBSubnetGroupName='string',
            # DBParameterGroupName='string',
            
            # nopes:
            # LicenseModel='string',
            # CharacterSetName='string',
            # OptionGroupName='string',  #don't think this is required.
            # Domain='string',  # has the phrase "active directory" in the description
            # DomainIAMRoleName='string',
            # CopyTagsToSnapshot=True | False,
            
            Tags=[
                {
                    'Key': 'string',
                    'Value': 'string'
                },
            ],
            # DBClusterIdentifier='string',  #
        
            PromotionTier=123,
        
            EnableIAMDatabaseAuthentication=False,
            EnablePerformanceInsights=True | False,
            PerformanceInsightsKMSKeyId='string'
    )