from discord.ui import View

class RequestView(View):
    _message = None
    def __init__(self, *items, timeout=180):
        super().__init__(*items, timeout=timeout)

    async def on_timeout(self):
        self.clear_items()
        # This will update the original message to disable the buttons
        await self._message.edit(content="Request timed out.", view=self, embeds=[])

    @property
    def message(self):
        return self._message
    @message.setter
    def message(self, newMessage):
        self._message = newMessage