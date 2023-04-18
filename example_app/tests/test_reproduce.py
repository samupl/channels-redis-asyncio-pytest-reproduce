import pytest

from channels.testing import WebsocketCommunicator
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


@pytest.mark.django_db(transaction=True)
class TestChatCommunicator:

    @pytest.mark.asyncio
    async def test_reproduce_exception(self) -> None:
        connected_communicator = await get_connected_communicator()
        await connected_communicator.send_json_to({
            'command': 'raise'
        })
        response = await connected_communicator.receive_json_from()
        assert response == {'status': 'raised'}
        await connected_communicator.disconnect()

    @pytest.mark.asyncio
    async def test_reproduce_ok(self) -> None:
        connected_communicator = await get_connected_communicator()
        await connected_communicator.send_json_to({
            'command': 'ok'
        })
        response = await connected_communicator.receive_json_from()
        assert response == {'status': 'ok'}
        await connected_communicator.disconnect()
