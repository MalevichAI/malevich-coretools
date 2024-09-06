from enum import IntEnum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel

from malevich_coretools.abstract.abstract import (  # noqa: F401
    AdminRunInfo,
    Alias,
    JsonImage,
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
        assert (self.id is not None) + (self.collectionName is not None) + (self.collectionId is not None) == 1, "one way of constructing the argument must be chosen"


class Argument(BaseArgument):
    group: Optional[List[BaseArgument]] = None          # for constructed dfs, sink
    conditions: Optional[Dict[str, bool]] = None        # valid only for alternative, bindConditionId -> value, must be specified explicitly, then it will be derived from the pipeline structure

    def validation(self) -> None:
        if self.group is not None:
            assert self.id is None and self.collectionName is None and self.collectionId is None, "one way of constructing the argument must be chosen"
            for subarg in self.group:
                subarg.validation()
        else:
            assert (self.id is not None) + (self.collectionName is not None) + (self.collectionId is not None) == 1, "one way of constructing the argument must be chosen"


class AlternativeArgument(BaseArgument):
    group: Optional[List[BaseArgument]] = None          # for constructed dfs, sink
    alternative: Optional[List[Argument]] = None        # if set - should be only one valid argument with conditions

    def validation(self) -> None:
        if self.group is not None:
            assert self.id is None and self.collectionName is None and self.collectionId is None, "one way of constructing the argument must be chosen"
            for subarg in self.group:
                subarg.validation()
        elif self.alternative is not None:
            for alt_arg in self.alternative:
                if alt_arg.group is not None:
                    assert alt_arg.id is None and alt_arg.collectionName is None and alt_arg.collectionId is None, "one way of constructing the argument must be chosen"
                    for subarg in alt_arg.group:
                        subarg.validation()
                else:
                    assert (self.id is not None) + (self.collectionName is not None) + (self.collectionId is not None) == 1, "one way of constructing the argument must be chosen"
        else:
            assert (self.id is not None) + (self.collectionName is not None) + (self.collectionId is not None) == 1, "one way of constructing the argument must be chosen"


class AppEntity(BaseModel):
    cfg: Optional[str] = None                           # local cfg for processor/condition
    arguments: Dict[str, AlternativeArgument] = {}      # TODO or List[Argument]?
    conditions: Optional[Union[Dict[str, bool], List[Dict[str, bool]]]] = None          # condition bindId to it result (list - any variant of them)
    conditionsStructure: Optional[Union[Not, And, Or, InternalNot, InternalAnd, InternalOr, Value]] = None  # set BoolOp, it transform to internal before send

    loopArguments: Optional[Dict[str, AlternativeArgument]] = None  # other calls, TODO or List[Argument]?, problems
    loopConditions: Optional[Union[Dict[str, bool], List[Dict[str, bool]]]] = None          # condition bindId to it result for loop (list - any variant of them)
    loopConditionsStructure: Optional[Union[Not, And, Or, InternalNot, InternalAnd, InternalOr, Value]] = None  # set BoolOp, it transform to internal before send

    image: JsonImage
    platform: str = "base"
    platformSettings: Optional[str] = None

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
    cfg: str
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
