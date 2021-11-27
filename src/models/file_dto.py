class FileDto:
    def __init__(self, client_name: str, files: list) -> None:
        self.client_name = client_name
        self.files = files
