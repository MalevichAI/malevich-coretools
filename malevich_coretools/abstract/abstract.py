from typing import Any, Dict, List, Optional, Tuple, Union

from pydantic import BaseModel

from malevich_coretools.batch import (  # noqa: F401
    BatchOperation,
    BatchOperations,
    DefferOperation,
)

DEFAULT_MSG_URL = None

# aliases
class Alias:
    Json = str
    Info = str
    Id = Union[DefferOperation, str]
    Login = str
    Doc = str
    Empty = str

USERNAME = str
PASSWORD = str
AUTH = Tuple[USERNAME, PASSWORD]

# models
class Operation(BaseModel):
    operationId: Alias.Id


class StopOperation(Operation):
    withLogs: bool = False
    infoUrl: Optional[str] = None


class StopOperationMany(BaseModel):
    withLogs: bool = False
    infoUrl: Optional[str] = None


class DocWithName(BaseModel):
    data: Alias.Json
    name: Optional[str] = None


class DocsCollection(BaseModel):
    data: List[Alias.Id]
    name: Optional[str] = None
    metadata: Optional[Alias.Json] = None


class DocsCollectionChange(BaseModel):
    data: List[Alias.Id]


class DocsDataCollection(BaseModel):
    data: List[Alias.Doc]
    name: Optional[str] = None
    metadata: Optional[Alias.Json] = None


class FixScheme(BaseModel):
    schemeName: str
    mode: str


class SchemeWithName(BaseModel):
    data: Alias.Json
    name: str


class SchemesFixMapping(BaseModel):
    schemeFromId: Alias.Id
    schemeToId: Alias.Id
    data: Dict[str, str]


class SchemesIds(BaseModel):
    schemeFromId: Alias.Id
    schemeToId: Alias.Id


class Shared(BaseModel):
    userLogins: List[Alias.Login]
    collectionsIds: Optional[List[Alias.Id]] = None
    schemesIds: Optional[List[Alias.Id]] = None
    userAppsIds: Optional[List[Alias.Id]] = None


class SharedWithUsers(BaseModel):
    userLogins: List[Alias.Login]


class User(BaseModel):
    login: Alias.Login
    password: str


class JsonImage(BaseModel):
    ref: str
    user: Optional[str] = None
    token: Optional[str] = None


class UserApp(BaseModel):
    appId: Alias.Id
    inputId: Optional[Alias.Id] = None
    processorId: Alias.Id
    outputId: Optional[Alias.Id] = None
    cfg: Optional[Alias.Json] = None
    image: JsonImage
    platform: str
    platformSettings: Optional[str] = None
    extraCollectionsFrom: Optional[Dict[str, List[Alias.Id]]] = None


class UserTask(BaseModel):
    taskId: Alias.Id
    appId: Optional[Alias.Id] = None
    appsDepends: List[Alias.Id]
    tasksDepends: List[Alias.Id]
    synthetic: bool


class UserCfg(BaseModel):
    cfgId: Alias.Id
    cfg: Alias.Json


class KeysValues(Operation):
    data: Dict[str, str]


class ScaleInfo(BaseModel):
    taskId: Optional[Alias.Id] = None
    appId: Alias.Id
    scale: int


class TaskComponent(BaseModel):
    appControl: Optional[str] = None
    control: Optional[str] = None
    extra: Optional[str] = None
    internal: Optional[str] = None
    keyValue: Optional[str] = None
    minimal: Optional[str] = None
    objectStorage: Optional[str] = None


class TaskPolicy(BaseModel):
    lazyAppInit: bool = False
    removeAppAfterRun: bool = False
    continueAfterProcessor: bool = False    # continue without run output function (it run separately), app success even if output fail


class Schedule(BaseModel):
    delay: int                      # seconds
    startAfter: int = 0             # seconds
    count: Optional[int] = None     # iters


class Schedules(BaseModel):
    data: List[str]


class UnscheduleOperation(BaseModel):
    scheduleId: Alias.Id


class Restrictions(BaseModel):
    honestScale: bool = True
    singlePod: bool = False
    smartAppsReuse: bool = False


