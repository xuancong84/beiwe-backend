"""
A script for setting up an AWS environment to run the Beiwe Data Access Pipeline
"""

from scripts import ami_script, docker_script, job_queue_script


if __name__ == '__main__':
    repo_uri = docker_script.run()
    ami_id = ami_script.run()
    job_queue_script.run(repo_uri, ami_id)
