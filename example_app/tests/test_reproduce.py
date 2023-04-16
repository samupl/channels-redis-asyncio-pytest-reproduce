import pytest

from example_app.tests.conftest import QSWebsocketCommunicator


@pytest.mark.django_db(transaction=True)
class TestChatCommunicator:

    @pytest.mark.asyncio
    async def test_reproduce_exception(self, connected_communicator: QSWebsocketCommunicator) -> None:
        await connected_communicator.send_json_to({
            'command': 'raise'
        })
        response = await connected_communicator.receive_json_from()
        assert response == {'status': 'raised'}

    @pytest.mark.asyncio
    async def test_reproduce_ok(self, connected_communicator: QSWebsocketCommunicator) -> None:
        await connected_communicator.send_json_to({
            'command': 'ok'
        })
        response = await connected_communicator.receive_json_from()
        assert response == {'status': 'ok'}