class MainTask(BaseModel):
    taskId: Alias.Id
    cfgId: Optional[Alias.Id] = None
    infoUrl: Optional[str] = None
    debugMode: bool = False
    run: bool = True
    coreManage: bool = False
    kafkaMode: bool = False
    singleRequest: bool = False
    kafkaModeUrl: Optional[str] = None
    withListener: bool = False      # use only if kafkaMode = True
    tlWithoutData: Optional[int] = None
    waitRuns: bool = True
    profileMode: Optional[str] = None
    withLogs: bool = False  # use only in prepare
    saveFails: bool = True
    scaleInfo: List[ScaleInfo]
    component: TaskComponent
    policy: TaskPolicy
    schedule: Optional[Schedule] = None
    restrictions: Optional[Restrictions] = Restrictions()


class MainPipeline(BaseModel):
    pipelineId: str
    cfgId: str
    infoUrl: Optional[str] = None
    debugMode: bool = False
    coreManage: bool = False
    kafkaMode: bool = False
    singleRequest: bool = True
    tlWithoutData: Optional[int] = None
    waitRuns: bool = True
    profileMode: Optional[str] = None
    withLogs: bool = False
    component: TaskComponent = TaskComponent()
    policy: TaskPolicy = TaskPolicy()
    schedule: Optional[Schedule] = None
    restrictions: Optional[Restrictions] = Restrictions()
    scaleInfo: List[ScaleInfo] = []
    withListener: bool = False
    kafkaModeUrl: Optional[str] = None
    run: bool = True
    synthetic: bool = False
    saveFails: bool = True


class RunTask(Operation):
    cfgId: Optional[Alias.Id] = None
    infoUrl: Optional[str] = None
    debugMode: Optional[bool] = None
    runId: Alias.Id
    singleRequest: Optional[str] = None
    profileMode: Optional[str] = None
    withLogs: bool = False
    schedule: Optional[Schedule] = None


class AppManage(Operation):
    taskId: Optional[Alias.Id] = None
    appId: Alias.Id
    runId: Alias.Id

# results

class ResultIds(BaseModel):
    ids: List[Alias.Id]


class FilesDirs(BaseModel):
    files: Dict[str, int]
    directories: List[str]


class ResultDoc(BaseModel):
    data: Alias.Json
    name: Alias.Id
    id: Alias.Id


class ResultOwnAndSharedIds(BaseModel):
    ownIds: List[Alias.Id]
    sharedIds: List[Alias.Id]


class IdsMap(BaseModel):
    id: Alias.Id
    realId: Alias.Id


class ResultIdsMap(BaseModel):
    ids: List[IdsMap]


class ResultOwnAndSharedIdsMap(BaseModel):
    ownIds: List[IdsMap]
    sharedIds: List[IdsMap]


class Scheme(BaseModel):
    data: str
    name: str
    id: Alias.Id


class ResultCollection(BaseModel):
    id: Alias.Id
    name: Optional[str] = None
    docs: List[ResultDoc]
    length: int
    scheme: Optional[Scheme] = None
    metadata: Optional[Alias.Json] = None
    fromDocs: bool = False


class ResultCollections(BaseModel):
    data: List[ResultCollection]


class ResultScheme(BaseModel):
    data: Alias.Json
    name: str
    id: Alias.Id


class ResultMapping(BaseModel):
    data: Dict[str, str]
    id: Alias.Id


class ResultLogins(BaseModel):
    logins: List[Alias.Login]


class ResultSharedForLogin(BaseModel):
    collectionsIds: List[Alias.Id]
    schemesIds: List[Alias.Id]
    userAppsIds: List[Alias.Id]


class ResultUserCfg(BaseModel):
    data: Alias.Json
    cfgId: Alias.Id
    id: Alias.Id


# TODO add smth from Cfg
class AppSettings(BaseModel):
    taskId: Optional[Alias.Id] = None
    appId: Alias.Id
    saveCollectionsName: Union[str, List[str]]


class Cfg(BaseModel):
    collections: Dict[Alias.Id, Union[Alias.Id, Dict[str, Any]]] = {}
    different: Dict[Alias.Id, Alias.Id] = {}
    schemes_aliases: Dict[Alias.Id, Alias.Id] = {}
    msg_url: str = DEFAULT_MSG_URL
    init_apps_update: Dict[str, bool] = {}
    app_settings: List[AppSettings] = []
    app_cfg_extension: Dict[str, Alias.Json] = {}   # taskId$appId -> app_cfg json
    email: Optional[str] = None


class Condition(BaseModel):
    jsonCondition: dict[str, str]


