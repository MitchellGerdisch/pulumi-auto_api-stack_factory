import pulumi
from pulumi import automation as auto
from pulumi_aws import s3

# This file contains all the knowledge needed for this project/stack (i.e. "S3" project and stack)
# This includes which plugins need to be installed, etc.
class Project:
  def __init__(self, project_name, stack_name, base_name, config):
    self.project_name = project_name
    self.stack_name = stack_name
    self.base_name = base_name
    self.config = config

  def create_stack(self):
    project_name = self.project_name
    stack_name = self.stack_name
    base_name = self.base_name
    config = self.config

    # Create pulumi program to launch as project/stack
    def pulumi_program():
      return create_pulumi_project(base_name, config)

    # create or select a stack matching the specified name and project.
    # this will set up a workspace with everything necessary to run our inline program (pulumi_program)
    stack = auto.create_or_select_stack(stack_name=stack_name,
                                        project_name=project_name,
                                        program=pulumi_program)

    print("successfully initialized stack")

    # for inline programs, we must manage plugins ourselves
    print("installing plugins...")
    stack.workspace.install_plugin("aws", "v4.0.0")
    print("plugins installed")

    # set stack configuration specifying the AWS region to deploy
    print("setting up config")
    stack.set_config("aws:region", auto.ConfigValue(value="us-east-2"))
    print("config set")

    return(stack)


#### The Pulumi Project Code for the "Network-DB" project/stack pattern.
def create_pulumi_project(base_name, config):

    bucket_acl = config['bucket']['acl']
    bucket = s3.Bucket('my-bucket', 
      acl=bucket_acl
    )
    pulumi.export("bucket_id", bucket.id)

