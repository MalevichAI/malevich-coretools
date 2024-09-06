from abc import ABC, abstractmethod
from typing import Optional, Union

from pydantic import BaseModel


class InternalBoolOp(ABC, BaseModel):
    pass

    @abstractmethod
    def simplify(self) -> 'BoolOp':
        pass


class BoolOp(ABC, BaseModel):
    pass

    @abstractmethod
    def internal(self) -> InternalBoolOp:
        pass


class Value(BaseModel):
    bindId: str
    result: bool


class BoolOpOrValue(BaseModel):
    # set only one of them
    op: Optional[Union['InternalNot', 'InternalAnd', 'InternalOr']] = None
    value: Optional[Value] = None


class InternalNot(InternalBoolOp):
    notOp: BoolOpOrValue

    def simplify(self) -> 'BoolOp':
        return Not(op=value if (value := self.notOp.value) is not None else self.notOp.op.simplify())


class Not(BoolOp):
    op: Union[BoolOp, Value]

    def internal(self) -> InternalBoolOp:
        if isinstance(self.op, BoolOp):
            internal_op = BoolOpOrValue(op=self.op.internal())
        else:
            internal_op = BoolOpOrValue(value=self.op)
        return InternalNot(notOp=internal_op)


class InternalAnd(InternalBoolOp):
    andOp: BoolOpOrValue
    andOp2: BoolOpOrValue

    def simplify(self) -> 'BoolOp':
        return And(
            op=value if (value := self.andOp.value) is not None else self.andOp.op.simplify(),
            op2=value if (value := self.andOp2.value) is not None else self.andOp2.op.simplify()
        )


class And(BoolOp):
    op: Union[BoolOp, Value]
    op2: Union[BoolOp, Value]

    def internal(self) -> InternalBoolOp:
        if isinstance(self.op, BoolOp):
            internal_op = BoolOpOrValue(op=self.op.internal())
        else:
            internal_op = BoolOpOrValue(value=self.op)

        if isinstance(self.op2, BoolOp):
            internal_op2 = BoolOpOrValue(op=self.op2.internal())
        else:
            internal_op2 = BoolOpOrValue(value=self.op2)
        return InternalAnd(andOp=internal_op, andOp2=internal_op2)


class InternalOr(InternalBoolOp):
    orOp: BoolOpOrValue
    orOp2: BoolOpOrValue

    def simplify(self) -> 'BoolOp':
        return Or(
            op=value if (value := self.orOp.value) is not None else self.orOp.op.simplify(),
            op2=value if (value := self.orOp2.value) is not None else self.orOp2.op.simplify()
        )


class Or(BoolOp):
    op: Union[BoolOp, Value]
    op2: Union[BoolOp, Value]

    def internal(self) -> InternalBoolOp:
        if isinstance(self.op, BoolOp):
            internal_op = BoolOpOrValue(op=self.op.internal())
        else:
            internal_op = BoolOpOrValue(value=self.op)

        if isinstance(self.op2, BoolOp):
            internal_op2 = BoolOpOrValue(op=self.op2.internal())
        else:
            internal_op2 = BoolOpOrValue(value=self.op2)
        return InternalOr(orOp=internal_op, orOp2=internal_op2)


def operations_test() -> None:
    op = And(op=Or(op=Not(op=Value(bindId="cond", result=True)), op2=Value(bindId="cond2", result=False)), op2=Value(bindId="proc"))
    assert op == op.internal().simplify(), "fail: operations"
