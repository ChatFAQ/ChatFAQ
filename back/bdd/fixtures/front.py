"""Fixtures related to the front end we're testing on"""

import fcntl
import os
import select
import subprocess
import time
from logging import getLogger
from pathlib import Path
from typing import List

import httpx
import pytest
from django.conf import settings
from playwright.sync_api import ConsoleMessage, Page, Request

from . import utils

logger = getLogger(__name__)


@pytest.fixture(autouse=True)
def console(page: Page) -> List[ConsoleMessage]:
    """
    Captures the messages from the browser console and returns them as a list

    To use, simply add `console` as an argument to your test function
    Example:
    ```
    def test_something(console):
        assert any("Hello world!" in msg.text for msg in console)
        assert any("error" == msg.type for msg in console)
    ```
    """

    logs: List[ConsoleMessage] = []

    def capture_log(msg: ConsoleMessage):
        logs.append(msg)

    page.on("console", capture_log)

    return logs


@pytest.fixture(autouse=True)
def network_requests(page: Page) -> List[Request]:
    """
    Captures the network requests made by the browser and returns them in a list

    To use, simply add `network_requests` as an argument to your test function
    Example:
    ```
    def test_something(network_requests):
        assert any("example.com" in request.url for request in network_requests)
    ```
    """

    requests: List[Request] = []

    def capture_request(request: Request):
        requests.append(request)

    page.on("request", capture_request)

    return requests


@pytest.fixture(scope="session")
def front_dir() -> Path:
    """Location of the front-end source code"""

    return settings.BASE_DIR / ".." / "front"


@pytest.fixture(scope="session")
def front_env(live_server):
    """
    Environment variables to be injected into the front
    """
    target_url = httpx.URL(live_server.url)

    return dict(
        NUXT_API_URL=str(target_url),
        NUXT_PROXY_OPTIONS_TARGET=str(target_url),
        PUBLIC_SENTRY_ENVIRONMENT="pytest",
        HOST="localhost",
        PORT="3001",
    )


@pytest.fixture(scope="session")
def front_build(front_dir: Path, front_env) -> None:
    """
    Builds the front-end

    Note: As sometimes you want a test to run quickly without the build
          rather long stage, you can set the environment variable SKIPBUILD=1
    """

    if os.environ.get("SKIPBUILD", "0") != "1":
        logger.info("Running npm run build")
        subprocess.run(
            ["npm", "run", "build"],
            cwd=front_dir,
            check=True,
            env={**os.environ, **front_env},
        )
    else:
        logger.info("Not running npm run build")


@pytest.fixture(scope="session")
def front_server(front_build: None, front_dir: Path, front_env):
    """Starts the front-end until the fixture isn't required any more.
    The returned value is the base URL of that running front-end.
    """
    with subprocess.Popen(
        ["npm", "run", "preview"],
        cwd=front_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.DEVNULL,
        text=True,
        env={**os.environ, **front_env},
    ) as p:
        for stream in [p.stdout, p.stderr]:
            fd = stream.fileno()
            fl = fcntl.fcntl(fd, fcntl.F_GETFL)
            fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

        server_address = None
        total_timeout = 5
        start_time = time.time()
        output = {"stdout": "", "stderr": ""}

        try:
            while not server_address:
                remaining_time = total_timeout - (time.time() - start_time)

                if remaining_time <= 0:
                    raise TimeoutError(
                        f"Server did not start within the given timeout. "
                        f"Stdout: {output['stdout']} Stderr: {output['stderr']}"
                    )

                ready, _, _ = select.select(
                    [p.stdout, p.stderr], [], [], remaining_time
                )

                for stream in ready:
                    try:
                        line = stream.readline()
                        if stream is p.stdout:
                            output["stdout"] += line
                        else:
                            output["stderr"] += line
                    except IOError:
                        continue

                    if stream is p.stdout and line:
                        if match := utils.get_nuxt_3_server_url(line):
                            server_address = match
                            break
                    elif not line:
                        break

            server_address = utils.strip_ansi(server_address)

            # We force localhost rather than IP, so the cookies work
            if "127.0.0.1" in server_address:
                server_address = server_address.replace("127.0.0.1", "localhost")

            yield server_address

        except Exception as e:
            raise ChildProcessError(
                f"Failed to start the server: {str(e)} "
                f"Stdout: {output['stdout']} Stderr: {output['stderr']}"
            )
        finally:
            utils.kill_child_processes(p.pid)
            p.terminate()
            p.wait()
