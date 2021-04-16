# The aim is to replace the Quart class exception handling defaults to
# allow for Werkzeug HTTPExceptions to be considered in a special way
# (like the quart HTTPException). In addition a Flask reference is
# created.
from __future__ import annotations

from functools import wraps
from typing import Any, Awaitable, Callable, Optional, Union

from werkzeug.wrappers import Response as WerkzeugResponse

from quart import Response
from quart.app import Quart
from quart.ctx import _request_ctx_stack, RequestContext
from quart.utils import is_coroutine_function

old_full_dispatch_request = Quart.full_dispatch_request


async def new_full_dispatch_request(
    self: Quart, request_context: Optional[RequestContext] = None
) -> Union[Response, WerkzeugResponse]:
    request_ = (request_context or _request_ctx_stack.top).request
    await request_.get_data()
    return await old_full_dispatch_request(self, request_context)


Quart.full_dispatch_request = new_full_dispatch_request  # type: ignore


def new_ensure_async(  # type: ignore
    self, func: Callable[..., Any]
) -> Callable[..., Awaitable[Any]]:
    if is_coroutine_function(func):
        return func
    else:

        @wraps(func)
        async def _wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        _wrapper._quart_async_wrapper = True  # type: ignore
        return _wrapper


Quart.ensure_async = new_ensure_async  # type: ignore

Flask = Quart

__all__ = ("Quart",)
