from httpx import Response


class UnauthorizedExc(Exception):
    pass


class ServerIsUnavailableExc(Exception):
    def __init__(self, response: Response | None):
        super().__init__(response)
        self.response = response
