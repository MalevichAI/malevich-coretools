import json
import os
import re
import subprocess
from typing import Type, Union

import pandas as pd

import malevich_coretools.funcs.funcs as f
import malevich_coretools.funcs.helpers as fh
from malevich_coretools.abstract import *  # noqa: F403
from malevich_coretools.batch import (  # noqa: F401
    Batcher,
    BatcherRaiseOption,
    DefferOperation,
)
from malevich_coretools.funcs.helpers import (  # noqa: F401
    base_settings,
    create_app_settings,
    create_cfg_struct,
    create_endpoint_override,
    create_restrictions,
    create_run_settings,
    create_task_component,
    create_task_policy,
    create_user_config,
    raw_collection_from_df,
    raw_collection_from_file,
)
from malevich_coretools.secondary import Config, to_json
from malevich_coretools.secondary.const import (
    POSSIBLE_APPS_PLATFORMS,
    SCHEME_PATTERN,
    WAIT_RESULT_TIMEOUT,
)
from malevich_coretools.secondary.helpers import rand_str

__unique_digest_substring = "@sha256:"

# config


def set_host_port(host_port: str) -> None:
    """update host and port for malevich-core, example: `http://localhost:8080/` """
    assert len(host_port) > 0, "empty host port"
    host_port = host_port if host_port[-1] == "/" else f"{host_port}/"
    Config.HOST_PORT = host_port


def set_kafka_host_port(host_port: str) -> None:
    """update kafka host and port for malevich-kafka, example: `localhost:9092` """
    assert len(host_port) > 0, "empty host port"
    Config.KAFKA_HOST_PORT = host_port


def set_conn_url(conn_url: str) -> None:
    """analogue set_host_port; update `conn_url` for malevich-core, example: `http://localhost:8080/` """
    set_host_port(conn_url)


def set_verbose(verbose: bool) -> None:
    """set post/delete operations verbose"""
    Config.VERBOSE = verbose


def set_warnings(with_warnings: bool) -> None:
    """set show warnings or not"""
    Config.WITH_WARNINGS = with_warnings


def set_logger(logger):  # noqa: ANN201
    """set custom logger"""
    Config.logger = logger


def get_logger():  # noqa: ANN201
    """get logger"""
    return Config.logger


def update_core_credentials(username: USERNAME, password: PASSWORD) -> None:
    """update credentials for malevich-core"""
    Config.CORE_USERNAME = username
    Config.CORE_PASSWORD = password


def digest_by_image(
    image_ref: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
) -> Optional[str]:
    """return image in digest format by `image_ref`, if fail - return None and log error. If `image_ref` in digest format - return itself without check

    Args:
        image_ref (str): image_ref
        username (Optional[str], optional): username if necessary. Defaults to None.
        password (Optional[str], optional): password if necessary. Defaults to None.

    Returns:
        Optional[str]: image_ref in digest format or None if failed
    """
    if __unique_digest_substring in image_ref:
        return image_ref
    if username is None and password is None:
        cmd = ["skopeo", "inspect", "--no-creds", f"docker://{image_ref}"]
    else:
        cmd = ["skopeo", "inspect", "--username", username, "--password", password, f"docker://{image_ref}"]
    result = subprocess.run(cmd, capture_output=True)
    info = result.stdout.decode("utf-8")
    if info != "":
        digest = json.loads(info)["Digest"]
        return f"{image_ref[:len(image_ref) if (index := image_ref.rfind(':')) == -1 else index]}@{digest}"
    else:
        info = result.stderr.decode("utf-8")
        Config.logger.error(info)
        return None


# Docs


