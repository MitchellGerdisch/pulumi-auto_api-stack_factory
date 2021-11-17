import sys
import getopt
import json
import yaml
import pulumi
from pulumi import automation as auto
from pulumi_aws import s3

### This program and the related config and related plugins install is the part that needs to be repeated for different patterns
### Using component resources can abstract this further as done below.
def create_pulumi_program(base_name, config):
    import network # Not sure why I have to import network in this scope - maybe because there's no __init__.py type of stuff?
    import backend

    vpc_cidr = config['vpc']['cidr']

    network = network.Vpc(f'{base_name}-net', network.VpcArgs(cidr_block=vpc_cidr))
    pulumi.export("vpc_id", network.vpc.id)
    subnet_ids=[]
    for subnet in network.subnets:
        subnet_ids.append(subnet.id)

    # Create a backend DB instance
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

def main(argv):
    ####
    # Get the config from the yaml file passed as an argument
    config = ''
    destroy= False
    try:
        opts, args = getopt.getopt(argv,"hdc:")
    except getopt.GetoptError:
        print('test.py -c <config yaml>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('test.py -c <config yaml>')
            sys.exit()
        elif opt in ("-c"):
            config_file = arg
            with open(arg) as config_file:
                config = yaml.safe_load(config_file)
        elif opt in ("-d"):
            destroy = True

    pulumi_project_name = config['pulumi']['project']
    pulumi_stack_name = config['pulumi']['stack']
    base_name = f'{pulumi_project_name}-{pulumi_stack_name}'.lower()
    # stack_name = auto.fully_qualified_stack_name("myOrgOrUser", project_name, stack_name)

    # function that returns the project program with the config values inserted appropriately
    def pulumi_program():
        return create_pulumi_program(base_name, config)

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


    ###### Put below in a module or class to manage the up and down bits? #####
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

if __name__ == "__main__":
   main(sys.argv[1:])

