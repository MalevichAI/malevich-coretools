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
    name: Optional[str]


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
    collectionsIds: Optional[List[Alias.Id]]
    schemesIds: Optional[List[Alias.Id]]
    userAppsIds: Optional[List[Alias.Id]]


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
    extraCollectionsFrom: Optional[Dict[str, Alias.Id]] = None


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
    taskId: Optional[Alias.Id]
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


class MainTask(BaseModel):
    taskId: Alias.Id
    cfgId: Optional[Alias.Id]
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
    scaleInfo: List[ScaleInfo]
    component: TaskComponent
    policy: TaskPolicy
    schedule: Optional[Schedule] = None
    restrictions: Optional[Restrictions] = Restrictions()


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
    taskId: Optional[Alias.Id]
    appId: Alias.Id
    runId: Alias.Id

# results

class ResultIds(BaseModel):
    ids: List[Alias.Id]


class FilesDirs(BaseModel):
    files: List[str]
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
    infoUrl: Optional[str]
    debugMode: bool
    login: Optional[Alias.Login]
    coreManage: bool
    kafkaMode: bool
    tlWithoutData: Optional[int]


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


class AppLogs(BaseModel):
    operationId: Alias.Id
    dagLogs: str = ""
    data: Dict[str, AppLog] = {}
    error: Optional[str] = None


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
    finishMsg: Optional[str]
    doc: Optional[str]


class InputFunctionInfo(FunctionInfo):
    collectionsNames: Optional[List[str]]
    extraCollectionsNames: Optional[List[str]]
    query: Optional[str]
    mode: str


class ProcessorFunctionInfo(FunctionInfo):
    contextClass: Optional[Dict[str, Any]] = None   # model_json_schema


class OutputFunctionInfo(FunctionInfo):
    collectionOutNames: Optional[List[str]]


class InitInfo(BaseModel):
    id: Alias.Id
    enable: bool
    tl: Optional[int]
    prepare: bool
    argname: Optional[str]
    doc: Optional[str]


class AppFunctionsInfo(BaseModel):
    inputs: Dict[Alias.Id, InputFunctionInfo] = dict()
    processors: Dict[Alias.Id, ProcessorFunctionInfo] = dict()
    outputs: Dict[Alias.Id, OutputFunctionInfo] = dict()
    schemes: Dict[Alias.Id, str] = dict()
    inits: Dict[Alias.Id, InitInfo] = dict()
    logs: Optional[str] = None
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


class AdminRunsInfo(BaseModel):
    data: List[AdminRunInfo]


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
    cfgId: Optional[Alias.Id] = None
    sla: Optional[str] = None
    active: Optional[bool] = None
    prepare: Optional[bool] = None
    runSettings: Optional[RunSettings] = None


class EndpointRunInfo(BaseModel):   # TODO improve
    active: bool


class Endpoints(BaseModel):
    data: List[Endpoint]


class UserConfig(BaseModel):
    collections: Dict[Alias.Id, Alias.Id] = {}
    rawCollections: Dict[Alias.Id, List[Alias.Doc]] = {}
    rawMapCollections: Dict[Alias.Id, List[Dict[str, Any]]] = {}
    different: Dict[Alias.Id, Alias.Id] = {}
    schemesAliases: Dict[str, str] = {}
    msgUrl: Optional[str] = None
    initAppsUpdate: Dict[str, bool] = {}
    appSettings: List[AppSettings] = []
    appCfgExtension: Dict[str, Alias.Json] = {}
    email: Optional[str] = None


class EndpointOverride(BaseModel):
    cfgId: Optional[Alias.Id] = None
    cfg: Optional[UserConfig] = None
    runSettings: Optional[RunSettings] = None


class BatchResponse(BaseModel):
    alias: str
    data: str
    code: int


class BatchResponses(BaseModel):
    data: List[BatchResponse]
