import malevich_coretools.funcs.funcs as f
from malevich_coretools.abstract import *  # noqa: F403


def admin_get_runs(
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
) -> AdminRunsInfo:
    """return info about all runs"""
    return f.get_admin_runs(auth=auth, conn_url=conn_url)


def admin_get_run_info(
    id: Alias.Id,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
) -> Alias.Info:
    """return run info by operation `id`"""
    data = OperationOrNone(operationId=id)
    return f.get_admin_runs_info(data, auth=auth, conn_url=conn_url)


def admin_get_runs_info(
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
) -> Alias.Json:
    """return json: dm id -> info about its runs"""
    data = OperationOrNone()
    return f.get_admin_runs_info(data, auth=auth, conn_url=conn_url)


def admin_delete_run(
    id: Alias.Id,
    withLogs: bool = False,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
) -> Alias.Json:
    """delete run by operation `id`"""
    data = AdminStopOperation(operationId=id, withLogs=withLogs)
    return f.delete_admin_runs(data, auth=auth, conn_url=conn_url)


def admin_delete_runs(
    withLogs: bool = False,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
) -> Alias.Json:
    """delete all runs"""
    data = AdminStopOperation(withLogs=withLogs)
    return f.delete_admin_runs(data, auth=auth, conn_url=conn_url)
