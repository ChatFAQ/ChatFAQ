"""
This file is for utility functions that fixtures may need.
"""

import re
import signal

import psutil


def kill_child_processes(parent_pid, sig=signal.SIGTERM):
    """
    Kill all child processes spawned by the parent process with ID `parent_pid`.
    Nuxt 3 spawns child processes, which aren't terminated when
    the parent process is terminated. This function kills all child processes
    """
    try:
        parent = psutil.Process(parent_pid)
    except psutil.NoSuchProcess:
        return
    children = parent.children(recursive=True)
    for process in children:
        process.send_signal(sig)


def strip_ansi(text: str) -> str:
    """
    Removes ANSI escape sequences from `text`, as defined by ECMA-048 in
    http://www.ecma-international.org/publications/files/ECMA-ST/Ecma-048.pdf

    Incorporated from https://github.com/ewen-lbh/python-strip-ansi/ which hasn't been
    updated since 2020 after it was made.  As it's such a small function, it's not worth
    it's not worth the added dependency to use a package.
    """

    pattern = re.compile(r"\x1B\[\d+(;\d+){0,2}m")
    stripped = pattern.sub("", text)
    return stripped


def get_nuxt_3_server_url(text: str) -> str | None:
    """
    Used for extracting the server address from the output
    of the Nuxt 3 server when it starts up.

    Expected output from Nuxt is:
    `Listening on http://localhost:3000\n`
    """
    if match := re.search(r"Listening on (https?://[^/]+/?)", text):
        return match.group(1).rstrip()


def get_svelte_1_server_url(text: str) -> str | None:
    """
    Used for extracting the server address from the output
    of the Svelte server when it starts up.

    Expected output from Sveltekit is:
    `  ➜  Local:   http://localhost:3000/`
    """
    if match := re.search(r"Local:\W+(https?://[^/]+/)", text):
        return match.group(1).rstrip()
