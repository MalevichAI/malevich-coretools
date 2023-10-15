import json
import string
from typing import Union, Callable, Any, Tuple, Dict
from pydantic import BaseModel
import random as rand
from malevich_coretools.abstract.abstract import Alias, AppLogs, LogsResult
from malevich_coretools.secondary import Config

__mini__delimiter = "-" * 25
__delimiter = "-" * 50


def to_json(data: Union[Dict[str, Any], Alias.Json], condition_and_msg: Tuple[Callable[[Dict[str, Any]], bool], str] = (lambda _: True, "")) -> str:
    if isinstance(data, Alias.Json):
        data = json.loads(data)     # json validation
        assert condition_and_msg[0](data), f"wrong data: {condition_and_msg[1]}"
        res = json.dumps(data)
    elif isinstance(data, dict):
        assert condition_and_msg[0](data), f"wrong data: {condition_and_msg[1]}"
        res = json.dumps(data)
    else:
        raise Exception("wrong type")
    return res


def model_from_json(data: Union[Dict[str, Any], Alias.Json], model: BaseModel) -> Any:
    if isinstance(data, Alias.Json):
        data = json.loads(data)
    assert isinstance(data, dict), data
    return model.parse_obj(data)


def rand_str(size: int = 10, chars=string.ascii_letters):
    return ''.join(rand.choice(chars) for _ in range(size))


def bool_to_str(b: bool):
    return "true" if b else "false"


def __show_logs_result(res: LogsResult):
    if len(res.data) > 0:
        print(f"------- main:")
        print(res.data)
    for run_id, logs in res.logs.items():
        print(f"------- {run_id}:")
        print(logs)


def show_logs(app_logs: AppLogs, err: bool = False):
    show = Config.logger.error if err else Config.logger.info
    show(f"operation_id = {app_logs.operationId}")
    if app_logs.error is not None:
        show(f"error: {app_logs.error}")
        print(__delimiter)
    print(f"------- dag logs -------")
    print(app_logs.dagLogs)
    for app_name, app_log in app_logs.data.items():
        print(f"------- {app_name} -------")
        if len(app_log.data) == 1:
            __show_logs_result(app_log.data[0])
        else:
            for i, log_res in enumerate(app_log.data):
                print(f"------- {i}:")
                __show_logs_result(log_res)
                print(__mini__delimiter)
        print(__delimiter)


def show_logs_func(data: str, err: bool = False):
    try:
        app_logs = AppLogs.parse_raw(data)
        show_logs(app_logs, err=err)
    except:
        Config.logger.error("decode logs failed")
        show = Config.logger.error if err else Config.logger.info
        show(data)


def show_fail_app_info(data: str, err: bool):
    assert err == True, "show only for fails"
    try:
        res = json.loads(data)
        assert "result" in res
        print(res["result"])
    except:
        Config.logger.error("decode unsuccessful app_info fail")
        print(data)
