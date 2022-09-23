from __future__ import annotations

import asyncio
import logging
from contextlib import contextmanager
from typing import Awaitable, Callable, Dict, Generator, List, Optional, Union

import justpy as jp
from starlette.applications import Starlette
from uvicorn import Server

from .config import Config
from .page_builder import PageBuilder
from .task_logger import create_task

app: Starlette
config: Optional[Config] = None
server: Optional[Server] = None
loop: Optional[asyncio.AbstractEventLoop] = None
page_builders: Dict[str, 'PageBuilder'] = {}
view_stack: List[jp.HTMLBaseComponent] = []
tasks: List[asyncio.tasks.Task] = []
log: logging.Logger = logging.getLogger('nicegui')
connect_handlers: List[Union[Callable, Awaitable]] = []
disconnect_handlers: List[Union[Callable, Awaitable]] = []
startup_handlers: List[Union[Callable, Awaitable]] = []
shutdown_handlers: List[Union[Callable, Awaitable]] = []


def find_route(function: Callable) -> str:
    routes = [route for route, page_builder in page_builders.items() if page_builder.function == function]
    if not routes:
        raise ValueError(f'Invalid page function {function}')
    return routes[0]


@contextmanager
def within_view(view: jp.HTMLBaseComponent) -> Generator[None, None, None]:
    child_count = len(view)
    view_stack.append(view)
    yield
    view_stack.pop()
    if len(view) != child_count:
        create_task(view.update())
