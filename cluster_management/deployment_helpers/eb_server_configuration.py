def _configure_namespace(options, namespace):
    for option in options:
        option['Namespace'] = namespace

environment_variables = [
    # aws_credentials
    {
        "OptionName": "AWS_ACCESS_KEY_ID",
        "Value": "weeee"
    },
    {
        "OptionName": "AWS_SECRET_ACCESS_KEY",
        "Value": "weeee"
    },
    # db_credentials
    {
        "OptionName": "MONGO_IP",
        "Value": "weeee"
    },
    {
        "OptionName": "MONGO_IP",
        "Value": "weeee"
    },
    # env_variables
    {
        "OptionName": "CELERY_EXPIRY_MINUTES",
        "Value": "weeee"
    },
    {
        "OptionName": "SYSADMIN_EMAILS",
        "Value": "weeee"
    },
    {
        "OptionName": "MONGO_PASSWORD",
        "Value": "weeee"
    },
    {
        "OptionName": "S3_BUCKET",
        "Value": "weeee"
    },
    # sentry_dsns
    {
        "OptionName": "SENTRY_JAVASCRIPT_DSN",
        "Value": "weeee"
    },
    # generated_by_us
    {
        "OptionName": "FLASK_SECRET_KEY",
        "Value": "weeee"
    },
    # optional
    # {
    #     "OptionName": "IS_STAGING",
    #     "Value": "weeee"
    # },
]
_configure_namespace(environment_variables, "aws:elasticbeanstalk:application:environment")
