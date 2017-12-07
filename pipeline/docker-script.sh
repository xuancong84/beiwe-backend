# This should be run on a machine running Amazon Linux

# Installations
# -y means "don't ask for confirmation"
sudo yum update -y &&
sudo yum install -y docker &&
sudo yum install -y git &&
pip install awscli --upgrade --user &&
echo "  >>>>>  SUCCESS: installation complete" ||
echo "  >>>>>  FAILURE: installation not complete"

# Get git repo to put in the docker
rm -rf Beiwe-Analysis  # Just in case. If this fails, there is no such folder, and that's fine.
git clone git@github.com:onnela-lab/Beiwe-Analysis.git --branch pipeline &&
echo "  >>>>>  SUCCESS: repository cloned" ||
echo "  >>>>>  FAILURE: repository not cloned"

# Create the docker image. This expects there to be a file called Dockerfile in the same folder as this file
sudo docker build -t beiwe-analysis . &&
echo "  >>>>>  SUCCESS: docker built" ||
echo "  >>>>>  FAILURE: docker not built"

# Create an ECR repository to put the docker container into
aws ecr create-repository \
  --repository-name data-pipeline-docker

# TODO ensure that AWS credentials are configured (or environment variables or whatever)
# Delete the first five columns from the repository description, leaving only the remote repository name
# TODO dynamically generate ARN
# REMOTE=$(aws ecr describe-repositories --output=text | sed "s/\(\S\+\s\+\)\{5\}//") &&
REMOTE="284616134063.dkr.ecr.us-east-2.amazonaws.com/data-pipeline-docker"
sudo docker tag beiwe-analysis $REMOTE &&
echo "  >>>>>  SUCCESS: docker tagged" ||
echo "  >>>>>  FAILURE: docker not tagged"

# Push the docker file to AWS ECR
sudo $(aws ecr get-login --no-include-email) &&
sudo docker push $REMOTE &&
echo "  >>>>>  SUCCESS: docker pushed" ||
echo "  >>>>>  FAILURE: docker not pushed"
