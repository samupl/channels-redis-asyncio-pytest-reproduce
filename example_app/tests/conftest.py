import asyncio
from typing import Optional, Union

import pytest
import pytest_asyncio
from channels.testing import WebsocketCommunicator, ApplicationCommunicator

from channels_pytest_issue.routing import application


class QSWebsocketCommunicator(WebsocketCommunicator):
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


# @pytest.fixture(scope="session")
# def event_loop():
#     try:
#         loop = asyncio.get_running_loop()
#     except RuntimeError:
#         loop = asyncio.new_event_loop()
#     yield loop
#     loop.close()
