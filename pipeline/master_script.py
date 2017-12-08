from scripts import docker_script, job_queue_script, lambda_script


def run(ecr_repo_name, comp_env_role, comp_env_name, queue_name, job_defn_name, lambda_role, function_name, rule_name):
    docker_script.run(ecr_repo_name)
    job_queue_script.run(comp_env_name, comp_env_role, queue_name, job_defn_name)
    lambda_script.run(lambda_role, function_name, rule_name)


if __name__ == '__main__':
    _ecr_repo_name = 'data-pipeline-docker'
    _comp_env_role = 'AWSBatchServiceRole'
    _comp_env_name = 'data-pipeline-env'
    _queue_name = 'data-pipeline-queue'
    _job_defn_name = 'data-pipeline-job-defn'
    _lambda_role = 'data-pipeline-lambda-role'
    _function_name = 'create-{freq}-batch-jobs'
    _rule_name = '{freq}-trigger'
    run(
        _ecr_repo_name,
        _comp_env_role,
        _comp_env_name,
        _queue_name,
        _job_defn_name,
        _lambda_role,
        _function_name,
        _rule_name
    )
