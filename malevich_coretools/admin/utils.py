import malevich_coretools.funcs.funcs as f
from malevich_coretools.abstract import *  # noqa: F403
from malevich_coretools.batch import Batcher
from malevich_coretools.secondary import Config


def admin_get_runs(
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
) -> AdminRunsInfo:
    """return info about all runs"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getAllRuns", result_model=AdminRunsInfo)
    return f.get_admin_runs(auth=auth, conn_url=conn_url)


def admin_get_run_info(
    id: Alias.Id,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
) -> Alias.Info:
    """return run info by operation `id`"""
    if batcher is None:
        batcher = Config.BATCHER
    data = OperationOrNone(operationId=id)
    if batcher is not None:
        return batcher.add("getRunInfo", data=data)
    return f.get_admin_runs_info(data, auth=auth, conn_url=conn_url)


def admin_get_runs_info(
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
) -> Alias.Json:
    """return json: dm id -> info about its runs"""
    if batcher is None:
        batcher = Config.BATCHER
    data = OperationOrNone()
    if batcher is not None:
        return batcher.add("getRunInfo", data=data)
    return f.get_admin_runs_info(data, auth=auth, conn_url=conn_url)


def admin_update_superuser(
    login: str,
    is_superuser: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
) -> Alias.Info:
    """update user role by login"""
    if batcher is None:
        batcher = Config.BATCHER
    data = Superuser(login=login, isSuperuser=is_superuser)
    if batcher is not None:
        return batcher.add("postUpdateSuperuser", data=data)
    return f.post_admin_update_superuser(data, auth=auth, conn_url=conn_url)


def admin_delete_run(
    id: Alias.Id,
    withLogs: bool = False,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
) -> Alias.Json:
    """delete run by operation `id`"""
    if batcher is None:
        batcher = Config.BATCHER
    data = AdminStopOperation(operationId=id, withLogs=withLogs)
    if batcher is not None:
        return batcher.add("deleteRuns", data=data)
    return f.delete_admin_runs(data, auth=auth, conn_url=conn_url)


def admin_delete_runs(
    withLogs: bool = False,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
) -> Alias.Json:
    """delete all runs"""
    if batcher is None:
        batcher = Config.BATCHER
    data = AdminStopOperation(withLogs=withLogs)
    if batcher is not None:
        return batcher.add("deleteRuns", data=data)
    return f.delete_admin_runs(data, auth=auth, conn_url=conn_url)
