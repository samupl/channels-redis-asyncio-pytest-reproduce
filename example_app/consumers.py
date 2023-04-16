from channels.generic.websocket import AsyncJsonWebsocketConsumer


class ExampleException(Exception):
    ...


class ExampleConsumer(AsyncJsonWebsocketConsumer):

    async def receive_json(self, content, **kwargs):
        command = content.get('command', None)
        try:
            if command == 'raise':
                await self.raise_exception()
            elif command == 'ok':
                await self.ok()
        except ExampleException:
            await self.send_json({'status': 'raised'})

    async def raise_exception(self):
        raise ExampleException('Example exception')

    async def ok(self):
        await self.send_json({'status': 'ok'})

    async def connect(self):
        await self.channel_layer.group_add('test', self.channel_name)

    async def disconnect(self, code):
        await self.channel_layer.group_discard('test', self.channel_name)
