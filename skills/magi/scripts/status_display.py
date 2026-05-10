from typing import List, Any


class StatusDisplay:
    def __init__(self, names: List[str], stream: Any = None) -> None:
        self.names = names

    async def start(self) -> None:
        pass

    async def stop(self) -> None:
        pass

    def update(self, name: str, state: str) -> None:
        print(f"[{name}] {state}")
