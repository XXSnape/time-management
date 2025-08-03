from httpx import Response


class UnauthorizedExc(Exception):
    def __init__(self, delete_markup: bool = True):
        super().__init__(delete_markup)
        self.delete_markup = delete_markup


class ServerIsUnavailableExc(Exception):
    def __init__(
        self,
        response: Response | None = None,
        delete_markup: bool = True,
    ):
        super().__init__(response)
        self.response = response
        self.delete_markup = delete_markup


class DataIsOutdated(Exception):
    pass
