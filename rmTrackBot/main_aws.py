from event_hdl import event_handler


def lambda_handler(event, context):
    return event_handler(event, context)
