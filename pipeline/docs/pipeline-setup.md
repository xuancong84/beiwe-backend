# Beiwe Data Pipeline Documentation
## Setting up the Beiwe Data Pipeline
1.  Create an IAM Role with the necessary permissions for running the deploy script.
    1.  Go to <https://console.aws.amazon.com/iam/home?#/policies$new>.
    1.  Select the _JSON_ tab.
    1.  Replace the existing text with the following blob:
        ```json
        {
          "Version": "2012-10-17",
          "Statement": [{
            "Effect": "Allow",
            "Action": [
              "batch:CreateComputeEnvironment",
              "batch:CreateJobQueue",
              "batch:DescribeComputeEnvironments",
              "batch:RegisterJobDefinition",
              "iam:CreateInstanceProfile",
              "ec2:CopyImage",
              "ec2:CreateImage",
              "ec2:DeregisterImage",
              "ec2:RunInstances",
              "ec2:TerminateInstances",
              "ecr:*",
              "iam:AddRoleToInstanceProfile",
              "iam:CreateRole",
              "iam:PassRole",
              "iam:PutRolePolicy"
            ],
            "Resource": "*"
          }]
        }
        ```
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
    1.  Select the box to the left of _Compute optimized | c4.large_.
    1.  Click _Next: Configure Instance Details_.
    1.  Set IAM role to be the name of the role you created in the previous step.
    1.  Click _Review and Launch_.
    1.  Click _Launch_.
    1.  In the dialog that appears, choose or create an SSH key pair that you will use in the next step. If choosing an existing key pair, check the _I acknowledge..._ box.
    1.  Click _Launch Instances_.
    1.  The next page that loads will have a text box with the text _The following instance launches have been initiated_. Click the link immediately after that; it should look something like `i-0383b7cd6eecfa393`.
1.  Run the deploy script.
    1.  In the screen that opens upon clicking the link in the previous step, wait until the `Status Checks` column says `2/2 checks passed`. This may take several minutes. Go get a snack.
    1.  Copy the text in the column `Public DNS (IPv4)`. Make sure you expand the column if necessary to get the full text.
    1.  Open a bash shell on your computer.
    1.  Run the following code in the shell:
        ```bash
        ssh -i [PRIVATE-KEY-FILELOC] ec2-user@[DNS]
        ```
        where `[PRIVATE-KEY-FILELOC]` is the location of the private key for the instance you just created, and `[DNS]` is the text you copied in the previous step.
    1.  If you see a prompt asking `Are you sure you want to continue connecting (yes/no)?`, type `yes` and press enter.
    1.  Run the following code in the shell, one line at a time:
        ```bash
        sudo yum install -y gcc git
        git clone https://github.com/onnela-lab/beiwe-backend.git --branch pipeline
        ```
    1.  Enter your github username and password at the prompts.
    1.  When that has completed, run the following line of code:
        ```bash
        sudo pip install -r beiwe-backend/Requirements.txt
        ```
    1.  The next step takes several minutes to run to completion. You will have to enter your git credentials again towards the beginning.
    1.  If you are setting up your Beiwe Data Pipeline for the first time:
        1.  Run the following line of code:
            ```bash
            python beiwe-backend/pipeline/setup_batch.py
            ```
        1.  When that has completed, you should see the line `Job definition created` printed.
    1.  If you already have the Beiwe Data Pipeline set up, and you want to update the code it is executing: 
        1.  Run the following line of code:
            ```bash
            python beiwe-backend/pipeline/update-docker.py
            ```
        1.  When that has completed, you should see the line `Docker pushed` printed.
    1.  You can now exit the SSH session by typing `logout` and pressing enter.
1.  Terminate the EC2 instance.
    1.  Go to <https://[YOUR-REGION-NAME].console.aws.amazon.com/ec2> again.
    1.  At the top, you should see a link with the text `[X] Running Instances`, where `[X]` is a number. Click on that link.
    1.  Find the instance with the name you gave your EC2 instance earlier, and select the box to the left of the instance name.
    1.  Click _Actions_, then _Instance State_, then _Terminate_.
### Congratulations! You have set up your Beiwe Data Pipeline!
