"""
A script for setting up an AWS environment to run the Beiwe Data Access Pipeline
"""

from scripts import docker_script, job_queue_script


if __name__ == '__main__':
    repo_uri = docker_script.run()
    job_queue_script.run(repo_uri)
