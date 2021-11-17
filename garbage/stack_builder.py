class Stack:
  def __init__(self, stack_name, network_cidr, backend_db_name, ):
    self.stack_name = stack_name
    self.network_cidr = network_cidr
    self.backend_db_name = backend_db_name

class StackBuilder:
  def build_stack(self, stack):
    network = self._build_network()