class MainTaskCfg(BaseModel):
    operationId: Alias.Id
    taskId: Alias.Id
    apps: Dict[Alias.Id, UserApp]
    tasks: Dict[Alias.Id, UserTask]
    cfg: str
    schemesNames: List[str]
    infoUrl: Optional[str] = None
    debugMode: bool
    login: Optional[Alias.Login] = None
    coreManage: bool
    kafkaMode: bool
    tlWithoutData: Optional[int] = None


class KafkaMsg(BaseModel):
    operationId: Alias.Id
    runId: Alias.Id
    data: Dict[str, Alias.Json]
    metadata: Dict[str, Alias.Json] = {}


class CollectionMetadata(BaseModel):
    data: Optional[Alias.Json] = None


class LogsResult(BaseModel):
    data: str
    logs: Dict[str, str]
    userLogs: Dict[str, str] = {}


class AppLog(BaseModel):
    data: List[LogsResult]


class PipelineRunInfo(BaseModel):
    conditions: Dict[str, Dict[int, bool]]  # condition bindId -> iteration -> value
    fails: Dict[str, List[int]]             # bindId -> fail iterations (1 in common situation)


class AppLogs(BaseModel):
    operationId: Alias.Id
    dagLogs: str = ""
    data: Dict[str, AppLog] = {}
    error: Optional[str] = None
    pipeline: Optional[PipelineRunInfo] = None # only for pipeline


class AppLogsWithResults(AppLogs):
    results: Optional[Dict[str, List[List[Dict[str, Any]]]]] = None


class FlattenAppLogsWithResults(BaseModel):
    operationId: Alias.Id
    logs: str = ""
    error: Optional[str] = None
    results: Optional[Dict[str, List[List[Dict[str, Any]]]]] = None


class LogsTask(BaseModel):
    operationId: Alias.Id
    appId: Optional[Alias.Id] = None
    taskId: Optional[Alias.Id] = None
    runId: Optional[Alias.Id] = None
    force: bool = True


class PostS3Settings(BaseModel):
    isCsv: bool = True
    key: Optional[Alias.Id] = None


class FunctionInfo(BaseModel):
    id: Alias.Id
    name: str
    arguments: List[Tuple[str, Optional[str]]]
    finishMsg: Optional[str] = None
    doc: Optional[str] = None


class InputFunctionInfo(FunctionInfo):
    collectionsNames: Optional[List[str]] = None
    extraCollectionsNames: Optional[List[str]] = None
    query: Optional[str] = None
    mode: str


class ProcessorFunctionInfo(FunctionInfo):
    contextClass: Optional[Dict[str, Any]] = None   # model_json_schema


class ConditionFunctionInfo(FunctionInfo):
    contextClass: Optional[Dict[str, Any]] = None   # model_json_schema


class OutputFunctionInfo(FunctionInfo):
    collectionOutNames: Optional[List[str]] = None


class InitInfo(BaseModel):
    id: Alias.Id
    enable: bool
    tl: Optional[int] = None
    prepare: bool
    argname: Optional[str] = None
    doc: Optional[str] = None


class AppFunctionsInfo(BaseModel):
    inputs: Dict[Alias.Id, InputFunctionInfo] = dict()
    processors: Dict[Alias.Id, ProcessorFunctionInfo] = dict()
    conditions: Dict[Alias.Id, ConditionFunctionInfo] = dict()
    outputs: Dict[Alias.Id, OutputFunctionInfo] = dict()
    schemes: Dict[Alias.Id, str] = dict()
    inits: Dict[Alias.Id, InitInfo] = dict()
    logs: Optional[str] = None
    version: Optional[str] = None
    instanceInfo: Optional[str] = None  # json with info about instance


class TaskInfo(BaseModel):
    taskId: Alias.Id
    apps: Dict[Alias.Id, UserApp]
    tasks: Dict[Alias.Id, UserTask]
    cfg: Alias.Json
    login: Alias.Login


class AdminRunInfo(BaseModel):
    operationId: Alias.Id
    taskInfo: TaskInfo
    cfgId: Alias.Id


class OperationOrNone(BaseModel):
    operationId: Optional[Alias.Id] = None


class AdminStopOperation(BaseModel):
    operationId: Optional[Alias.Id] = None
    withLogs: bool


class Superuser(BaseModel):
    login: str
    isSuperuser: bool


