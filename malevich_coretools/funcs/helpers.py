import json
from typing import Any, Coroutine, Dict, List, Literal, Optional, Union, overload
from uuid import uuid4

import pandas as pd

from malevich_coretools.abstract.abstract import (
    DEFAULT_MSG_URL,
    Alias,
    AppSettings,
    BasePlatformSettings,
    Cfg,
    DocsDataCollection,
    EndpointOverride,
    Restrictions,
    RunSettings,
    ScaleInfo,
    TaskComponent,
    TaskPolicy,
    UserConfig,
)
from malevich_coretools.batch import Batcher
from malevich_coretools.funcs.checks import check_profile_mode
from malevich_coretools.funcs.funcs import (
    post_collections_data,
    post_collections_data_async,
    post_collections_data_id,
    post_collections_data_id_async,
)
from malevich_coretools.secondary import Config, to_json

__all__ = ["create_collection_from_file_df", "update_collection_from_file_df", "raw_collection_from_df", "raw_collection_from_file", "create_collection_from_df", "update_collection_from_df", "create_app_settings", "create_user_config", "create_task_component", "create_task_policy", "create_restrictions", "create_run_settings", "create_endpoint_override", "create_cfg_struct"]


@overload
def create_collection_from_file_df(
    file: str,
    name: Optional[str],
    metadata: Optional[Union[Dict[str, Any], str]],
    *args,
    is_async: Literal[False] = False,
    **kwargs
) -> Alias.Id:
    pass


@overload
def create_collection_from_file_df(
    file: str,
    name: Optional[str],
    metadata: Optional[Union[Dict[str, Any], str]],
    *args,
    is_async: Literal[True],
    **kwargs
) -> Coroutine[Any, Any, Alias.Id]:
    pass


def create_collection_from_file_df(
    file: str,
    name: Optional[str],
    metadata: Optional[Union[Dict[str, Any], str]],
    *args,
    is_async: bool = False,
    **kwargs
) -> Union[Alias.Id, Coroutine[Any, Any, Alias.Id]]:
    try:
        data = pd.read_csv(file)
    except pd.errors.EmptyDataError:
        data = pd.DataFrame()
    if name is None:
        name = file
    return create_collection_from_df(data, name=file, metadata=metadata, *args, is_async=is_async, **kwargs)


@overload
def update_collection_from_file_df(
    id: str,
    file: str,
    name: Optional[str],
    metadata: Optional[Union[Dict[str, Any], str]],
    *args,
    is_async: Literal[False] = False,
    **kwargs
) -> Alias.Id:
    pass


@overload
def update_collection_from_file_df(
    id: str,
    file: str,
    name: Optional[str],
    metadata: Optional[Union[Dict[str, Any], str]],
    *args,
    is_async: Literal[True],
    **kwargs
) -> Coroutine[Any, Any, Alias.Id]:
    pass


def update_collection_from_file_df(
    id: str,
    file: str,
    name: Optional[str],
    metadata: Optional[Union[Dict[str, Any], str]],
    *args,
    is_async: bool = False,
    **kwargs
) -> Union[Alias.Id, Coroutine[Any, Any, Alias.Id]]:
    try:
        data = pd.read_csv(file)
    except pd.errors.EmptyDataError:
        data = pd.DataFrame()
    if name is None:
        name = file
    return update_collection_from_df(id, data, name=file, metadata=metadata, *args, is_async=is_async, **kwargs)


def raw_collection_from_df(
    data: pd.DataFrame,
    name: Optional[str],
    metadata: Optional[Union[Dict[str, Any], str]],
) -> DocsDataCollection:
    if metadata is not None:
        if isinstance(metadata, str):
            with open(metadata) as f:
                metadata = json.load(f)
            metadata = json.dumps(metadata)
        elif isinstance(data, dict):
            metadata = json.dumps(metadata)
        elif Config.WITH_WARNINGS:
            Config.logger.warning("wrong metadata type, ignore")
            metadata = None
    return DocsDataCollection(data=[row.to_json() for _, row in data.iterrows()], name=name, metadata=metadata)


def raw_collection_from_file(
    file: str,
    name: Optional[str] = None,
    metadata: Optional[Union[Dict[str, Any], str]] = None,
) -> DocsDataCollection:
    try:
        data = pd.read_csv(file)
    except pd.errors.EmptyDataError:
        data = pd.DataFrame()
    return raw_collection_from_df(data, name, metadata)


@overload
def create_collection_from_df(
    data: pd.DataFrame,
    name: Optional[str],
    metadata: Optional[Union[Dict[str, Any], str]],
    batcher: Optional[Batcher] = None,
    *args,
    is_async: Literal[False] = False,
    **kwargs
) -> Alias.Id:
    pass


