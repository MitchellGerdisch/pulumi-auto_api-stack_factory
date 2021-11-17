# Studies in Auto API and Stack Patterns
Playing with automation API and creating stacks based on config yaml files and some patterns.
Also uses component resources.

## Big Picture
- auto_api.py: This is the main entry point and is called with a given yaml config file (and an optional "destroy" flag). 
- stack_factory.project_stack.py: This is a (mostly) stack-agnostic factory that contains the if-then logic to call the right project/stack/pattern module based on the yaml config file settings. Currently, there is an explicity "pattern" property in the yaml but the pattern could be inferred in the factory to figure out which pattern module to call.
- projects: Contain modules where each module captures all the knowledge for the given project/pattern. This knowledge includes the inline pulumi program itself that stands up the stack as well any config and plugins management needed for the given project/pattern.

## To Use:
- Use one of the example config yaml files or create your own. 
- Run `python ./auto_api.py -c ./config_XXX.yaml` to create the project (if not already existing) and create or update the stack.
- To destroy, run `python ./auto_api.py -c ./config_XXX.yaml -d`

## Possible Future Updates
1) There may (is?) a use-case where the user's request needs to create/update multiple Pulumi stacks. Currently the code handles a single pattern which represents a single stack. But it wouldn't be hard to put a loop around that to create multiple stacks if needed.

1) Currently most of the config from the YAML is inserted directly into the resources. I think it would be good to insert the config into Pulumi config so that it shows up in the Pulumi SaaS for the given update.
- stack.set_config(yamlconfig_property_key, auto.ConfigValue(value=yamlconfig_property_value)))

1) Support a parmeter to remove the stack completely.
