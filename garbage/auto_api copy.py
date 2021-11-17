import sys
import json
import pulumi
from pulumi import automation as auto
from pulumi_aws import s3

def pulumi_program():
    import network # Not sure why I have to import network in this scope - maybe because there's no __init__.py type of stuff?
    import backend

    base_name = f'{pulumi_project_name}-{pulumi_stack_name}'.lower()
    db_name = "backend"
    db_user = "admin"
    db_password = "Gerdisch#419"


    network = network.Vpc(f'{base_name}-net', network.VpcArgs())
    pulumi.export("vpc_id", network.vpc.id)
    subnet_ids=[]
    for subnet in network.subnets:
        subnet_ids.append(subnet.id)

    # Create a backend DB instance
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


# Fred is a generic engineer who is using the service to stand up resources.
# This pair will have to be unique to represent Fred's stack
pulumi_project_name = "DevEnvironment" # Not sure if they see it being a unique project for each Fred or one project and then Fred-unique stacks
pulumi_stack_name = "Fred"
# stack_name = auto.fully_qualified_stack_name("myOrgOrUser", project_name, stack_name)

# To destroy our program, we can run python main.py destroy
destroy = False
args = sys.argv[1:]
if len(args) > 0:
    if args[0] == "destroy":
        destroy = True

# create or select a stack matching the specified name and project.
# this will set up a workspace with everything necessary to run our inline program (pulumi_program)
stack = auto.create_or_select_stack(stack_name=pulumi_stack_name,
                                    project_name=pulumi_project_name,
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

print("refreshing stack...")
stack.refresh(on_output=print)
print("refresh complete")

if destroy:
    print("destroying stack...")
    stack.destroy(on_output=print)
    print("stack destroy complete")
    sys.exit()

print("updating stack...")
up_res = stack.up(on_output=print)
# print(f"update summary: \n{json.dumps(up_res.summary.resource_changes, indent=4)}")



