import urllib
from typing import Dict, Optional

import aiohttp

from malevich_coretools.batch import DefferOperationInternal
from malevich_coretools.secondary.helpers import bool_to_str

# const
API_VERSION = "api/v1"
HEADERS = {'Content-type': 'application/json', 'Accept': 'application/json', 'User-Agent': 'malevich user agent'}
HEADERS_RAW = {'Content-type': 'text/plain; base64', 'Accept': 'application/json', 'User-Agent': 'malevich user agent'}
SLEEP_TIME = 0.1
LONG_SLEEP_TIME = 1             # second
WAIT_RESULT_TIMEOUT = 60 * 60   # hour
AIOHTTP_TIMEOUT = aiohttp.ClientTimeout(total=60 * 10) # 10 min
AIOHTTP_TIMEOUT_MINI = aiohttp.ClientTimeout(total=60 * 5) # 5 min
POSSIBLE_APPS_PLATFORMS = {"base", "vast", "ws"}
SCHEME_PATTERN = r"[a-zA-Z_]\w+"

# endpoints
def with_wait(url, wait) -> str:
    return url if wait is None else f"{url}?wait={bool_to_str(wait)}"    # always first

def with_key_values(url: str, key_values: Dict[str, Optional[str]]) -> str:
    sep = "?"
    for key, value in key_values.items():
        if value is not None:
            if isinstance(value, DefferOperationInternal):
                value = urllib.parse.quote(str(value), safe='')
            elif isinstance(value, str):
                value = urllib.parse.quote(value, safe='')
            url = f"{url}{sep}{key}={value}"
            if sep == "?":
                sep = "&"
    return url

## DocsController
DOCS_MAIN = f"{API_VERSION}/docs"
DOCS = lambda wait: with_wait(f"{DOCS_MAIN}/", wait)
DOCS_ID = lambda id, wait: with_wait(f"{DOCS_MAIN}/{id}", wait)
DOCS_NAME = lambda name, wait: with_wait(f"{DOCS_MAIN}/name/{name}", wait)

## CollectionsController
COLLECTIONS_MAIN = f"{API_VERSION}/collections"
COLLECTIONS = lambda wait: with_wait(f"{COLLECTIONS_MAIN}/", wait)
COLLECTIONS_IDS_NAME = lambda name, operation_id, run_id: with_key_values(f"{COLLECTIONS_MAIN}/ids/name/{urllib.parse.quote(str(name), safe='')}", {"operationId": operation_id, "runId": run_id})
COLLECTIONS_NAME = lambda name, operation_id, run_id, offset, limit: with_key_values(f"{COLLECTIONS_MAIN}/name/{urllib.parse.quote(str(name), safe='')}", {"operationId": operation_id, "runId": run_id, "offset": offset, "limit": limit})
COLLECTIONS_IDS_GROUP_NAME = lambda name, operation_id, run_id: with_key_values(f"{COLLECTIONS_MAIN}/ids/groupName/{urllib.parse.quote(str(name), safe='')}", {"operationId": operation_id, "runId": run_id})
COLLECTIONS_GROUP_NAME = lambda name, operation_id, run_id: with_key_values(f"{COLLECTIONS_MAIN}/groupName/{urllib.parse.quote(str(name), safe='')}", {"operationId": operation_id, "runId": run_id})
COLLECTIONS_ID = lambda id, offset, limit: with_key_values(f"{COLLECTIONS_MAIN}/{urllib.parse.quote(str(id), safe='')}", {"offset": offset, "limit": limit})
COLLECTIONS_ID_MODIFY = lambda id, wait: with_wait(f"{COLLECTIONS_MAIN}/{urllib.parse.quote(str(id), safe='')}", wait)
COLLECTIONS_ID_S3 = lambda id, wait: with_wait(f"{COLLECTIONS_MAIN}/s3/{urllib.parse.quote(str(id), safe='')}", wait)
COLLECTIONS_ID_ADD = lambda id, wait: with_wait(f"{COLLECTIONS_MAIN}/{urllib.parse.quote(str(id), safe='')}/add", wait)
COLLECTIONS_ID_COPY = lambda id, full_copy, wait: with_key_values(f"{COLLECTIONS_MAIN}/{urllib.parse.quote(str(id), safe='')}/copy", {"wait": None if wait is None else bool_to_str(wait), "fullCopy": None if full_copy is None else bool_to_str(full_copy)})
COLLECTIONS_ID_DEL = lambda id, wait: with_wait(f"{COLLECTIONS_MAIN}/{urllib.parse.quote(str(id), safe='')}/del", wait)
COLLECTIONS_DATA = lambda wait: with_wait(f"{COLLECTIONS_MAIN}/data", wait)
COLLECTIONS_DATA_ID = lambda id, wait: with_wait(f"{COLLECTIONS_MAIN}/data/{urllib.parse.quote(str(id), safe='')}", wait)
COLLECTIONS_APPLY_SCHEME = lambda id, wait: with_wait(f"{COLLECTIONS_MAIN}/{urllib.parse.quote(str(id), safe='')}/applyScheme", wait)
COLLECTIONS_FIX_SCHEME = lambda id, wait: with_wait(f"{COLLECTIONS_MAIN}/{urllib.parse.quote(str(id), safe='')}/fixScheme", wait)
COLLECTIONS_UNFIX_SCHEME = lambda id, wait: with_wait(f"{COLLECTIONS_MAIN}/{urllib.parse.quote(str(id), safe='')}/unfixScheme", wait)
COLLECTIONS_METADATA = lambda id, wait: with_wait(f"{COLLECTIONS_MAIN}/{urllib.parse.quote(str(id), safe='')}/metadata", wait)

