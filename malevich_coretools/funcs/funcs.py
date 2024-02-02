import asyncio
import datetime
import json
from asyncio import exceptions
from http import HTTPStatus
from typing import Any, Callable, Optional

import aiohttp
import requests
from requests.models import Response

from malevich_coretools.abstract.abstract import *  # noqa: F403
from malevich_coretools.funcs.checks import check_profile_mode
from malevich_coretools.secondary import Config, model_from_json, show_logs_func
from malevich_coretools.secondary.const import *  # noqa: F403
from malevich_coretools.secondary.helpers import show_fail_app_info

# DocsController


def get_docs(*args, **kwargs) -> ResultIds:
    return model_from_json(send_to_core_get(DOCS(None), *args, **kwargs), ResultIds)


def get_docs_id(id: str, *args, **kwargs) -> ResultDoc:
    return model_from_json(send_to_core_get(DOCS_ID(id, None), *args, **kwargs), ResultDoc)


def post_docs(data: DocWithName, wait: bool, *args, **kwargs) -> Alias.Id:
    return send_to_core_modify(DOCS(wait), data, *args, **kwargs)


def post_docs_id(id: str, data: DocWithName, wait: bool, *args, **kwargs) -> Alias.Id:
    return send_to_core_modify(DOCS_ID(id, wait), data, *args, **kwargs)


def delete_docs_id(id: str, wait: bool, *args, **kwargs) -> Alias.Info:
    return send_to_core_modify(DOCS_ID(id, wait), *args, **kwargs, is_post=False)


def delete_docs(wait: bool, *args, **kwargs) -> Alias.Info:
    return send_to_core_modify(DOCS(wait), *args, **kwargs, is_post=False)

# CollectionsController


def get_collections(*args, **kwargs) -> ResultOwnAndSharedIds:
    return model_from_json(send_to_core_get(COLLECTIONS(None), *args, **kwargs), ResultOwnAndSharedIds)


def get_collections_name(name: str, operation_id: Optional[str], run_id: Optional[str], *args, **kwargs) -> ResultOwnAndSharedIds:
    return model_from_json(send_to_core_get(COLLECTIONS_IDS_NAME(name, operation_id, run_id), *args, **kwargs), ResultOwnAndSharedIds)


def get_collection_name(name: str, operation_id: Optional[str], run_id: Optional[str], offset: int, limit: int, *args, **kwargs) -> ResultCollection:
    return model_from_json(send_to_core_get(COLLECTIONS_NAME(name, operation_id, run_id, offset, limit), *args, **kwargs), ResultCollection)


def get_collections_ids_groupName(name: str, operation_id: str, run_id: str, *args, **kwargs) -> ResultIds:
    return model_from_json(send_to_core_get(COLLECTIONS_IDS_GROUP_NAME(name, operation_id, run_id), *args, **kwargs), ResultIds)


def get_collections_groupName(name: str, operation_id: str, run_id: str, *args, **kwargs) -> ResultCollections:
    return model_from_json(send_to_core_get(COLLECTIONS_GROUP_NAME(name, operation_id, run_id), *args, **kwargs), ResultCollections)


def get_collections_id(id: str, offset: int, limit: int, *args, **kwargs) -> ResultCollection:
    return model_from_json(send_to_core_get(COLLECTIONS_ID(id, offset, limit), *args, **kwargs), ResultCollection)


def post_collections(data: DocsCollection, wait: bool, *args, **kwargs) -> Alias.Id:
    return send_to_core_modify(COLLECTIONS(wait), data, *args, **kwargs)


def post_collections_id(id: str, data: DocsCollection, wait: bool, *args, **kwargs) -> Alias.Id:
    return send_to_core_modify(COLLECTIONS_ID_MODIFY(id, wait), data, *args, **kwargs)


def post_collections_id_s3(id: str, data: PostS3Settings, wait: bool, *args, **kwargs) -> Alias.Info:
    return send_to_core_modify(COLLECTIONS_ID_S3(id, wait), data, *args, **kwargs)


def post_collections_data(data: DocsDataCollection, wait: bool=True, *args, **kwargs) -> Alias.Id:
    return send_to_core_modify(COLLECTIONS_DATA(wait), data, *args, **kwargs)


def post_collections_id_add(id: str, data: DocsCollectionChange, wait: bool, *args, **kwargs) -> Alias.Info:
    return send_to_core_modify(COLLECTIONS_ID_ADD(id, wait), data, *args, **kwargs)


def post_collections_id_copy(id: str, full_copy: bool, wait: bool, *args, **kwargs) -> Alias.Id:
    return send_to_core_modify(COLLECTIONS_ID_COPY(id, full_copy, wait), *args, **kwargs)


def post_collections_id_applyScheme(id: str, data: FixScheme, wait: bool, *args, **kwargs) -> Alias.Id:
    return send_to_core_modify(COLLECTIONS_APPLY_SCHEME(id, wait), data, *args, **kwargs)


