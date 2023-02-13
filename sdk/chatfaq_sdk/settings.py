import logging

import coloredlogs


def configure():
    coloredlogs.install(
        level=logging.DEBUG,
        fmt="%(asctime)s %(name)s[%(process)d] %(levelname)s %(message)s",
    )
    logging.basicConfig()
    logging.root.setLevel(logging.DEBUG)
    logging.getLogger("websockets").setLevel(logging.INFO)
    logging.getLogger("asyncio").setLevel(logging.INFO)
