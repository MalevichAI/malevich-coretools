from typing import Coroutine, Literal, Union, overload

import malevich_coretools.funcs.funcs as f
from malevich_coretools.abstract import *  # noqa: F403
from malevich_coretools.batch import Batcher
from malevich_coretools.secondary import Config


@overload
def admin_get_runs(
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: Literal[False] = False,
) -> AdminRunsInfo:
    pass


@overload
def admin_get_runs(
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: Literal[True],
) -> Coroutine[Any, Any, AdminRunsInfo]:
    pass


def admin_get_runs(
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Union[AdminRunsInfo, Coroutine[Any, Any, AdminRunsInfo]]:
    """return info about all runs"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getAllRuns", result_model=AdminRunsInfo)
    if is_async:
        return f.get_admin_runs_async(auth=auth, conn_url=conn_url)
    return f.get_admin_runs(auth=auth, conn_url=conn_url)


@overload
def admin_get_run_info(
    id: Alias.Id,
    *,
    dm_id: Optional[str] = None,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: Literal[False] = False,
) -> Alias.Json:
    pass


@overload
def admin_get_run_info(
    id: Alias.Id,
    *,
    dm_id: Optional[str] = None,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: Literal[True],
) -> Coroutine[Any, Any, Alias.Json]:
    pass


def admin_get_run_info(
    id: Alias.Id,
    *,
    dm_id: Optional[str] = None,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Union[Alias.Json, Coroutine[Any, Any, Alias.Json]]:
    """return run info by operation `id`"""
    if batcher is None:
        batcher = Config.BATCHER
    data = AdminRunInfoReq(operationId=id, dmId=dm_id)
    if batcher is not None:
        return batcher.add("getRunInfo", data=data)
    if is_async:
        return f.get_admin_runs_info_async(data, auth=auth, conn_url=conn_url)
    return f.get_admin_runs_info(data, auth=auth, conn_url=conn_url)


@overload
def admin_get_runs_info(
    *,
    dm_id: Optional[str] = None,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: Literal[False] = False,
) -> Alias.Json:
    pass


@overload
def admin_get_runs_info(
    *,
    dm_id: Optional[str] = None,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: Literal[True],
) -> Coroutine[Any, Any, Alias.Json]:
    pass


def admin_get_runs_info(
    *,
    dm_id: Optional[str] = None,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Union[Alias.Json, Coroutine[Any, Any, Alias.Json]]:
    """return json: dm id -> info about its runs"""
    if batcher is None:
        batcher = Config.BATCHER
    data = AdminRunInfoReq(dmId=dm_id)
    if batcher is not None:
        return batcher.add("getRunInfo", data=data)
    if is_async:
        return f.get_admin_runs_info_async(data, auth=auth, conn_url=conn_url)
    return f.get_admin_runs_info(data, auth=auth, conn_url=conn_url)


@overload
def admin_dm_register(
    id: Optional[int] = None,
    url: Optional[str] = None,
    secret: Optional[str] = None,
    app_secret: Optional[str] = None,
    login: Optional[str] = None,
    actuary_dm_id: Optional[int] = None,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: Literal[False] = False,
) -> None:
    pass


@overload
def admin_dm_register(
    id: Optional[int] = None,
    url: Optional[str] = None,
    secret: Optional[str] = None,
    app_secret: Optional[str] = None,
    login: Optional[str] = None,
    actuary_dm_id: Optional[int] = None,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: Literal[True],
) -> Coroutine[Any, Any, None]:
    pass


def admin_dm_register(
    id: Optional[int] = None,
    url: Optional[str] = None,
    secret: Optional[str] = None,
    app_secret: Optional[str] = None,
    login: Optional[str] = None,
    actuary_dm_id: Optional[int] = None,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Union[None, Coroutine[Any, Any, None]]:
    assert id is not None or (url is not None and secret is not None and app_secret is not None and login is not None), "id or url & secret & app_secret & login should set"
    if batcher is None:
        batcher = Config.BATCHER
    data = AdminDMRegister(id=id, url=url, secret=secret, appSecret=app_secret, login=login, actuaryDMId=actuary_dm_id)
    if batcher is not None:
        return batcher.add("postDMRegister", data=data)
    if is_async:
        return f.post_admin_dm_register_async(data, auth=auth, conn_url=conn_url)
    return f.post_admin_dm_register(data, auth=auth, conn_url=conn_url)


@overload
def admin_dm_unregister(
    id: Union[str, int] = 0,
    actuary_dm_id: Optional[int] = None,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: Literal[False] = False,
) -> None:
    pass


@overload
def admin_dm_unregister(
    id: Union[str, int] = 0,
    actuary_dm_id: Optional[int] = None,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: Literal[True],
) -> Coroutine[Any, Any, None]:
    pass


def admin_dm_unregister(
    id: Union[str, int] = 0,    # id or login
    actuary_dm_id: Optional[int] = None,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Union[None, Coroutine[Any, Any, None]]:
    if isinstance(id, int):
        id = f'{id:05d}'
    if batcher is None:
        batcher = Config.BATCHER
    data = AdminDMUnregister(id=id, actuaryDMId=actuary_dm_id)
    if batcher is not None:
        return batcher.add("deleteDMRegister", data=data)
    if is_async:
        return f.delete_admin_dm_register_async(data, auth=auth, conn_url=conn_url)
    return f.delete_admin_dm_register(data, auth=auth, conn_url=conn_url)


@overload
def admin_update_superuser(
    login: str,
    is_superuser: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: Literal[False] = False,
) -> Alias.Info:
    pass


@overload
def admin_update_superuser(
    login: str,
    is_superuser: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: Literal[True],
) -> Coroutine[Any, Any, Alias.Info]:
    pass


def admin_update_superuser(
    login: str,
    is_superuser: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Union[Alias.Info, Coroutine[Any, Any, Alias.Info]]:
    """update user role by login"""
    if batcher is None:
        batcher = Config.BATCHER
    data = Superuser(login=login, isSuperuser=is_superuser)
    if batcher is not None:
        return batcher.add("postUpdateSuperuser", data=data)
    if is_async:
        return f.post_admin_update_superuser_async(data, auth=auth, conn_url=conn_url)
    return f.post_admin_update_superuser(data, auth=auth, conn_url=conn_url)


@overload
def admin_delete_run(
    id: Alias.Id,
    withLogs: bool = False,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: Literal[False] = False,
) -> Alias.Json:
    pass


@overload
def admin_delete_run(
    id: Alias.Id,
    withLogs: bool = False,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: Literal[True],
) -> Coroutine[Any, Any, Alias.Json]:
    pass


def admin_delete_run(
    id: Alias.Id,
    withLogs: bool = False,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Union[Alias.Json, Coroutine[Any, Any, Alias.Json]]:
    """delete run by operation `id`"""
    if batcher is None:
        batcher = Config.BATCHER
    data = AdminStopOperation(operationId=id, withLogs=withLogs)
    if batcher is not None:
        return batcher.add("deleteRuns", data=data)
    if is_async:
        return f.delete_admin_runs_async(data, auth=auth, conn_url=conn_url)
    return f.delete_admin_runs(data, auth=auth, conn_url=conn_url)


@overload
def admin_delete_runs(
    withLogs: bool = False,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: Literal[False] = False,
) -> Alias.Json:
    pass


@overload
def admin_delete_runs(
    withLogs: bool = False,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: Literal[True],
) -> Coroutine[Any, Any, Alias.Json]:
    pass


def admin_delete_runs(
    withLogs: bool = False,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Union[Alias.Json, Coroutine[Any, Any, Alias.Json]]:
    """delete all runs"""
    if batcher is None:
        batcher = Config.BATCHER
    data = AdminStopOperation(withLogs=withLogs)
    if batcher is not None:
        return batcher.add("deleteRuns", data=data)
    if is_async:
        return f.delete_admin_runs_async(data, auth=auth, conn_url=conn_url)
    return f.delete_admin_runs(data, auth=auth, conn_url=conn_url)