@overload
def create_collection_from_df(
    data: pd.DataFrame,
    name: Optional[str],
    metadata: Optional[Union[Dict[str, Any], str]],
    batcher: Optional[Batcher] = None,
    *args,
    is_async: Literal[True],
    **kwargs
) -> Coroutine[Any, Any, Alias.Id]:
    pass


def create_collection_from_df(
    data: pd.DataFrame,
    name: Optional[str],
    metadata: Optional[Union[Dict[str, Any], str]],
    batcher: Optional[Batcher] = None,
    *args,
    is_async: bool = False,
    **kwargs
) -> Union[Alias.Id, Coroutine[Any, Any, Alias.Id]]:
    if batcher is None:
        batcher = Config.BATCHER
    data = raw_collection_from_df(data, name, metadata)
    if batcher is not None:
        return batcher.add("postCollectionByDocs", data=data)
    if is_async:
        return post_collections_data_async(data, *args, **kwargs)
    return post_collections_data(data, *args, **kwargs)


@overload
def update_collection_from_df(
    id: str,
    data: pd.DataFrame,
    name: Optional[str],
    metadata: Optional[Union[Dict[str, Any], str]],
    batcher: Optional[Batcher] = None,
    *args,
    is_async: Literal[False] = False,
    **kwargs
) -> Alias.Id:
    pass


@overload
def update_collection_from_df(
    id: str,
    data: pd.DataFrame,
    name: Optional[str],
    metadata: Optional[Union[Dict[str, Any], str]],
    batcher: Optional[Batcher] = None,
    *args,
    is_async: Literal[True],
    **kwargs
) -> Coroutine[Any, Any, Alias.Id]:
    pass


def update_collection_from_df(
    id: str,
    data: pd.DataFrame,
    name: Optional[str],
    metadata: Optional[Union[Dict[str, Any], str]],
    batcher: Optional[Batcher] = None,
    *args,
    is_async: bool = False,
    **kwargs
) -> Union[Alias.Id, Coroutine[Any, Any, Alias.Id]]:
    if batcher is None:
        batcher = Config.BATCHER
    data = raw_collection_from_df(data, name, metadata)
    if batcher is not None:
        return batcher.add("postCollectionByDocsAndId", data=data, vars={"id": id})
    if is_async:
        return post_collections_data_id_async(id, data, *args, **kwargs)
    return post_collections_data_id(id, data, *args, **kwargs)


def create_app_settings(
    app_id: str,
    task_id: Optional[str] = None,
    save_collections_name: Union[str, List[str]] = None,
) -> AppSettings:
    if save_collections_name is None:
        gen_collections_name = f"collection-{uuid4()}"
        Config.logger.warning(f"auto generating save collections name for {task_id}${app_id}: {gen_collections_name}")
        save_collections_name = [gen_collections_name]
    elif not isinstance(save_collections_name, list):
        save_collections_name = [save_collections_name]
    return AppSettings(
        appId=app_id, taskId=task_id, saveCollectionsName=save_collections_name
    )


def create_user_config(
    collections: Optional[Dict[str, str]] = None,
    raw_collections: Optional[Dict[str, List[Alias.Doc]]] = None,
    raw_map_collections: Optional[Dict[str, List[Dict[str, Any]]]] = None,
    different: Optional[Dict[str, str]] = None,
    schemes_aliases: Optional[Dict[str, str]] = None,
    msgUrl: Optional[str] = None,
    init_apps_update: Optional[Dict[str, bool]] = None,
    app_settings: Optional[List[AppSettings]] = None,
    app_cfg_extension: Optional[Dict[str, Union[Dict[str, Any], Alias.Json]]] = None,
    email: Optional[str] = None,
) -> UserConfig:
    app_cfg_extension_fixed = {}
    if app_cfg_extension is not None:
        for task_id_app_id, cfg in app_cfg_extension.items():
            app_cfg_extension_fixed[task_id_app_id] = to_json(cfg)
    return UserConfig(
        collections=collections,
        rawCollections=raw_collections,
        rawMapCollections=raw_map_collections,
        different=different,
        schemesAliases=schemes_aliases,
        msgUrl=msgUrl,
        initAppsUpdate=init_apps_update,
        appSettings=app_settings,
        appCfgExtension=app_cfg_extension_fixed,
        email=email,
    )


def create_task_component(
    app_control: Optional[str] = None,
    control: Optional[str] = None,
    extra: Optional[str] = None,
    internal: Optional[str] = None,
    key_value: Optional[str] = None,
    minimal: Optional[str] = None,
    object_storage: Optional[str] = None,
) -> TaskComponent:
    return TaskComponent(
        appControl=app_control,
        control=control,
        extra=extra,
        internal=internal,
        keyValue=key_value,
        minimal=minimal,
        objectStorage=object_storage
    )


