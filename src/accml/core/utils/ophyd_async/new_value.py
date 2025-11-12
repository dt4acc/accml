from ophyd_async.core import SignalR, observe_value


async def aenumerate(aiterable):
    """async version of enumerate

    To be replaced by standard version as soon as available
    """
    cnt = 0
    async for item in aiterable:
        yield cnt, item
        cnt += 1


async def wait_for_new_value(signal: SignalR, timeout=None):
    """ensure that new data arrived

    It is a bit hacky: first value is ignored as this is the one
    to be assumed to be in the cache.

    Need something like SubscriptionStatus(sig, cb, run=False)
    """
    async for cnt, _ in aenumerate(observe_value(signal, timeout=timeout)):
        if cnt >= 1:
            return
