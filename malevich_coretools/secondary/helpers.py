import json
import random as rand
import string
from typing import Any, Callable, Dict, Optional, Tuple, Union

from pydantic import BaseModel

from malevich_coretools.abstract.abstract import (
    Alias,
    AppLog,
    AppLogs,
    FlattenAppLogsWithResults,
    LogsResult,
)
from malevich_coretools.secondary import Config
from malevich_coretools.secondary.kafka_utils import handle_logs

__all__ = ["to_json", "model_from_json", "rand_str", "bool_to_str", "show_logs", "show_logs_colored", "show_logs_func", "show_fail_app_info", "logs_streaming"]

__mini__delimiter = "-" * 25
__delimiter = "-" * 50
__colors = [f"\x1b[{i};20m" for i in range(31, 38)]
__color_reset = "\x1b[0m"


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


def model_from_json(data: Union[Dict[str, Any], Alias.Json], model: BaseModel, is_list: Optional[bool] = False):  # noqa: ANN201
    if isinstance(data, Alias.Json):
        data = json.loads(data)
    if is_list is None:
        is_list = isinstance(data, list)
    if is_list:
        assert isinstance(data, list), data
        return [model.model_validate(item) for item in data]
    else:
        assert isinstance(data, dict), data
        return model.model_validate(data)


def rand_str(size: int = 10, chars=string.ascii_letters) -> str:
    return ''.join(rand.choice(chars) for _ in range(size))


def bool_to_str(b: bool) -> str:
    return "true" if b else "false"


def __show_logs_result(res: LogsResult, i: Optional[int] = None):  # noqa: ANN202
    if len(res.data) > 0:
        print(f"------- main ({i}):" if i is not None else "------- main:")
        print(res.data)
    if res.logs is None:
        res.logs = {}
    if res.userLogs is None:
        res.userLogs = {}
    for run_id, logs in res.logs.items():
        userLogs = res.userLogs.get(run_id, "")
        print(f"------- {run_id} ({i}):" if i is not None else f"------- {run_id}:")
        if len(logs) == 0:
            print(userLogs)
        else:
            if len(userLogs) > 0:
                print(userLogs)
                print("-------")
            print(logs)
    for run_id, logs in res.userLogs.items():
        if run_id not in res.logs:
            print(f"------- {run_id} ({i}):" if i is not None else f"------- {run_id}:")
            print(logs)


def __logs_parts(app_log: AppLog) -> Dict[int, LogsResult]:
    parts = {}
    for i, log_res in enumerate(app_log.data):
        if len(log_res.data) > 0 or (log_res.logs is not None and len(log_res.logs) > 0) or (log_res.userLogs is not None and len(log_res.userLogs) > 0):
            parts[i] = log_res
    return parts


def show_logs(app_logs: AppLogs, err: bool = False) -> None:  # noqa: ANN202
    show = Config.logger.error if err else Config.logger.info
    show(f"operation_id = {app_logs.operationId}")
    if app_logs.error is not None:
        show(f"error: {app_logs.error}")
        print(__delimiter)
    if len(app_logs.dagLogs) > 0:
        print("------- dm logs -------")
        print(app_logs.dagLogs)
    for app_name, app_log in app_logs.data.items():
        parts = __logs_parts(app_log)
        if len(parts) == 0:
            continue
        print(f"------- {app_name} -------")
        if len(app_log.data) == 1:
            __show_logs_result(app_log.data[0])
        else:
            c = len(parts)
            for i, log_res in parts.items():
                __show_logs_result(log_res, i)
                c -= 1
                if c != 0:
                    print(__mini__delimiter)
        print(__delimiter)


def show_logs_colored(app_logs: AppLogs, colors_dict: Optional[Dict[str, str]] = None) -> None:
    """colors_dict - should be unique for all app_logs by operation_id"""
    def format(log, color: Optional[str] = None) -> None:
        if color is None:
            Config.logger.warning(log)
        else:
            Config.logger.warning(color + log + __color_reset)

    def get_color(name: str) -> str:
        color = colors_dict.get(name, None)
        if color is None:
            color = __colors[len(colors_dict) % len(__colors)]
            colors_dict[name] = color
        return color

    if colors_dict is None:
        colors_dict = {}

    format(f"operation_id = {app_logs.operationId}")
    if app_logs.error is not None:
        color = get_color("error")
        format(f"error: {app_logs.error}", color)
        format(__delimiter, color)
    if len(app_logs.dagLogs) > 0:
        color = get_color("dm")
        format("------- dm logs -------", color)
        for line in app_logs.dagLogs.splitlines():
            format(f"dm: {line}", color)
    for app_name, app_log in app_logs.data.items():
        parts = __logs_parts(app_log)
        if len(parts) == 0:
            continue

        color = get_color(app_name)
        for i, logs_result in parts.items():
            app_name_prefix = f"{app_name}${i}" if i != 0 or len(parts) > 1 else app_name
            if len(logs_result.data) > 0:
                for line in logs_result.data.splitlines():
                    format(f"{app_name_prefix}$main: {line}", color)
            if logs_result.logs is None:
                logs_result.logs = {}
            if logs_result.userLogs is None:
                logs_result.userLogs = {}
            for run_id, logs in logs_result.logs.items():
                user_logs = logs_result.userLogs.get(run_id, "")
                if len(user_logs) > 0:
                    for line in user_logs.splitlines():
                        format(f"{app_name_prefix}${run_id}$user: {line}", color)
                if len(logs) > 0:
                    for line in logs.splitlines():
                        format(f"{app_name_prefix}${run_id}: {line}", color)
            for run_id, user_logs in logs_result.userLogs.items():
                if run_id not in logs_result.logs:
                    for line in user_logs.splitlines():
                        format(f"{app_name_prefix}${run_id}$user: {line}", color)


def show_logs_func(data: str, err: bool = False):  # noqa: ANN201
    try:
        app_logs = AppLogs.model_validate_json(data)
        show_logs(app_logs, err=err)
    except BaseException:
        Config.logger.error("decode logs failed")
        show = Config.logger.error if err else Config.logger.info
        show(data)


def show_logs_flatten_func_endpoint(data: str, err: bool = False) -> None:
    show = Config.logger.error if err else Config.logger.info
    try:
        app_logs_flatten = FlattenAppLogsWithResults.model_validate_json(data)
        show(f"operation_id = {app_logs_flatten.operationId}")
        if app_logs_flatten.error is not None:
            show(f"error: {app_logs_flatten.error}")
            print(__delimiter)
        show(app_logs_flatten.logs)
    except BaseException:
        Config.logger.error("decode logs failed")
        show(data)


def show_fail_app_info(data: str, err: bool):  # noqa: ANN201
    assert err, "show only for fails"
    try:
        res = json.loads(data)
        assert "result" in res
        print(res["result"])
    except BaseException:
        Config.logger.error("decode unsuccessful app_info fail")
        print(data)


def logs_streaming(operation_id: str, kafka_host_port: Optional[str] = None, app_logs_show: Callable[[AppLogs], None] = show_logs_colored) -> None:
    colors_dict = {}
    for appLogs in handle_logs(operation_id, kafka_host_port=kafka_host_port):
        app_logs_show(appLogs, colors_dict=colors_dict)
