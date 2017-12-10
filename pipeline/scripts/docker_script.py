"""
A script for creating a docker image and uploading it to an AWS ECS repository.
This should be run on a machine running Amazon Linux.
"""

import subprocess

# TODO make sure to pip install this, however, wherever
import boto3


def run(ecr_repo_name):
    """
    Run the code
    :param ecr_repo_name: Name of the repository we will create and upload to
    :return: The repository's URI, to be used in creating AWS Batch jobs elsewhere
    """
    
    # Install docker, git and AWS command line interface
    # -y means "don't ask for confirmation"
    # check_call will raise an error if the command fails (i.e. returns nonzero)
    subprocess.check_call(['sudo', 'yum', 'update', '-y'])
    subprocess.check_call(['sudo', 'yum', 'install', '-y', 'docker'])
    subprocess.check_call(['sudo', 'yum', 'install', '-y', 'git'])
    subprocess.check_call(['pip', 'install', 'awscli', '--upgrade', '--user'])
    print('Installations complete')
    
    # Get git repo to put in the docker
    # TODO: when this branch has been merged with master, get rid of the --branch pipeline argument
    subprocess.check_call(['git', 'clone', 'git@github.com:onnela-lab/Beiwe-Analysis.git',
                           '--branch', 'pipeline'])
    print('Git repository cloned')
    
    # Create the docker image
    subprocess.check_call(['sudo', 'docker', 'build', '-t', 'beiwe-analysis', '.'])
    print('Docker image created')
    
    # Create an AWS ECR repository to put the docker image into, and get the repository's URI
    client = boto3.client('ecr')
    resp = client.create_repository(
        repositoryName=ecr_repo_name,
    )
    repo_uri = resp['repository']['repositoryUri']
    print('ECR repository created')
    
    # TODO ensure that AWS credentials are configured (or environment variables or whatever)
    # Tag the local docker image with the remote repository's URI. This is similar to
    # having a local git branch track a remote one.
    subprocess.check_call(['sudo', 'docker', 'tag', 'beiwe-analysis', repo_uri])
    
    # Push the docker file to our new repository
    # TODO make sure this isn't insecure (cause of using shell=True)
    subprocess.check_call('sudo $(aws ecr get-login --no-include-email)', shell=True)
    subprocess.check_call(['sudo', 'docker', 'push', repo_uri])
    print('Docker pushed')
    
    return repo_uri
