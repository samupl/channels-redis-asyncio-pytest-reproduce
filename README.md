# Issue reproduction
## Django channels + pytest-asyncio + channels-redis 

This repo reproduces a weird issue I encountered after upgrading from legacy 2.x channels repo to the newest version of
all packages.

The issue is that if any code within a consumer calls `self.channel_layer.group_discard()`, consecutive tests start to 
fail with a `TimeoutError` due to the event loop being closed.

## How to run:

```shell
docker compose build
docker compose run app pytest example_app/tests/test_reproduce.py::TestChatCommunicator::test_reproduce_exception example_app/tests/test_reproduce.py::TestChatCommunicator::test_reproduce_ok --reuse-db
```

The expected output is to see both tests passed. The observed output, however, is a timeout error:

<details>
    <summary>Click to see the output</summary>

    ```
    ――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――― ERROR at setup of TestChatCommunicator.test_reproduce_ok ――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――
    
    self = <example_app.tests.conftest.QSWebsocketCommunicator object at 0x7f91fa011610>, timeout = 1
    
        async def receive_output(self, timeout=1):
            """
            Receives a single message from the application, with optional timeout.
            """
            # Make sure there's not an exception to raise from the task
            if self.future.done():
                self.future.result()
            # Wait and receive the message
            try:
                async with async_timeout(timeout):
    >               return await self.output_queue.get()
    
    /usr/local/lib/python3.11/site-packages/asgiref/testing.py:74: 
    _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
    
    self = <Queue at 0x7f91fa010750 maxsize=0>
    
        async def get(self):
            """Remove and return an item from the queue.
        
            If queue is empty, wait until an item is available.
            """
            while self.empty():
                getter = self._get_loop().create_future()
                self._getters.append(getter)
                try:
    >               await getter
    E               asyncio.exceptions.CancelledError
    
    /usr/local/lib/python3.11/asyncio/queues.py:158: CancelledError
    
    During handling of the above exception, another exception occurred:
    
    event_loop = <_UnixSelectorEventLoop running=False closed=False debug=False>, request = <SubRequest 'connected_communicator' for <Function test_reproduce_ok>>, kwargs = {}
    func = <function connected_communicator at 0x7f91fa0496c0>, setup = <function _wrap_asyncgen_fixture.<locals>._asyncgen_fixture_wrapper.<locals>.setup at 0x7f91f9fda0c0>
    finalizer = <function _wrap_asyncgen_fixture.<locals>._asyncgen_fixture_wrapper.<locals>.finalizer at 0x7f91f9fd85e0>
    
        @functools.wraps(fixture)
        def _asyncgen_fixture_wrapper(
            event_loop: asyncio.AbstractEventLoop, request: SubRequest, **kwargs: Any
        ):
            func = _perhaps_rebind_fixture_func(
                fixture, request.instance, fixturedef.unittest
            )
            gen_obj = func(**_add_kwargs(func, kwargs, event_loop, request))
        
            async def setup():
                res = await gen_obj.__anext__()
                return res
        
            def finalizer() -> None:
                """Yield again, to finalize."""
        
                async def async_finalizer() -> None:
                    try:
                        await gen_obj.__anext__()
                    except StopAsyncIteration:
                        pass
                    else:
                        msg = "Async generator fixture didn't stop."
                        msg += "Yield only once."
                        raise ValueError(msg)
        
                event_loop.run_until_complete(async_finalizer())
        
    >       result = event_loop.run_until_complete(setup())
    
    /usr/local/lib/python3.11/site-packages/pytest_asyncio/plugin.py:298: 
    _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
    /usr/local/lib/python3.11/asyncio/base_events.py:653: in run_until_complete
        return future.result()
    /usr/local/lib/python3.11/site-packages/pytest_asyncio/plugin.py:280: in setup
        res = await gen_obj.__anext__()
    /home/js/git/channels-redis-asyncio-pytest-reproduce/example_app/tests/conftest.py:52: in connected_communicator
        ???
    /home/js/git/channels-redis-asyncio-pytest-reproduce/example_app/tests/conftest.py:43: in get_connected_communicator
        ???
    /usr/local/lib/python3.11/site-packages/channels/testing/websocket.py:36: in connect
        response = await self.receive_output(timeout)
    /usr/local/lib/python3.11/site-packages/asgiref/testing.py:85: in receive_output
        raise e
    /usr/local/lib/python3.11/site-packages/asgiref/testing.py:73: in receive_output
        async with async_timeout(timeout):
    /usr/local/lib/python3.11/site-packages/asgiref/timeout.py:71: in __aexit__
        self._do_exit(exc_type)
    _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
    
    self = <asgiref.timeout.timeout object at 0x7f91fa011850>, exc_type = <class 'asyncio.exceptions.CancelledError'>
    
        def _do_exit(self, exc_type: Type[BaseException]) -> None:
            if exc_type is asyncio.CancelledError and self._cancelled:
                self._cancel_handler = None
                self._task = None
    >           raise asyncio.TimeoutError
    E           TimeoutError
    
    /usr/local/lib/python3.11/site-packages/asgiref/timeout.py:108: TimeoutError
                                                                                                                                                                                                              100% ██████████
    ================================================================================================ short test summary info ================================================================================================
    FAILED example_app/tests/test_reproduce.py::TestChatCommunicator::test_reproduce_exception - TimeoutError
    FAILED example_app/tests/test_reproduce.py::TestChatCommunicator::test_reproduce_ok - TimeoutError
    
    Results (2.26s):
           2 error
    ```
</details>

If you comment out `connect` and `disconnect` methods in `example_app/consumers.py`, the tests start to work again.
