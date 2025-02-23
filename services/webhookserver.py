from aiohttp import web
import asyncio
import logging
import json

class WebhookServer:
    __port = 0
    def __init__(self, port):
        self.__port = port
        self.queue = asyncio.Queue()
        self.app = web.Application()
        self.app.router.add_post("/webhook", self.handle_webhook)
        self.runner = web.AppRunner(self.app)

    async def handle_webhook(self, request):
        try:
            data = await request.post()
            payload = json.loads(data['payload'])
            logging.info(f"Received webhook: {data}")
            await self.queue.put(payload)
            return web.Response(text="OK")
        except Exception as e:
            logging.warning(f"Error parsing JSON data: {data}")

    async def start(self):
        await self.runner.setup()
        site = web.TCPSite(self.runner, "0.0.0.0", self.__port)
        await site.start()
        logging.info(f"Webhook server running on port {self.__port}")
        #while True:
            #await asyncio.sleep(3600)

""" async def main():
    serv = WebhookServer(5000)
    await serv.start()

# Run the event loop
asyncio.run(main()) """