## CollectionObjectsController
COLLECTION_OBJECTS_MAIN = f"{API_VERSION}/collectionObjects"
COLLECTION_OBJECTS_ALL_GET = lambda path, recursive: with_key_values(f"{COLLECTION_OBJECTS_MAIN}/all", {"path": path, "recursive": recursive})
COLLECTION_OBJECTS_ALL = lambda wait: with_wait(f"{COLLECTION_OBJECTS_MAIN}/all", wait)
COLLECTION_OBJECTS_PATH = lambda path, wait, zip: with_key_values(f"{COLLECTION_OBJECTS_MAIN}/", {"path": path, "wait": None if wait is None else bool_to_str(wait), "zip": None if zip is None else bool_to_str(zip)})
COLLECTION_OBJECTS_PRESIGN_PUT = lambda path, callback_url, expires_in, wait: with_key_values(f"{COLLECTION_OBJECTS_MAIN}/presign/put", {"path": path, "callback_url": callback_url, "expiresIn": expires_in, "wait": bool_to_str(wait)})
COLLECTION_OBJECTS_PRESIGN_GET = lambda path, callback_url, expires_in, wait: with_key_values(f"{COLLECTION_OBJECTS_MAIN}/presign/get", {"path": path, "callback_url": callback_url, "expiresIn": expires_in, "wait": bool_to_str(wait)})
COLLECTION_OBJECTS_PRESIGN = lambda signature, zip: with_key_values(f"{COLLECTION_OBJECTS_MAIN}/presign", {"signature": signature, "zip": None if zip is None else bool_to_str(zip)})

## EndpointController
ENDPOINTS_MAIN = f"{API_VERSION}/endpoints"
ENDPOINTS = lambda hash, wait: with_wait(f"{ENDPOINTS_MAIN}/{urllib.parse.quote(str(hash), safe='')}", wait)
ENDPOINTS_ALL = lambda wait: with_wait(f"{ENDPOINTS_MAIN}/all", wait)
ENDPOINTS_RUN = lambda hash: f"{ENDPOINTS_MAIN}/run/{urllib.parse.quote(str(hash), safe='')}"
ENDPOINTS_CREATE = lambda wait: with_wait(f"{ENDPOINTS_MAIN}/create", wait)
ENDPOINTS_UPDATE = lambda wait: with_wait(f"{ENDPOINTS_MAIN}/update", wait)
ENDPOINTS_PAUSE = lambda hash, wait: with_wait(f"{ENDPOINTS_MAIN}/pause/{urllib.parse.quote(str(hash), safe='')}", wait)
ENDPOINTS_RESUME = lambda hash, wait: with_wait(f"{ENDPOINTS_MAIN}/resume/{urllib.parse.quote(str(hash), safe='')}", wait)

