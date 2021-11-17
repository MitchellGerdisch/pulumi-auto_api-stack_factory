# This module contains the logic for 
import pulumi
from projects import network_db, s3

class Project:
  def __init__(self, config):
    self.config = config

  def create_stack(self):
    config = self.config
    pulumi_project_name = config['pulumi']['project']
    pulumi_stack_name = config['pulumi']['stack']
    base_name = f'{pulumi_project_name}-{pulumi_stack_name}'.lower()
    # stack_name = auto.fully_qualified_stack_name("myOrgOrUser", project_name, stack_name)

    pattern = config['pattern']

    # if config is for given pattern ...
    project=None
    if (pattern == "network-db"):
        project = network_db.Project(pulumi_project_name, pulumi_stack_name, base_name, config)
    elif (pattern == "s3"):
        project = s3.Project(pulumi_project_name, pulumi_stack_name, base_name, config)

    stack = project.create_stack()
    return(stack)

    