def post_collections_id_fixScheme(id: str, data: FixScheme, wait: bool, *args, **kwargs) -> Alias.Info:
    return send_to_core_modify(COLLECTIONS_FIX_SCHEME(id, wait), data, *args, **kwargs)


def post_collections_id_unfixScheme(id: str, wait: bool, *args, **kwargs) -> Alias.Info:
    return send_to_core_modify(COLLECTIONS_UNFIX_SCHEME(id, wait), *args, **kwargs)


def post_collections_metadata(id: str, data: CollectionMetadata, wait: bool, *args, **kwargs) -> Alias.Info:
    return send_to_core_modify(COLLECTIONS_METADATA(id, wait), data, *args, **kwargs)


def delete_collections(wait: bool, *args, **kwargs) -> Alias.Info:
    return send_to_core_modify(COLLECTIONS(wait), *args, **kwargs, is_post=False)


def delete_collections_id(id: str, wait: bool, *args, **kwargs) -> Alias.Info:
    return send_to_core_modify(COLLECTIONS_ID_MODIFY(id, wait), *args, **kwargs, is_post=False)


def delete_collections_id_s3(key: str, wait: bool, *args, **kwargs) -> Alias.Info:
    return send_to_core_modify(COLLECTIONS_ID_S3(key, wait), *args, **kwargs, is_post=False)


def delete_collections_id_del(id: str, data: DocsCollectionChange, wait: bool, *args, **kwargs) -> Alias.Info:
    return send_to_core_modify(COLLECTIONS_ID_DEL(id, wait), data, *args, **kwargs, is_post=False)

# CollectionObjectsController


def get_collection_objects(path: Optional[str], recursive: Optional[str], *args, **kwargs) -> FilesDirs:
    return model_from_json(send_to_core_get(COLLECTION_OBJECTS_ALL_GET(path, recursive), *args, **kwargs), FilesDirs)


def get_collection_object(path: str, *args, **kwargs) -> bytes:
    return send_to_core_get(COLLECTION_OBJECTS_PATH(path, None, None), is_text=None, *args, **kwargs)


def post_collection_object_presigned_url(path: str, callback_url: Optional[str], expires_in: int, wait: bool, *args, **kwargs) -> str:
    return send_to_core_get(COLLECTION_OBJECTS_PRESIGN_PUT(path, callback_url, expires_in, wait), is_text=True, *args, **kwargs)


def get_collection_object_presigned_url(path: str, callback_url: Optional[str], expires_in: int, wait: bool, *args, **kwargs) -> str:
    return send_to_core_get(COLLECTION_OBJECTS_PRESIGN_GET(path, callback_url, expires_in, wait), is_text=True, *args, **kwargs)


def get_collections_object_presigned(signature: str, *args, **kwargs) -> bytes:
    return send_to_core_get(COLLECTION_OBJECTS_PRESIGN(signature, None), is_text=None, *args, **kwargs)


def post_collections_object(path: str, data: bytes, zip: bool, wait: bool, *args, **kwargs) -> Alias.Info:
    return send_to_core_modify_raw(COLLECTION_OBJECTS_PATH(path, wait, zip), data, *args, **kwargs)


def post_collections_object_presigned(signature: str, data: bytes, zip: bool, *args, **kwargs) -> Alias.Info:
    return send_to_core_modify_raw(COLLECTION_OBJECTS_PRESIGN(signature, zip), data, *args, **kwargs)


def delete_collection_objects(wait: bool, *args, **kwargs) -> Alias.Info:
    return send_to_core_modify(COLLECTION_OBJECTS_ALL(wait), *args, **kwargs, is_post=False)


def delete_collection_object(path: str, wait: bool, *args, **kwargs) -> Alias.Info:
    return send_to_core_modify(COLLECTION_OBJECTS_PATH(path, wait, None), *args, **kwargs, is_post=False)


# EndpointController


def get_endpoints(*args, **kwargs) -> Endpoints:
    return model_from_json(send_to_core_get(ENDPOINTS_ALL(None), *args, **kwargs), Endpoints)


def get_endpoint_by_hash(hash: str, *args, **kwargs) -> Endpoint:
    return model_from_json(send_to_core_get(ENDPOINTS(hash, None), *args, **kwargs), Endpoint)


def get_endpoint_run(hash: str, *args, **kwargs) -> Endpoint:
    return model_from_json(send_to_core_get(ENDPOINTS_RUN(hash), *args, **kwargs), EndpointRunInfo)


def run_endpoint(hash: str, data: Optional[EndpointOverride], with_show: bool, *args, **kwargs) -> Union[AppLogs, Any]:
    res = send_to_core_modify(ENDPOINTS_RUN(hash), data, with_show=with_show, show_func=show_logs_func, *args, **kwargs)
    try:
        res = AppLogs.parse_raw(res)
    except BaseException:
        pass
    return res


