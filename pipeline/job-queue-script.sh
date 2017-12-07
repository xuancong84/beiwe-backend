# TODO same todos as other -script.sh files
# Create a new IAM role for the compute environment 
aws iam create-role \
  --role-name AWSBatchServiceRole \
  --assume-role-policy-document file://assume-batch-role.json
aws iam put-role-policy \
  --role-name AWSBatchServiceRole \
  --policy-name aws-batch-service-policy \
  --policy-document file://batch-service-role.json

# Create the batch compute environment
aws batch create-compute-environment \
  --compute-environment-name data-pipeline-env \
  --type MANAGED \
  --compute-resources file://compute-env.json \
  --service-role arn:aws:iam::284616134063:role/service-role/AWSBatchServiceRole

# Create the batch job queue
aws batch create-job-queue \
  --job-queue-name data-pipeline-queue \
  --priority 1 \
  --compute-environment-order order=0,computeEnvironment=data-pipeline-env

# Define a job definition
aws batch register-job-definition \
  --job-definition-name data-pipeline-job-defn \
  --type container \
  --container-properties file://container-props.json
