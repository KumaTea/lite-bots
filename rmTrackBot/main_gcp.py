import functions_framework
from req_hdl import req_handler


@functions_framework.http
def main(request):
    return req_handler(request)