def create_endpoint(data: Endpoint, wait: bool, *args, **kwargs) -> str:
    return send_to_core_modify(ENDPOINTS_CREATE(wait), data, *args, **kwargs)


def update_endpoint(data: Endpoint, wait: bool, *args, **kwargs) -> str:
    return send_to_core_modify(ENDPOINTS_UPDATE(wait), data, *args, **kwargs)


def pause_endpoint(hash: str, wait: bool, *args, **kwargs) -> Alias.Info:
    return send_to_core_modify(ENDPOINTS_PAUSE(hash, wait), *args, **kwargs)


def resume_endpoint(hash: str, wait: bool, *args, **kwargs) -> Alias.Info:
    return send_to_core_modify(ENDPOINTS_RESUME(hash, wait), *args, **kwargs)


def delete_endpoints(wait: bool, *args, **kwargs) -> Alias.Info:
    return send_to_core_modify(ENDPOINTS_ALL(wait), *args, **kwargs, is_post=False)


def delete_endpoint(hash: str, wait: bool, *args, **kwargs) -> Alias.Info:
    return send_to_core_modify(ENDPOINTS(hash, wait), *args, **kwargs, is_post=False)


# SchemeController


def get_schemes(*args, **kwargs) -> ResultOwnAndSharedIds:
    return model_from_json(send_to_core_get(SCHEMES(None), *args, **kwargs), ResultOwnAndSharedIds)


def get_schemes_id(id: str, *args, **kwargs) -> ResultScheme:
    return model_from_json(send_to_core_get(SCHEMES_ID(id, None), *args, **kwargs), ResultScheme)


def get_schemes_id_raw(id: str, *args, **kwargs) -> Alias.Json:
    return send_to_core_get(SCHEMES_ID_RAW(id), *args, **kwargs)


def get_schemes_mapping(scheme_from_id: str, scheme_to_id: str, *args, **kwargs) -> ResultMapping:
    return model_from_json(send_to_core_get(SCHEMES_MAPPING_IDS(scheme_from_id, scheme_to_id), *args, **kwargs), ResultMapping)


def post_schemes(data: SchemeWithName, wait: bool, *args, **kwargs) -> Alias.Id:
    return send_to_core_modify(SCHEMES(wait), data, *args, **kwargs)


def post_schemes_id(id: str, data: SchemeWithName, wait: bool, *args, **kwargs) -> Alias.Id:
    return send_to_core_modify(SCHEMES_ID(id, wait), data, *args, **kwargs)


def post_schemes_mapping(data: SchemesFixMapping, wait: bool, *args, **kwargs) -> Alias.Id:
    return send_to_core_modify(SCHEMES_MAPPING(wait), data, *args, **kwargs)


def delete_schemes(wait: bool, *args, **kwargs) -> Alias.Info:
    return send_to_core_modify(SCHEMES(wait), *args, **kwargs, is_post=False)


def delete_schemes_id(id: str, wait: bool, *args, **kwargs) -> Alias.Info:
    return send_to_core_modify(SCHEMES_ID(id, wait), *args, **kwargs, is_post=False)


def delete_schemes_mapping(data: SchemesIds, wait: bool, *args, **kwargs) -> Alias.Info:
    return send_to_core_modify(SCHEMES_MAPPING(wait), data, *args, **kwargs, is_post=False)

# CommonController


def get_check_auth(*args, **kwargs) -> Alias.Info:
    return send_to_core_get(CHECK, *args, **kwargs, is_text=True)


def get_ping(*args, **kwargs) -> Alias.Info:
    return send_to_core_get(PING, *args, **kwargs, is_text=True)


# def get_mapping(wait: bool, *args, **kwargs) -> ResultDocMappingsFull:
#     return model_from_json(send_to_core_get(MAPPING, *args, **kwargs), ResultDocMappingsFull)


# def get_mapping_id(id: str, wait: bool, *args, **kwargs) -> ResultMapping:
#     return model_from_json(send_to_core_get(MAPPING_ID(id, None), *args, **kwargs), ResultMapping)


# def post_mapping(data: DocsAndScheme, wait: bool, *args, **kwargs) -> Alias.Info:
#     return send_to_core_modify(MAPPING(wait), data, *args, **kwargs)


# def delete_mapping_id(id: str, wait: bool, *args, **kwargs) -> Alias.Info:
#     return send_to_core_modify(MAPPING_ID(id, wait), *args, **kwargs, is_post=False)


# def delete_all(wait: bool, *args, **kwargs) -> Alias.Info:
#     return send_to_core_modify(COMMON_ALL(wait), *args, **kwargs, is_post=False)

# UserShareController


def get_share_collection_id(id: str, *args, **kwargs) -> ResultLogins:
    return model_from_json(send_to_core_get(SHARE_COLLECTION_ID(id, None), *args, **kwargs), ResultLogins)


