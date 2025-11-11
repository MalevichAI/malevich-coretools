import json
from enum import IntEnum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel

from malevich_coretools.abstract.abstract import (  # noqa: F401
    AdminRunInfo,
    Alias,
    JsonImage,
    MainTaskCfg,
    Restrictions,
    ScaleInfo,
    Schedule,
    TaskComponent,
    TaskPolicy,
)
from malevich_coretools.abstract.operations import (
    And,
    BoolOp,
    InternalAnd,
    InternalBoolOp,
    InternalNot,
    InternalOr,
    Not,
    Or,
    Value,
)


def _validation_common(arg: 'BaseArgument', other_k = 0) -> None:
    k = (arg.id is not None) + (arg.collectionName is not None) + (arg.collectionId is not None) + other_k
    if k == 0:
        raise ValueError("argument construction requires exactly one parameter, got none")
    if k > 1:
        raise ValueError("argument construction requires exactly one parameter, multiple provided")


class PullCollectionPolicy(IntEnum):
    INIT = 0
    IF_NOT_EXIST = 1
    FORCE_RELOAD = 2
    FORCE_RELOAD_ALL = 3


class BaseArgument(BaseModel):
    id: Optional[str] = None                            # from - bindProcessorId
    indices: Optional[List[int]] = None                 # full if None
    # or
    collectionName: Optional[str] = None                # get id (or obj path) from cfg by it
    # or
    collectionId: Optional[str] = None                  # hardcode collection with id (or obj path)

    def validation(self) -> None:
        _validation_common(self)


class Argument(BaseArgument):
    group: Optional[List[BaseArgument]] = None          # for constructed dfs, sink
    conditions: Optional[Dict[str, bool]] = None        # valid only for alternative, bindConditionId -> value, must be specified explicitly, then it will be derived from the pipeline structure

    def validation(self) -> None:
        if self.group is not None:
            _validation_common(self, 1)
            for subarg in self.group:
                subarg.validation()
        else:
            _validation_common(self)


class AlternativeArgument(BaseArgument):
    group: Optional[List[BaseArgument]] = None          # for constructed dfs, sink
    alternative: Optional[List[Argument]] = None        # if set - should be only one valid argument with conditions

    def validation(self) -> None:
        if self.group is not None:
            _validation_common(self, 1)
            for subarg in self.group:
                subarg.validation()
        elif self.alternative is not None:
            for alt_arg in self.alternative:
                if alt_arg.group is not None:
                    _validation_common(self, 1)
                    for subarg in alt_arg.group:
                        subarg.validation()
                else:
                    _validation_common(self)
        else:
            _validation_common(self)


class AppEntity(BaseModel):
    cfg: Optional[Union[Alias.Json, Dict]] = None       # local cfg for processor/condition
    arguments: Dict[str, AlternativeArgument] = {}      # TODO or List[Argument]?
    conditions: Optional[Union[Dict[str, bool], List[Dict[str, bool]]]] = None          # condition bindId to it result (list - any variant of them)
    conditionsStructure: Optional[Union[Not, And, Or, InternalNot, InternalAnd, InternalOr, Value]] = None  # set BoolOp, it transform to internal before send

    loopArguments: Optional[Dict[str, AlternativeArgument]] = None  # other calls, TODO or List[Argument]?, problems
    loopConditions: Optional[Union[Dict[str, bool], List[Dict[str, bool]]]] = None          # condition bindId to it result for loop (list - any variant of them)
    loopConditionsStructure: Optional[Union[Not, And, Or, InternalNot, InternalAnd, InternalOr, Value]] = None  # set BoolOp, it transform to internal before send

    image: JsonImage
    platform: str = "base"
    platformSettings: Optional[str] = None
    requestedKeys: Optional[list[str]] = None   # user secret keys
    optionalKeys: Optional[list[str]] = None    # user secret keys

    def internal(self) -> None:
        assert self.conditions is None or self.conditionsStructure is None, "should be set not more, than one of (conditions, conditionsStructure)"
        assert self.loopConditions is None or self.loopConditionsStructure is None, "should be set not more, than one of (loopConditions, loopConditionsStructure)"

        if isinstance(self.conditions, Dict):
            self.conditions = [self.conditions]
        if isinstance(self.conditionsStructure, BoolOp):
            self.conditionsStructure = self.conditionsStructure.internal()
        if isinstance(self.loopConditions, Dict):
            self.loopConditions = [self.loopConditions]
        if isinstance(self.loopConditionsStructure, BoolOp):
            self.loopConditionsStructure = self.loopConditionsStructure.internal()
        if isinstance(self.cfg, Dict):
            self.cfg = json.dumps(self.cfg)

    def simplify(self) -> None:
        if isinstance(self.conditionsStructure, InternalBoolOp):
            self.conditionsStructure = self.conditionsStructure.simplify()
        if isinstance(self.loopConditionsStructure, InternalBoolOp):
            self.loopConditionsStructure = self.loopConditionsStructure.simplify()


