from uuid import uuid4


class ModelsUtil:
    def __init__(self) -> None:
        pass

    @staticmethod
    def generate_hash() -> str:
        return uuid4().hex