def get_share_scheme_id(id: str, *args, **kwargs) -> ResultLogins:
    return model_from_json(send_to_core_get(SHARE_SCHEME_ID(id, None), *args, **kwargs), ResultLogins)


def get_share_userApp_id(id: str, *args, **kwargs) -> ResultLogins:
    return model_from_json(send_to_core_get(SHARE_USER_APP_ID(id, None), *args, **kwargs), ResultLogins)


def get_share_login(login: str, *args, **kwargs) -> ResultSharedForLogin:
    return model_from_json(send_to_core_get(SHARE_LOGIN(login), *args, **kwargs), ResultSharedForLogin)


def post_share_collection_id(id: str, data: SharedWithUsers, wait: bool, *args, **kwargs) -> Alias.Info:
    return send_to_core_modify(SHARE_COLLECTION_ID(id, wait), data, *args, **kwargs)


def post_share_scheme_id(id: str, data: SharedWithUsers, wait: bool, *args, **kwargs) -> Alias.Info:
    return send_to_core_modify(SHARE_SCHEME_ID(id, wait), data, *args, **kwargs)


def post_share_userApp_id(id: str, data: SharedWithUsers, wait: bool, *args, **kwargs) -> Alias.Info:
    return send_to_core_modify(SHARE_USER_APP_ID(id, wait), data, *args, **kwargs)


def post_share(data: Shared, wait: bool, *args, **kwargs) -> Alias.Info:
    return send_to_core_modify(SHARE(wait), data, *args, **kwargs)


def delete_share(data: Shared, wait: bool, *args, **kwargs) -> Alias.Info:
    return send_to_core_modify(SHARE(wait), data, *args, **kwargs, is_post=False)


def delete_share_all(wait: bool, *args, **kwargs) -> Alias.Info:
    return send_to_core_modify(SHARE_ALL(wait), *args, **kwargs, is_post=False)

# RegistrationController


def get_register_login(login: str, *args, **kwargs) -> Alias.Info:
    return send_to_core_get(REGISTER_LOGIN(login, None), is_text=True, *args, **kwargs)


def get_register_all(*args, **kwargs) -> ResultLogins:
    return model_from_json(send_to_core_get(REGISTER_ALL, *args, **kwargs), ResultLogins)


def post_register(data: User, auth: Optional[AUTH]=None, conn_url: Optional[str]=None) -> Alias.Info:
    send_to_core_modify(REGISTER, data, auth=auth, with_auth=True, with_show=False, conn_url=conn_url)
    info = f"user {data.login} created"
    if Config.VERBOSE:
        Config.logger.info(info)
    return info


def delete_register(auth: Optional[AUTH]=None, conn_url: Optional[str]=None, *args, **kwargs) -> Alias.Info:
    send_to_core_modify(REGISTER, *args, **kwargs, auth=auth, with_show=False, is_post=False, conn_url=conn_url)
    login = auth[0] if auth is not None else Config.CORE_USERNAME
    info = f"user {login} removed"
    if Config.VERBOSE:
        Config.logger.info(info)
    return info


def delete_register_login(login: str, wait: bool, *args, **kwargs) -> Alias.Info:
    send_to_core_modify(REGISTER_LOGIN(login, wait), *args, **kwargs, with_show=False, is_post=False)
    info = f"user {login} removed"
    if Config.VERBOSE:
        Config.logger.info(info)
    return info

# UserAppsController


def get_userApps(*args, **kwargs) -> ResultOwnAndSharedIds:
    return model_from_json(send_to_core_get(USER_APPS(None), *args, **kwargs), ResultOwnAndSharedIds)


def get_userApps_realIds(*args, **kwargs) -> ResultOwnAndSharedIds:
    return model_from_json(send_to_core_get(USER_APPS_REAL_IDS, *args, **kwargs), ResultOwnAndSharedIds)


def get_userApps_mapIds(*args, **kwargs) -> ResultOwnAndSharedIdsMap:
    return model_from_json(send_to_core_get(USER_APPS_MAP_IDS, *args, **kwargs), ResultOwnAndSharedIdsMap)


def get_userApps_id(id: str, *args, **kwargs) -> UserApp:
    return model_from_json(send_to_core_get(USER_APPS_ID(id, None), *args, **kwargs), UserApp)


def get_userApps_realId(id: str, *args, **kwargs) -> UserApp:
    return model_from_json(send_to_core_get(USER_APPS_REAL_ID(id), *args, **kwargs), UserApp)


def post_userApps(data: UserApp, wait: bool, *args, **kwargs) -> Alias.Id:
    return send_to_core_modify(USER_APPS(wait), data, *args, **kwargs)


def post_userApps_id(id: str, data: UserApp, wait: bool, *args, **kwargs) -> Alias.Info:
    return send_to_core_modify(USER_APPS_ID(id, wait), data, *args, **kwargs)


