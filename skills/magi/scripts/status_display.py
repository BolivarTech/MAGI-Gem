class StatusDisplay:
    def __init__(self, names, stream=None):
        self.names = names

    async def start(self):
        pass

    async def stop(self):
        pass

    def update(self, name, state):
        print(f"[{name}] {state}")