## SchemeController
SCHEMES_MAIN = f"{API_VERSION}/schemes"
SCHEMES = lambda wait: with_wait(f"{SCHEMES_MAIN}/", wait)
SCHEMES_ID = lambda id, wait: with_wait(f"{SCHEMES_MAIN}/{urllib.parse.quote(str(id), safe='')}", wait)
SCHEMES_ID_RAW = lambda id: f"{SCHEMES_MAIN}/{urllib.parse.quote(str(id), safe='')}/raw"
SCHEMES_MAPPING = lambda wait: with_wait(f"{SCHEMES_MAIN}/mapping", wait)
SCHEMES_MAPPING_IDS = lambda from_id, to_id: f"{SCHEMES_MAIN}/mapping/{urllib.parse.quote(str(from_id), safe='')}/{urllib.parse.quote(str(to_id), safe='')}"

## CommonController
CHECK = ""
PING = "ping"
# COMMON_MAIN = f"{API_VERSION}/common"
# MAPPING = lambda wait: with_wait(f"{COMMON_MAIN}/mapping", wait)
# MAPPING_ID = lambda id, wait: with_wait(f"{COMMON_MAIN}/mapping/{urllib.parse.quote(str(id), safe='')}", wait)
# COMMON_ALL = lambda wait: with_wait(f"{COMMON_MAIN}/all", wait)

## UserShareController
SHARE_MAIN = f"{API_VERSION}/share"
SHARE = lambda wait: with_wait(f"{SHARE_MAIN}/", wait)
SHARE_COLLECTION_ID = lambda id, wait: with_wait(f"{SHARE_MAIN}/collection/{urllib.parse.quote(str(id), safe='')}", wait)
SHARE_SCHEME_ID = lambda id, wait: with_wait(f"{SHARE_MAIN}/scheme/{urllib.parse.quote(str(id), safe='')}", wait)
SHARE_USER_APP_ID = lambda id, wait: with_wait(f"{SHARE_MAIN}/userApp/{urllib.parse.quote(str(id), safe='')}", wait)
SHARE_LOGIN = lambda login: f"{SHARE_MAIN}/login/{urllib.parse.quote(str(login), safe='')}"
SHARE_ALL = lambda wait: with_wait(f"{SHARE_MAIN}/all", wait)

## RegistrationController
REGISTER_MAIN = f"{API_VERSION}/register"
REGISTER = f"{REGISTER_MAIN}/"
REGISTER_LOGIN = lambda login, wait: with_wait(f"{REGISTER_MAIN}/login/{urllib.parse.quote(str(login), safe='')}", wait)
REGISTER_ALL = f"{REGISTER_MAIN}/all"

## UserAppsController
USER_APPS_MAIN = f"{API_VERSION}/userApps"
USER_APPS = lambda wait: with_wait(f"{USER_APPS_MAIN}/", wait)
USER_APPS_REAL_IDS = f"{USER_APPS_MAIN}/realIds"
USER_APPS_MAP_IDS = f"{USER_APPS_MAIN}/mapIds"
USER_APPS_MAP_ID = lambda id: f"{USER_APPS_MAIN}/mapIds/{urllib.parse.quote(str(id), safe='')}"
USER_APPS_ID = lambda id, wait: with_wait(f"{USER_APPS_MAIN}/{urllib.parse.quote(str(id), safe='')}", wait)
USER_APPS_REAL_ID = lambda id: f"{USER_APPS_MAIN}/realIds/{urllib.parse.quote(str(id), safe='')}"

## UserTasksController
USER_TASKS_MAIN = f"{API_VERSION}/userTasks"
USER_TASKS = lambda wait: with_wait(f"{USER_TASKS_MAIN}/", wait)
USER_TASKS_REAL_IDS = f"{USER_TASKS_MAIN}/realIds"
USER_TASKS_MAP_IDS = f"{USER_TASKS_MAIN}/mapIds"
USER_TASKS_MAP_ID = lambda id: f"{USER_TASKS_MAIN}/mapIds/{urllib.parse.quote(str(id), safe='')}"
USER_TASKS_ID = lambda id, wait: with_wait(f"{USER_TASKS_MAIN}/{urllib.parse.quote(str(id), safe='')}", wait)
USER_TASKS_REAL_ID = lambda id: f"{USER_TASKS_MAIN}/realIds/{urllib.parse.quote(str(id), safe='')}"