def create_task_policy(
    lazy_app_init: bool = False,
    remove_app_after_run: bool = False,
    continue_after_processor: bool = False,
) -> TaskPolicy:
    return TaskPolicy(
        lazyAppInit=lazy_app_init,
        removeAppAfterRun=remove_app_after_run,
        continueAfterProcessor=continue_after_processor,
    )


def create_restrictions(
    honest_scale: bool = True,
    single_pod: bool = False,
    smart_apps_reuse: bool = False,
) -> Restrictions:
    return Restrictions(
        honestScale=honest_scale,
        singlePod=single_pod,
        smartAppsReuse=smart_apps_reuse,
    )


def create_run_settings(
    callback_url: Optional[str] = None,
    debug_mode: bool = False,
    core_manage: bool = False,
    single_request: bool = True,
    wait_runs: bool = True,
    profile_mode: Optional[str] = None,
    scale_info: Optional[List[ScaleInfo]] = None,
    component: Optional[TaskComponent] = None,
    policy: Optional[TaskPolicy] = None,
    restrictions: Optional[Restrictions] = None,
) -> RunSettings:
    check_profile_mode(profile_mode)
    scale_info = [] if scale_info is None else scale_info
    component = create_task_component() if component is None else component
    policy = create_task_policy() if policy is None else policy
    restrictions = create_restrictions() if restrictions is None else restrictions
    return RunSettings(
        callbackUrl=callback_url,
        debugMode=debug_mode,
        coreManage=core_manage,
        singleRequest=single_request,
        waitRuns=wait_runs,
        profileMode=profile_mode,
        scaleInfo=scale_info,
        component=component,
        policy=policy,
        restrictions=restrictions,
    )


def create_endpoint_override(
    cfg_id: Optional[str] = None,
    cfg: Optional[UserConfig] = None,
    override_config: bool = False,
    format_logs: bool = True,
    with_result: bool = True,
    # runSettings part
    callback_url: Optional[str] = None,
    debug_mode: bool = False,
    core_manage: bool = False,
    single_request: bool = True,
    wait_runs: bool = True,
    profile_mode: Optional[str] = None,
    scale_info: Optional[List[ScaleInfo]] = None,
    component: Optional[TaskComponent] = None,
    policy: Optional[TaskPolicy] = None,
    restrictions: Optional[Restrictions] = None,
) -> EndpointOverride:
    return EndpointOverride(
        cfgId=cfg_id,
        cfg=cfg,
        overrideConfig=override_config,
        formatLogs=format_logs,
        withResult=with_result,
        runSettings=create_run_settings(
            callback_url=callback_url,
            debug_mode=debug_mode,
            core_manage=core_manage,
            single_request=single_request,
            wait_runs=wait_runs,
            profile_mode=profile_mode,
            scale_info=scale_info,
            component=component,
            policy=policy,
            restrictions=restrictions,
        )
    )


def create_cfg_struct(
    collections: Optional[Dict[Alias.Id, Union[Alias.Id, Dict[str, Any]]]] = None,
    different: Optional[Dict[Alias.Id, Alias.Id]] = None,
    schemes_aliases: Optional[Dict[Alias.Id, Alias.Id]] = None,
    msg_url: str = DEFAULT_MSG_URL,
    init_apps_update: Optional[Dict[str, bool]] = None,
    app_settings: Optional[List[AppSettings]] = None,
    app_cfg_extension: Optional[Dict[str, Union[Dict[str, Any], Alias.Json]]] = None,   # taskId$appId -> app_cfg json
    email: Optional[str] = None,
) -> Cfg:
    collections = {} if collections is None else collections
    different = {} if different is None else different
    schemes_aliases = {} if schemes_aliases is None else schemes_aliases
    init_apps_update = {} if init_apps_update is None else init_apps_update
    app_settings = [] if app_settings is None else app_settings
    app_cfg_extension_fixed = {}
    if app_cfg_extension is not None:
        for task_id_app_id, cfg in app_cfg_extension.items():
            app_cfg_extension_fixed[task_id_app_id] = to_json(cfg)
    return Cfg(
        collections=collections,
        different=different,
        schemes_aliases=schemes_aliases,
        msg_url=msg_url,
        init_apps_update=init_apps_update,
        app_settings=app_settings,
        app_cfg_extension=app_cfg_extension_fixed,
        email=email,
    )


def base_settings(
    memory_request: Optional[int] = None,
    memory_limit: Optional[int] = None,
    cpu_request: Optional[int] = None,
    cpu_limit: Optional[int] = None,
    storage_request: Optional[int] = None,
    storage_limit: Optional[int] = None,
    kubeconfig: Optional[str] = None,
) -> str:
    return BasePlatformSettings(
        memoryRequest=memory_request,
        memoryLimit=memory_limit,
        cpuRequest=cpu_request,
        cpuLimit=cpu_limit,
        storageRequest=storage_request,
        storageLimit=storage_limit,
        kubeconfig=kubeconfig,
    ).model_dump_json()