class Processor(AppEntity):
    processorId: str
    outputId: Optional[str] = None


class Condition(AppEntity):                             # at least one of (true, false) set
    conditionId: str


class Result(BaseModel):                                # save collection (only processor)
    name: str
    index: Optional[int] = None


class Pipeline(BaseModel):
    pipelineId: str
    processors: Dict[str, Processor] = {}               # bindProcessorId to Processor
    conditions: Dict[str, Condition] = {}               # bindConditionId to Condition
    results: Dict[str, List[Result]] = {}               # bindProcessorId to results
    pullCollectionPolicy: PullCollectionPolicy = PullCollectionPolicy.IF_NOT_EXIST

    def internal(self) -> 'Pipeline':
        for proc in self.processors.values():
            proc.internal()
        for cond in self.conditions.values():
            cond.internal()
        return self

    def simplify(self) -> 'Pipeline':
        for proc in self.processors.values():
            proc.simplify()
        for cond in self.conditions.values():
            cond.simplify()
        return self


class MainPipelineCfg(BaseModel):
    operationId: Alias.Id
    pipelineId: Alias.Id
    processors: Dict[str, Processor]
    conditions: Dict[str, Condition]
    results: Dict[str, List[Result]]
    pullCollectionPolicy: PullCollectionPolicy
    cfg: Alias.Json
    infoUrl: Optional[str] = None
    debugMode: bool
    coreManage: bool
    kafkaMode: bool
    singleRequest: bool
    tlWithoutData: Optional[int] = None
    waitRuns: bool
    profileMode: Optional[str] = None
    withLogs: bool
    component: TaskComponent
    policy: TaskPolicy
    schedule: Optional[Schedule] = None
    restrictions: Optional[Restrictions] = None
    scaleInfo: List[ScaleInfo]
    schemesNames: List[str]
    login: Optional[Alias.Login] = None
    withListener: bool
    kafkaModeUrl: Optional[str] = None
    run: bool
    synthetic: bool = False


class PipelineInfo(BaseModel):
    pipelineId: Alias.Id
    processors: Dict[str, Processor]
    conditions: Dict[str, Condition]
    results: Dict[str, List[Result]]
    cfg: Alias.Json
    login: Alias.Login


class AdminRunPipelineInfo(BaseModel):
    operationId: Alias.Id
    pipelineInfo: PipelineInfo
    cfgId: Alias.Id


class AdminRunsInfo(BaseModel):
    tasks: List[AdminRunInfo]
    pipelines: List[AdminRunPipelineInfo]


class TaskRunInfo(BaseModel):
    logs: str
    inputs: Dict[str, Union[str, Dict[str, Any]]]   # collections from cfg
    results: Dict[str, List[str]]                   # name -> collections list (1 collection common)


class RunInfo(BaseModel):
    jsonMainTask: Optional[MainTaskCfg] = None
    jsonMainPipeline: Optional[MainPipelineCfg] = None
    tags: Optional[Dict[str, str]] = None
    cfgId: str
    runs: Dict[str, str] = {}
    info: Dict[str, TaskRunInfo] = {}
    stopped: bool
