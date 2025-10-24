from http import HTTPStatus
from typing import Any, AsyncIterable, Iterable, List, Optional, Union

import aiohttp
import requests
from requests.models import Response

from malevich_coretools.secondary import Config
from malevich_coretools.secondary.const import *  # noqa: F403


def dm_stream(operation_id: str, run_id: str, bind_id: str, conn_url: Optional[str]=None) -> Iterable:
    return send_to_dm_stream(DM_STREAM(operation_id, run_id, bind_id), conn_url=conn_url)


async def dm_stream_async(operation_id: str, run_id: str, bind_id: str, conn_url: Optional[str]=None) -> AsyncIterable:
    return await send_to_dm_stream_async(DM_STREAM(operation_id, run_id, bind_id), conn_url=conn_url)


def dm_continue(operation_id: str, run_id: str, id: str, data: Any, conn_url: Optional[str]=None) -> None:
    return send_to_dm_post(DM_CONTINUE(operation_id, run_id, id), data, conn_url=conn_url)


async def dm_continue_async(operation_id: str, run_id: str, id: str, data: Any, conn_url: Optional[str]=None) -> None:
    return await send_to_dm_post_async(DM_CONTINUE(operation_id, run_id, id), data, conn_url=conn_url)


def dm_state(operation_id: str, run_id: str, bind_id: str, key: Optional[str] = None, index: Optional[int] = None, conn_url: Optional[str]=None) -> Any:
    return send_to_dm_get(DM_STATE(operation_id, run_id, bind_id, key, index), conn_url=conn_url)


async def dm_state_async(operation_id: str, run_id: str, bind_id: str, key: Optional[str] = None, index: Optional[int] = None, conn_url: Optional[str]=None) -> Any:
    return await send_to_dm_get_async(DM_STATE(operation_id, run_id, bind_id, key, index), conn_url=conn_url)


def dm_journal_list(operation_id: str, run_id: str, conn_url: Optional[str]=None) -> List[str]:
    return send_to_dm_get(DM_JOURNAL_LIST(operation_id, run_id), is_text=False, conn_url=conn_url)


async def dm_journal_list_async(operation_id: str, run_id: str, conn_url: Optional[str]=None) -> List[str]:
    return await send_to_dm_get_async(DM_JOURNAL_LIST(operation_id, run_id), is_text=False, conn_url=conn_url)


def dm_journal(operation_id: str, run_id: str, key: str, is_stream: bool, conn_url: Optional[str]=None) -> Union[Any, Iterable]:
    if is_stream:
        return send_to_dm_stream(DM_JOURNAL(operation_id, run_id, key, is_stream), conn_url=conn_url)
    return send_to_dm_get(DM_JOURNAL(operation_id, run_id, key, is_stream), conn_url=conn_url)


async def dm_journal_async(operation_id: str, run_id: str, key: str, is_stream: bool, conn_url: Optional[str]=None) -> Union[Any, AsyncIterable]:
    if is_stream:
        return await send_to_dm_stream_async(DM_JOURNAL(operation_id, run_id, key, is_stream), conn_url=conn_url)
    return await send_to_dm_get_async(DM_JOURNAL(operation_id, run_id, key, is_stream), conn_url=conn_url)


#

def __check_response(path: str, response: Response):  # noqa: ANN202
    if response.status_code >= 400:
        text = response.text
        msg = f"failed: {text}" if len(text) > 0 else "failed"
        Config.logger.error(f"{path} {msg}")

        if response.reason is not None and len(response.reason) == 0:
            response.reason = text
    response.raise_for_status()


async def __async_check_response(response: aiohttp.ClientResponse, path: Optional[str] = None):  # noqa: ANN202
    if not response.ok:
        text = await response.text()
        if path is not None:
            msg = f"failed: {text}" if len(text) > 0 else "failed"
            Config.logger.error(f"{path} {msg}")
        else:
            Config.logger.error(text)

        if response.reason is not None and len(response.reason) == 0:
            response.reason = text
    response.raise_for_status()


def send_to_dm_get(path: str, is_text: bool=True, conn_url: Optional[str]=None) -> Optional[Union[str, bytes]]:
    host = Config.DM_HOST_PORT if conn_url is None else conn_url
    assert host is not None, "dm host port not set"
    response = requests.get(f"{host}{path}", headers=HEADERS)
    __check_response(f"{host}{path}", response)
    if response.status_code == HTTPStatus.NO_CONTENT:
        return None
    if is_text is True:
        return response.text
    elif is_text is False:
        return response.json()
    else:
        return response.content


async def send_to_dm_get_async(path: str, is_text: bool=True, conn_url: Optional[str]=None, async_session = None) -> Optional[Union[str, bytes]]:
    host = Config.DM_HOST_PORT if conn_url is None else conn_url
    assert host is not None, "dm host port not set"
    async with async_session or aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False), timeout=aiohttp.ClientTimeout(total=None)) as session:
        async with session.get(f"{host}{path}", headers=HEADERS) as response:
            await __async_check_response(response, f"{host}{path}")
            if response.status == HTTPStatus.NO_CONTENT:
                return None
            if is_text is True:
                return await response.text()
            elif is_text is False:
                return await response.json()
            else:
                return await response.read()


def send_to_dm_post(path: str, operation: Optional[Any] = None, conn_url: Optional[str]=None) -> Optional[str]:  # noqa: ANN401
    host = Config.DM_HOST_PORT if conn_url is None else conn_url
    assert host is not None, "dm host port not set"
    response = requests.post(f"{host}{path}", data=operation, headers=HEADERS)
    __check_response(f"{host}{path}", response)
    if response.status_code == HTTPStatus.NO_CONTENT:
        return None
    return response.text


async def send_to_dm_post_async(path: str, operation: Optional[Any] = None, conn_url: Optional[str]=None, async_session=None) -> str:  # noqa: ANN401
    host = Config.DM_HOST_PORT if conn_url is None else conn_url
    assert host is not None, "dm host port not set"
    async with async_session or aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False), timeout=aiohttp.ClientTimeout(total=None)) as session:
        async with session.post(f"{host}{path}", data=operation, headers=HEADERS) as response:
            await __async_check_response(response, f"{host}{path}")
            if response.status == HTTPStatus.NO_CONTENT:
                return None
            return response.text()


def send_to_dm_stream(path: str, conn_url: Optional[str]=None) -> Iterable:
    host = Config.DM_HOST_PORT if conn_url is None else conn_url
    assert host is not None, "dm host port not set"

    def stream_generator() -> None:
        with requests.get(f"{host}{path}", headers=HEADERS, stream=True) as response:
            __check_response(f"{host}{path}", response)
            if response.status_code == HTTPStatus.NO_CONTENT:
                return
            for chunk in response.iter_content(chunk_size=4096):
                if chunk:
                    yield chunk.decode("utf-8", errors="ignore")
    return stream_generator()


async def send_to_dm_stream_async(path: str, conn_url: Optional[str]=None, async_session = None) -> AsyncIterable:
    host = Config.DM_HOST_PORT if conn_url is None else conn_url
    assert host is not None, "dm host port not set"

    async def stream_generator() -> None:
        async with async_session or aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False), timeout=aiohttp.ClientTimeout(total=None)) as session:
            async with session.get(f"{host}{path}", headers=HEADERS) as response:
                await __async_check_response(response, f"{host}{path}")
                if response.status == HTTPStatus.NO_CONTENT:
                    return
                async for chunk in response.content.iter_any():
                    yield chunk.decode("utf-8", errors="ignore")
    return stream_generator()
