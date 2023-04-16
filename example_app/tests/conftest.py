import asyncio
from typing import Optional, Union

import pytest
import pytest_asyncio
from channels.testing import WebsocketCommunicator, ApplicationCommunicator

from channels_pytest_issue.routing import application


class QSWebsocketCommunicator(WebsocketCommunicator):
    def __init__(self, application, path, headers=None, subprotocols=None,
                 query_string: Optional[Union[str, bytes]]=None):
        if isinstance(query_string, str):
            query_string = str.encode(query_string)
        self.scope = {
            'type': 'websocket',
            'path': path,
            'headers': headers or [],
            'subprotocols': subprotocols or [],
            'query_string': query_string or '',
        }
        ApplicationCommunicator.__init__(self, application, self.scope)

    async def join_huddle(self, huddle_id: int, *, wait_for_response=False):
        await self.send_json_to({
            'command': 'join',
            'huddle': huddle_id,
        })
        if wait_for_response:
            assert (await self.receive_json_from())['meta']

    async def receive_json_from(self, timeout=1, msg_type=None) -> dict:
        message = await super().receive_json_from(timeout)
        if msg_type is not None:
            while message["msg_type"] != msg_type:
                message = await super().receive_json_from(timeout)
        return message


async def get_connected_communicator() -> QSWebsocketCommunicator:
    communicator = QSWebsocketCommunicator(application, '/test/')
    connected, subprotocol = await communicator.connect()
    if not connected:
        await communicator.disconnect()
        raise AssertionError
    return communicator


@pytest_asyncio.fixture
async def connected_communicator():
    communicator = await get_connected_communicator()
    yield communicator
    await communicator.disconnect()


@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()
