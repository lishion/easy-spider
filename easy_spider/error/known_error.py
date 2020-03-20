
class KnownError(Exception):
    error_type = ""


class ClientError(KnownError):
    error_type = "请求错误"


class ConnectionError(ClientError):
    error_type = "连接错误"


class ResponseError(ClientError):

    def __init__(self, code):
        self.code: int = code

    error_type = "响应错误"


class HandlerError(KnownError):
    error_type = "handler错误"