## UserPipelinesController
USER_PIPELINES_MAIN = f"{API_VERSION}/userPipelines"
USER_PIPELINES = lambda wait: with_wait(f"{USER_PIPELINES_MAIN}/", wait)
USER_PIPELINES_REAL_IDS = f"{USER_PIPELINES_MAIN}/realIds"
USER_PIPELINES_MAP_IDS = f"{USER_PIPELINES_MAIN}/mapIds"
USER_PIPELINES_MAP_ID = lambda id: f"{USER_PIPELINES_MAIN}/mapIds/{urllib.parse.quote(str(id), safe='')}"
USER_PIPELINES_ID = lambda id, wait: with_wait(f"{USER_PIPELINES_MAIN}/{urllib.parse.quote(str(id), safe='')}", wait)
USER_PIPELINES_REAL_ID = lambda id: f"{USER_PIPELINES_MAIN}/realIds/{urllib.parse.quote(str(id), safe='')}"

## UserCfgsController
USER_CFGS_MAIN = f"{API_VERSION}/userCfgs"
USER_CFGS = lambda wait: with_wait(f"{USER_CFGS_MAIN}/", wait)
USER_CFGS_REAL_IDS = f"{USER_CFGS_MAIN}/realIds"
USER_CFGS_MAP_IDS = f"{USER_CFGS_MAIN}/mapIds"
USER_CFGS_MAP_ID = lambda id: f"{USER_CFGS_MAIN}/mapIds/{urllib.parse.quote(str(id), safe='')}"
USER_CFGS_ID = lambda id, wait: with_wait(f"{USER_CFGS_MAIN}/{urllib.parse.quote(str(id), safe='')}", wait)
USER_CFGS_REAL_ID = lambda id: f"{USER_CFGS_MAIN}/realIds/{urllib.parse.quote(str(id), safe='')}"

## OperationResultsController
OPERATION_RESULTS_MAIN = f"{API_VERSION}/operationResults"
OPERATION_RESULTS = lambda wait: with_wait(f"{OPERATION_RESULTS_MAIN}/", wait)
OPERATION_RESULTS_ID = lambda id, wait: with_wait(f"{OPERATION_RESULTS_MAIN}/{urllib.parse.quote(str(id), safe='')}", wait)

## TempRunController
TEMP_RUN_MAIN = f"{API_VERSION}/run"
TEMP_RUN_CONDITION = lambda operationId: f"{TEMP_RUN_MAIN}/condition/{urllib.parse.quote(str(operationId), safe='')}"
TEMP_RUN_ACTIVE_RUNS = f"{TEMP_RUN_MAIN}/activeRuns"
TEMP_RUN_MAIN_TASK_CFG = lambda operationId: f"{TEMP_RUN_MAIN}/mainTaskCfg/{urllib.parse.quote(str(operationId), safe='')}"
TEMP_RUN_MAIN_PIPELINE_CFG = lambda operationId: f"{TEMP_RUN_MAIN}/mainPipelineCfg/{urllib.parse.quote(str(operationId), safe='')}"
TEMP_RUN_OPERATIONS_IDS = lambda taskId, cfgId: f"{TEMP_RUN_MAIN}/operationsIds/{urllib.parse.quote(str(taskId), safe='')}" if cfgId is None else f"{TEMP_RUN_MAIN}/operationsIds/{urllib.parse.quote(str(taskId), safe='')}/{urllib.parse.quote(str(cfgId), safe='')}"

## AdminController
ADMIN_MAIN = f"{API_VERSION}/admin"
ADMIN_RUNS = f"{ADMIN_MAIN}/runs"
ADMIN_RUNS_INFO = f"{ADMIN_MAIN}/runs/info"
ADMIN_SUPERUSER = f"{ADMIN_MAIN}/superuser"

