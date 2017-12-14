# Beiwe Data Pipeline Documentation
## Setting up the Beiwe Data Pipeline for the first time
1.  Create an IAM Role with the necessary permissions for running the deploy script.
    1.  Go to <https://console.aws.amazon.com/iam/home?#/policies$new>.
    1.  Select the _JSON_ tab.
    1.  Replace the existing text with the full text of `pipeline-setup-policy.json`.
    1.  Click _Review policy_.
    1.  Enter a name and click _Create policy_.
    1.  Go to <https://console.aws.amazon.com/iam/home?#/roles$new?step=permissions&selectedService=EC2&selectedUseCase=EC2>.
    1.  Select the box to the left of the name of the policy you just created.
    1.  Click _Next: Review_.
    1.  Enter a role name and click _Create role_.
1.  Create an EC2 instance to run the deploy script on.
    1.  Go to <https://[YOUR-REGION-NAME].console.aws.amazon.com/ec2>, where `[YOUR-REGION-NAME]` is replaced with the name of a region you use (e.g. `us-east-2`).
    1.  Click _Launch instance_ (about halfway down the page).
    1.  Select the first _Amazon Linux AMI_ option.
    1.  Select ***TODO: figure out a minimal functional instance***.
    1.  Click _Next: Configure Instance Details_.
    1.  Set IAM role to be the name of the role you created in the previous step.
    1.  Click _Review and Launch_.
    1.  Click _Launch_.
    1.  ***TODO: figure out ssh credentials***
1.  Run the deploy script.
    1.  SSH into the instance you just created. ***TODO details***
    1.  Run the following code in the terminal: `git clone https://github.com/onnela-lab/beiwe-backend.git`.
    1.  Enter your github username and password at the prompts.
    1.  When that has completed, run the following code: `python beiwe-backend/pipeline/setup_batch.py`. This takes a couple of minutes to run to completion.
    1.  When that has completed, you should see the line `Job definition created` printed. You can now exit the SSH session by typing `logout`.
1.  Terminate the EC2 instance.
    1.  Go to <https://[YOUR-REGION-NAME].console.aws.amazon.com/ec2> again.
    1.  At the top, you should see a link with the text `[X] Running Instances`, where `[X]` is a number. Click on that link.
    1.  Find the instance with the name you gave your EC2 instance earlier, and select the box to the left of the instance name.
    1.  Click _Actions_, then _Instance State_, then _Terminate_.
### Congratulations! You have set up your Beiwe Data Pipeline!

## Updating the code in the Beiwe Data Pipeline
1.  ***TODO***