def delete_userApps(wait: bool, *args, **kwargs) -> Alias.Info:
    return send_to_core_modify(USER_APPS(wait), *args, **kwargs, is_post=False)


def delete_userApps_id(id: str, wait: bool, *args, **kwargs) -> Alias.Info:
    return send_to_core_modify(USER_APPS_ID(id, wait), *args, **kwargs, is_post=False)

# UserTasksController


def get_userTasks(*args, **kwargs) -> ResultIds:
    return model_from_json(send_to_core_get(USER_TASKS(None), *args, **kwargs), ResultIds)


def get_userTasks_realIds(*args, **kwargs) -> ResultIds:
    return model_from_json(send_to_core_get(USER_TASKS_REAL_IDS, *args, **kwargs), ResultIds)


def get_userTasks_mapIds(*args, **kwargs) -> ResultIdsMap:
    return model_from_json(send_to_core_get(USER_TASKS_MAP_IDS, *args, **kwargs), ResultIdsMap)


def get_userTasks_id(id: str, *args, **kwargs) -> UserTask:
    return model_from_json(send_to_core_get(USER_TASKS_ID(id, None), *args, **kwargs), UserTask)


def get_userTasks_realId(id: str, *args, **kwargs) -> UserTask:
    return model_from_json(send_to_core_get(USER_TASKS_REAL_ID(id), *args, **kwargs), UserTask)


def post_userTasks(data: UserTask, wait: bool, *args, **kwargs) -> Alias.Id:
    return send_to_core_modify(USER_TASKS(wait), data, *args, **kwargs)


def post_userTasks_id(id: str, data: UserTask, wait: bool, *args, **kwargs) -> Alias.Info:
    return send_to_core_modify(USER_TASKS_ID(id, wait), data, *args, **kwargs)


def delete_userTasks(wait: bool, *args, **kwargs) -> Alias.Info:
    return send_to_core_modify(USER_TASKS(wait), *args, **kwargs, is_post=False)


def delete_userTasks_id(id: str, wait: bool, *args, **kwargs) -> Alias.Info:
    return send_to_core_modify(USER_TASKS_ID(id, wait), *args, **kwargs, is_post=False)

# UserCfgsController


def get_userCfgs(*args, **kwargs) -> ResultIds:
    return model_from_json(send_to_core_get(USER_CFGS(None), *args, **kwargs), ResultIds)


def get_userCfgs_realIds(*args, **kwargs) -> ResultIds:
    return model_from_json(send_to_core_get(USER_CFGS_REAL_IDS, *args, **kwargs), ResultIds)


def get_userCfgs_mapIds(*args, **kwargs) -> ResultIdsMap:
    return model_from_json(send_to_core_get(USER_CFGS_MAP_IDS, *args, **kwargs), ResultIdsMap)


def get_userCfgs_id(id: str, *args, **kwargs) -> ResultUserCfg:
    return model_from_json(send_to_core_get(USER_CFGS_ID(id, None), *args, **kwargs), ResultUserCfg)


def get_userCfgs_realId(id: str, *args, **kwargs) -> ResultUserCfg:
    return model_from_json(send_to_core_get(USER_CFGS_REAL_ID(id), *args, **kwargs), ResultUserCfg)


def post_userCfgs(data: UserCfg, wait: bool, *args, **kwargs) -> Alias.Id:
    return send_to_core_modify(USER_CFGS(wait), data, *args, **kwargs)


def post_userCfgs_id(id: str, data: UserCfg, wait: bool, *args, **kwargs) -> Alias.Info:
    return send_to_core_modify(USER_CFGS_ID(id, wait), data, *args, **kwargs)


def delete_userCfgs(wait: bool, *args, **kwargs) -> Alias.Info:
    return send_to_core_modify(USER_CFGS(wait), *args, **kwargs, is_post=False)


def delete_userCfgs_id(id: str, wait: bool, *args, **kwargs) -> Alias.Info:
    return send_to_core_modify(USER_CFGS_ID(id, wait), *args, **kwargs, is_post=False)

# OperationResultsController


def get_operationResults(*args, **kwargs) -> ResultIds:
    return model_from_json(send_to_core_get(OPERATION_RESULTS(None), *args, **kwargs), ResultIds)


def get_operationResults_id(id: str, is_text=True, *args, **kwargs) -> Optional[str]:
    return send_to_core_get(OPERATION_RESULTS_ID(id, None), is_text=is_text, *args, **kwargs)


def delete_operationResults(wait: bool, *args, **kwargs) -> Alias.Info:
    return send_to_core_modify(OPERATION_RESULTS(wait), *args, **kwargs, is_post=False)


def delete_operationResults_id(id: str, wait: bool, *args, **kwargs) -> Alias.Info:
    return send_to_core_modify(OPERATION_RESULTS_ID(id, wait), *args, **kwargs, is_post=False)

