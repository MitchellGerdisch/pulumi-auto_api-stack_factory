import pulumi
from pulumi import automation as auto

# This file contains all the knowledge needed for this project/stack (i.e. "Network_DB" project and stack)
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


# The Pulumi Project Code for the "Network-DB" project/stack pattern.
def create_pulumi_project(base_name, config):
    from components import network
    from components import backend

    vpc_cidr = config['vpc']['cidr']
    network = network.Vpc(f'{base_name}-net', network.VpcArgs(cidr_block=vpc_cidr))
    pulumi.export("vpc_id", network.vpc.id)
    subnet_ids=[]
    for subnet in network.subnets:
        subnet_ids.append(subnet.id)

    # Create a backend DB instance if config set
    if ('db' in config.keys()):
        db_name = config['db']['name']
        db_user = config['db']['user']
        db_password = config['db']['password']
        be=backend.Db(f'{base_name}-be', backend.DbArgs(
            db_name=db_name,
            db_user=db_user,
            db_password=db_password,
            # publicly_accessible=True,  # Uncomment this to override for testing
            subnet_ids=subnet_ids,
            security_group_ids=[network.rds_security_group.id]
        ))

        pulumi.export('DB Endpoint', be.db.address)
        pulumi.export('DB User Name', be.db.username)
        pulumi.export('DB Password', be.db.password)