class RunSettings(BaseModel):
    callbackUrl: Optional[str] = None
    debugMode: bool = False
    coreManage: bool = False
    singleRequest: bool = True
    waitRuns: bool = True
    profileMode: Optional[str] = None
    scaleInfo: List[ScaleInfo] = []
    component: TaskComponent = TaskComponent()
    policy: TaskPolicy = TaskPolicy()
    restrictions: Optional[Restrictions] = Restrictions()


class Endpoint(BaseModel):
    hash: Optional[Alias.Id] = None
    taskId: Optional[Alias.Id] = None
    pipelineId: Optional[Alias.Id] = None   # should set taskId or pipelineId
    cfgId: Optional[Alias.Id] = None
    sla: Optional[str] = None
    active: Optional[bool] = None
    prepare: Optional[bool] = None
    runSettings: Optional[RunSettings] = None
    enableNotAuthorized: Optional[bool] = None                          # True by default
    expectedCollectionsWithSchemes: Optional[Dict[str, str]] = None     # collection -> scheme
    description: Optional[str] = None


class EndpointRunInfo(BaseModel):
    active: bool
    description: Optional[str] = None
    author: str
    collections: Optional[Dict[str, str]] = None


class Endpoints(BaseModel):
    data: List[Endpoint]


class UserConfig(BaseModel):
    collections: Optional[Dict[Alias.Id, Alias.Id]] = None
    rawCollections: Optional[Dict[Alias.Id, List[Alias.Doc]]] = None
    rawMapCollections: Optional[Dict[Alias.Id, List[Dict[str, Any]]]] = None
    different: Optional[Dict[Alias.Id, Alias.Id]] = None
    schemesAliases: Optional[Dict[str, str]] = None
    msgUrl: Optional[str] = None
    initAppsUpdate: Optional[Dict[str, bool]] = None
    appSettings: Optional[List[AppSettings]] = None
    appCfgExtension: Optional[Dict[str, Alias.Json]] = None
    email: Optional[str] = None


class EndpointOverride(BaseModel):
    cfgId: Optional[Alias.Id] = None
    cfg: Optional[UserConfig] = None
    runSettings: Optional[RunSettings] = None
    overrideConfig: bool = False
    formatLogs: bool = True
    withResult: bool = True


class BatchResponse(BaseModel):
    alias: str
    data: str
    code: int


class BatchResponses(BaseModel):
    data: List[BatchResponse]


class UserLimits(BaseModel):
    # set by superuser
    appMemoryRequest: int       # in Mi
    appMemoryLimit: int         # in Mi
    appCpuRequest: int          # in m
    appCpuLimit: int            # in m
    appStorageRequest: int      # in Mi
    appStorageLimit: int        # in Mi
    assetsLimit: int            # in Mi, if < 0 - unlimited
    allowCommonGpu: int         # ignore if exist access key
    gpuDiskMax: int             # ignore if exist access key

    # set by user
    defaultMemoryRequest: int   # in Mi
    defaultMemoryLimit: int     # in Mi
    defaultCpuRequest: int      # in m
    defaultCpuLimit: int        # in m
    defaultStorageRequest: int  # in Mi
    defaultStorageLimit: int    # in Mi
    defaultGpuDisk: int


class BasePlatformSettings(BaseModel):
    memoryRequest: Optional[int] = None
    memoryLimit: Optional[int] = None
    cpuRequest: Optional[int] = None
    cpuLimit: Optional[int] = None
    storageRequest: Optional[int] = None
    storageLimit: Optional[int] = None


class Limits(BasePlatformSettings):
    gpuDisk: Optional[int] = None


class LimitsScope(BaseModel):   # for superuser/admin
    login: str
    appMemoryRequest: Optional[int] = None
    appMemoryLimit: Optional[int] = None
    appCpuRequest: Optional[int] = None
    appCpuLimit: Optional[int] = None
    appStorageRequest: Optional[int] = None
    appStorageLimit: Optional[int] = None
    assetsLimit: Optional[int] = None
    allowCommonGpu: Optional[bool] = None
    gpuDiskMax: Optional[int] = None


class UserAnalytics(BaseModel):
    name: str
    data: Dict[str, Any]
    timestamp: Optional[str] = None
    id: Optional[str] = None


class UserAnalyticsBatch(BaseModel):
    data: List[UserAnalytics]


class WSApp(BaseModel):
    id: Alias.Id
    secret: str
    active: bool
    dm: str


class WSApps(BaseModel):
    data: List[WSApp]
