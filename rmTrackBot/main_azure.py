import azure.functions as func
from req_hdl import req_handler


app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


@app.route(route='bot', auth_level=func.AuthLevel.ANONYMOUS)
def main(request):
    return req_handler(request)
