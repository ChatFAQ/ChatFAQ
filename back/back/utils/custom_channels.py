import asyncio
import functools

from asgiref.sync import async_to_sync
from channels import DEFAULT_CHANNEL_LAYER
from channels.exceptions import StopConsumer
from channels.layers import get_channel_layer


async def concurrent_await_many_dispatch(consumer_callables, dispatch):
    """
    Given a set of consumer callables, awaits on them all and passes results
    from them to the dispatch awaitable as they come in.

    This is a modification of channels/utils.py (await_many_dispatch) just so multiple
    tasks of the same consumer get executed in parallel.
    """
    # Start them all off as tasks
    tasks = [
        asyncio.ensure_future(consumer_callable())
        for consumer_callable in consumer_callables
    ]
    dispatch_tasks = []
    try:
        while True:
            # Wait for any of them to complete
            await asyncio.wait(tasks + dispatch_tasks, return_when=asyncio.FIRST_COMPLETED)
            dispatch_tasks_to_remove = []
            # Find the completed one(s), create dispatch_tasks with results, and replace them
            for i, task in enumerate(tasks + dispatch_tasks):
                if task.done():
                    if task in dispatch_tasks:
                        dispatch_tasks_to_remove.append(task)
                    else:
                        result = task.result()
                        dispatch_tasks.append(asyncio.create_task(dispatch(result)))
                        tasks[i] = asyncio.ensure_future(consumer_callables[i]())
            for task in dispatch_tasks_to_remove:
                if task.exception():
                    raise task.exception()
                dispatch_tasks.remove(task)
    finally:
        # Make sure we clean up tasks on exit
        for task in (*tasks, *dispatch_tasks):
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            except asyncio.TimeoutError:
                print(f"timeout canceling task: {task}")
                pass


class CustomAsyncConsumer:
    """
    Base consumer class. Implements the ASGI application spec, and adds on
    channel layer management and routing of events to named methods based
    on their type.

    This is a modification of channels/consumer.py (AsyncConsumer) to use our custom function
    "concurrent_await_many_dispatch" instead of the original "await_many_dispatch" just so multiple tasks of the same
    consumer get executed in parallel.
    """

    _sync = False
    channel_layer_alias = DEFAULT_CHANNEL_LAYER

    async def __call__(self, scope, receive, send):
        """
        Dispatches incoming messages to type-based handlers asynchronously.
        """
        self.scope = scope

        # Initialize channel layer
        self.channel_layer = get_channel_layer(self.channel_layer_alias)
        if self.channel_layer is not None:
            self.channel_name = await self.channel_layer.new_channel()
            self.channel_receive = functools.partial(
                self.channel_layer.receive, self.channel_name
            )
        # Store send function
        if self._sync:
            self.base_send = async_to_sync(send)
        else:
            self.base_send = send
        # Pass messages in from channel layer or client to dispatch method
        try:
            if self.channel_layer is not None:
                await concurrent_await_many_dispatch(
                    [receive, self.channel_receive], self.dispatch
                )
            else:
                await concurrent_await_many_dispatch([receive], self.dispatch)
        except StopConsumer:
            # Exit cleanly
            pass
