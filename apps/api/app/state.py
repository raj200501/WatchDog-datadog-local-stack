from .sse import LogBroadcaster


broadcaster = LogBroadcaster()


def get_broadcaster() -> LogBroadcaster:
    return broadcaster
