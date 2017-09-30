discovered = [
    {
        "OptionName": "/static/",
        "ValueType": "Scalar",
        "ChangeSeverity": "RestartApplicationServer",
        "Namespace": "aws:elasticbeanstalk:container:python:staticfiles"
    },{
        "ValueType": "List",
        "ChangeSeverity": "Unknown",
        "Namespace": "aws:elb:listener",
        "OptionName": "PolicyNames",
    },{
        "OptionName": "SystemType",
        "DefaultValue": "basic",
        "ChangeSeverity": "RestartEnvironment",
        "Namespace": "aws:elasticbeanstalk:healthreporting:system",
        "ValueType": "Scalar",
        "ValueOptions": ["basic","enhanced"]
    },{
        "OptionName": "NumProcesses",
        "DefaultValue": "1",
        "ChangeSeverity": "RestartApplicationServer",
        "Namespace": "aws:elasticbeanstalk:container:python",
        "MinValue": 0,
        "ValueType": "Scalar"
    },{
        "ValueType": "Scalar",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:autoscaling:scheduledaction",
        "OptionName": "Recurrence",
    },{
        "OptionName": "LoadBalancerSSLPortProtocol",
        "DefaultValue": "HTTPS",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elb:loadbalancer",
        "ValueType": "Scalar",
        "ValueOptions": ["HTTPS","SSL"]
    },{
        "OptionName": "XRayEnabled",
        "DefaultValue": "false",
        "ChangeSeverity": "RestartApplicationServer",
        "Namespace": "aws:elasticbeanstalk:xray",
        "ValueType": "Scalar",
        "ValueOptions": ["true","false"]
    },{
        "OptionName": "PauseTime",
        "ValueType": "Scalar",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:autoscaling:updatepolicy:rollingupdate"
    },{
        "OptionName": "ManagedActionsEnabled",
        "DefaultValue": "false",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elasticbeanstalk:managedactions",
        "ValueType": "Boolean"
    },{
        "OptionName": "BlockDeviceMappings",
        "ValueType": "CommaSeparatedList",
        "ChangeSeverity": "RestartEnvironment",
        "Namespace": "aws:autoscaling:launchconfiguration"
    },{
        "OptionName": "Notification Protocol",
        "DefaultValue": "email",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elasticbeanstalk:sns:topics",
        "ValueType": "Scalar",
        "ValueOptions": ["http","https","email","email-json","sqs"]
    },{
        "OptionName": "LoadBalancerType",
        "DefaultValue": "classic",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elasticbeanstalk:environment",
        "ValueType": "Scalar",
        "ValueOptions": ["classic","application","network"]
    },{
        "OptionName": "InstanceRefreshEnabled",
        "DefaultValue": "false",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elasticbeanstalk:managedactions:platformupdate",
        "ValueType": "Boolean"
    },{
        "OptionName": "IgnoreHealthCheck",
        "DefaultValue": "false",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elasticbeanstalk:command",
        "ValueType": "Boolean"
    },{
        "OptionName": "LaunchType",
        "DefaultValue": "Normal",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elasticbeanstalk:control",
        "ValueType": "Scalar",
        "ValueOptions": ["Migration","Normal"]
    },{
        "OptionName": "Period",
        "DefaultValue": "5",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:autoscaling:trigger",
        "MaxValue": 600,
        "MinValue": 1,
        "ValueType": "Scalar"
    },{
        "OptionName": "WSGIPath",
        "DefaultValue": "application.py",
        "ChangeSeverity": "RestartApplicationServer",
        "Namespace": "aws:elasticbeanstalk:container:python",
        "ValueType": "Scalar"
    },{
        "OptionName": "DesiredCapacity",
        "ValueType": "Scalar",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:autoscaling:scheduledaction",
        "MaxValue": 10000,
        "MinValue": 0
    },{
        "OptionName": "Suspend",
        "DefaultValue": "false",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:autoscaling:scheduledaction",
        "ValueType": "Boolean"
    },{
        "ValueType": "CommaSeparatedList",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elb:policies",
        "OptionName": "PublicKeyPolicyNames",
    },{
        "OptionName": "EnvironmentVariables",
        "DefaultValue": "",
        "ChangeSeverity": "RestartApplicationServer",
        "Namespace": "aws:cloudformation:template:parameter",
        "ValueType": "KeyValueList"
    },{
        "OptionName": "InstancePort",
        "DefaultValue": "80",
        "ChangeSeverity": "Unknown",
        "Namespace": "aws:elb:listener",
        "MaxValue": 65535,
        "MinValue": 1,
        "ValueType": "Scalar"
    },{
        "OptionName": "UpperBreachScaleIncrement",
        "DefaultValue": "1",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:autoscaling:trigger",
        "MaxLength": 200,
        "ValueType": "Scalar"
    },{
        "OptionName": "Automatically Terminate Unhealthy Instances",
        "DefaultValue": "true",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elasticbeanstalk:monitoring",
        "ValueType": "Boolean"
    },{
        "OptionName": "HooksPkgUrl",
        "DefaultValue": "https://s3.dualstack.us-east-1.amazonaws.com/elasticbeanstalk-env-resources-us-east-1/stalks/eb_python_4.0.1.95.6/lib/hooks.tar.gz",
        "ChangeSeverity": "Unknown",
        "Namespace": "aws:cloudformation:template:parameter",
        "ValueType": "Scalar"
    },{
        "OptionName": "MonitoringInterval",
        "DefaultValue": "5 minute",
        "ChangeSeverity": "RestartEnvironment",
        "Namespace": "aws:autoscaling:launchconfiguration",
        "ValueType": "Scalar",
        "ValueOptions": ["1 minute","5 minute"]
    },{
        "OptionName": "ConfigDocument",
        "DefaultValue": "{\"Version\":1,\"CloudWatchMetrics\":{\"Instance\":{\"CPUIrq\":null,\"LoadAverage5min\":null,\"ApplicationRequests5xx\":null,\"ApplicationRequests4xx\":null,\"CPUUser\":null,\"LoadAverage1min\":null,\"ApplicationLatencyP50\":null,\"CPUIdle\":null,\"InstanceHealth\":null,\"ApplicationLatencyP95\":null,\"ApplicationLatencyP85\":null,\"RootFilesystemUtil\":null,\"ApplicationLatencyP90\":null,\"CPUSystem\":null,\"ApplicationLatencyP75\":null,\"CPUSoftirq\":null,\"ApplicationLatencyP10\":null,\"ApplicationLatencyP99\":null,\"ApplicationRequestsTotal\":null,\"ApplicationLatencyP99.9\":null,\"ApplicationRequests3xx\":null,\"ApplicationRequests2xx\":null,\"CPUIowait\":null,\"CPUNice\":null},\"Environment\":{\"InstancesSevere\":null,\"InstancesDegraded\":null,\"ApplicationRequests5xx\":null,\"ApplicationRequests4xx\":null,\"ApplicationLatencyP50\":null,\"ApplicationLatencyP95\":null,\"ApplicationLatencyP85\":null,\"InstancesUnknown\":null,\"ApplicationLatencyP90\":null,\"InstancesInfo\":null,\"InstancesPending\":null,\"ApplicationLatencyP75\":null,\"ApplicationLatencyP10\":null,\"ApplicationLatencyP99\":null,\"ApplicationRequestsTotal\":null,\"InstancesNoData\":null,\"ApplicationLatencyP99.9\":null,\"ApplicationRequests3xx\":null,\"ApplicationRequests2xx\":null,\"InstancesOk\":null,\"InstancesWarning\":null}}}",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elasticbeanstalk:healthreporting:system",
        "MaxLength": 32000,
        "ValueType": "Json"
    },{
        "OptionName": "EvaluationPeriods",
        "DefaultValue": "1",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:autoscaling:trigger",
        "MaxValue": 600,
        "MinValue": 1,
        "ValueType": "Scalar"
    },{
        "OptionName": "RootVolumeSize",
        "ValueType": "Scalar",
        "ChangeSeverity": "RestartEnvironment",
        "Namespace": "aws:autoscaling:launchconfiguration",
        "MaxValue": 16384,
        "MinValue": 8
    },{
        "OptionName": "Target",
        "DefaultValue": "TCP:80",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elb:healthcheck",
        "ValueType": "Scalar"
    },{
        "OptionName": "RootVolumeIOPS",
        "ValueType": "Scalar",
        "ChangeSeverity": "RestartEnvironment",
        "Namespace": "aws:autoscaling:launchconfiguration",
        "MaxValue": 20000,
        "MinValue": 100
    },{
        "ValueType": "Boolean",
        "ChangeSeverity": "RestartEnvironment",
        "Namespace": "aws:ec2:vpc",
        "OptionName": "AssociatePublicIpAddress",
    },{
        "OptionName": "DeploymentPolicy",
        "DefaultValue": "AllAtOnce",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elasticbeanstalk:command",
        "ValueType": "Scalar",
        "ValueOptions": ["AllAtOnce","Rolling","RollingWithAdditionalBatch","Immutable"]
    },{
        "OptionName": "EnvironmentType",
        "DefaultValue": "LoadBalanced",
        "ChangeSeverity": "RestartEnvironment",
        "Namespace": "aws:elasticbeanstalk:environment",
        "ValueType": "Scalar",
        "ValueOptions": ["LoadBalanced","SingleInstance"]
    },{
        "OptionName": "UpperThreshold",
        "DefaultValue": "2000000",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:autoscaling:trigger",
        "MinValue": 0,
        "ValueType": "Scalar"
    },{
        "ValueType": "CommaSeparatedList",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elb:policies",
        "OptionName": "LoadBalancerPorts",
    },{
        "OptionName": "AppSource",
        "DefaultValue": "http://s3.amazonaws.com/elasticbeanstalk-samples-us-east-1/python-sample-20150402.zip",
        "ChangeSeverity": "Unknown",
        "Namespace": "aws:cloudformation:template:parameter",
        "ValueType": "Scalar"
    },{
        "ValueType": "Scalar",
        "ChangeSeverity": "Unknown",
        "Namespace": "aws:elb:listener",
        "OptionName": "SSLCertificateId",
    },{
        "ValueType": "Scalar",
        "ChangeSeverity": "Unknown",
        "Namespace": "aws:ec2:vpc",
        "OptionName": "VPCId",
    },{
        "OptionName": "MinSize",
        "DefaultValue": "1",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:autoscaling:asg",
        "MaxValue": 10000,
        "MinValue": 0,
        "ValueType": "Scalar"
    },{
        "OptionName": "LaunchTimeout",
        "DefaultValue": "0",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elasticbeanstalk:control",
        "MinValue": 0,
        "ValueType": "Scalar"
    },{
        "OptionName": "RollingUpdateType",
        "DefaultValue": "Time",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:autoscaling:updatepolicy:rollingupdate",
        "ValueType": "Scalar",
        "ValueOptions": ["Time","Health","Immutable"]
    },{
        "OptionName": "LowerThreshold",
        "DefaultValue": "2000000",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:autoscaling:trigger",
        "MinValue": 0,
        "ValueType": "Scalar"
    },{
        "OptionName": "Availability Zones",
        "DefaultValue": "Any",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:autoscaling:asg",
        "ValueType": "Scalar",
        "ValueOptions": ["Any","Any 1","Any 2","Any 3"]
    },{
        "OptionName": "NumThreads",
        "DefaultValue": "15",
        "ChangeSeverity": "RestartApplicationServer",
        "Namespace": "aws:elasticbeanstalk:container:python",
        "MinValue": 0,
        "ValueType": "Scalar"
    },{
        "OptionName": "BreachDuration",
        "DefaultValue": "5",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:autoscaling:trigger",
        "MaxValue": 600,
        "MinValue": 1,
        "ValueType": "Scalar"
    },{
        "ValueType": "CommaSeparatedList",
        "ChangeSeverity": "RestartEnvironment",
        "Namespace": "aws:ec2:vpc",
        "OptionName": "Subnets",
    },{
        "OptionName": "MinSize",
        "ValueType": "Scalar",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:autoscaling:scheduledaction",
        "MaxValue": 10000,
        "MinValue": 0
    },{
        "OptionName": "LoadBalancerHTTPPort",
        "DefaultValue": "OFF",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elb:loadbalancer",
        "ValueType": "Scalar",
        "ValueOptions": ["OFF","80"]
    },{
        "OptionName": "SSHSourceRestriction",
        "DefaultValue": "tcp,22,22,0.0.0.0/0",
        "ChangeSeverity": "RestartEnvironment",
        "Namespace": "aws:autoscaling:launchconfiguration",
        "ValueType": "Scalar"
    },{
        "OptionName": "SecurityGroups",
        "ValueType": "CommaSeparatedList",
        "ChangeSeverity": "RestartEnvironment",
        "Namespace": "aws:autoscaling:launchconfiguration",
        "MaxLength": 200
    },{
        "OptionName": "InstanceProtocol",
        "ValueType": "Scalar",
        "ChangeSeverity": "Unknown",
        "Namespace": "aws:elb:listener",
        "ValueOptions": ["HTTP","TCP","HTTPS","SSL"]
    },{
        "OptionName": "ImageId",
        "ValueType": "Scalar",
        "ChangeSeverity": "RestartEnvironment",
        "Namespace": "aws:autoscaling:launchconfiguration",
        "MaxLength": 200
    },{
        "OptionName": "Timeout",
        "DefaultValue": "600",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elasticbeanstalk:command",
        "MaxValue": 3600,
        "MinValue": 1,
        "ValueType": "Scalar"
    },{
        "OptionName": "HealthyThreshold",
        "DefaultValue": "3",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elb:healthcheck",
        "MaxValue": 10,
        "MinValue": 2,
        "ValueType": "Scalar"
    },{
        "OptionName": "RetentionInDays",
        "DefaultValue": "7",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elasticbeanstalk:cloudwatch:logs",
        "ValueType": "Scalar",
        "ValueOptions": ["1","3","5","7","14","30","60","90","120","150","180","365","400","545","731","1827","3653"]
    },{
        "OptionName": "UpdateLevel",
        "ValueType": "Scalar",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elasticbeanstalk:managedactions:platformupdate",
        "ValueOptions": ["patch","minor"]
    },{
        "OptionName": "ConnectionSettingIdleTimeout",
        "DefaultValue": "60",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elb:policies",
        "MaxValue": 3600,
        "MinValue": 1,
        "ValueType": "Scalar"
    },{
        "ValueType": "Boolean",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:autoscaling:updatepolicy:rollingupdate",
        "OptionName": "RollingUpdateEnabled",
    },{
        "OptionName": "LogPublicationControl",
        "DefaultValue": "false",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elasticbeanstalk:hostmanager",
        "ValueType": "Boolean",
        "ValueOptions": ["true","false"]
    },{
        "OptionName": "MaxSize",
        "DefaultValue": "4",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:autoscaling:asg",
        "MaxValue": 10000,
        "MinValue": 0,
        "ValueType": "Scalar"
    },{
        "OptionName": "ServiceRole",
        "ValueType": "Scalar",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elasticbeanstalk:environment",
        "MaxLength": 500
    },{
        "OptionName": "ConnectionDrainingEnabled",
        "DefaultValue": "false",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elb:policies",
        "ValueType": "Boolean"
    },{
        "ValueType": "Scalar",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elb:policies",
        "OptionName": "PublicKey",
    },{
        "OptionName": "ListenerEnabled",
        "DefaultValue": "true",
        "ChangeSeverity": "Unknown",
        "Namespace": "aws:elb:listener",
        "ValueType": "Boolean"
    },{
        "OptionName": "UnhealthyThreshold",
        "DefaultValue": "5",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elb:healthcheck",
        "MaxValue": 10,
        "MinValue": 2,
        "ValueType": "Scalar"
    },{
        "OptionName": "DefaultSSHPort",
        "DefaultValue": "22",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elasticbeanstalk:control",
        "ValueType": "Scalar"
    },{
        "OptionName": "LoadBalancerPortProtocol",
        "DefaultValue": "HTTP",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elb:loadbalancer",
        "ValueType": "Scalar",
        "ValueOptions": ["HTTP","TCP"]
    },{
        "OptionName": "Timeout",
        "DefaultValue": "5",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elb:healthcheck",
        "MaxValue": 60,
        "MinValue": 2,
        "ValueType": "Scalar"
    },{
        "OptionName": "SSLCertificateId",
        "ValueType": "Scalar",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elb:loadbalancer",
        "MaxLength": 200
    },{
        "OptionName": "Application Healthcheck URL",
        "DefaultValue": "",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elasticbeanstalk:application",
        "MaxLength": 200,
        "ValueType": "Scalar"
    },{
        "ValueType": "Scalar",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:autoscaling:scheduledaction",
        "OptionName": "StartTime",
    },{
        "OptionName": "MaxSize",
        "ValueType": "Scalar",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:autoscaling:scheduledaction",
        "MaxValue": 10000,
        "MinValue": 0
    },{
        "ValueType": "CommaSeparatedList",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elb:loadbalancer",
        "OptionName": "SecurityGroups",
    },{
        "OptionName": "InstanceType",
        "DefaultValue": "t1.micro",
        "ChangeSeverity": "RestartEnvironment",
        "Namespace": "aws:autoscaling:launchconfiguration",
        "ValueType": "Scalar",
        "ValueOptions": ["t2.micro","t2.small","t2.medium","t2.large","t2.xlarge","t2.2xlarge","m3.medium","m3.large","m3.xlarge","m3.2xlarge","c3.large","c3.xlarge","c3.2xlarge","c3.4xlarge","c3.8xlarge","t1.micro","t2.nano","m1.small","m1.medium","m1.large","m1.xlarge","c1.medium","c1.xlarge","c4.large","c4.xlarge","c4.2xlarge","c4.4xlarge","c4.8xlarge","m2.xlarge","m2.2xlarge","m2.4xlarge","r4.large","r4.xlarge","r4.2xlarge","r4.4xlarge","r4.8xlarge","r4.16xlarge","m4.large","m4.xlarge","m4.2xlarge","m4.4xlarge","m4.10xlarge","m4.16xlarge","cc1.4xlarge","cc2.8xlarge","hi1.4xlarge","hs1.8xlarge","cr1.8xlarge","g2.2xlarge","g2.8xlarge","p2.xlarge","p2.8xlarge","p2.16xlarge","i2.xlarge","i2.2xlarge","i2.4xlarge","i2.8xlarge","i3.large","i3.xlarge","i3.2xlarge","i3.4xlarge","i3.8xlarge","i3.16xlarge","r3.large","r3.xlarge","r3.2xlarge","r3.4xlarge","r3.8xlarge","d2.xlarge","d2.2xlarge","d2.4xlarge","d2.8xlarge","x1.16xlarge","x1.32xlarge","x1e.32xlarge","f1.2xlarge","f1.16xlarge","g3.4xlarge","g3.8xlarge","g3.16xlarge"]
    },{
        "OptionName": "BatchSizeType",
        "DefaultValue": "Percentage",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elasticbeanstalk:command",
        "ValueType": "Scalar",
        "ValueOptions": ["Percentage","Fixed"]
    },{
        "OptionName": "MinInstancesInService",
        "ValueType": "Scalar",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:autoscaling:updatepolicy:rollingupdate",
        "MaxValue": 9999,
        "MinValue": 0
    },{
        "OptionName": "Interval",
        "DefaultValue": "30",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elb:healthcheck",
        "MaxValue": 300,
        "MinValue": 5,
        "ValueType": "Scalar"
    },{
        "OptionName": "HealthCheckSuccessThreshold",
        "DefaultValue": "Ok",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elasticbeanstalk:healthreporting:system",
        "ValueType": "Scalar",
        "ValueOptions": ["Ok","Warning","Degraded",
            "Severe"
        ]
    },{
        "OptionName": "CrossZone",
        "DefaultValue": "false",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elb:loadbalancer",
        "ValueType": "Boolean"
    },{
        "OptionName": "EC2KeyName",
        "ValueType": "Scalar",
        "ChangeSeverity": "RestartEnvironment",
        "Namespace": "aws:autoscaling:launchconfiguration",
        "MaxLength": 200
    },{
        "ValueType": "Scalar",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elasticbeanstalk:sns:topics",
        "OptionName": "Notification Topic Name",
    },{
        "OptionName": "ExternalExtensionsS3Key",
        "ValueType": "Scalar",
        "ChangeSeverity": "RestartEnvironment",
        "Namespace": "aws:elasticbeanstalk:environment",
        "MaxLength": 1024
    },{
        "OptionName": "LoadBalancerHTTPSPort",
        "DefaultValue": "OFF",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elb:loadbalancer",
        "ValueType": "Scalar",
        "ValueOptions": ["OFF","443","8443"
        ]
    },{
        "OptionName": "DeleteOnTerminate",
        "DefaultValue": "false",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elasticbeanstalk:cloudwatch:logs",
        "ValueType": "Boolean"
    },{
        "OptionName": "LowerBreachScaleIncrement",
        "DefaultValue": "-1",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:autoscaling:trigger",
        "MaxLength": 200,
        "ValueType": "Scalar"
    },{
        "OptionName": "PreferredStartTime",
        "ValueType": "Scalar",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elasticbeanstalk:managedactions",
        "MaxLength": 9
    },{
        "OptionName": "ConnectionDrainingTimeout",
        "DefaultValue": "20",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elb:policies",
        "MaxValue": 3600,
        "MinValue": 1,
        "ValueType": "Scalar"
    },{
        "OptionName": "MeasureName",
        "DefaultValue": "NetworkOut",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:autoscaling:trigger",
        "ValueType": "Scalar",
        "ValueOptions": ["CPUUtilization","NetworkIn","NetworkOut","DiskWriteOps","DiskReadBytes","DiskReadOps","DiskWriteBytes","Latency","RequestCount","HealthyHostCount","UnHealthyHostCount"]
    },{
        "OptionName": "MaxBatchSize",
        "ValueType": "Scalar",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:autoscaling:updatepolicy:rollingupdate",
        "MaxValue": 10000,
        "MinValue": 1
    },{
        "OptionName": "StreamLogs",
        "DefaultValue": "false",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elasticbeanstalk:cloudwatch:logs",
        "ValueType": "Boolean"
    },{
        "OptionName": "StaticFiles",
        "DefaultValue": "/static/=static/",
        "ChangeSeverity": "RestartApplicationServer",
        "Namespace": "aws:elasticbeanstalk:container:python",
        "ValueType": "KeyValueList"
    },{
        "OptionName": "Cooldown",
        "DefaultValue": "360",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:autoscaling:asg",
        "MaxValue": 10000,
        "MinValue": 0,
        "ValueType": "Scalar"
    },{
        "OptionName": "Stickiness Cookie Expiration",
        "ValueType": "Scalar",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elb:policies",
        "MaxValue": 1000000,
        "MinValue": 0
    },{
        "ValueType": "CommaSeparatedList",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elb:policies",
        "OptionName": "InstancePorts",
    },{
        "ValueType": "CommaSeparatedList",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elb:policies",
        "OptionName": "SSLProtocols",
    },{
        "ValueType": "Scalar",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elasticbeanstalk:sns:topics",
        "OptionName": "Notification Endpoint",
    },{
        "OptionName": "BatchSize",
        "DefaultValue": "100",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elasticbeanstalk:command",
        "MaxValue": 10000,
        "MinValue": 1,
        "ValueType": "Scalar"
    },{
        "ValueType": "Scalar",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elb:policies",
        "OptionName": "CookieName",
    },{
        "ValueType": "Scalar",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elb:policies",
        "OptionName": "SSLReferencePolicy",
    },{
        "ValueType": "Scalar",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elb:loadbalancer",
        "OptionName": "ManagedSecurityGroup",
    },{
        "ValueType": "CommaSeparatedList",
        "ChangeSeverity": "Unknown",
        "Namespace": "aws:ec2:vpc",
        "OptionName": "ELBSubnets",
    },{
        "OptionName": "ListenerProtocol",
        "DefaultValue": "HTTP",
        "ChangeSeverity": "Unknown",
        "Namespace": "aws:elb:listener",
        "ValueType": "Scalar",
        "ValueOptions": ["HTTP","TCP","HTTPS","SSL"]
    },{
        "OptionName": "RollbackLaunchOnFailure",
        "DefaultValue": "false",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elasticbeanstalk:control",
        "ValueType": "Boolean"
    },{
        "OptionName": "InstancePort",
        "DefaultValue": "80",
        "ChangeSeverity": "Unknown",
        "Namespace": "aws:cloudformation:template:parameter",
        "ValueType": "Scalar"
    },{
        "OptionName": "Timeout",
        "DefaultValue": "PT30M",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:autoscaling:updatepolicy:rollingupdate",
        "ValueType": "Scalar"
    },{
        "ValueType": "Scalar",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elasticbeanstalk:sns:topics",
        "OptionName": "Notification Topic ARN",
    },{
        "ValueType": "Scalar",
        "ChangeSeverity": "RestartEnvironment",
        "Namespace": "aws:autoscaling:launchconfiguration",
        "OptionName": "IamInstanceProfile",
    },{
        "ValueType": "Boolean",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elb:policies",
        "OptionName": "ProxyProtocol",
    },{
        "OptionName": "Statistic",
        "DefaultValue": "Average",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:autoscaling:trigger",
        "ValueType": "Scalar",
        "ValueOptions": ["Minimum","Maximum","Sum","Average"]
    },{
        "OptionName": "Stickiness Policy",
        "DefaultValue": "false",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elb:policies",
        "ValueType": "Boolean"
    },{
        "OptionName": "ExternalExtensionsS3Bucket",
        "ValueType": "Scalar",
        "ChangeSeverity": "RestartEnvironment",
        "Namespace": "aws:elasticbeanstalk:environment",
        "MaxLength": 255
    },{
        "OptionName": "RootVolumeType",
        "ValueType": "Scalar",
        "ChangeSeverity": "RestartEnvironment",
        "Namespace": "aws:autoscaling:launchconfiguration",
        "ValueOptions": ["standard","gp2","io1"]
    },{
        "OptionName": "Unit",
        "DefaultValue": "Bytes",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:autoscaling:trigger",
        "ValueType": "Scalar",
        "ValueOptions": ["Seconds","Percent","Bytes","Bits","Count","Bytes/Second","Bits/Second","Count/Second","None"
        ]
    },{
        "ValueType": "Scalar",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:autoscaling:scheduledaction",
        "OptionName": "EndTime",
    },{
        "OptionName": "Custom Availability Zones",
        "DefaultValue": "",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:autoscaling:asg",
        "ValueType": "List",
        "ValueOptions": ["us-east-1a","us-east-1b","us-east-1c","us-east-1d","us-east-1e","us-east-1f"]
    },{
        "OptionName": "ELBScheme",
        "DefaultValue": "public",
        "ChangeSeverity": "Unknown",
        "Namespace": "aws:ec2:vpc",
        "ValueType": "Scalar"
    }
]