# TempRunController


def get_run_condition(id: str, *args, **kwargs) -> Condition:
    return model_from_json(send_to_core_get(TEMP_RUN_CONDITION(id), *args, **kwargs), Condition)


def get_run_activeRuns(*args, **kwargs) -> ResultIds:
    return model_from_json(send_to_core_get(TEMP_RUN_ACTIVE_RUNS, *args, **kwargs), ResultIds)


def get_run_mainTaskCfg(id: str, *args, **kwargs) -> MainTaskCfg:
    return model_from_json(send_to_core_get(TEMP_RUN_MAIN_TASK_CFG(id), *args, **kwargs), MainTaskCfg)


def get_run_operationsIds(task_id: str, cfg_id: Optional[str]=None, *args, **kwargs) -> ResultIds:
    return model_from_json(send_to_core_get(TEMP_RUN_OPERATIONS_IDS(task_id, cfg_id), *args, **kwargs), ResultIds)

# AdminController


def get_admin_runs(*args, **kwargs) -> AdminRunsInfo:
    return model_from_json(send_to_core_get(ADMIN_RUNS, *args, **kwargs), AdminRunsInfo)


def get_admin_runs_info(data: OperationOrNone, *args, **kwargs) -> Union[Alias.Json, Alias.Info]:
    return send_to_core_modify(ADMIN_RUNS_INFO, data, *args, **kwargs)


def post_admin_update_superuser(data: Superuser, *args, **kwargs) -> Alias.Info:
    return send_to_core_modify(ADMIN_SUPERUSER, data, *args, **kwargs)


def delete_admin_runs(data: AdminStopOperation, *args, **kwargs) -> Alias.Json:
    return send_to_core_modify(ADMIN_RUNS, data, is_post=False, *args, **kwargs)

# ManagerController


def get_manager_logs(data: LogsTask, with_show: bool, *args, **kwargs) -> AppLogs:
    return model_from_json(send_to_core_modify(MANAGER_LOGS, data, with_show=with_show, show_func=show_logs_func, *args, **kwargs), AppLogs)


def get_clickhouse_all(*args, **kwargs) -> str:
    return send_to_core_get(MANAGER_CLICKHOUSE_ALL, is_text=True, *args, **kwargs)


def get_clickhouse_id(id: str, *args, **kwargs) -> str:
    return send_to_core_get(MANAGER_CLICKHOUSE_ID(id), is_text=True, *args, **kwargs)


def get_manager_dagKeyValue_operationId(id: str, *args, **kwargs) -> Alias.Json:
    return send_to_core_get(MANAGER_DAG_KEY_VALUE_OPERATION_ID(id), *args, **kwargs)


def post_manager_dagKeyValue(data: KeysValues, wait: bool, *args, **kwargs) -> Alias.Info:
    return send_to_core_modify(MANAGER_DAG_KEY_VALUE(wait), data, *args, **kwargs)


def get_app_info(id: str, parse: bool, *args, **kwargs) -> Union[Alias.Json, AppFunctionsInfo]:
    res = send_to_core_get(MANAGER_APP_INFO(id), show_func = show_fail_app_info, *args, **kwargs)
    if parse:
        res = model_from_json(res, AppFunctionsInfo)
    return res


def get_app_info_by_real_id(id: str, parse: bool, *args, **kwargs) -> Union[Alias.Json, AppFunctionsInfo]:
    res = send_to_core_get(MANAGER_APP_INFO_REAL_ID(id), show_func = show_fail_app_info, *args, **kwargs)
    if parse:
        res = model_from_json(res, AppFunctionsInfo)
    return res


def get_image_info(data: JsonImage, parse: bool, *args, **kwargs) -> Union[Alias.Json, AppFunctionsInfo]:
    res = send_to_core_modify(MANAGER_IMAGE_INFO, data, with_auth=False, with_show=False, show_func = show_fail_app_info, *args, **kwargs)
    if parse:
        res = model_from_json(res, AppFunctionsInfo)
    return res


def get_task_schedules(data: Operation, with_show: bool, *args, **kwargs) -> Schedules:
    res = model_from_json(send_to_core_modify(MANAGER_TASK_SCHEDULES, data, with_show=False, *args, **kwargs), Schedules)
    if with_show:
        Config.logger.info(res)
    return res


def post_manager_task(data: MainTask, with_show: bool, long: bool, long_timeout: int, wait: bool, auth: Optional[AUTH], conn_url: Optional[str]=None, *args, **kwargs) -> Union[Alias.Id, AppLogs]:
    check_profile_mode(data.profileMode)
    res = send_to_core_modify(MANAGER_TASK(wait and not long), data, with_show=with_show, show_func=show_logs_func, auth=auth, conn_url=conn_url, *args, **kwargs)
    if wait and long:
        res = asyncio.run(__get_result(res, timeout=long_timeout, auth=auth))
    if not wait:
        return res
    return AppLogs.parse_raw(res)


