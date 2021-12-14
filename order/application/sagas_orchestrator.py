
class Orchestrator(object):
    def __init__(self):
        self.order_process_list = list()

    def manage_message(self, event, values):
        order_process = self.get_order(values['order_id'])
        order_process.on_event(event, values)

    def get_order(self, order_id):
        for order_process in self.order_process_list:
            if order_process.order_id == order_id:
                return order_process
        return None


orchestrator = Orchestrator()


def get_orchestrator():
    return orchestrator
