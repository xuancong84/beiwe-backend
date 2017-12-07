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