def post_manager_task_run(data: RunTask, with_show: bool, long: bool, long_timeout: int, wait: bool, auth: Optional[AUTH], conn_url: Optional[str]=None, *args, **kwargs) -> Optional[Union[Alias.Id, AppLogs]]:
    check_profile_mode(data.profileMode)
    res = send_to_core_modify(MANAGER_TASK_RUN(wait and not long), data, with_show=with_show, show_func=show_logs_func, auth=auth, conn_url=conn_url, *args, **kwargs)
    if wait and long:
        res = asyncio.run(__get_result(res, timeout=long_timeout, auth=auth))
    if data.withLogs or data.schedule is not None:
        if not wait:
            return res
        return AppLogs.parse_raw(res)


def post_manager_task_unschedule(data: UnscheduleOperation, with_show: bool, wait: bool, *args, **kwargs) -> Alias.Info:
    return send_to_core_modify(MANAGER_TASK_UNSCHEDULE(wait), data, with_show=with_show, *args, **kwargs)


def post_manager_task_stop(data: StopOperation, with_show: bool, wait: bool, *args, **kwargs) -> Optional[Union[Alias.Id, AppLogs]]:
    show_func = show_logs_func if data.withLogs else None
    res = send_to_core_modify(MANAGER_TASK_STOP(wait), data, with_show=with_show, show_func=show_func, *args, **kwargs)
    if data.withLogs:
        if not wait:
            return res
        return AppLogs.parse_raw(res)


def post_manager_task_stop_all(data: StopOperationMany, wait: bool, *args, **kwargs) -> Alias.Json: # FIXME show
    return send_to_core_modify(MANAGER_TASK_STOP_ALL(wait), data, *args, **kwargs)


def post_manager_task_resume(data: Operation, wait: bool, *args, **kwargs) -> Alias.Empty:
    return send_to_core_modify(MANAGER_TASK_RESUME(wait), data, *args, **kwargs)


def post_manager_task_pause(data: Operation, wait: bool, *args, **kwargs) -> Alias.Empty:
    return send_to_core_modify(MANAGER_TASK_PAUSE(wait), data, *args, **kwargs)


def post_manager_app_stop(data: AppManage, wait: bool, *args, **kwargs) -> Alias.Empty:
    return send_to_core_modify(MANAGER_APP_STOP(wait), data, *args, **kwargs)


def post_manager_app_resume(data: AppManage, wait: bool, *args, **kwargs) -> Alias.Empty:
    return send_to_core_modify(MANAGER_APP_RESUME(wait), data, *args, **kwargs)


def post_manager_app_pause(data: AppManage, wait: bool, *args, **kwargs) -> Alias.Empty:
    return send_to_core_modify(MANAGER_APP_PAUSE(wait), data, *args, **kwargs)


async def kafka_send(data: KafkaMsg, *args, **kwargs) -> Union[Alias.Info, KafkaMsg]:
    result = await send_to_core_post_async(KAFKA_SEND, data, *args, **kwargs)
    try:
        return KafkaMsg.parse_raw(result)
    except BaseException:
        return result

# BatchController


def post_batch(data: BatchOperations, *args, **kwargs) -> BatchResponses:
    return model_from_json(send_to_core_modify(BATCH, data, *args, **kwargs), BatchResponses)


##################################


async def __get_result(id: str, is_text: bool = True, check_time: float = LONG_SLEEP_TIME, timeout: int = WAIT_RESULT_TIMEOUT, auth: Optional[AUTH]=None, conn_url: Optional[str]=None) -> str:      # FIXME
    host = Config.HOST_PORT if conn_url is None else conn_url
    assert host is not None, "host port not set"
    if auth is None:
        auth = aiohttp.BasicAuth(login=Config.CORE_USERNAME, password=Config.CORE_PASSWORD, encoding='utf-8')

    timeout_deadline = None if timeout is None else datetime.datetime.now() + datetime.timedelta(0, timeout)
    while True:
        try:
            async with aiohttp.ClientSession(auth=auth, connector=aiohttp.TCPConnector(verify_ssl=False), timeout=AIOHTTP_TIMEOUT_MINI) as session:
                while True:
                    async with session.get(f"{host}{OPERATION_RESULTS_ID(id, None)}", headers=HEADERS) as response:
                        if response.ok:
                            if is_text:
                                result = await response.text()
                            else:
                                result = await response.json()
                            return result
                        else:
                            if timeout_deadline is not None:
                                now = datetime.datetime.now()
                                if now >= timeout_deadline:
                                    raise Exception("wait get result timeout")
                            await asyncio.sleep(check_time)
        except exceptions.TimeoutError:
            pass    # recreate ClientSession