def get_docs(
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> ResultIds:
    """return list ids """
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getDocs", result_model=ResultIds)
    if is_async:
        return f.get_docs_async(auth=auth, conn_url=conn_url)
    return f.get_docs(auth=auth, conn_url=conn_url)


def get_doc(
    id: str,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> ResultDoc:
    """return doc by `id` """
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getDocById", vars={"id": id}, result_model=ResultDoc)
    if is_async:
        return f.get_docs_id_async(id, auth=auth, conn_url=conn_url)
    return f.get_docs_id(id, auth=auth, conn_url=conn_url)


def get_doc_by_name(
    name: str,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> ResultDoc:
    """return doc by `name` """
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getDocByName", vars={"name": name}, result_model=ResultDoc)
    if is_async:
        return f.get_docs_name_async(name, auth=auth, conn_url=conn_url)
    return f.get_docs_name(name, auth=auth, conn_url=conn_url)


def create_doc(
    data: Union[Alias.Json, Dict, Type[BaseModel]],
    name: Optional[str] = None,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Id:
    """save doc with `data` and `name`, return `id` """
    if batcher is None:
        batcher = Config.BATCHER
    if isinstance(data, Dict):
        data = json.dumps(data)
    elif issubclass(data.__class__, BaseModel):
        data = data.model_dump_json()
    data = DocWithName(data=data, name=name)
    if batcher is not None:
        return batcher.add("postDoc", data=data)
    if is_async:
        return f.post_docs_async(
            data, wait=wait, auth=auth, conn_url=conn_url
        )
    return f.post_docs(
        data, wait=wait, auth=auth, conn_url=conn_url
    )


def update_doc(
    id: str,
    data: Alias.Json,
    name: Optional[str],
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Id:
    """update doc by `id`, return `id` """
    if batcher is None:
        batcher = Config.BATCHER
    data = DocWithName(data=data, name=name)
    if batcher is not None:
        return batcher.add("postDocById", data=data, vars={"id": id})
    if is_async:
        return f.post_docs_id_async(
            id, data, wait=wait, auth=auth, conn_url=conn_url
        )
    return f.post_docs_id(
        id, data, wait=wait, auth=auth, conn_url=conn_url
    )


def delete_doc(
    id: str,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Info:
    """delete doc by `id` """
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("deleteDocById", vars={"id": id})
    if is_async:
        return f.delete_docs_id_async(id, wait=wait, auth=auth, conn_url=conn_url)
    return f.delete_docs_id(id, wait=wait, auth=auth, conn_url=conn_url)


def delete_docs(
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Info:
    """delete all docs"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("deleteDocs")
    if is_async:
        return f.delete_docs_async(wait=wait, auth=auth, conn_url=conn_url)
    return f.delete_docs(wait=wait, auth=auth, conn_url=conn_url)


# Collections


def get_collections(
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> ResultOwnAndSharedIds:
    """return 2 list: own collections ids and shared collections ids"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getCollections", result_model=ResultOwnAndSharedIds)
    if is_async:
        return f.get_collections_async(auth=auth, conn_url=conn_url)
    return f.get_collections(auth=auth, conn_url=conn_url)


def get_collections_by_name(
    name: str,
    operation_id: Optional[str] = None,
    run_id: Optional[str] = None,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> ResultOwnAndSharedIds:
    """return 2 list: own collections ids and shared collections ids by `name` and mb also `operation_id` and `run_id` with which it was saved"""
    assert not (
        operation_id is None and run_id is not None
    ), "if run_id set, operation_id should be set too"
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getCollectionsByNameAndOperationId", vars={"name": name, "operationId": operation_id, "runId": run_id}, result_model=ResultOwnAndSharedIds)
    if is_async:
        return f.get_collections_name_async(
            name, operation_id, run_id, auth=auth, conn_url=conn_url
        )
    return f.get_collections_name(
        name, operation_id, run_id, auth=auth, conn_url=conn_url
    )


def get_collection_by_name(
    name: str,
    operation_id: Optional[str] = None,
    run_id: Optional[str] = None,
    offset: int = 0,
    limit: int = -1,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> ResultCollection:
    """return collection by `name` and mb also `operation_id` and `run_id` with which it was saved. raise if there are multiple collections, pagination: unlimited - `limit` < 0"""
    assert not (
        operation_id is None and run_id is not None
    ), "if run_id set, operation_id should be set too"
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getCollectionByName", vars={"name": name, "operationId": operation_id, "runId": run_id, "offset": offset, "limit": limit}, result_model=ResultCollection)
    if is_async:
        return f.get_collection_name_async(
            name, operation_id, run_id, offset, limit, auth=auth, conn_url=conn_url
        )
    return f.get_collection_name(
        name, operation_id, run_id, offset, limit, auth=auth, conn_url=conn_url
    )


def get_collection(
    id: str,
    offset: int = 0,
    limit: int = -1,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> ResultCollection:
    """return collection by `id`, pagination: unlimited - `limit` < 0"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getCollectionById", vars={"id": id, "offset": offset, "limit": limit}, result_model=ResultCollection)
    if is_async:
        return f.get_collections_id_async(id, offset, limit, auth=auth, conn_url=conn_url)
    return f.get_collections_id(id, offset, limit, auth=auth, conn_url=conn_url)


def get_collections_ids_by_group_name(
    group_name: str,
    operation_id: str,
    run_id: Optional[str] = None,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> ResultIds:
    """return collections ids by `group_name`, `operation_id` and `run_id` with which it was saved"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getCollectionsIdsByGroupName", vars={"name": group_name, "operationId": operation_id, "runId": run_id}, result_model=ResultIds)
    if is_async:
        return f.get_collections_ids_groupName_async(
            group_name, operation_id, run_id, auth=auth, conn_url=conn_url
        )
    return f.get_collections_ids_groupName(
        group_name, operation_id, run_id, auth=auth, conn_url=conn_url
    )


def get_collections_by_group_name(
    group_name: str,
    operation_id: str,
    run_id: Optional[str] = None,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> ResultCollections:
    """return collections by `group_name`, `operation_id` and `run_id` with which it was saved"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getCollectionsByGroupName", vars={"name": group_name, "operationId": operation_id, "runId": run_id}, result_model=ResultCollections)
    if is_async:
        return f.get_collections_groupName_async(
            group_name, operation_id, run_id, auth=auth, conn_url=conn_url
        )
    return f.get_collections_groupName(
        group_name, operation_id, run_id, auth=auth, conn_url=conn_url
    )


def create_collection(
    ids: List[str],
    name: Optional[str] = None,
    metadata: Optional[str] = None,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Id:
    """save collection by list docs `ids`, return id"""
    if batcher is None:
        batcher = Config.BATCHER
    data = DocsCollection(data=ids, name=name, metadata=metadata)
    if batcher is not None:
        return batcher.add("postCollection", data=data)
    if is_async:
        return f.post_collections_async(
            data,
            wait=wait,
            auth=auth,
            conn_url=conn_url,
        )
    return f.post_collections(
        data,
        wait=wait,
        auth=auth,
        conn_url=conn_url,
    )


def update_collection(
    id: str,
    ids: List[str],
    name: Optional[str] = None,
    metadata: Optional[str] = None,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Id:
    """update collection with `id` by list docs `ids`, return `id` """
    if batcher is None:
        batcher = Config.BATCHER
    data = DocsCollection(data=ids, name=name, metadata=metadata)
    if batcher is not None:
        return batcher.add("postCollectionById", data=data, vars={"id": id})
    if is_async:
        return f.post_collections_id_async(
            id,
            data,
            wait=wait,
            auth=auth,
            conn_url=conn_url,
        )
    return f.post_collections_id(
        id,
        data,
        wait=wait,
        auth=auth,
        conn_url=conn_url,
    )


def s3_put_collection(
    id: str,
    is_csv=True,
    key: Optional[str] = None,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Info:
    """is_csv = false -> save json, key by default = id"""
    if batcher is None:
        batcher = Config.BATCHER
    data = PostS3Settings(isCsv=is_csv, key=key)
    if batcher is not None:
        return batcher.add("postCollectionByIdS3", data=data, vars={"id": id})
    if is_async:
        return f.post_collections_id_s3_async(
            id,
            data,
            wait=wait,
            auth=auth,
            conn_url=conn_url,
        )
    return f.post_collections_id_s3(
        id,
        data,
        wait=wait,
        auth=auth,
        conn_url=conn_url,
    )


def create_collection_by_docs(
    docs: List[Alias.Json],
    name: Optional[str] = None,
    metadata: Optional[str] = None,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Id:
    """save collection by `docs`, return `id` """
    if batcher is None:
        batcher = Config.BATCHER
    data = DocsDataCollection(data=docs, name=name, metadata=metadata)
    if batcher is not None:
        return batcher.add("postCollectionByDocs", data=data)
    if is_async:
        return f.post_collections_data_async(
            data,
            wait=wait,
            auth=auth,
            conn_url=conn_url,
        )
    return f.post_collections_data(
        data,
        wait=wait,
        auth=auth,
        conn_url=conn_url,
    )


def update_collection_by_docs(
    id: str,
    docs: List[Alias.Json],
    name: Optional[str] = None,
    metadata: Optional[str] = None,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Id:
    """update collection by `id` with `docs`, return `id` """
    if batcher is None:
        batcher = Config.BATCHER
    data = DocsDataCollection(data=docs, name=name, metadata=metadata)
    if batcher is not None:
        return batcher.add("postCollectionByDocsAndId", data=data, vars={"id": id})
    if is_async:
        return f.post_collections_data_id_async(
            id,
            data,
            wait=wait,
            auth=auth,
            conn_url=conn_url,
        )
    return f.post_collections_data_id(
        id,
        data,
        wait=wait,
        auth=auth,
        conn_url=conn_url,
    )


def add_to_collection(
    id: str,
    ids: List[str],
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Info:
    """add to collection with `id` docs with `ids` """
    if batcher is None:
        batcher = Config.BATCHER
    data = DocsCollectionChange(data=ids)
    if batcher is not None:
        return batcher.add("postCollectionByIdAdd", data=data, vars={"id": id})
    if is_async:
        return f.post_collections_id_add_async(
            id, data, wait=wait, auth=auth, conn_url=conn_url
        )
    return f.post_collections_id_add(
        id, data, wait=wait, auth=auth, conn_url=conn_url
    )


def copy_collection(
    id: str,
    full_copy: bool = True,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Id:
    """copy collection with `id`, if not `full_copy` docs same as in collection with `id` """
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("postCollectionByIdCopy", vars={"id": id, "fullCopy": full_copy})
    if is_async:
        return f.post_collections_id_copy_async(
            id, full_copy=full_copy, wait=wait, auth=auth, conn_url=conn_url
        )
    return f.post_collections_id_copy(
        id, full_copy=full_copy, wait=wait, auth=auth, conn_url=conn_url
    )


def apply_scheme(
    coll_id: str,
    scheme_name: str,
    mode: str = "drop",
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Id:
    """apply scheme with `scheme_name` to collection with `coll_id` return new collection with another `coll_id` """
    if batcher is None:
        batcher = Config.BATCHER
    data = FixScheme(schemeName=scheme_name, mode=mode)
    if batcher is not None:
        return batcher.add("postCollectionApplyScheme", data=data, vars={"id": coll_id})
    if is_async:
        return f.post_collections_id_applyScheme_async(
            coll_id,
            data,
            wait=wait,
            auth=auth,
            conn_url=conn_url,
        )
    return f.post_collections_id_applyScheme(
        coll_id,
        data,
        wait=wait,
        auth=auth,
        conn_url=conn_url,
    )


def fix_scheme(
    coll_id: str,
    scheme_name: str,
    mode="check",
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Info:
    """optimization to core (not necessary call), sets the schema with `scheme_name` for the collection with `coll_id` """
    if batcher is None:
        batcher = Config.BATCHER
    data = FixScheme(schemeName=scheme_name, mode=mode)
    if batcher is not None:
        return batcher.add("postCollectionFixScheme", data=data, vars={"id": coll_id})
    if is_async:
        return f.post_collections_id_fixScheme_async(
            coll_id, data, wait=wait, auth=auth, conn_url=conn_url
        )
    return f.post_collections_id_fixScheme(
        coll_id, data, wait=wait, auth=auth, conn_url=conn_url
    )


def unfix_scheme(
    coll_id: str,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Info:
    """unfix scheme for collection with `coll_id` """
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("postCollectionUnfixScheme", vars={"id": coll_id})
    if is_async:
        return f.post_collections_id_unfixScheme_async(
            coll_id, wait=wait, auth=auth, conn_url=conn_url
        )
    return f.post_collections_id_unfixScheme(
        coll_id, wait=wait, auth=auth, conn_url=conn_url
    )


def update_metadata(
    coll_id: str,
    metadata: Optional[str],
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Info:
    """update `metadata` for collection with `coll_id` """
    if batcher is None:
        batcher = Config.BATCHER
    data = CollectionMetadata(data=metadata)
    if batcher is not None:
        return batcher.add("postCollectionMetadata", data=data, vars={"id": coll_id})
    if is_async:
        return f.post_collections_metadata_async(
            coll_id, data, wait=wait, auth=auth, conn_url=conn_url
        )
    return f.post_collections_metadata(
        coll_id, data, wait=wait, auth=auth, conn_url=conn_url
    )


def delete_collections(
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Info:
    """delete all collections"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("deleteCollections")
    if is_async:
        return f.delete_collections_async(wait=wait, auth=auth, conn_url=conn_url)
    return f.delete_collections(wait=wait, auth=auth, conn_url=conn_url)


def delete_collection(
    id: str,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Info:
    """delete collection with `id` """
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("deleteCollectionById", vars={"id": id})
    if is_async:
        return f.delete_collections_id_async(id, wait=wait, auth=auth, conn_url=conn_url)
    return f.delete_collections_id(id, wait=wait, auth=auth, conn_url=conn_url)


def s3_delete_collection(
    key: str,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Info:
    """delete collection from s3 by `key` (that =id if not specified in s3_save_collection)"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("deleteCollectionByIdS3", vars={"id": key})
    if is_async:
         return f.delete_collections_id_s3_async(key, wait=wait, auth=auth, conn_url=conn_url)
    return f.delete_collections_id_s3(key, wait=wait, auth=auth, conn_url=conn_url)


def delete_from_collection(
    id: str,
    ids: List[str],
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Info:
    """delete docs with `ids` from collection with `id` """
    if batcher is None:
        batcher = Config.BATCHER
    data = DocsCollectionChange(data=ids)
    if batcher is not None:
        return batcher.add("deleteCollectionByIdDel", data=data, vars={"id": id})
    if is_async:
        return f.delete_collections_id_del_async(
            id, data, wait=wait, auth=auth, conn_url=conn_url
        )
    return f.delete_collections_id_del(
        id, data, wait=wait, auth=auth, conn_url=conn_url
    )


# CollectionObjects


def get_collection_objects(
    path: Optional[str] = None,
    recursive: Optional[bool] = None,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> FilesDirs:
    """return struct with list of paths: directories and files: walk if `recursive` else ls"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getCollectionObjects", vars={"path": path, "recursive": recursive}, result_model=FilesDirs)
    if is_async:
        return f.get_collection_objects_async(path, recursive, auth=auth, conn_url=conn_url)
    return f.get_collection_objects(path, recursive, auth=auth, conn_url=conn_url)


def get_collection_object(
    path: str,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> bytes:
    """return collection object bytes by `path`"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getCollectionObject", vars={"path": path})
    if is_async:
        return f.get_collection_object_async(
            path, auth=auth, conn_url=conn_url
        )
    return f.get_collection_object(
        path, auth=auth, conn_url=conn_url
    )


def post_collection_object_presigned_url(
    path: str,
    expires_in: int,
    callback_url: Optional[str] = None,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> str:
    """get presigned url to put object with `path`, valid only `expiresIn` seconds, one-time use"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("presignCollectionObject", vars={"path": path, "callbackUrl": callback_url, "expiresIn": expires_in})
    if is_async:
        return f.post_collection_object_presigned_url_async(path, callback_url, expires_in, wait=wait, auth=auth, conn_url=conn_url)
    return f.post_collection_object_presigned_url(path, callback_url, expires_in, wait=wait, auth=auth, conn_url=conn_url)


def get_collection_object_presigned_url(
    path: str,
    expires_in: int,
    callback_url: Optional[str] = None,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> str:
    """get presigned url to get object with `path`, valid only `expiresIn` seconds, one-time use"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("presignGetCollectionObject", vars={"path": path, "callbackUrl": callback_url, "expiresIn": expires_in})
    if is_async:
        return f.get_collection_object_presigned_url_async(path, callback_url, expires_in, wait=wait, auth=auth, conn_url=conn_url)
    return f.get_collection_object_presigned_url(path, callback_url, expires_in, wait=wait, auth=auth, conn_url=conn_url)


def load_collection_object_presigned(
    signature: str,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> bytes:
    """get collection object by presigned `signature`"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getPresignCollectionObject", vars={"signature": signature})
    if is_async:
        return f.get_collections_object_presigned_async(signature, auth=auth, conn_url=conn_url)
    return f.get_collections_object_presigned(signature, auth=auth, conn_url=conn_url)


def update_collection_object(
    path: str,
    data: bytes,
    zip: bool = False,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Info:
    """update collection object with `path` by `data` """
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("postCollectionObject", data=data, vars={"path": path, "zip": zip})
    if is_async:
        return f.post_collections_object_async(path, data, zip, wait=wait, auth=auth, conn_url=conn_url)
    return f.post_collections_object(path, data, zip, wait=wait, auth=auth, conn_url=conn_url)


def update_collection_object_presigned(
    signature: str,
    data: bytes,
    zip: bool = False,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Info:
    """update collection object by `data` with presigned `signature`"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("postPresignCollectionObject", data=data, vars={"signature": signature, "zip": zip})
    if is_async:
        return f.post_collections_object_presigned_async(signature, data, zip, auth=auth, conn_url=conn_url)
    return f.post_collections_object_presigned(signature, data, zip, auth=auth, conn_url=conn_url)


def delete_collection_objects(
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Info:
    """delete all collection objects"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("deleteCollectionObjects")
    if is_async:
        return f.delete_collection_objects_async(wait=wait, auth=auth, conn_url=conn_url)
    return f.delete_collection_objects(wait=wait, auth=auth, conn_url=conn_url)


def delete_collection_object(
    path: str,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Info:
    """delete collection object with `path` (or directory with them) """
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("deleteCollectionObjectByPath", vars={"path": path})
    if is_async:
        return f.delete_collection_object_async(path, wait=wait, auth=auth, conn_url=conn_url)
    return f.delete_collection_object(path, wait=wait, auth=auth, conn_url=conn_url)


# Endpoint


def get_endpoints(
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Endpoints:
    """get registered endpoints structs"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getEndpoints", result_model=Endpoints)
    if is_async:
        return f.get_endpoints_async(auth=auth, conn_url=conn_url)
    return f.get_endpoints(auth=auth, conn_url=conn_url)


def get_endpoint(
    hash: str,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Endpoint:
    """get endpoint struct by hash"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getEndpointByHash", result_model=Endpoint)
    if is_async:
        return f.get_endpoint_by_hash_async(hash, auth=auth, conn_url=conn_url)
    return f.get_endpoint_by_hash(hash, auth=auth, conn_url=conn_url)


def get_run_endpoint(
    hash: str,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> EndpointRunInfo:
    """get info for endpoint"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getEndpointRun", vars={"hash": hash}, result_model=EndpointRunInfo)
    if is_async:
        return f.get_endpoint_run_async(hash, auth=auth, conn_url=conn_url)
    return f.get_endpoint_run(hash, auth=auth, conn_url=conn_url)


def run_endpoint(
    hash: str,
    endpoint_override: Optional[EndpointOverride] = None,
    with_show: bool = True,
    *,
    with_auth: bool = True,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Union[AppLogsWithResults, FlattenAppLogsWithResults, Any]:
    """run by endpoint, failed if `taskId`, `cfgId` not set or it is not active"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        if endpoint_override is None or endpoint_override.formatLogs:
            model = FlattenAppLogsWithResults
        else:
            model = AppLogsWithResults
        return batcher.add("postEndpointRun", data=endpoint_override, vars={"hash": hash}, result_model=model)
    if is_async:
        return f.run_endpoint_async(hash, endpoint_override, with_show=with_show, with_auth=with_auth, auth=auth, conn_url=conn_url)
    return f.run_endpoint(hash, endpoint_override, with_show=with_show, with_auth=with_auth, auth=auth, conn_url=conn_url)


def create_endpoint(
    task_id: Optional[str] = None,
    pipeline_id: Optional[str] = None,
    cfg_id: Optional[str] = None,
    sla: Optional[str] = None,
    active: Optional[bool] = None,
    prepare: Optional[bool] = None,
    run_settings: Optional[RunSettings] = None,
    enable_not_auth: Optional[str] = None,
    expected_colls_with_schemes: Optional[Dict[str, str]] = None,
    description: Optional[str] = None,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Id:
    """create endpoint, return hash, url - api/v1/endpoints/run/{hash}. fields may not be initialized - this will only cause an error at startup"""
    assert task_id is None or pipeline_id is None, "endpoint should be defined in one way"
    if batcher is None:
        batcher = Config.BATCHER
    data = Endpoint(taskId=task_id, pipelineId=pipeline_id, cfgId=cfg_id, sla=sla, active=active, prepare=prepare, runSettings=run_settings,
                    enableNotAuthorized=enable_not_auth, expectedCollectionsWithSchemes=expected_colls_with_schemes, description=description)
    if batcher is not None:
        return batcher.add("postEndpointCreate", data=data)
    if is_async:
        return f.create_endpoint_async(data, wait=wait, auth=auth, conn_url=conn_url)
    return f.create_endpoint(data, wait=wait, auth=auth, conn_url=conn_url)


def update_endpoint(
    hash: str,
    task_id: Optional[str] = None,
    pipeline_id: Optional[str] = None,
    cfg_id: Optional[str] = None,
    sla: Optional[str] = None,
    active: Optional[bool] = None,
    prepare: Optional[bool] = None,
    run_settings: Optional[RunSettings] = None,
    enable_not_auth: Optional[str] = None,
    expected_colls_with_schemes: Optional[Dict[str, str]] = None,
    description: Optional[str] = None,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Id:
    """update endpoint, return hash, url - api/v1/endpoints/run/{hash}. update field if it is not None"""
    assert task_id is None or pipeline_id is None, "endpoint should be defined in one way"
    if batcher is None:
        batcher = Config.BATCHER
    data = Endpoint(hash=hash, taskId=task_id, pipelineId=pipeline_id, cfgId=cfg_id, sla=sla, active=active, prepare=prepare, runSettings=run_settings,
                    enableNotAuthorized=enable_not_auth, expectedCollectionsWithSchemes=expected_colls_with_schemes, description=description)
    if batcher is not None:
        return batcher.add("postEndpointUpdate", data=data)
    if is_async:
        return f.update_endpoint_async(data, wait=wait, auth=auth, conn_url=conn_url)
    return f.update_endpoint(data, wait=wait, auth=auth, conn_url=conn_url)


def pause_endpoint(
    hash: str,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Info:
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("postEndpointPause", vars={"hash": hash})
    if is_async:
        return f.pause_endpoint_async(hash, wait=wait, auth=auth, conn_url=conn_url)
    return f.pause_endpoint(hash, wait=wait, auth=auth, conn_url=conn_url)


def resume_endpoint(
    hash: str,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Info:
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("postEndpointResume", vars={"hash": hash})
    if is_async:
        return f.resume_endpoint_async(hash, wait=wait, auth=auth, conn_url=conn_url)
    return f.resume_endpoint(hash, wait=wait, auth=auth, conn_url=conn_url)


def delete_endpoints(
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Info:
    """delete all endpoints"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("deleteEndpoints")
    if is_async:
        return f.delete_endpoints_async(wait=wait, auth=auth, conn_url=conn_url)
    return f.delete_endpoints(wait=wait, auth=auth, conn_url=conn_url)


def delete_endpoint(
    hash: str,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Info:
    """delete endpoint with `hash` """
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("deleteEndpoint", vars={"hash": hash})
    if is_async:
        return f.delete_endpoint_async(hash, wait=wait, auth=auth, conn_url=conn_url)
    return f.delete_endpoint(hash, wait=wait, auth=auth, conn_url=conn_url)


# Scheme


def get_schemes(
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> ResultOwnAndSharedIds:
    """return 2 list: own schemes ids and shared schemes ids"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getSchemes", result_model=ResultOwnAndSharedIds)
    if is_async:
        return f.get_schemes_async(auth=auth, conn_url=conn_url)
    return f.get_schemes(auth=auth, conn_url=conn_url)


def get_scheme(
    id: str,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> ResultScheme:
    """return scheme by `id` """
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getSchemeById", vars={"id": id}, result_model=ResultScheme)
    if is_async:
        return f.get_schemes_id_async(id, auth=auth, conn_url=conn_url)
    return f.get_schemes_id(id, auth=auth, conn_url=conn_url)


def get_scheme_raw(
    id: str,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Json:
    """return raw scheme data by `id` """
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getSchemeRawById", vars={"id": id})
    if is_async:
        return f.get_schemes_id_raw_async(id, auth=auth, conn_url=conn_url)
    return f.get_schemes_id_raw(id, auth=auth, conn_url=conn_url)


def get_schemes_mapping(
    scheme_from_id: str,
    scheme_to_id: str,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> ResultMapping:
    """return mapping by schemes ids, does not assume if it is not"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getSchemesMapping", vars={"schemeFromId": scheme_from_id, "schemeToId": scheme_to_id}, result_model=ResultMapping)
    if is_async:
        return f.get_schemes_mapping_async(
            scheme_from_id, scheme_to_id, auth=auth, conn_url=conn_url
        )
    return f.get_schemes_mapping(
        scheme_from_id, scheme_to_id, auth=auth, conn_url=conn_url
    )


def create_scheme(
    scheme_data: Union[Dict[str, Any], Alias.Json],
    name: str,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Id:
    """create scheme\n
    `scheme_data` must be json or dict
    return `id` """
    assert re.fullmatch(SCHEME_PATTERN, name) is not None, f"wrong scheme name: {name}"
    if batcher is None:
        batcher = Config.BATCHER
    scheme_json = to_json(scheme_data)
    data = SchemeWithName(data=scheme_json, name=name)
    if batcher is not None:
        return batcher.add("postScheme", data=data)
    if is_async:
        return f.post_schemes_async(data, wait=wait, auth=auth, conn_url=conn_url)
    return f.post_schemes(data, wait=wait, auth=auth, conn_url=conn_url)


def update_scheme(
    id: str,
    scheme_data: Union[Dict[str, Any], Alias.Json],
    name: str,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Id:
    """update scheme\n
    `scheme_data` must be json or dict
    return `id` """
    assert re.fullmatch(SCHEME_PATTERN, name) is not None, f"wrong scheme name: {name}"
    if batcher is None:
        batcher = Config.BATCHER
    scheme_json = to_json(scheme_data)
    data = SchemeWithName(data=scheme_json, name=name)
    if batcher is not None:
        return batcher.add("postSchemeById", data=data, vars={"id": id})
    if is_async:
        return f.post_schemes_id_async(id, data, wait=wait, auth=auth, conn_url=conn_url)
    return f.post_schemes_id(id, data, wait=wait, auth=auth, conn_url=conn_url)


def create_schemes_mapping(
    scheme_from_id: str,
    scheme_to_id: str,
    mapping: Dict[str, str],
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Id:
    """save mapping between schemes with ids"""
    if batcher is None:
        batcher = Config.BATCHER
    data = SchemesFixMapping(
            schemeFromId=scheme_from_id, schemeToId=scheme_to_id, data=mapping
        )
    if batcher is not None:
        return batcher.add("postSchemesFixMapping", data=data)
    if is_async:
        return f.post_schemes_mapping_async(
            data,
            wait=wait,
            auth=auth,
            conn_url=conn_url,
        )
    return f.post_schemes_mapping(
        data,
        wait=wait,
        auth=auth,
        conn_url=conn_url,
    )


def delete_schemes(
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Info:
    """delete all schemes"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("deleteSchemes")
    if is_async:
        return f.delete_schemes_async(wait=wait, auth=auth, conn_url=conn_url)
    return f.delete_schemes(wait=wait, auth=auth, conn_url=conn_url)


def delete_scheme(
    id: str,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Info:
    """delete scheme by `id` """
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("deleteSchemeById", vars={"id": id})
    if is_async:
        return f.delete_schemes_id_async(id, wait=wait, auth=auth, conn_url=conn_url)
    return f.delete_schemes_id(id, wait=wait, auth=auth, conn_url=conn_url)


def delete_schemes_mapping(
    scheme_from_id: str,
    scheme_to_id: str,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Info:
    """delete mapping between schemes with ids"""
    if batcher is None:
        batcher = Config.BATCHER
    data = SchemesIds(schemeFromId=scheme_from_id, schemeToId=scheme_to_id)
    if batcher is not None:
        return batcher.add("deleteSchemesMapping", data=data)
    if is_async:
        return f.delete_schemes_mapping_async(
            data,
            wait=wait,
            auth=auth,
            conn_url=conn_url,
        )
    return f.delete_schemes_mapping(
        data,
        wait=wait,
        auth=auth,
        conn_url=conn_url,
    )


# Common


def check_auth(
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Info:
    """check auth in core for current user"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("home")
    if is_async:
        return f.get_check_auth_async(auth=auth, conn_url=conn_url)
    return f.get_check_auth(auth=auth, conn_url=conn_url)


def ping(
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Info:
    """return `pong` """
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("ping")
    if is_async:
        return f.get_ping_async(with_auth=False, conn_url=conn_url)
    return f.get_ping(with_auth=False, conn_url=conn_url)

# UserShare


def get_shared_collection(
    id: str,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> ResultLogins:
    """return list logins to which user has given access to the collection with `id` """
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getShareByCollection", vars={"id": id}, result_model=ResultLogins)
    if is_async:
        return f.get_share_collection_id_async(id, auth=auth, conn_url=conn_url)
    return f.get_share_collection_id(id, auth=auth, conn_url=conn_url)


def get_shared_scheme(
    id: str,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> ResultLogins:
    """return list logins to which user has given access to the scheme with `id` """
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getShareByScheme", vars={"id": id}, result_model=ResultLogins)
    if is_async:
        return f.get_share_scheme_id_async(id, auth=auth, conn_url=conn_url)
    return f.get_share_scheme_id(id, auth=auth, conn_url=conn_url)


def get_shared_app(
    id: str,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> ResultLogins:
    """return list logins to which user has given access to the app with `id` """
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getShareByUserApp", vars={"id": id}, result_model=ResultLogins)
    if is_async:
        return f.get_share_userApp_id_async(id, auth=auth, conn_url=conn_url)
    return f.get_share_userApp_id(id, auth=auth, conn_url=conn_url)


def get_shared_by_login(
    login: str,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> ResultSharedForLogin:
    """return structure with all info about share to user with `login` """
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getShareByLogin", vars={"login": login}, result_model=ResultSharedForLogin)
    if is_async:
        return f.get_share_login_async(login, auth=auth, conn_url=conn_url)
    return f.get_share_login(login, auth=auth, conn_url=conn_url)


def share_collection(
    id: str,
    user_logins: List[str],
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Info:
    """gives access to the collection with `id` to all users with `user_logins` """
    if batcher is None:
        batcher = Config.BATCHER
    data = SharedWithUsers(userLogins=user_logins)
    if batcher is not None:
        return batcher.add("postShareByCollection", data=data, vars={"id": id})
    if is_async:
        return f.post_share_collection_id_async(
            id,
            data,
            wait=wait,
            auth=auth,
            conn_url=conn_url,
        )
    return f.post_share_collection_id(
        id,
        data,
        wait=wait,
        auth=auth,
        conn_url=conn_url,
    )


def share_scheme(
    id: str,
    user_logins: List[str],
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Info:
    """gives access to the scheme with `id` to all users with `user_logins` """
    if batcher is None:
        batcher = Config.BATCHER
    data = SharedWithUsers(userLogins=user_logins)
    if batcher is not None:
        return batcher.add("postShareByScheme", data=data, vars={"id": id})
    if is_async:
        return f.post_share_scheme_id_async(
            id,
            data,
            wait=wait,
            auth=auth,
            conn_url=conn_url,
        )
    return f.post_share_scheme_id(
        id,
        data,
        wait=wait,
        auth=auth,
        conn_url=conn_url,
    )


def share_app(
    id: str,
    user_logins: List[str],
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Info:
    """gives access to the app with `id` to all users with `user_logins` """
    if batcher is None:
        batcher = Config.BATCHER
    data = SharedWithUsers(userLogins=user_logins)
    if batcher is not None:
        return batcher.add("postShareByUserApp", data=data, vars={"id": id})
    if is_async:
        return f.post_share_userApp_id_async(
            id,
            data,
            wait=wait,
            auth=auth,
            conn_url=conn_url,
        )
    return f.post_share_userApp_id(
        id,
        data,
        wait=wait,
        auth=auth,
        conn_url=conn_url,
    )


def share(
    user_logins: List[str],
    collections_ids: Optional[List[str]] = None,
    schemes_ids: Optional[List[str]] = None,
    user_apps_ids: Optional[List[str]] = None,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Info:
    """gives access to everything listed to all users with `user_logins` """
    assert user_logins is not None, '"user_logins" is empty'
    if batcher is None:
        batcher = Config.BATCHER
    collections_ids = [] if collections_ids is None else collections_ids
    schemes_ids = [] if schemes_ids is None else schemes_ids
    user_apps_ids = [] if user_apps_ids is None else user_apps_ids
    data = Shared(
        userLogins=user_logins,
        collectionsIds=collections_ids,
        schemesIds=schemes_ids,
        userAppsIds=user_apps_ids,
    )
    if batcher is not None:
        return batcher.add("postShare", data=data)
    if is_async:
        return f.post_share_async(
            data,
            wait=wait,
            auth=auth,
            conn_url=conn_url,
        )
    return f.post_share(
        data,
        wait=wait,
        auth=auth,
        conn_url=conn_url,
    )


def delete_shared(
    user_logins: List[str],
    collections_ids: Optional[List[str]] = None,
    schemes_ids: Optional[List[str]] = None,
    user_apps_ids: Optional[List[str]] = None,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Info:
    """removes access to everything listed to all users with `user_logins` """
    assert user_logins is not None, '"user_logins" is empty'
    if batcher is None:
        batcher = Config.BATCHER
    collections_ids = [] if collections_ids is None else collections_ids
    schemes_ids = [] if schemes_ids is None else schemes_ids
    user_apps_ids = [] if user_apps_ids is None else user_apps_ids
    data = Shared(
        userLogins=user_logins,
        collectionsIds=collections_ids,
        schemesIds=schemes_ids,
        userAppsIds=user_apps_ids,
    )
    if batcher is not None:
        return batcher.add("deleteShare", data=data)
    if is_async:
        return f.delete_share_async(
            data,
            wait=wait,
            auth=auth,
            conn_url=conn_url,
        )
    return f.delete_share(
        data,
        wait=wait,
        auth=auth,
        conn_url=conn_url,
    )


def delete_shared_all(
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Info:
    """removes access to everything for all for current user"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("deleteShareAll")
    if is_async:
        return f.delete_share_all_async(wait=wait, auth=auth, conn_url=conn_url)
    return f.delete_share_all(wait=wait, auth=auth, conn_url=conn_url)


# Registration


def get_user(
    login: str,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Info:
    """admin: displays saved information about the user"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getRegisterByLogin", vars={"login": login})
    if is_async:
        return f.get_register_login_async(login, auth=auth, conn_url=conn_url)
    return f.get_register_login(login, auth=auth, conn_url=conn_url)


def get_users(
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> ResultLogins:
    """admin: returns a list of all logins"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getRegisterAll", result_model=ResultLogins)
    if is_async:
        return f.get_register_all_async(auth=auth, conn_url=conn_url)
    return f.get_register_all(auth=auth, conn_url=conn_url)


def create_user(
    login: str,
    password: str,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Info:
    """create user in malevich-core, all operations will continue on his behalf"""
    if batcher is None:
        batcher = Config.BATCHER
    data = User(login=login, password=password)
    if batcher is not None:
        return batcher.add("postRegister", data=data)
    if is_async:
        return f.post_register_async(data, auth=auth, conn_url=conn_url)
    return f.post_register(data, auth=auth, conn_url=conn_url)


def delete_user_login(
    login: str,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> None:
    """admin: delete user by `login` """
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("deleteRegisterByLogin", vars={"login": login})
    if is_async:
        f.delete_register_login_async(login, wait=wait, auth=auth, conn_url=conn_url)
    f.delete_register_login(login, wait=wait, auth=auth, conn_url=conn_url)


def delete_user(
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Info:
    """delete current user, not raise if user not exist"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("deleteRegister")
    if is_async:
        return f.delete_register_async(auth=auth, conn_url=conn_url)
    return f.delete_register(auth=auth, conn_url=conn_url)


# UserApps


def get_apps(
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> ResultOwnAndSharedIds:
    """return apps ids for current user"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getApps", result_model=ResultOwnAndSharedIds)
    if is_async:
        return f.get_userApps_async(auth=auth, conn_url=conn_url)
    return f.get_userApps(auth=auth, conn_url=conn_url)


def get_apps_real(
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> ResultOwnAndSharedIds:
    """return apps real ids for current user"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getAppsReal", result_model=ResultOwnAndSharedIds)
    if is_async:
        return f.get_userApps_realIds_async(auth=auth, conn_url=conn_url)
    return f.get_userApps_realIds(auth=auth, conn_url=conn_url)


def get_apps_map(
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> ResultOwnAndSharedIdsMap:
    """return apps ids with real ids for current user"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getAppsMapIds", result_model=ResultOwnAndSharedIdsMap)
    if is_async:
        return f.get_userApps_mapIds_async(auth=auth, conn_url=conn_url)
    return f.get_userApps_mapIds(auth=auth, conn_url=conn_url)


def get_app_map(
    id: str,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Id:
    """return real id by app id for current user"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getAppsMapIdsById", vars={"id": id})
    if is_async:
        return f.get_userApps_mapId_async(id, auth=auth, conn_url=conn_url)
    return f.get_userApps_mapId(id, auth=auth, conn_url=conn_url)


def get_app(
    id: str,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> UserApp:
    """return app by `id` """
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getAppById", vars={"id": id}, result_model=UserApp)
    if is_async:
        return f.get_userApps_id_async(id, auth=auth, conn_url=conn_url)
    return f.get_userApps_id(id, auth=auth, conn_url=conn_url)


def get_app_real(
    id: str,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> UserApp:
    """return app by real `id` """
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getAppByRealId", vars={"id": id}, result_model=UserApp)
    if is_async:
        return f.get_userApps_realId_async(id, auth=auth, conn_url=conn_url)
    return f.get_userApps_realId(id, auth=auth, conn_url=conn_url)


def create_app(
    app_id: str,
    processor_id: str,
    input_id: Optional[str] = None,
    output_id: Optional[str] = None,
    app_cfg: Optional[Union[Dict[str, Any], Alias.Json]] = None,
    image_ref: Optional[str] = None,
    image_auth: Optional[AUTH] = None,
    platform: str = "base",
    platform_settings: Optional[str] = None,
    extra_collections_from: Optional[Dict[str, Union[List[str], str]]] = None,
    wait: bool = True,
    *,
    use_system_auth: bool = True,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Id:
    """create app\n
    `app_cfg` must be json or dict or None\n
    return `id` """
    assert (
        platform in POSSIBLE_APPS_PLATFORMS
    ), f"wrong platform: {platform}, possible platforms: {POSSIBLE_APPS_PLATFORMS}"
    assert image_ref is not None, "image_ref not set"
    if batcher is None:
        batcher = Config.BATCHER
    app_cfg_json = None if app_cfg is None else to_json(app_cfg)
    image_user = image_auth[0] if image_auth is not None else Config.USERNAME if use_system_auth else None
    image_token = image_auth[1] if image_auth is not None else Config.TOKEN if use_system_auth else None
    if Config.WITH_WARNINGS and (image_user is None or image_token is None):
        Config.logger.warning("image_auth not set")
    json_image = JsonImage(ref=image_ref, user=image_user, token=image_token)
    if extra_collections_from is not None:
        for k, v in extra_collections_from.items():
            if isinstance(v, str):
                extra_collections_from[k] = [v]
    data = UserApp(
        appId=app_id,
        inputId=input_id,
        processorId=processor_id,
        outputId=output_id,
        cfg=app_cfg_json,
        image=json_image,
        platform=platform,
        platformSettings=platform_settings,
        extraCollectionsFrom=extra_collections_from,
    )
    if batcher is not None:
        return batcher.add("postApp", data=data)
    if is_async:
        return f.post_userApps_async(data, wait=wait, auth=auth, conn_url=conn_url)
    return f.post_userApps(data, wait=wait, auth=auth, conn_url=conn_url)


def update_app(
    id: str,
    app_id: str,
    processor_id: str,
    input_id: Optional[str] = None,
    output_id: Optional[str] = None,
    app_cfg: Optional[Union[Dict[str, Any], Alias.Json]] = None,
    image_ref: Optional[str] = None,
    image_auth: Optional[AUTH] = None,
    platform: str = "base",
    platform_settings: Optional[str] = None,
    extra_collections_from: Optional[Dict[str, Union[List[str], str]]] = None,
    wait: bool = True,
    *,
    use_system_auth: bool = True,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Info:
    """update app by `id`\n
    `app_cfg` must be json or dict or None"""
    assert (
        platform in POSSIBLE_APPS_PLATFORMS
    ), f"wrong platform: {platform}, possible platforms: {POSSIBLE_APPS_PLATFORMS}"
    assert image_ref is not None, "image_ref not set"
    if batcher is None:
        batcher = Config.BATCHER
    app_cfg_json = None if app_cfg is None else to_json(app_cfg)
    image_user = image_auth[0] if image_auth is not None else Config.USERNAME if use_system_auth else None
    image_token = image_auth[1] if image_auth is not None else Config.TOKEN if use_system_auth else None
    if Config.WITH_WARNINGS and (image_user is None or image_token is None):
        Config.logger.warning("image_auth not set")
    json_image = JsonImage(ref=image_ref, user=image_user, token=image_token)
    if extra_collections_from is not None:
        for k, v in extra_collections_from.items():
            if isinstance(v, str):
                extra_collections_from[k] = [v]
    data = UserApp(
        appId=app_id,
        inputId=input_id,
        processorId=processor_id,
        outputId=output_id,
        cfg=app_cfg_json,
        image=json_image,
        platform=platform,
        platformSettings=platform_settings,
        extraCollectionsFrom=extra_collections_from,
    )
    if batcher is not None:
        return batcher.add("postAppById", data=data, vars={"id": id})
    if is_async:
        return f.post_userApps_id_async(id, data, wait=wait, auth=auth, conn_url=conn_url)
    return f.post_userApps_id(id, data, wait=wait, auth=auth, conn_url=conn_url)


def delete_apps(
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Info:
    """delete all user apps"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("deleteApps")
    if is_async:
        return f.delete_userApps_async(wait=wait, auth=auth, conn_url=conn_url)
    return f.delete_userApps(wait=wait, auth=auth, conn_url=conn_url)


def delete_app(
    id: str,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Info:
    """delete user app by `id` """
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("deleteAppById", vars={"id": id})
    if is_async:
        return f.delete_userApps_id_async(id, wait=wait, auth=auth, conn_url=conn_url)
    return f.delete_userApps_id(id, wait=wait, auth=auth, conn_url=conn_url)


# UserTasks


def get_tasks(
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> ResultIds:
    """return tasks ids for current user"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getTasks", result_model=ResultIds)
    if is_async:
        return f.get_userTasks(auth=auth, conn_url=conn_url)
    return f.get_userTasks(auth=auth, conn_url=conn_url)


def get_tasks_real(
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> ResultIds:
    """return tasks real ids for current user"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getTasksReal", result_model=ResultIds)
    if is_async:
        return f.get_userTasks_realIds_async(auth=auth, conn_url=conn_url)
    return f.get_userTasks_realIds(auth=auth, conn_url=conn_url)


def get_tasks_map(
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> ResultIdsMap:
    """return tasks ids with real ids for current user"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getTasksMapIds", result_model=ResultIdsMap)
    if is_async:
        return f.get_userTasks_mapIds_async(auth=auth, conn_url=conn_url)
    return f.get_userTasks_mapIds(auth=auth, conn_url=conn_url)


def get_task_map(
    id: str,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Id:
    """return real id by task id for current user"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getTasksMapIdsById", vars={"id": id})
    if is_async:
        return f.get_userTasks_mapId_async(id, auth=auth, conn_url=conn_url)
    return f.get_userTasks_mapId(id, auth=auth, conn_url=conn_url)


def get_task(
    id: str,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> UserTask:
    """return task by `id` """
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getTaskById", vars={"id": id}, result_model=UserTask)
    if is_async:
        return f.get_userTasks_id_async(id, auth=auth, conn_url=conn_url)
    return f.get_userTasks_id(id, auth=auth, conn_url=conn_url)


def get_task_real(
    id: str,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> UserTask:
    """return task by real `id` """
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getTaskByRealId", vars={"id": id}, result_model=UserTask)
    if is_async:
        return f.get_userTasks_realId_async(id, auth=auth, conn_url=conn_url)
    return f.get_userTasks_realId(id, auth=auth, conn_url=conn_url)


def create_task(
    task_id: str,
    app_id: Optional[str] = None,
    apps_depends: Optional[List[str]] = None,
    tasks_depends: Optional[List[str]] = None,
    synthetic: bool = False,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Id:
    """create task"""
    if synthetic:
        assert app_id is None, "app_id should be None for synthetic task"
    else:
        assert app_id is not None, "app_id should be not None for not synthetic task"
    if batcher is None:
        batcher = Config.BATCHER
    if apps_depends is None:
        apps_depends = []
    if tasks_depends is None:
        tasks_depends = []
    data = UserTask(
        taskId=task_id,
        appId=app_id,
        appsDepends=apps_depends,
        tasksDepends=tasks_depends,
        synthetic=synthetic,
    )
    if batcher is not None:
        return batcher.add("postTask", data=data)
    if is_async:
        return f.post_userTasks_async(data, wait=wait, auth=auth, conn_url=conn_url)
    return f.post_userTasks(data, wait=wait, auth=auth, conn_url=conn_url)


def update_task(
    id: str,
    task_id: str,
    app_id: str,
    apps_depends: Optional[List[str]] = None,
    tasks_depends: Optional[List[str]] = None,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Info:
    """update task by `id` """
    if batcher is None:
        batcher = Config.BATCHER
    if apps_depends is None:
        apps_depends = []
    if tasks_depends is None:
        tasks_depends = []
    data = UserTask(
        taskId=task_id,
        appId=app_id,
        appsDepends=apps_depends,
        tasksDepends=tasks_depends,
    )
    if batcher is not None:
        return batcher.add("postTaskById", data=data, vars={"id": id})
    if is_async:
        return f.post_userTasks_id_async(id, data, wait=wait, auth=auth, conn_url=conn_url)
    return f.post_userTasks_id(id, data, wait=wait, auth=auth, conn_url=conn_url)


def delete_tasks(
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Info:
    """delete all user tasks"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("deleteTasks")
    if is_async:
        return f.delete_userTasks_async(wait=wait, auth=auth, conn_url=conn_url)
    return f.delete_userTasks(wait=wait, auth=auth, conn_url=conn_url)


def delete_task(
    id: str,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Info:
    """delete user task by `id` """
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("deleteTaskById", vars={"id": id})
    if is_async:
        return f.delete_userTasks_id_async(id, wait=wait, auth=auth, conn_url=conn_url)
    return f.delete_userTasks_id(id, wait=wait, auth=auth, conn_url=conn_url)


# UserPipelines


def get_pipelines(
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> ResultIds:
    """return pipelines ids for current user"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getPipelines", result_model=ResultIds)
    if is_async:
        return f.get_userPipelines_async(auth=auth, conn_url=conn_url)
    return f.get_userPipelines(auth=auth, conn_url=conn_url)


def get_pipelines_real(
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> ResultIds:
    """return pipelines real ids for current user"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getPipelinesReal", result_model=ResultIds)
    if is_async:
        return f.get_userPipelines_realIds_async(auth=auth, conn_url=conn_url)
    return f.get_userPipelines_realIds(auth=auth, conn_url=conn_url)


def get_pipelines_map(
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> ResultIdsMap:
    """return pipelines ids with real ids for current user"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getPipelinesMapIds", result_model=ResultIdsMap)
    if is_async:
        return f.get_userPipelines_mapIds_async(auth=auth, conn_url=conn_url)
    return f.get_userPipelines_mapIds(auth=auth, conn_url=conn_url)


def get_pipeline_map(
    id: str,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Id:
    """return real id by pipeline id for current user"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getPipelinesMapIdsById", vars={"id": id})
    if is_async:
        return f.get_userPipelines_mapId_async(id, auth=auth, conn_url=conn_url)
    return f.get_userPipelines_mapId(id, auth=auth, conn_url=conn_url)


def get_pipeline(
    id: str,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Pipeline:
    """return pipeline by `id` """
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getPipelineById", vars={"id": id}, result_model=Pipeline)
    if is_async:
        return f.get_userPipelines_id_async(id, auth=auth, conn_url=conn_url)
    return f.get_userPipelines_id(id, auth=auth, conn_url=conn_url)


def get_pipeline_real(
    id: str,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Pipeline:
    """return pipeline by real `id` """
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getPipelineByRealId", vars={"id": id}, result_model=Pipeline)
    if is_async:
        return f.get_userPipelines_realId_async(id, auth=auth, conn_url=conn_url)
    return f.get_userPipelines_realId(id, auth=auth, conn_url=conn_url)


def create_pipeline(
    pipeline_id: str,
    processors: Dict[str, Processor] = None,
    conditions: Dict[str, Condition] = None,
    results: Dict[str, List[Result]] = None,
    pull_collection_policy: PullCollectionPolicy = PullCollectionPolicy.IF_NOT_EXIST,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Id:
    """create pipeline"""
    if batcher is None:
        batcher = Config.BATCHER
    if processors is None:
        processors = {}
    if conditions is None:
        conditions = {}
    if results is None:
        results = {}
    data = Pipeline(
        pipelineId=pipeline_id,
        processors=processors,
        conditions=conditions,
        results=results,
        pullCollectionPolicy=pull_collection_policy,
    ).internal()
    if batcher is not None:
        return batcher.add("postPipeline", data=data)
    if is_async:
        return f.post_userPipelines_async(data, wait=wait, auth=auth, conn_url=conn_url)
    return f.post_userPipelines(data, wait=wait, auth=auth, conn_url=conn_url)


def update_pipeline(
    id: str,
    pipeline_id: str,
    processors: Dict[str, Processor] = None,
    conditions: Dict[str, Condition] = None,
    results: Dict[str, List[Result]] = None,
    pull_collection_policy: PullCollectionPolicy = PullCollectionPolicy.IF_NOT_EXIST,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Info:
    """update pipeline by `id` """
    if batcher is None:
        batcher = Config.BATCHER
    if processors is None:
        processors = {}
    if conditions is None:
        conditions = {}
    if results is None:
        results = {}
    data = Pipeline(
        pipelineId=pipeline_id,
        processors=processors,
        conditions=conditions,
        results=results,
        pullCollectionPolicy=pull_collection_policy,
    ).internal()
    if batcher is not None:
        return batcher.add("postPipelineById", data=data, vars={"id": id})
    if is_async:
        return f.post_userPipelines_id_async(id, data, wait=wait, auth=auth, conn_url=conn_url)
    return f.post_userPipelines_id(id, data, wait=wait, auth=auth, conn_url=conn_url)


def delete_pipelines(
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Info:
    """delete all user pipelines"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("deletePipelines")
    if is_async:
        return f.delete_userPipelines_async(wait=wait, auth=auth, conn_url=conn_url)
    return f.delete_userPipelines(wait=wait, auth=auth, conn_url=conn_url)


def delete_pipeline(
    id: str,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Info:
    """delete user pipeline by `id` """
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("deletePipelineById", vars={"id": id})
    if is_async:
        return f.delete_userPipelines_id_async(id, wait=wait, auth=auth, conn_url=conn_url)
    return f.delete_userPipelines_id(id, wait=wait, auth=auth, conn_url=conn_url)


# UserCfgs


def get_cfgs(
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> ResultIds:
    """return cfgs ids for current user"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getCfgs", result_model=ResultIds)
    if is_async:
        return f.get_userCfgs_async(auth=auth, conn_url=conn_url)
    return f.get_userCfgs(auth=auth, conn_url=conn_url)


def get_cfgs_real(
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> ResultIds:
    """return cfgs real ids for current user"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getCfgsReal", result_model=ResultIds)
    if is_async:
        return f.get_userCfgs_realIds_async(auth=auth, conn_url=conn_url)
    return f.get_userCfgs_realIds(auth=auth, conn_url=conn_url)


def get_cfgs_map(
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> ResultIdsMap:
    """return cfgs ids with real ids for current user"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getCfgsMapIds", result_model=ResultIdsMap)
    if is_async:
        return f.get_userCfgs_mapIds_async(auth=auth, conn_url=conn_url)
    return f.get_userCfgs_mapIds(auth=auth, conn_url=conn_url)



def get_cfg_map(
    id: str,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Id:
    """return real id by cfg id for current user"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getCfgsMapIdsById", vars={"id": id})
    if is_async:
        return f.get_userCfgs_mapId_async(id, auth=auth, conn_url=conn_url)
    return f.get_userCfgs_mapId(id, auth=auth, conn_url=conn_url)


def get_cfg(
    id: str,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> ResultUserCfg:
    """return cfg by `id` """
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getCfgById", vars={"id": id}, result_model=ResultUserCfg)
    if is_async:
        return f.get_userCfgs_id_async(id, auth=auth, conn_url=conn_url)
    return f.get_userCfgs_id(id, auth=auth, conn_url=conn_url)


def get_cfg_real(
    id: str,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> ResultUserCfg:
    """return cfg by real `id` """
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getCfgByRealId", vars={"id": id}, result_model=ResultUserCfg)
    if is_async:
        return f.get_userCfgs_realId_async(id, auth=auth, conn_url=conn_url)
    return f.get_userCfgs_realId(id, auth=auth, conn_url=conn_url)


def __fix_cfg(cfg: Union[Dict[str, Any], Alias.Json, Cfg]) -> str:
    if isinstance(cfg, Cfg):
        for app_setting in cfg.app_settings:
            if isinstance(app_setting.saveCollectionsName, str):
                app_setting.saveCollectionsName = [app_setting.saveCollectionsName]
        cfg_json = cfg.model_dump_json()
    else:
        if isinstance(cfg, Alias.Json):
            cfg = json.loads(cfg)
        assert isinstance(cfg, dict), "wrong cfg type"
        for app_setting in cfg.get("app_settings", []):
            if isinstance(name := app_setting.get("saveCollectionsName"), str):
                app_setting["saveCollectionsName"] = [name]
        cfg_json = json.dumps(cfg)
    return cfg_json


def create_cfg(
    cfg_id: str,
    cfg: Union[Dict[str, Any], Alias.Json, Cfg],
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Id:
    """create configuration file\n
    `cfg` must be json or dict or Cfg\n
    return `id` """
    if batcher is None:
        batcher = Config.BATCHER
    data = UserCfg(cfgId=cfg_id, cfg=__fix_cfg(cfg))
    if batcher is not None:
        return batcher.add("postCfg", data=data)
    if is_async:
        return f.post_userCfgs_async(data, wait=wait, auth=auth, conn_url=conn_url)
    return f.post_userCfgs(data, wait=wait, auth=auth, conn_url=conn_url)


def update_cfg(
    id: str,
    cfg_id: str,
    cfg: Union[Dict[str, Any], Alias.Json, Cfg],
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Info:
    """update configuration file\n
    `cfg` must be json or dict or Cfg"""
    if batcher is None:
        batcher = Config.BATCHER
    data = UserCfg(cfgId=cfg_id, cfg=__fix_cfg(cfg))
    if batcher is not None:
        return batcher.add("postCfgById", data=data, vars={"id": id})
    if is_async:
        return f.post_userCfgs_id_async(id, data, wait=wait, auth=auth, conn_url=conn_url)
    return f.post_userCfgs_id(id, data, wait=wait, auth=auth, conn_url=conn_url)


def delete_cfgs(
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Info:
    """delete all user cfgs"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("deleteCfgs")
    if is_async:
        return f.delete_userCfgs_async(wait=wait, auth=auth, conn_url=conn_url)
    return f.delete_userCfgs(wait=wait, auth=auth, conn_url=conn_url)


def delete_cfg(
    id: str,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Info:
    """delete user cfg by `id` """
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("deleteCfgs", vars={"id": id})
    if is_async:
        return f.delete_userCfgs_id_async(id, wait=wait, auth=auth, conn_url=conn_url)
    return f.delete_userCfgs_id(id, wait=wait, auth=auth, conn_url=conn_url)


# OperationResults


def get_operations_results(
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> ResultIds:
    """return list of operations ids"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getOperationResults", result_model=ResultIds)
    if is_async:
        return f.get_operationResults_async(auth=auth, conn_url=conn_url)
    return f.get_operationResults(auth=auth, conn_url=conn_url)


def get_operation_result(
    id: str,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> str:
    """return result by operation `id` if operation status is `OK` """
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getOperationResultById", vars={"id": id})
    if is_async:
        return f.get_operationResults_id_async(id, auth=auth, conn_url=conn_url)
    return f.get_operationResults_id(id, auth=auth, conn_url=conn_url)


def delete_operations_results(
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Info:
    """delete all operations results"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("deleteOperationResults")
    if is_async:
        return f.delete_operationResults_async(wait=wait, auth=auth, conn_url=conn_url)
    return f.delete_operationResults(wait=wait, auth=auth, conn_url=conn_url)


def delete_operation_result(
    id: str,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Info:
    """delete operation result by `id` """
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("deleteOperationResultById", vars={"id": id})
    if is_async:
        return f.delete_operationResults_id_async(id, wait=wait, auth=auth, conn_url=conn_url)
    return f.delete_operationResults_id(id, wait=wait, auth=auth, conn_url=conn_url)


# TempRun


def get_run_condition(
    id: str,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Condition:
    """return run condition by operation `id` for running task"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getCondition", vars={"operationId": id}, result_model=Condition)
    if is_async:
        return f.get_run_condition_async(id, auth=auth, conn_url=conn_url)
    return f.get_run_condition(id, auth=auth, conn_url=conn_url)


def get_run_active_runs(
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> ResultIds:
    """return list running operationIds"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getActiveRuns", result_model=ResultIds)
    if is_async:
        return f.get_run_activeRuns_async(auth=auth, conn_url=conn_url)
    return f.get_run_activeRuns(auth=auth, conn_url=conn_url)


def get_run_main_task_cfg(
    id: str,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> MainTaskCfg:
    """return mainTaskCfg by operation `id` for running task"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getMainTaskCfg", vars={"operationId": id}, result_model=MainTaskCfg)
    if is_async:
        return f.get_run_mainTaskCfg_async(id, auth=auth, conn_url=conn_url)
    return f.get_run_mainTaskCfg(id, auth=auth, conn_url=conn_url)


def get_run_main_pipeline_cfg(
    id: str,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> MainPipelineCfg:
    """return mainPipelineCfg by operation `id` for running pipeline"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getMainPipelineCfg", vars={"operationId": id}, result_model=MainPipelineCfg)
    if is_async:
        return f.get_run_mainPipelineCfg_async(id, auth=auth, conn_url=conn_url)
    return f.get_run_mainPipelineCfg(id, auth=auth, conn_url=conn_url)


def get_task_runs(
    task_id: str,
    cfg_id: Optional[str] = None,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> ResultIds:
    """return list running operationIds with `task_id` and `cfg_id` if specified"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        vars = {"taskId": task_id}
        if cfg_id is not None:
            vars["cfgId"] = cfg_id
        return batcher.add("getOperationsIds", vars=vars, result_model=ResultIds)
    if is_async:
        return f.get_run_operationsIds_async(task_id, cfg_id, auth=auth, conn_url=conn_url)
    return f.get_run_operationsIds(task_id, cfg_id, auth=auth, conn_url=conn_url)


# Manager


def logs(
    id: str,
    run_id: Optional[str] = None,
    force: bool = True,
    with_show: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> AppLogs:
    """return task logs by operation `id` and `run_id` """
    if batcher is None:
        batcher = Config.BATCHER
    data = LogsTask(operationId=id, runId=run_id, force=force)
    if batcher is not None:
        return batcher.add("logs", data=data, result_model=AppLogs)
    if is_async:
        return f.get_manager_logs_async(data, with_show=with_show, auth=auth, conn_url=conn_url)
    return f.get_manager_logs(data, with_show=with_show, auth=auth, conn_url=conn_url)


def logs_app(
    id: str,
    task_id: str,
    app_id: str,
    run_id: Optional[str] = None,
    force: bool = True,
    with_show: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> AppLogs:
    """return app logs by operation `id`, `run_id`, `task_id` (that "null" if not exist) and `app_id` """
    if batcher is None:
        batcher = Config.BATCHER
    data = LogsTask(
        operationId=id, runId=run_id, appId=app_id, taskId=task_id, force=force
    )
    if batcher is not None:
        return batcher.add("logs", data=data, result_model=AppLogs)
    if is_async:
        return f.get_manager_logs_async(data, with_show=with_show, auth=auth, conn_url=conn_url)
    return f.get_manager_logs(data, with_show=with_show, auth=auth, conn_url=conn_url)


def logs_clickhouse(
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Json:
    """return all clickhouse logs"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("clickhouseAll")
    if is_async:
        return f.get_clickhouse_all_async(auth=auth, conn_url=conn_url)
    return f.get_clickhouse_all(auth=auth, conn_url=conn_url)


def logs_clickhouse_id(
    id: str,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Json:
    """return clickhouse logs by operation `id` """
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("clickhouseId", vars={"operationId": id})
    if is_async:
        return f.get_clickhouse_id_async(id, auth=auth, conn_url=conn_url)
    return f.get_clickhouse_id(id, auth=auth, conn_url=conn_url)


def get_dag_key_value(
    id: str,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Json:
    """return key-value cfg from dag by operation `id` """
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getDagKeyValue", vars={"operationId": id})
    if is_async:
        return f.get_manager_dagKeyValue_operationId_async(id, auth=auth, conn_url=conn_url)
    return f.get_manager_dagKeyValue_operationId(id, auth=auth, conn_url=conn_url)


def update_dag_key_value(
    data: Dict[str, str],
    operationId: str,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> None:
    """update key-value cfg from dag by operation `id` and `data` """
    if batcher is None:
        batcher = Config.BATCHER
    data = KeysValues(data=data, operationId=operationId)
    if batcher is not None:
        return batcher.add("postDagKeyValue", data=data)
    if is_async:
        return f.post_manager_dagKeyValue_async(
            data,
            wait=wait,
            auth=auth,
            conn_url=conn_url,
        )
    return f.post_manager_dagKeyValue(
        data,
        wait=wait,
        auth=auth,
        conn_url=conn_url,
    )


def get_app_info(
    id: str,
    parse: bool = False,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Union[Alias.Json, AppFunctionsInfo]:
    """return json with functions app info, `id` is appId"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("appInfo", vars={"appId": id}, result_model=AppFunctionsInfo if parse else None)
    if is_async:
        return f.get_app_info_async(id, parse=parse, auth=auth, conn_url=conn_url)
    return f.get_app_info(id, parse=parse, auth=auth, conn_url=conn_url)


def get_app_info_by_real_id(
    id: str,
    parse: bool = False,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Union[Alias.Json, AppFunctionsInfo]:
    """return json with functions app info, `id` is real id for app"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("appInfoRealId", vars={"appId": id}, result_model=AppFunctionsInfo if parse else None)
    if is_async:
        return f.get_app_info_by_real_id_async(id, parse=parse, auth=auth, conn_url=conn_url)
    return f.get_app_info_by_real_id(id, parse=parse, auth=auth, conn_url=conn_url)


def get_image_info(
    image_ref: str,
    image_auth: Optional[AUTH] = None,
    parse: bool = False,
    *,
    use_system_auth: bool = False,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Union[Alias.Json, AppFunctionsInfo]:
    """return json with functions image info"""
    if batcher is None:
        batcher = Config.BATCHER
    image_user = image_auth[0] if image_auth is not None else Config.USERNAME if use_system_auth else None
    image_token = image_auth[1] if image_auth is not None else Config.TOKEN if use_system_auth else None
    if Config.WITH_WARNINGS and (image_user is None or image_token is None):
        Config.logger.warning("image_auth not set")
    data = JsonImage(ref=image_ref, user=image_user, token=image_token)
    if batcher is not None:
        return batcher.add("imageInfo", data=data, result_model=AppFunctionsInfo if parse else None)
    if is_async:
        return f.get_image_info_async(data, parse=parse, auth=auth, conn_url=conn_url)
    return f.get_image_info(data, parse=parse, auth=auth, conn_url=conn_url)


def get_task_schedules(
    operation_id: str,
    with_show: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Schedules:
    """return schedule ids by `operation_id` """
    if batcher is None:
        batcher = Config.BATCHER
    data = Operation(operationId=operation_id)
    if batcher is not None:
        return batcher.add("sendTaskSchedules", data=data, result_model=Schedules)
    if is_async:
        return f.get_task_schedules_async(
            data, with_show=with_show, auth=auth, conn_url=conn_url
        )
    return f.get_task_schedules(
        data, with_show=with_show, auth=auth, conn_url=conn_url
    )


# FIXME check component
def task_full(
    task_id: str,
    cfg_id: str,
    info_url: Optional[str] = None,
    debug_mode: bool = False,
    core_manage: bool = False,
    single_request: bool = False,
    profile_mode: Optional[str] = None,
    save_fails: bool = True,
    with_show: bool = True,
    long: bool = False,
    long_timeout: Optional[int] = WAIT_RESULT_TIMEOUT,
    scaleInfo: List[ScaleInfo] = None,
    component: TaskComponent = None,
    policy: TaskPolicy = None,
    schedule: Optional[Schedule] = None,
    restrictions: Optional[Restrictions] = None,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Union[Alias.Id, AppLogs]:
    """prepare, run and stop task by `task_id`, `cfg_id` and other

    Args:
        task_id (str): task id
        cfg_id (str): cfg id
        info_url (Optional[str]): url to which the request is sent. If not specified, the default url is used. Rewrite msg_url from cfg if exist
        debug_mode (bool): more error info if True
        core_manage (bool): whether it is necessary to send requests through 'CORE' (otherwise through 'DAG'). Faster with 'False'. The version with 'True' will have more functionality later
        single_request (bool): if True, one request is sent (otherwise sequentially for input, processor, output). It's faster. But the ability to stop when switching between input, processor, output disappears
        profile_mode (Optional[str]): extra prints. possible modes: [None, "no", "all", "time", "df_info", "df_show"]
        with_show (bool): show result (like for each operation)
        long (bool): for long runs (more than 10 minutes). If more has passed, stops trying to get the result of the run, but does not stop the run itself
        long_timeout (Optional[int]): default timeout for long run (hour by default). If 'long=False' ignored. If None, then there is no limit. Doesn't stop the task, just stops trying to get the run result
        scaleInfo (List[ScaleInfo]): info about apps scale
        component: (TaskComponent): which component should run it (dag id, base id - None)
        policy: (TaskPolicy): policy for task
        schedule: (Optional[Schedule]): schedule task settings - return scheduleId instead of operationId
        restrictions: (Optional[Restrictions]): permissions to handle deployment
        wait (bool): is it worth waiting for the result or immediately return `operation_id`
        auth (Optional[AUTH]): redefined auth if not None"""
    if batcher is None:
        batcher = Config.BATCHER
    if scaleInfo is None:
        scaleInfo = []
    if component is None:
        component = TaskComponent()
    if policy is None:
        policy = TaskPolicy()
    if restrictions is None:
        restrictions = Restrictions()
    data = MainTask(
        taskId=task_id,
        cfgId=cfg_id,
        infoUrl=info_url,
        debugMode=debug_mode,
        coreManage=core_manage,
        kafkaMode=False,
        singleRequest=single_request,
        kafkaModeUrl=None,
        tlWithoutData=None,
        waitRuns=True,
        profileMode=profile_mode,
        withLogs=True,
        saveFails=save_fails,
        scaleInfo=scaleInfo,
        component=component,
        policy=policy,
        schedule=schedule,
        restrictions=restrictions,
    )
    if batcher is not None:
        return batcher.add("sendTask", data=data, result_model=AppLogs)
    if is_async:
        return f.post_manager_task_async(
            data,
            with_show=with_show,
            long=long,
            long_timeout=long_timeout,
            wait=wait,
            auth=auth,
            conn_url=conn_url,
        )
    return f.post_manager_task(
        data,
        with_show=with_show,
        long=long,
        long_timeout=long_timeout,
        wait=wait,
        auth=auth,
        conn_url=conn_url,
    )


def task_prepare(
    task_id: str,
    cfg_id: Optional[str] = None,
    info_url: Optional[str] = None,
    debug_mode: bool = False,
    core_manage: bool = False,
    kafka_mode: bool = False,
    single_request: bool = False,
    kafka_mode_url_response: Optional[str] = None,
    with_listener: bool = False,
    tl_without_data: Optional[int] = None,
    wait_runs: bool = True,
    with_logs: bool = False,
    profile_mode: Optional[str] = None,
    save_fails: bool = True,
    with_show: bool = None,
    long: bool = False,
    long_timeout: int = WAIT_RESULT_TIMEOUT,
    scaleInfo: List[ScaleInfo] = None,
    component: TaskComponent = None,
    policy: TaskPolicy = None,
    restrictions: Optional[Restrictions] = None,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Union[Alias.Id, AppLogs]:
    """prepare task by `task_id`, `cfg_id` and other, return `operation_id`

    Args:
        task_id (str): task id
        cfg_id (str, can be None only for synthetic task): cfg id
        info_url (Optional[str]): url to which the request is sent. If not specified, the default url is used. Rewrite msg_url from cfg if exist
        debug_mode (bool): more error info if True
        core_manage (bool): whether it is necessary to send requests through 'CORE' (otherwise through 'DAG'). Faster with 'False'. The version with 'True' will have more functionality later
        kafka_mode (bool): send data via kafka ('kafka_send') if True, doesn't work with 'task_run'. Works only through 'task_run' otherwise
        single_request (bool): if True, one request is sent (otherwise sequentially for input, processor, output). It's faster. But the ability to stop when switching between input, processor, output disappears
        kafka_mode_url_response (Optional[str]): url, only for send result in kafka mode (if None - return result in operation)
        with_listener (bool): use only if 'kafka_mode=True'. If False 'kafka_send' just send msg in kafka, no return
        tl_without_data (Optional[int]): the time after which the run will stop, if no data for the launch was received during it. Relevant for preparation
        wait_runs (bool): no wait runs if False
        with_logs (bool): return prepare logs if True after end
        profile_mode (Optional[str]): extra prints. possible modes: [None, "no", "all", "time", "df_info", "df_show"]
        with_show (bool): show result (like for each operation, default equals with_logs arg)
        long (bool): for long runs (more than 10 minutes). If more has passed, stops trying to get the result of the run, but does not stop the run itself
        long_timeout (Optional[int]): default timeout for long run (hour by default). If 'long=False' ignored. If None, then there is no limit. Doesn't stop the task, just stops trying to get the run result
        scaleInfo (List[ScaleInfo]): info about apps scale
        component: (TaskComponent): which component should run it (dag id, base id - None)
        policy: (TaskPolicy): policy for task
        restrictions: (Optional[Restrictions]): permissions to handle deployment
        wait (bool): is it worth waiting for the result or immediately return `operation_id`
        auth (Optional[AUTH]): redefined auth if not None"""
    if batcher is None:
        batcher = Config.BATCHER
    if kafka_mode_url_response is not None and kafka_mode is False:
        Config.logger.info(
            '"kafka_mode_url_response" ignored because "kafka_mode" = False'
        )
        kafka_mode_url_response = None
    if with_show is None:
        with_show = with_logs
    if scaleInfo is None:
        scaleInfo = []
    if component is None:
        component = TaskComponent()
    if policy is None:
        policy = TaskPolicy()
    if restrictions is None:
        restrictions = Restrictions()
    data = MainTask(
        taskId=task_id,
        cfgId=cfg_id,
        infoUrl=info_url,
        debugMode=debug_mode,
        coreManage=core_manage,
        kafkaMode=kafka_mode,
        singleRequest=single_request,
        kafkaModeUrl=kafka_mode_url_response,
        withListener=with_listener,
        tlWithoutData=tl_without_data,
        run=False,
        waitRuns=wait_runs,
        withLogs=with_logs,
        saveFails=save_fails,
        profileMode=profile_mode,
        scaleInfo=scaleInfo,
        component=component,
        policy=policy,
        restrictions=restrictions,
    )
    if batcher is not None:
        return batcher.add("sendTask", data=data, result_model=AppLogs)
    if is_async:
        return f.post_manager_task_async(
            data,
            with_show=with_show,
            long=long,
            long_timeout=long_timeout,
            wait=wait,
            auth=auth,
            conn_url=conn_url,
        )
    return f.post_manager_task(
        data,
        with_show=with_show,
        long=long,
        long_timeout=long_timeout,
        wait=wait,
        auth=auth,
        conn_url=conn_url,
    )


def task_run(
    operation_id: str,
    cfg_id: Optional[str] = None,
    info_url: Optional[str] = None,
    debug_mode: Optional[bool] = None,
    run_id: Optional[str] = None,
    single_request: Optional[bool] = None,
    profile_mode: Optional[str] = None,
    with_show: bool = None,
    long: bool = False,
    long_timeout: int = WAIT_RESULT_TIMEOUT,
    with_logs: bool = False,
    schedule: Optional[Schedule] = None,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Optional[Union[Alias.Id, AppLogs]]:
    """run prepared task by `operation_id` with `cfg_id` and other overridden parameters

    Args:
        operation_id (str): `operation_id`, that returned from 'task_prepare'
        cfg_id (Optional[str]): cfg id, override default cfg id (from 'task_prepare') if exist
        info_url (Optional[str]): Rewrite for this run if exist
        debug_mode (Optional[bool]): Rewrite for this run if exist
        run_id (Optional[str]): run id for current run, must be different if given
        single_request (Optional[bool]): Rewrite for this run if exist
        profile_mode (Optional[str]): Rewrite for this run if exist
        with_show (bool): show result (like for each operation, default equals with_logs arg)
        long (bool): for long runs (more than 10 minutes). If more has passed, stops trying to get the result of the run, but does not stop the run itself
        long_timeout (Optional[int]): default timeout for long run (hour by default). If 'long=False' ignored. If None, then there is no limit. Doesn't stop the task, just stops trying to get the run result
        with_logs (bool): return run logs if True after end
        schedule: (Optional[Schedule]): schedule task runs settings - return scheduleId instead of operationId
        wait (bool): is it worth waiting for the result or immediately return `operation_id`
        auth (Optional[AUTH]): redefined auth if not None"""
    if batcher is None:
        batcher = Config.BATCHER
    if run_id is None:
        run_id = rand_str(15)
    if with_show is None:
        with_show = with_logs
    data = RunTask(
        operationId=operation_id,
        cfgId=cfg_id,
        infoUrl=info_url,
        debugMode=debug_mode,
        runId=run_id,
        singleRequest=single_request,
        profileMode=profile_mode,
        withLogs=with_logs,
        schedule=schedule,
    )
    if batcher is not None:
        return batcher.add("sendTaskRun", data=data, result_model=AppLogs if with_logs or schedule is not None else None)
    if is_async:
        return f.post_manager_task_run_async(
            data,
            with_show=with_show,
            long=long,
            long_timeout=long_timeout,
            wait=wait,
            auth=auth,
            conn_url=conn_url,
        )
    return f.post_manager_task_run(
        data,
        with_show=with_show,
        long=long,
        long_timeout=long_timeout,
        wait=wait,
        auth=auth,
        conn_url=conn_url,
    )


def pipeline_full(
    pipeline_id: str,
    cfg_id: str,
    info_url: Optional[str] = None,
    debug_mode: bool = False,
    core_manage: bool = False,
    single_request: bool = False,
    profile_mode: Optional[str] = None,
    component: TaskComponent = None,
    policy: TaskPolicy = None,
    schedule: Optional[Schedule] = None,
    restrictions: Optional[Restrictions] = None,
    scaleInfo: List[ScaleInfo] = None,
    save_fails: bool = True,
    with_show: bool = True,
    long: bool = False,
    long_timeout: Optional[int] = WAIT_RESULT_TIMEOUT,
    return_response: bool = False,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Union[Alias.Id, AppLogs]:
    if batcher is None:
        batcher = Config.BATCHER
    if scaleInfo is None:
        scaleInfo = []
    if component is None:
        component = TaskComponent()
    if policy is None:
        policy = TaskPolicy()
    if restrictions is None:
        restrictions = Restrictions()
    data = MainPipeline(
        pipelineId=pipeline_id,
        cfgId=cfg_id,
        infoUrl=info_url,
        debugMode=debug_mode,
        coreManage=core_manage,
        kafkaMode=False,
        singleRequest=single_request,
        tlWithoutData=None,
        waitRuns=True,
        profileMode=profile_mode,
        withLogs=True,
        component=component,
        policy=policy,
        schedule=schedule,
        restrictions=restrictions,
        scaleInfo=scaleInfo,
        withListener=False,
        kafkaModeUrl=None,
        run=True,
        saveFails=save_fails,
    )
    if batcher is not None:
        return batcher.add("sendPipeline", data=data, result_model=AppLogs)
    if is_async:
        return f.post_manager_pipeline_async(
            data,
            with_show=with_show,
            long=long,
            long_timeout=long_timeout,
            return_response=return_response,
            wait=wait,
            auth=auth,
            conn_url=conn_url,
        )
    return f.post_manager_pipeline(
        data,
        with_show=with_show,
        long=long,
        long_timeout=long_timeout,
        return_response=return_response,
        wait=wait,
        auth=auth,
        conn_url=conn_url,
    )


def pipeline_prepare(
    pipeline_id: str,
    cfg_id: str,
    info_url: Optional[str] = None,
    debug_mode: bool = False,
    core_manage: bool = False,
    kafka_mode: bool = False,
    single_request: bool = False,
    tl_without_data: Optional[int] = None,
    wait_runs: bool = True,
    profile_mode: Optional[str] = None,
    with_logs: bool = False,
    component: TaskComponent = None,
    policy: TaskPolicy = None,
    restrictions: Optional[Restrictions] = None,
    scaleInfo: List[ScaleInfo] = None,
    with_listener: bool = False,
    kafka_mode_url_response: Optional[str] = None,
    synthetic: bool = False,
    save_fails: bool = True,
    with_show: bool = True,
    long: bool = False,
    long_timeout: Optional[int] = WAIT_RESULT_TIMEOUT,
    return_response: bool = False,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Union[Alias.Id, AppLogs]:
    if batcher is None:
        batcher = Config.BATCHER
    if scaleInfo is None:
        scaleInfo = []
    if component is None:
        component = TaskComponent()
    if policy is None:
        policy = TaskPolicy()
    if restrictions is None:
        restrictions = Restrictions()
    data = MainPipeline(
        pipelineId=pipeline_id,
        cfgId=cfg_id,
        infoUrl=info_url,
        debugMode=debug_mode,
        coreManage=core_manage,
        kafkaMode=kafka_mode,
        singleRequest=single_request,
        tlWithoutData=tl_without_data,
        waitRuns=wait_runs,
        profileMode=profile_mode,
        withLogs=with_logs,
        component=component,
        policy=policy,
        restrictions=restrictions,
        scaleInfo=scaleInfo,
        withListener=with_listener,
        kafkaModeUrl=kafka_mode_url_response,
        run=False,
        synthetic=synthetic,
        saveFails=save_fails,
    )
    if batcher is not None:
        return batcher.add("sendPipeline", data=data, result_model=AppLogs)
    if is_async:
        return f.post_manager_pipeline_async(
            data,
            with_show=with_show,
            long=long,
            long_timeout=long_timeout,
            return_response=return_response,
            wait=wait,
            auth=auth,
            conn_url=conn_url,
        )
    return f.post_manager_pipeline(
        data,
        with_show=with_show,
        long=long,
        long_timeout=long_timeout,
        return_response=return_response,
        wait=wait,
        auth=auth,
        conn_url=conn_url,
    )


def task_unschedule(
    schedule_id: str,
    with_show: bool = True,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Info:
    """unschedule task by `schedule_id` """
    if batcher is None:
        batcher = Config.BATCHER
    data = UnscheduleOperation(scheduleId=schedule_id)
    if batcher is not None:
        return batcher.add("sendTaskUnschedule", data=data)
    if is_async:
        return f.post_manager_task_unschedule_async(
            data, with_show=with_show, wait=wait, auth=auth, conn_url=conn_url
        )
    return f.post_manager_task_unschedule(
        data, with_show=with_show, wait=wait, auth=auth, conn_url=conn_url
    )


def task_stop(
    operation_id: str,
    with_logs: bool = False,
    info_url: Optional[str] = None,
    with_show: bool = None,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Optional[Union[Alias.Id, AppLogs]]:
    """stop task by `operation_id`

    Args:
       operation_id (str): `operation_id`, that returned from 'task_prepare', or just operation_id for runned task
       with_logs (bool): return logs for task if True
       info_url (Optional[str]): send also result to info_url if it exist and 'with_logs=True'
       with_show (bool): show result (like for each operation, default equals with_logs arg)
       wait (bool): is it worth waiting for the result or immediately return `operation_id`
       auth (Optional[AUTH]): redefined auth if not None"""
    if batcher is None:
        batcher = Config.BATCHER
    if with_show is None:
        with_show = with_logs
    data = StopOperation(operationId=operation_id, withLogs=with_logs, infoUrl=info_url)
    if batcher is not None:
        return batcher.add("sendTaskStop", data=data, result_model=AppLogs if with_logs else None)
    if is_async:
        return f.post_manager_task_stop_async(
            data, with_show=with_show, wait=wait, auth=auth, conn_url=conn_url
        )
    return f.post_manager_task_stop(
        data, with_show=with_show, wait=wait, auth=auth, conn_url=conn_url
    )


def task_stop_all(
    with_logs: bool = False,
    info_url: Optional[str] = None,
    with_show: bool = True,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Json:
    """stop all tasks"""
    if batcher is None:
        batcher = Config.BATCHER
    data = StopOperationMany(withLogs=with_logs, infoUrl=info_url)
    if batcher is not None:
        return batcher.add("sendTaskStopAll", data=data, result_model=AppLogs if with_logs else None)
    if is_async:
        return f.post_manager_task_stop_all_async(
            data, with_show=with_show, wait=wait, auth=auth, conn_url=conn_url
        )
    return f.post_manager_task_stop_all(
        data, with_show=with_show, wait=wait, auth=auth, conn_url=conn_url
    )


def task_resume(
    operation_id: str,
    with_show: bool = True,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Empty:
    """resume task by `operation_id` """
    if batcher is None:
        batcher = Config.BATCHER
    data = Operation(operationId=operation_id)
    if batcher is not None:
        return batcher.add("sendTaskResume", data=data)
    if is_async:
        return f.post_manager_task_resume_async(
            data, with_show=with_show, wait=wait, auth=auth, conn_url=conn_url
        )
    return f.post_manager_task_resume(
        data, with_show=with_show, wait=wait, auth=auth, conn_url=conn_url
    )


def task_pause(
    operation_id: str,
    with_show: bool = True,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Empty:
    """pause task by `operation_id` """
    if batcher is None:
        batcher = Config.BATCHER
    data = Operation(operationId=operation_id)
    if batcher is not None:
        return batcher.add("sendTaskPause", data=data)
    if is_async:
        return f.post_manager_task_pause_async(
            data, with_show=with_show, wait=wait, auth=auth, conn_url=conn_url
        )
    return f.post_manager_task_pause(
        data, with_show=with_show, wait=wait, auth=auth, conn_url=conn_url
    )


def app_stop(
    operation_id: str,
    task_id: Optional[str],
    app_id: str,
    run_id: str,
    with_show: bool = True,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Empty:
    """stop app by `operation_id`, `task_id` and `app_id` """
    if batcher is None:
        batcher = Config.BATCHER
    data = AppManage(
        operationId=operation_id, taskId=task_id, appId=app_id, runId=run_id
    )
    if batcher is not None:
        return batcher.add("sendAppStop", data=data)
    if is_async:
        return f.post_manager_app_stop_async(
            data, with_show=with_show, wait=wait, auth=auth, conn_url=conn_url
        )
    return f.post_manager_app_stop(
        data, with_show=with_show, wait=wait, auth=auth, conn_url=conn_url
    )


def app_resume(
    operation_id: str,
    task_id: Optional[str],
    app_id: str,
    run_id: str,
    with_show: bool = True,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Empty:
    """resume app by `operation_id`, `task_id` and `app_id` """
    if batcher is None:
        batcher = Config.BATCHER
    data = AppManage(
        operationId=operation_id, taskId=task_id, appId=app_id, runId=run_id
    )
    if batcher is not None:
        return batcher.add("sendAppResume", data=data)
    if is_async:
        return f.post_manager_app_resume_async(
            data, with_show=with_show, wait=wait, auth=auth, conn_url=conn_url
        )
    return f.post_manager_app_resume(
        data, with_show=with_show, wait=wait, auth=auth, conn_url=conn_url
    )


def app_pause(
    operation_id: str,
    task_id: Optional[str],
    app_id: str,
    run_id: str,
    with_show: bool = True,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Empty:
    """pause app by `operation_id`, `task_id` and `app_id` """
    if batcher is None:
        batcher = Config.BATCHER
    data = AppManage(
        operationId=operation_id, taskId=task_id, appId=app_id, runId=run_id
    )
    if batcher is not None:
        return batcher.add("sendAppPause", data=data)
    if is_async:
        return f.post_manager_app_pause_async(
            data, with_show=with_show, wait=wait, auth=auth, conn_url=conn_url
        )
    return f.post_manager_app_pause(
        data, with_show=with_show, wait=wait, auth=auth, conn_url=conn_url
    )


# Limits


def get_user_limits(
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> UserLimits:
    """return limits for user"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getLimits", result_model=UserLimits)
    if is_async:
        return f.get_limits_async(auth=auth, conn_url=conn_url)
    return f.get_limits(auth=auth, conn_url=conn_url)


def update_user_limits(
    memory_request: Optional[int] = None,
    memory_limit: Optional[int] = None,
    cpu_request: Optional[int] = None,
    cpu_limit: Optional[int] = None,
    storage_request: Optional[int] = None,
    storage_limit: Optional[int] = None,
    gpu_disk: Optional[int] = None,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Info:
    """update limits for user"""
    if batcher is None:
        batcher = Config.BATCHER
    data = Limits(memoryRequest=memory_request, memoryLimit=memory_limit, cpuRequest=cpu_request, cpuLimit=cpu_limit, storageRequest=storage_request, storageLimit=storage_limit, gpuDisk=gpu_disk)
    if batcher is not None:
        return batcher.add("postLimits", data=data)
    if is_async:
        return f.post_limits_async(
            data, wait=wait, auth=auth, conn_url=conn_url
        )
    return f.post_limits(
        data, wait=wait, auth=auth, conn_url=conn_url
    )


def update_user_limits_scope(
    login: str,
    app_memory_request: Optional[int] = None,
    app_memory_limit: Optional[int] = None,
    app_cpu_request: Optional[int] = None,
    app_cpu_limit: Optional[int] = None,
    app_storage_request: Optional[int] = None,
    app_storage_limit: Optional[int] = None,
    assets_limit: Optional[int] = None,
    allow_common_gpu: Optional[bool] = None,
    gpu_disk_max: Optional[int] = None,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Info:
    """update limits scope for user, for superuser/admin"""
    if batcher is None:
        batcher = Config.BATCHER
    data = LimitsScope(login=login, appMemoryRequest=app_memory_request, appMemoryLimit=app_memory_limit, appCpuRequest=app_cpu_request, appCpuLimit=app_cpu_limit, appStorageRequest=app_storage_request, appStorageLimit=app_storage_limit, assetsLimit=assets_limit, allowCommonGpu=allow_common_gpu, gpuDiskMax=gpu_disk_max)
    if batcher is not None:
        return batcher.add("postUserLimits", data=data)
    if is_async:
        return f.post_user_limits_async(
            data, wait=wait, auth=auth, conn_url=conn_url
        )
    return f.post_user_limits(
        data, wait=wait, auth=auth, conn_url=conn_url
    )


# HandlerUrls


def get_user_handler_url(
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> str:
    """return handler url for user"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getHandlerUrls")
    if is_async:
        return f.get_handler_url_async(auth=auth, conn_url=conn_url)
    return f.get_handler_url(auth=auth, conn_url=conn_url)


def update_user_handler_url(
    url: Optional[str] = None,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Info:
    """update handler url for user"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("postHandlerUrls", vars={"url": url})
    if is_async:
        return f.post_handler_url_async(
            url, wait=wait, auth=auth, conn_url=conn_url
        )
    return f.post_handler_url(
        url, wait=wait, auth=auth, conn_url=conn_url
    )


# Analytics


def get_analytics(
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> UserAnalyticsBatch:
    """return all analytics for current user """
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getAnalytics", result_model=UserAnalyticsBatch)
    if is_async:
        return f.get_analytics_async(auth=auth, conn_url=conn_url)
    return f.get_analytics(auth=auth, conn_url=conn_url)


def get_analytics_by_id(
    id: str,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> UserAnalytics:
    """return analytics by `id` """
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getAnalyticsById", vars={"id": id}, result_model=UserAnalytics)
    if is_async:
        return f.get_analytics_by_id_async(id, auth=auth, conn_url=conn_url)
    return f.get_analytics_by_id(id, auth=auth, conn_url=conn_url)


def get_analytics_by_name(
    name: str,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> UserAnalyticsBatch:
    """return analytics by `name` """
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getAnalyticsByName", vars={"name": name}, result_model=UserAnalyticsBatch)
    if is_async:
        return f.get_analytics_by_name_async(name, auth=auth, conn_url=conn_url)
    return f.get_analytics_by_name(name, auth=auth, conn_url=conn_url)


def create_analytics(
    data: Dict[str, Any],
    name: str,
    timestamp: Optional[str] = None,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Id:
    """save analytics with `data`, `name` and `timestamp`, return `id` """
    if batcher is None:
        batcher = Config.BATCHER
    data = UserAnalytics(name=name, data=data, timestamp=timestamp)
    if batcher is not None:
        return batcher.add("postAnalytics", data=data)
    if is_async:
        return f.post_analytics_async(
            data, wait=wait, auth=auth, conn_url=conn_url
        )
    return f.post_analytics(
        data, wait=wait, auth=auth, conn_url=conn_url
    )


def update_analytics(
    id: str,
    data: Dict[str, Any],
    name: str,
    timestamp: Optional[str] = None,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Id:
    """update analytics by `id` with `data`, `name` and `timestamp`, return `id` """
    if batcher is None:
        batcher = Config.BATCHER
    data = UserAnalytics(name=name, data=data, timestamp=timestamp, id=id)
    if batcher is not None:
        return batcher.add("postAnalytics", data=data)
    if is_async:
        return f.post_analytics_async(
            data, wait=wait, auth=auth, conn_url=conn_url
        )
    return f.post_analytics(
        data, wait=wait, auth=auth, conn_url=conn_url
    )


def update_analytics_many(
    data: List[UserAnalytics],
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> ResultIds:
    """update analytics by list of UserAnalytics, return ResultIds """
    if batcher is None:
        batcher = Config.BATCHER
    data = UserAnalyticsBatch(data=data)
    if batcher is not None:
        return batcher.add("postAnalyticsMany", data=data, result_model=ResultIds)
    if is_async:
        return f.post_analytics_many_async(
            data, wait=wait, auth=auth, conn_url=conn_url
        )
    return f.post_analytics_many(
        data, wait=wait, auth=auth, conn_url=conn_url
    )


# RunsInfo


def get_last_runs(
    count: int = 10,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> ResultIds:
    """return last operationIds (prepared task/pipeline)"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getLastOperationsIds", vars={"count": count}, result_model=ResultIds)
    if is_async:
        return f.get_runsInfo_last_operation_ids_async(count, auth=auth, conn_url=conn_url)
    return f.get_runsInfo_last_operation_ids(count, auth=auth, conn_url=conn_url)


def get_last_failed_runs(
    count: int = 5,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> ResultIds:
    """return last operationIds (failed prepare/run of task/pipeline)"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getLastFailedOperationsIds", vars={"count": count}, result_model=ResultIds)
    if is_async:
        return f.get_runsInfo_last_failed_operation_ids_async(count, auth=auth, conn_url=conn_url)
    return f.get_runsInfo_last_failed_operation_ids(count, auth=auth, conn_url=conn_url)


# WSApp


def get_ws_apps(
    only_active: bool = False,
    full: bool = False,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Union[ResultIds, WSApps]:
    """return list ids or list ws apps structure"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getWSApps", vars={"onlyActive": only_active, "full": full}, result_model=WSApps if full else ResultIds)
    if is_async:
        return f.get_ws_apps_async(only_active, full, auth=auth, conn_url=conn_url)
    return f.get_ws_apps(only_active, full, auth=auth, conn_url=conn_url)


def get_ws_app(
    id: str,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> WSApp:
    """return ws app struct by `id` """
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("getWSAppById", vars={"id": id}, result_model=WSApp)
    if is_async:
        return f.get_ws_apps_id_async(id, auth=auth, conn_url=conn_url)
    return f.get_ws_apps_id(id, auth=auth, conn_url=conn_url)


def create_ws_app(
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> WSApp:
    """save ws app, return ws app struct"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("postWSApp")
    if is_async:
        return f.post_ws_apps_async(wait=wait, auth=auth, conn_url=conn_url)
    return f.post_ws_apps(wait=wait, auth=auth, conn_url=conn_url)


def delete_ws_app(
    id: str,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Info:
    """delete ws app by `id` """
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("deleteWSAppById", vars={"id": id})
    if is_async:
        return f.delete_ws_apps_id_async(id, wait=wait, auth=auth, conn_url=conn_url)
    return f.delete_ws_apps_id(id, wait=wait, auth=auth, conn_url=conn_url)


def delete_ws_apps(
    only_not_active: bool = False,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Info:
    """delete all ws apps (only not active if `only_not_active`)"""
    if batcher is None:
        batcher = Config.BATCHER
    if batcher is not None:
        return batcher.add("deleteWSApps", vars={"onlyNotActive": only_not_active})
    if is_async:
        return f.delete_ws_apps_async(only_not_active, wait=wait, auth=auth, conn_url=conn_url)
    return f.delete_ws_apps(only_not_active, wait=wait, auth=auth, conn_url=conn_url)


# kafka


async def kafka_send(
    operation_id: str,
    run_id: Optional[str] = None,
    data: Dict[str, str] = None,
    metadata: Optional[Dict[str, Union[str, Dict[str, Any]]]] = None,
    with_show: bool = False,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
) -> Union[Alias.Info, KafkaMsg]:  # TODO add tl
    """send msg to kafka for task by `operation_id`, `run_id` and `data` """
    assert data is not None, "data should exists in kafka_send"
    if batcher is None:
        batcher = Config.BATCHER
    if run_id is None:
        run_id = rand_str(15)
    if metadata is not None:
        real_metadata = {}
        for key, value in metadata.items():
            if isinstance(value, dict):
                value = json.dumps(value)
            if isinstance(value, str):
                real_metadata[key] = value
            elif Config.WITH_WARNINGS:
                Config.logger.warning(f"wrong metadata type, ignore {key}")
    else:
        real_metadata = {}
    data = KafkaMsg(
        operationId=operation_id, runId=run_id, data=data, metadata=real_metadata
    )
    if batcher is not None:
        return batcher.add("sendKafkaMsg", data=data, result_model=KafkaMsg)
    return await f.kafka_send(
        data, with_show=with_show, auth=auth, conn_url=conn_url
    )


# other


def create_collection_from_file(
    filename: str,
    name: Optional[str] = None,
    metadata: Optional[Union[Dict[str, Any], str]] = None,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Id:
    """create collection\n
    return collection id"""
    return fh.create_collection_from_file_df(
        filename, name, metadata, auth=auth, conn_url=conn_url, batcher=batcher, is_async=is_async
    )


def update_collection_from_file(
    id: str,
    filename: str,
    name: Optional[str] = None,
    metadata: Optional[Union[Dict[str, Any], str]] = None,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Id:
    """create collection\n
    return collection id"""
    return fh.update_collection_from_file_df(
        id, filename, name, metadata, auth=auth, conn_url=conn_url, batcher=batcher, is_async=is_async
    )


def create_collection_from_df(
    data: pd.DataFrame,
    name: Optional[str] = None,
    metadata: Optional[Union[Dict[str, Any], str]] = None,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Id:
    """create collection\n
    return collection id"""
    return fh.create_collection_from_df(
        data, name, metadata, auth=auth, conn_url=conn_url, batcher=batcher, is_async=is_async
    )


def update_collection_from_df(
    id: str,
    data: pd.DataFrame,
    name: Optional[str] = None,
    metadata: Optional[Union[Dict[str, Any], str]] = None,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Id:
    """update collection by id\n
    return collection id"""
    return fh.update_collection_from_df(
        id, data, name, metadata, auth=auth, conn_url=conn_url, batcher=batcher, is_async=is_async
    )


async def get_collection_to_df_async(
    id: str,
    offset: int = 0,
    limit: int = -1,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
) -> pd.DataFrame:
    """return df from collection by `id`, pagination: unlimited - `limit` < 0"""
    collection = await get_collection(id, offset, limit, auth=auth, conn_url=conn_url, batcher=batcher, is_async=True)
    records = list(map(lambda x: json.loads(x.data), collection.docs))
    return pd.DataFrame.from_records(records)


def get_collection_to_df(
    id: str,
    offset: int = 0,
    limit: int = -1,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> pd.DataFrame:
    """return df from collection by `id`, pagination: unlimited - `limit` < 0"""
    if is_async:
        return get_collection_to_df_async(id, offset, limit, conn_url=conn_url, batcher=batcher)
    collection = get_collection(id, offset, limit, auth=auth, conn_url=conn_url, batcher=batcher, is_async=False)
    records = list(map(lambda x: json.loads(x.data), collection.docs))
    return pd.DataFrame.from_records(records)


async def get_collection_by_name_to_df_async(
    name: str,
    operation_id: Optional[str] = None,
    run_id: Optional[str] = None,
    offset: int = 0,
    limit: int = -1,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
) -> pd.DataFrame:
    """return df from collection by `name` and mb also `operation_id` and `run_id` with which it was saved. raise if there are multiple collections, pagination: unlimited - `limit` < 0"""
    collection = await get_collection_by_name(
        name, operation_id, run_id, offset, limit, auth=auth, conn_url=conn_url, batcher=batcher, is_async=True
    )
    records = list(map(lambda x: json.loads(x.data), collection.docs))
    return pd.DataFrame.from_records(records)


def get_collection_by_name_to_df(
    name: str,
    operation_id: Optional[str] = None,
    run_id: Optional[str] = None,
    offset: int = 0,
    limit: int = -1,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> pd.DataFrame:
    """return df from collection by `name` and mb also `operation_id` and `run_id` with which it was saved. raise if there are multiple collections, pagination: unlimited - `limit` < 0"""
    if is_async:
        return get_collection_by_name_to_df_async(
            name, operation_id, run_id, offset, limit, auth=auth, conn_url=conn_url, batcher=batcher
        )
    collection = get_collection_by_name(
        name, operation_id, run_id, offset, limit, auth=auth, conn_url=conn_url, batcher=batcher, is_async=False
    )
    records = list(map(lambda x: json.loads(x.data), collection.docs))
    return pd.DataFrame.from_records(records)


def create_doc_from_file(
    filename: str,
    name: Optional[str] = None,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Alias.Id:
    """create doc\n
    return doc id"""
    with open(filename) as f:
        data = json.load(f)
    return create_doc(
        data, name, auth=auth, conn_url=conn_url, batcher=batcher, is_async=is_async
    )


def create_schemes_by_path(
    path: str,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
    batcher: Optional[Batcher] = None,
    is_async: bool = False,
) -> Dict[str, Alias.Id]:
    """schemes are created from json along the path to the directory, scheme_name - is the name of the file without '.json', returned a dict from the name of the created scheme to id"""
    res = dict()
    for filename in os.listdir(path):
        if filename.endswith(".json"):
            name = filename[:-5]
            with open(f"{path}/{filename}") as f:
                data = f.read()
            res[name] = create_scheme(
                data, name, wait=wait, auth=auth, conn_url=conn_url, batcher=batcher, is_async=is_async
            )
    return res
