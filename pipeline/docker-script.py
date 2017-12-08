# This should be run on a machine running Amazon Linux
import subprocess

# TODO make sure to pip install this, however, wherever
import boto3


# Installations
# -y means "don't ask for confirmation"
subprocess.check_call(['sudo', 'yum', 'update', '-y'])
subprocess.check_call(['sudo', 'yum', 'install', '-y', 'docker'])
subprocess.check_call(['sudo', 'yum', 'install', '-y', 'git'])
subprocess.check_call(['pip', 'install', 'awscli', '--upgrade', '--user'])

# Get git repo to put in the docker
subprocess.check_call(['rm', '-rf', 'Beiwe-Analysis'])  # Just in case. If this fails, there is no such folder, and that's fine.
subprocess.check_call(['git', 'clone', 'git@github.com:onnela-lab/Beiwe-Analysis.git', '--branch', 'pipeline'])

# Create the docker image. This expects there to be a file called Dockerfile in the same folder as this file
subprocess.check_call(['sudo', 'docker', 'build', '-t', 'beiwe-analysis', '.'])

# Create an ECR repository to put the docker container into, and get the ARN of the repository
client = boto3.client('ecr')
resp = client.create_repository(
    repositoryName='data-pipeline-docker',
)
remote = resp['repository']['repositoryUri']

# TODO ensure that AWS credentials are configured (or environment variables or whatever)
subprocess.check_call(['sudo', 'docker', 'tag', 'beiwe-analysis', remote])

# Push the docker file to AWS ECR
# TODO make sure this isn't insecure (cause of using shell=True)
subprocess.check_call('sudo $(aws ecr get-login --no-include-email)', shell=True)
subprocess.check_call(['sudo', 'docker', 'push', remote])