async def __async_check_response(response: aiohttp.ClientResponse, show_func: Optional[Callable]=None):  # noqa: ANN202
    if not response.ok:
        if show_func is None:
            Config.logger.error(await response.text())
        else:
            show_func(await response.text(), err=True)
    response.raise_for_status()


def __check_response(path: str, response: Response, show_func: Optional[Callable]=None):  # noqa: ANN202
    if response.status_code >= 400:
        if show_func is None:
            text = response.text
            msg = f"failed: {text}" if len(text) > 0 else "failed"
            Config.logger.error(f"{path} {msg}")
        else:
            Config.logger.error(f"{path} failed")
            show_func(response.text, err=True)
    response.raise_for_status()


def send_to_core_get(path: str, with_auth=True, show_func: Optional[Callable]=None, is_text=False, auth: Optional[AUTH]=None, conn_url: Optional[str]=None) -> Optional[Union[str, bytes]]:
    host = Config.HOST_PORT if conn_url is None else conn_url
    assert host is not None, "host port not set"
    if auth is None or not with_auth:
        auth = (Config.CORE_USERNAME, Config.CORE_PASSWORD) if with_auth else None
    response = requests.get(f"{host}{path}", headers=HEADERS, auth=auth)
    __check_response(f"{host}{path}", response, show_func)
    if response.status_code == HTTPStatus.NO_CONTENT:
        return None
    if is_text is True:
        return response.text
    elif is_text is False:
        return response.json()
    else:
        return response.content


def send_to_core_modify(path: str, operation: Optional[Any] = None, with_auth: bool=True, with_show: Optional[bool]=None, show_func: Optional[Callable]=None, is_post: bool=True, auth: Optional[AUTH]=None, conn_url: Optional[str]=None) -> str:  # noqa: ANN401
    """modify: post by default, else - delete"""
    host = Config.HOST_PORT if conn_url is None else conn_url
    assert host is not None, "host port not set"
    if auth is None:
        auth = (Config.CORE_USERNAME, Config.CORE_PASSWORD)
    if operation is not None:
        operation = json.dumps(operation.model_dump())
    if is_post:
        response = requests.post(f"{host}{path}", data=operation, headers=HEADERS, auth=auth if with_auth else None)
    else:   # delete
        response = requests.delete(f"{host}{path}", data=operation, headers=HEADERS, auth=auth if with_auth else None)
    __check_response(f"{host}{path}", response, show_func=show_func)
    if response.status_code == HTTPStatus.NO_CONTENT:
        return ""
    result = response.text
    if with_show is None:
        with_show = Config.VERBOSE
    if with_show:
        if show_func is None:
            Config.logger.info(result)
        else:
            show_func(result)
    return result


def send_to_core_modify_raw(path: str, data: bytes, with_auth: bool=True, with_show: Optional[bool]=None, show_func: Optional[Callable]=None, is_post: bool=True, auth: Optional[AUTH]=None, conn_url: Optional[str]=None) -> str:  # noqa: ANN401
    """modify: post by default, else - delete"""
    host = Config.HOST_PORT if conn_url is None else conn_url
    assert host is not None, "host port not set"
    if auth is None:
        auth = (Config.CORE_USERNAME, Config.CORE_PASSWORD)
    if is_post:
        response = requests.post(f"{host}{path}", data=data, headers=HEADERS_RAW, auth=auth if with_auth else None)
    else:   # delete
        response = requests.delete(f"{host}{path}", data=data, headers=HEADERS_RAW, auth=auth if with_auth else None)
    __check_response(f"{host}{path}", response, show_func=show_func)
    if response.status_code == HTTPStatus.NO_CONTENT:
        return ""
    result = response.text
    if with_show is None:
        with_show = Config.VERBOSE
    if with_show:
        if show_func is None:
            Config.logger.info(result)
        else:
            show_func(result)
    return result


async def send_to_core_post_async(path: str, operation: Optional[str] = None, with_auth=True, with_show=True, show_func: Optional[Callable]=None, auth: Optional[AUTH]=None, conn_url: Optional[str]=None) -> str:
    host = Config.HOST_PORT if conn_url is None else conn_url
    assert host is not None, "host port not set"
    if auth is None or not with_auth:
        auth = aiohttp.BasicAuth(login=Config.CORE_USERNAME, password=Config.CORE_PASSWORD, encoding='utf-8') if with_auth else None
    if operation is not None:
        operation = json.dumps(operation.model_dump())

    async with aiohttp.ClientSession(auth=auth, connector=aiohttp.TCPConnector(verify_ssl=False), timeout=AIOHTTP_TIMEOUT) as session:
        async with session.post(f"{host}{path}", data=operation, headers=HEADERS) as response:
            await __async_check_response(response, show_func=show_func)
            result = await response.text()
    if with_show:
        if show_func is None:
            Config.logger.info(result)
        else:
            show_func(result)
    return result
