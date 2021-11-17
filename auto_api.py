import sys
import getopt
import json
import yaml
from stack_factory import project_stack

def main(argv):
    ####
    # Get the config from the yaml file passed as an argument
    config = None
    destroy = False
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

    #### Instantiate the project and stack
    ## TODO: Think about where best to handle the multiple stack use-case. 
    ## I.e. where Fred is asking for resources that will be deployed across multiple stacks.
    ## That would likely be orchestrated here and driven by the config data in some way.
    ## DOES THIS USE-CASE EXIST?
    project = project_stack.Project(config)
    stack = project.create_stack()

    # Logic to refresh, update, destroy the stack
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

