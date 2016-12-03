from app.functions.accounts_controller import handler as accounts_controller_module
from app.functions.users_controller import handler as users_controller_module
from app.functions.instagram_subscription_processor import handler as instagram_subscription_processor_module
from app.functions.instagram_accounts_controller import handler as instagram_accounts_controller_module
from app.functions.instagram_accounts_authorization_controller import handler as instagram_accounts_authorization_controller_module

def accounts_controller(event, context, session=None):
    return accounts_controller_module.handler(event, context, session)

def users_controller(event, context):
    return users_controller_module.handler(event, context)

def instagram_subscription_processor(event, context):
    return instagram_subscription_processor_module.handler(event, context)

def instagram_accounts_controller(event, context):
    return instagram_accounts_controller_module.handler(event, context)

def instagram_accounts_authorization_controller(event, context):
    return instagram_accounts_authorization_controller_module.handler(event, context)