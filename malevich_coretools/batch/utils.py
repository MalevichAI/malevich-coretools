import re
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

from pydantic import BaseModel, BeforeValidator, GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema
from typing_extensions import Annotated

from malevich_coretools.secondary.config import Config

__all__ = ["DefferOperation", "Batcher", "BatchOperation", "BatchOperations", "BatcherRaiseOption"]


class BatchOperation(BaseModel):
    type: str
    data: Optional[str] = None
    vars: Dict[str, str] = {}
    alias: str
    dependencies: List[str] = []
    stage: int = 0
    placeholders: Dict[str, str] = {}


class BatchOperations(BaseModel):
    data: List[BatchOperation]


#


class BatcherRaiseOption(Enum):
    IGNORE = 0
    DEFFER = 1
    QUICKLY = 2


class DefferOperationInternal(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler: GetCoreSchemaHandler) -> CoreSchema:    # noqa: ANN102
        return core_schema.no_info_after_validator_function(cls, handler(str))

    def __new__(cls, name: str, alias: str = None, result_model: Optional[BaseModel] = None, *, raise_on_error: bool = True) -> None:
        return super().__new__(cls, name)

    def __init__(self, name: str, alias: str = None, result_model: Optional[BaseModel] = None, *, raise_on_error: bool = True) -> None:
        self.__data: Union[BaseModel, str] = name   # self.__data should initialized first - hack
        self.__alias = alias
        self.__result_model = result_model
        self.__raise_on_error = raise_on_error
        self.__set = False
        self.__code: int = None

    def code(self) -> int:
        assert self.__set, "result not set"
        return self.__code

    def __ok(self) -> bool:
        return self.__code < 400

    def ok(self) -> bool:
        assert self.__set, "result not set"
        return self.__ok()

    def __validate(self) -> None:
        assert not self.__raise_on_error or self.__ok(), self.__data

    def __repr__(self) -> str:
        if self.__set:
            self.__validate()
        if isinstance(self.__data, str):
            return self.__data
        return str(self.__data)

    __str__ = __repr__

    def _set(self, res: str, code: int) -> None:
        assert not self.__set, "result already set"
        self.__set = True
        self.__code = code
        if self.__result_model is not None and self.__code < 400:   # ok
            try:
                from malevich_coretools.secondary import model_from_json
                self.__data = model_from_json(res, self.__result_model)
            except BaseException:
                Config.logger.error(f"parse {self.__alias} failed, model={self.__result_model.__name__}")
                self.__data = res
        else:
            self.__data = res

    def get(self) -> Union[BaseModel, str]:
        assert self.__set, "result not set"
        self.__validate()
        return self.__data

    @property
    def alias(self) -> str:
        return self.__alias


DefferOperation = Annotated[
    DefferOperationInternal,
    BeforeValidator(lambda x: str(x)),  # hack
]


class Batcher:
    __placeholder_prefix = "$$MalevichBatchPlaceholder_"
    __placeholder_prefix_re = r"\$\$MalevichBatchPlaceholder_"
    __alias_prefix = "BatchAlias"

    def __init__(self, validate: bool = True, raise_option: BatcherRaiseOption = BatcherRaiseOption.QUICKLY, auth: Optional['AUTH'] = None, conn_url: Optional[str] = None) -> None:   # noqa: F821
        self.__operations: Dict[str, BatchOperation] = {}
        self.__previous_batcher: Batcher = None
        self.__stage = 0
        self.__alias_index = 0
        self.__alias_to_operation = {}
        self.__placeholder_to_alias = {}
        self.__validate = validate
        self.__raise_option = raise_option
        self.__committed = False

        self.__auth = auth
        self.__conn_url = conn_url

    def __placeholder_and_alias(self) -> Tuple[str, str]:
        placeholder = f"{self.__placeholder_prefix}{self.__alias_index:03d}$$"
        alias = f"{self.__alias_prefix}{self.__alias_index}"
        self.__placeholder_to_alias[placeholder] = alias
        self.__alias_index += 1
        return placeholder, alias

    def __validation(self) -> None:
        pass    # TODO

    def __commit(self) -> None:
        from malevich_coretools.funcs.funcs import post_batch

        if len(self.__operations) != 0:
            if self.__validate:
                self.__validation()
            for operation in self.__operations.values():
                operation.dependencies = list(set(operation.dependencies))
            data = BatchOperations(data=self.__operations.values())
            for item in post_batch(data, auth=self.__auth, conn_url=self.__conn_url).data:
                self.__alias_to_operation[item.alias]._set(item.data, item.code)
        self.__committed = True
        if self.__raise_option == BatcherRaiseOption.QUICKLY:
            for operation in self.__alias_to_operation.values():
                assert operation.ok(), operation.get()

    def commit(self) -> None:
        assert not self.__committed, "already committed"
        self.__commit()

    def __enter__(self) -> 'Batcher':
        self.__previous_batcher, Config.BATCHER = Config.BATCHER, self
        return self

    def __exit__(self, type, value, traceback) -> bool:
        Config.BATCHER = self.__previous_batcher
        assert not self.__committed, "already committed"

        if type is not None or value is not None or traceback is not None:
            return False

        self.__commit()
        return True

    def add(self, type: str, *, data: Optional[BaseModel] = None, vars: Dict[str, Any] = {}, result_model: Optional[BaseModel] = None) -> DefferOperation:
        placeholder, alias = self.__placeholder_and_alias()
        deffer_operation = DefferOperation(placeholder, alias, result_model, raise_on_error=self.__raise_option == BatcherRaiseOption.DEFFER)
        self.__alias_to_operation[alias] = deffer_operation

        fixed_vars = {}
        placeholders = {}
        dependencies = []
        search_values = []

        if data is not None:
            if isinstance(data, BaseModel):
                data = data.model_dump_json()
                search_values.append(data)
            elif isinstance(data, bytes):
                data = data.decode(encoding='utf-8')    # FIXME
            else:
                raise RuntimeError(f"wrong data type: {data}")
        for k, v in vars.items():
            str_v = str(v)
            fixed_vars[k] = str_v
            search_values.append(str_v)

        for value in search_values:
            for m in re.finditer(self.__placeholder_prefix_re, value):
                potential_placeholder = value[m.start():m.end() + 5]
                dep_alias = self.__placeholder_to_alias.get(potential_placeholder, None)
                if dep_alias is not None:
                    dependencies.append(dep_alias)
                    placeholders[potential_placeholder] = dep_alias

        operation = BatchOperation(
            type=type,
            data=data,
            vars=fixed_vars,
            alias=alias,
            dependencies=dependencies,
            stage=self.__stage,
            placeholders=placeholders,
        )
        self.__operations[alias] = operation

        return deffer_operation

    def barrier(self) -> None:
        self.__stage += 1

    def dependency(self, op: DefferOperation, dep_op: DefferOperation) -> None:
        operation = self.__operations.get(op.alias, None)
        assert operation is not None, f"wrong op: {op}"
        operation.dependencies.append(dep_op.alias)