## ManagerController
MANAGER_MAIN = f"{API_VERSION}/manager"
MANAGER_LOGS = f"{MANAGER_MAIN}/logs"
MANAGER_CLICKHOUSE_ALL = f"{MANAGER_MAIN}/clickhouse"
MANAGER_CLICKHOUSE_ID = lambda operationId: f"{MANAGER_MAIN}/clickhouse/{urllib.parse.quote(str(operationId), safe='')}"
MANAGER_DAG_KEY_VALUE = lambda wait: with_wait(f"{MANAGER_MAIN}/dagKeyValue", wait)
MANAGER_DAG_KEY_VALUE_OPERATION_ID = lambda operationId: f"{MANAGER_MAIN}/dagKeyValue/{urllib.parse.quote(str(operationId), safe='')}"
MANAGER_APP_INFO = lambda appId: f"{MANAGER_MAIN}/appInfo/{urllib.parse.quote(str(appId), safe='')}"
MANAGER_APP_INFO_REAL_ID = lambda appId: f"{MANAGER_MAIN}/appInfo/realId/{urllib.parse.quote(str(appId), safe='')}"
MANAGER_IMAGE_INFO = f"{MANAGER_MAIN}/imageInfo"
MANAGER_TASK_SCHEDULES = f"{MANAGER_MAIN}/task/schedules"
MANAGER_TASK = lambda wait: with_wait(f"{MANAGER_MAIN}/task", wait)
MANAGER_TASK_RUN = lambda wait: with_wait(f"{MANAGER_MAIN}/task/run", wait)
MANAGER_TASK_UNSCHEDULE = lambda wait: with_wait(f"{MANAGER_MAIN}/task/unschedule", wait)
MANAGER_TASK_STOP = lambda wait: with_wait(f"{MANAGER_MAIN}/task/stop", wait)
MANAGER_TASK_STOP_ALL = lambda wait: with_wait(f"{MANAGER_MAIN}/task/stopAll", wait)
MANAGER_TASK_RESUME = lambda wait: with_wait(f"{MANAGER_MAIN}/task/resume", wait)
MANAGER_TASK_PAUSE = lambda wait: with_wait(f"{MANAGER_MAIN}/task/pause", wait)
MANAGER_PIPELINE = lambda wait: with_wait(f"{MANAGER_MAIN}/pipeline", wait)
MANAGER_APP_STOP = lambda wait: with_wait(f"{MANAGER_MAIN}/app/stop", wait)
MANAGER_APP_RESUME = lambda wait: with_wait(f"{MANAGER_MAIN}/app/resume", wait)
MANAGER_APP_PAUSE = lambda wait: with_wait(f"{MANAGER_MAIN}/app/pause", wait)

## LimitsController
LIMITS_MAIN = f"{API_VERSION}/limits"
LIMITS = lambda wait: with_wait(f"{LIMITS_MAIN}/", wait)
LIMITS_USER = lambda wait: with_wait(f"{LIMITS_MAIN}/user", wait)

## HandlerUrlController
HANDLER_URL_MAIN = f"{API_VERSION}/handlerUrls"
HANDLER_URL = lambda url, wait: with_key_values(f"{HANDLER_URL_MAIN}/", {"url": url, "wait": bool_to_str(wait)})

## AnalyticsController
ANALYTICS_MAIN = f"{API_VERSION}/analytics"
ANALYTICS = lambda wait: with_wait(f"{ANALYTICS_MAIN}/", wait)
ANALYTICS_MANY = lambda wait: with_wait(f"{ANALYTICS_MAIN}/many", wait)
ANALYTICS_ID = lambda id, wait: with_wait(f"{ANALYTICS_MAIN}/{id}", wait)
ANALYTICS_NAME = lambda name, wait: with_wait(f"{ANALYTICS_MAIN}/name/{name}", wait)

## RunsInfoController
RUNS_INFO_MAIN = f"{API_VERSION}/runsInfo"
RUNS_INFO_LAST = lambda count: with_key_values(f"{RUNS_INFO_MAIN}/lastOperationsIds", {"count": count})
RUNS_INFO_LAST_FAILED = lambda count: with_key_values(f"{RUNS_INFO_MAIN}/lastFailedOperationsIds", {"count": count})

## WSAppsController
WS_APPS_MAIN = f"{API_VERSION}/ws/apps"
WS_APPS = lambda only_active, full: with_key_values(f"{WS_APPS_MAIN}/", {"onlyActive": only_active, "full": full})
WS_APPS_ = lambda only_not_active, wait: with_key_values(f"{WS_APPS_MAIN}/", {"onlyNotActive": only_not_active, "wait": wait})
WS_APPS_ID = lambda id, wait: with_wait(f"{WS_APPS_MAIN}/{id}", wait)

### Kafka
KAFKA_SEND = f"{MANAGER_MAIN}/kafkaMsg"

## BatchController
BATCH_MAIN = f"{API_VERSION}/batch"
BATCH = f"{BATCH_MAIN}/"
