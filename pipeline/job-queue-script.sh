# TODO create parent .sh file
# TODO put constants in the parent .sh file, pass them here
# TODO make errors block later commands from executing (string together with && or put || exit -1 everywhere
# TODO create an IAM role for the EC2 instance, probably
# Create a new IAM role for the compute environment 
ROLE_NAME="AWSBatchServiceRole"
COMP_ENV_NAME="data-pipeline-env-1209"
QUEUE_NAME="data-pipeline-queue-1209"
JOB_DEFN_NAME="data-pipeline-job-defn-1209"
SERVICE_ROLE_ARN=$(
aws iam create-role \
  --role-name $ROLE_NAME \
  --assume-role-policy-document file://assume-batch-role.json \
  --output=text \
  | head -n 1 \
  | cut -f 2 \
)
aws iam put-role-policy \
  --role-name $ROLE_NAME \
  --policy-name aws-batch-service-policy \
  --policy-document file://batch-service-role.json

# Create the batch compute environment
aws batch create-compute-environment \
  --compute-environment-name $COMP_ENV_NAME \
  --type MANAGED \
  --compute-resources file://compute-env.json \
  --service-role $SERVICE_ROLE_ARN

# Wait for the compute environment to be valid. If it is deemed invalid, exit
echo "Waiting for compute environment..."
STATUS="CREATING"
while [ $STATUS == "CREATING" ]; do
  STATUS=$( \
  aws batch describe-compute-environments \
    --compute-environments $COMP_ENV_NAME \
    --output=text \
    | head -n 1 \
    | cut -f 7 \
  )
  if [ $STATUS == "INVALID" ]; then
    echo "  >>>>>  FAILURE: Compute environment is invalid"
    exit 1
  fi
  sleep 1
done

# Create the batch job queue
aws batch create-job-queue \
  --job-queue-name $QUEUE_NAME \
  --priority 1 \
  --compute-environment-order order=0,computeEnvironment=$COMP_ENV_NAME

# Define a job definition
aws batch register-job-definition \
  --job-definition-name $JOB_DEFN_NAME \
  --type container \
  --container-properties file://container-props.json
