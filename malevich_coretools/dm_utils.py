from typing import (
    Any,
    AsyncIterable,
    Coroutine,
    Iterable,
    List,
    Literal,
    Optional,
    Union,
    overload,
)

import malevich_coretools.funcs.dm_funcs as f


@overload
def dm_stream(
    operation_id: str,
    run_id: str,
    bind_id: str,
    *,
    conn_url: Optional[str] = None,
    is_async: Literal[False] = False,
) -> Iterable:
    pass


@overload
def dm_stream(
    operation_id: str,
    run_id: str,
    bind_id: str,
    *,
    conn_url: Optional[str] = None,
    is_async: Literal[True],
) -> Coroutine[Any, Any, AsyncIterable]:
    pass


def dm_stream(
    operation_id: str,
    run_id: str,
    bind_id: str,
    *,
    conn_url: Optional[str] = None,
    is_async: bool = False,
) -> Union[Iterable, Coroutine[Any, Any, AsyncIterable]]:
    if is_async:
        return f.dm_stream_async(operation_id, run_id, bind_id, conn_url=conn_url)
    return f.dm_stream(operation_id, run_id, bind_id, conn_url=conn_url)


@overload
def dm_continue(
    operation_id: str,
    run_id: str,
    id: str,
    data: Any,
    *,
    conn_url: Optional[str] = None,
    is_async: Literal[False] = False,
) -> None:
    pass


@overload
def dm_continue(
    operation_id: str,
    run_id: str,
    id: str,
    data: Any,
    *,
    conn_url: Optional[str] = None,
    is_async: Literal[True],
) -> Coroutine[Any, Any, None]:
    pass


def dm_continue(
    operation_id: str,
    run_id: str,
    id: str,
    data: Any,
    *,
    conn_url: Optional[str] = None,
    is_async: bool = False,
) -> Union[None, Coroutine[Any, Any, None]]:
    if is_async:
        return f.dm_continue_async(operation_id, run_id, id, data, conn_url=conn_url)
    return f.dm_continue(operation_id, run_id, id, data, conn_url=conn_url)


@overload
def dm_state(
    operation_id: str,
    run_id: str,
    bind_id: str,
    key: Optional[str] = None,
    index: Optional[int] = None,
    *,
    conn_url: Optional[str] = None,
    is_async: Literal[False] = False,
) -> Any:
    pass


@overload
def dm_state(
    operation_id: str,
    run_id: str,
    bind_id: str,
    key: Optional[str] = None,
    index: Optional[int] = None,
    *,
    conn_url: Optional[str] = None,
    is_async: Literal[True],
) -> Coroutine[Any, Any, Any]:
    pass


def dm_state(
    operation_id: str,
    run_id: str,
    bind_id: str,
    key: Optional[str] = None,
    index: Optional[int] = None,
    *,
    conn_url: Optional[str] = None,
    is_async: bool = False,
) -> Union[Any, Coroutine[Any, Any, Any]]:
    if is_async:
        return f.dm_state_async(operation_id, run_id, bind_id, key, index, conn_url=conn_url)
    return f.dm_state(operation_id, run_id, bind_id, key, index, conn_url=conn_url)


@overload
def dm_journal_list(
    operation_id: str,
    run_id: str,
    *,
    conn_url: Optional[str] = None,
    is_async: Literal[False] = False,
) -> List[str]:
    pass


@overload
def dm_journal_list(
    operation_id: str,
    run_id: str,
    *,
    conn_url: Optional[str] = None,
    is_async: Literal[True],
) -> Coroutine[Any, Any, List[str]]:
    pass


def dm_journal_list(
    operation_id: str,
    run_id: str,
    *,
    conn_url: Optional[str] = None,
    is_async: bool = False,
) -> Union[List[str], Coroutine[Any, Any, List[str]]]:
    if is_async:
        return f.dm_journal_list_async(operation_id, run_id, conn_url=conn_url)
    return f.dm_journal_list(operation_id, run_id, conn_url=conn_url)


@overload
def dm_journal(
    operation_id: str,
    run_id: str,
    key: str,
    is_stream: Literal[False] = False,
    *,
    conn_url: Optional[str] = None,
    is_async: Literal[False] = False,
) -> Any:
    pass


@overload
def dm_journal(
    operation_id: str,
    run_id: str,
    key: str,
    is_stream: Literal[False] = False,
    *,
    conn_url: Optional[str] = None,
    is_async: Literal[True],
) -> Coroutine[Any, Any, Any]:
    pass


@overload
def dm_journal(
    operation_id: str,
    run_id: str,
    key: str,
    is_stream: Literal[True],
    *,
    conn_url: Optional[str] = None,
    is_async: Literal[False] = False,
) -> Iterable:
    pass


@overload
def dm_journal(
    operation_id: str,
    run_id: str,
    key: str,
    is_stream: Literal[True],
    *,
    conn_url: Optional[str] = None,
    is_async: Literal[True],
) -> Coroutine[Any, Any, AsyncIterable]:
    pass


def dm_journal(
    operation_id: str,
    run_id: str,
    key: str,
    is_stream: bool = False,
    *,
    conn_url: Optional[str] = None,
    is_async: bool = False,
) -> Union[Any, Iterable, Coroutine[Any, Any, Union[Any, AsyncIterable]]]:
    if is_async:
        return f.dm_journal_async(operation_id, run_id, key, is_stream, conn_url=conn_url)
    return f.dm_journal(operation_id, run_id, key, is_stream, conn_url=conn_url)
