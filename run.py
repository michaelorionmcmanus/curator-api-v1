from app.functions.accounts_controller import handler as accounts_controller_module
from app.functions.users_controller import handler as users_controller_module

def accounts_controller(event, context):
    return accounts_controller_module.handler(event, context)

def users_controller(event, context):
    return users_controller_module.handler(event, context)