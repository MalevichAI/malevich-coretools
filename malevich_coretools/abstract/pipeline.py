from enum import IntEnum
from typing import Dict, List, Optional

from pydantic import BaseModel

from malevich_coretools.abstract import JsonImage
from malevich_coretools.abstract.abstract import (  # noqa: F401
    Restrictions,
    ScaleInfo,
    TaskComponent,
    TaskPolicy,
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
    conditions: Optional[Dict[str, bool]] = None        # condition bindId to it result

    loopArguments: Optional[Dict[str, AlternativeArgument]] = None  # other calls, TODO or List[Argument]?, problems
    loopConditions: Optional[Dict[str, bool]] = None    # condition bindId to it result for loop

    image: JsonImage
    platform: str = "base"
    platformSettings: Optional[str] = None


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
