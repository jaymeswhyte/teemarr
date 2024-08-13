from discord.ui import View
import logging

class RequestView(View):
    _message = None
    def __init__(self, *items, timeout=180):
        super().__init__(*items, timeout=timeout)

    async def on_timeout(self):
        # This will update the original message to disable the buttons
        try:
            self.clear_items()
            await self._message.edit(content="Request timed out.", view=self, embeds=[])
        except Exception as e:
            logging.error(f"Failed to remove embeds from timed-out message: {e}")

    @property
    def message(self):
        return self._message
    @message.setter
    def message(self, newMessage):
        self._message = newMessage