import json
import os
import re
import subprocess
from typing import Union

import pandas as pd

import malevich_coretools.funcs.funcs as f
import malevich_coretools.funcs.helpers as fh
from malevich_coretools.abstract import *  # noqa: F403
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


def digest_by_image(image_ref: str, username: Optional[str] = None, password: Optional[str] = None) -> Optional[str]:
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
    *, auth: Optional[AUTH] = None, conn_url: Optional[str] = None
) -> ResultIds:
    """return list ids """
    return f.get_docs(auth=auth, conn_url=conn_url)


def get_doc(
    id: str, *, auth: Optional[AUTH] = None, conn_url: Optional[str] = None
) -> ResultDoc:
    """return doc by `id` """
    return f.get_docs_id(id, auth=auth, conn_url=conn_url)


def create_doc(
    data: Alias.Json,
    name: Optional[str],
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
) -> Alias.Id:
    """save doc with `data` and `name`, return `id` """
    return f.post_docs(
        DocWithName(data=data, name=name), wait=wait, auth=auth, conn_url=conn_url
    )


def update_doc(
    id: str,
    data: Alias.Json,
    name: Optional[str],
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
) -> Alias.Id:
    """update doc by `id`, return `id` """
    return f.post_docs_id(
        id, DocWithName(data=data, name=name), wait=wait, auth=auth, conn_url=conn_url
    )


def delete_doc(
    id: str,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
) -> Alias.Info:
    """delete doc by `id` """
    return f.delete_docs_id(id, wait=wait, auth=auth, conn_url=conn_url)


def delete_docs(
    wait: bool = True, *, auth: Optional[AUTH] = None, conn_url: Optional[str] = None
) -> Alias.Info:
    """delete all docs"""
    return f.delete_docs(wait=wait, auth=auth, conn_url=conn_url)


# Collections


def get_collections(
    *, auth: Optional[AUTH] = None, conn_url: Optional[str] = None
) -> ResultOwnAndSharedIds:
    """return 2 list: own collections ids and shared collections ids"""
    return f.get_collections(auth=auth, conn_url=conn_url)


def get_collections_by_name(
    name: str,
    operation_id: Optional[str] = None,
    run_id: Optional[str] = None,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
) -> ResultOwnAndSharedIds:
    """return 2 list: own collections ids and shared collections ids by `name` and mb also `operation_id` and `run_id` with which it was saved"""
    assert not (
        operation_id is None and run_id is not None
    ), "if run_id set, operation_id should be set too"
    return f.get_collections_name(
        name, operation_id, run_id, auth=auth, conn_url=conn_url
    )


def get_collection(
    id: str,
    offset: int = 0,
    limit: int = -1,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
) -> ResultCollection:
    """return collection by `id`, pagination: unlimited - `limit` < 0"""
    return f.get_collections_id(id, offset, limit, auth=auth, conn_url=conn_url)


def get_collection_by_name(
    name: str,
    operation_id: Optional[str] = None,
    run_id: Optional[str] = None,
    offset: int = 0,
    limit: int = -1,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
) -> ResultCollection:
    """return collection by `name` and mb also `operation_id` and `run_id` with which it was saved. raise if there are multiple collections, pagination: unlimited - `limit` < 0"""
    assert not (
        operation_id is None and run_id is not None
    ), "if run_id set, operation_id should be set too"
    return f.get_collection_name(
        name, operation_id, run_id, offset, limit, auth=auth, conn_url=conn_url
    )


def get_collections_ids_by_group_name(
    group_name: str,
    operation_id: str,
    run_id: Optional[str] = None,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
) -> ResultIds:
    """return collections ids by `group_name`, `operation_id` and `run_id` with which it was saved"""
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
) -> ResultCollections:
    """return collections by `group_name`, `operation_id` and `run_id` with which it was saved"""
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
) -> Alias.Id:
    """save collection by list docs `ids`, return id"""
    return f.post_collections(
        DocsCollection(data=ids, name=name, metadata=metadata),
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
) -> Alias.Id:
    """update collection with `id` by list docs `ids`, return `id` """
    return f.post_collections_id(
        id,
        DocsCollection(data=ids, name=name, metadata=metadata),
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
) -> Alias.Info:
    """is_csv = false -> save json, key by default = id"""
    return f.post_collections_id_s3(
        id,
        PostS3Settings(isCsv=is_csv, key=key),
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
) -> Alias.Id:
    """save collection by `docs`, return `id` """
    return f.post_collections_data(
        DocsDataCollection(data=docs, name=name, metadata=metadata),
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
) -> Alias.Info:
    """add to collection with `id` docs with `ids` """
    return f.post_collections_id_add(
        id, DocsCollectionChange(data=ids), wait=wait, auth=auth, conn_url=conn_url
    )


def copy_collection(
    id: str,
    full_copy: bool = True,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
) -> Alias.Id:
    """copy collection with `id`, if not `full_copy` docs same as in collection with `id` """
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
) -> Alias.Id:
    """apply scheme with `scheme_name` to collection with `coll_id` return new collection with another `coll_id` """
    return f.post_collections_id_applyScheme(
        coll_id,
        FixScheme(schemeName=scheme_name, mode=mode),
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
) -> Alias.Info:
    """optimization to core (not necessary call), sets the schema with `scheme_name` for the collection with `coll_id` """
    fix_scheme_data = FixScheme(schemeName=scheme_name, mode=mode)
    return f.post_collections_id_fixScheme(
        coll_id, fix_scheme_data, wait=wait, auth=auth, conn_url=conn_url
    )


def unfix_scheme(
    coll_id: str,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
) -> Alias.Info:
    """unfix scheme for collection with `coll_id` """
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
) -> Alias.Info:
    """update `metadata` for collection with `coll_id` """
    collection_metadata = CollectionMetadata(data=metadata)
    return f.post_collections_metadata(
        coll_id, collection_metadata, wait=wait, auth=auth, conn_url=conn_url
    )


def delete_collections(
    wait: bool = True, *, auth: Optional[AUTH] = None, conn_url: Optional[str] = None
) -> Alias.Info:
    """delete all collections"""
    return f.delete_collections(wait=wait, auth=auth, conn_url=conn_url)


def delete_collection(
    id: str,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
) -> Alias.Info:
    """delete collection with `id` """
    return f.delete_collections_id(id, wait=wait, auth=auth, conn_url=conn_url)


def s3_delete_collection(
    key: str,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
) -> Alias.Info:
    """delete collection from s3 by `key` (that =id if not specified in s3_save_collection)"""
    return f.delete_collections_id_s3(key, wait=wait, auth=auth, conn_url=conn_url)


def delete_from_collection(
    id: str,
    ids: List[str],
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
) -> Alias.Info:
    """delete docs with `ids` from collection with `id` """
    return f.delete_collections_id_del(
        id, DocsCollectionChange(data=ids), wait=wait, auth=auth, conn_url=conn_url
    )


# CollectionObjects


def get_collection_objects(
    path: Optional[str] = None,
    recursive: Optional[str] = None,
    *, auth: Optional[AUTH] = None, conn_url: Optional[str] = None
) -> FilesDirs:
    """return struct with list of paths: directories and files: walk if `recursive` else ls"""
    return f.get_collection_objects(path, recursive, auth=auth, conn_url=conn_url)


def get_collection_object(
    path: str,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
) -> bytes:
    """return collection object bytes by `path`"""
    return f.get_collection_object(
        path, auth=auth, conn_url=conn_url
    )


def get_collection_object_presigned_url(
    path: str,
    expires_in: int,
    callback_url: Optional[str] = None,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
) -> Alias.Info:
    """get presigned url to load object with `path`, valid only `expiresIn` seconds, one-time use"""
    return f.get_collection_object_presigned_url(path, callback_url, expires_in, wait=wait, auth=auth, conn_url=conn_url)


def update_collection_object(
    path: str,
    data: bytes,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
) -> Alias.Info:
    """update collection object with `path` by `data` """
    return f.post_collections_object(path, data, wait=wait, auth=auth, conn_url=conn_url)


def update_collection_object_presigned(
    signature: str,
    data: bytes,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
) -> Alias.Info:
    """update collection object by `data` with presigned `signature`"""
    return f.post_collections_object_presigned(signature, data, auth=auth, conn_url=conn_url)


def delete_collection_objects(
    wait: bool = True, *, auth: Optional[AUTH] = None, conn_url: Optional[str] = None
) -> Alias.Info:
    """delete all collection objects"""
    return f.delete_collection_objects(wait=wait, auth=auth, conn_url=conn_url)


def delete_collection_object(
    path: str,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
) -> Alias.Info:
    """delete collection object with `path` (or directory with them) """
    return f.delete_collection_object(path, wait=wait, auth=auth, conn_url=conn_url)


# Endpoint


def get_endpoints(
    *, auth: Optional[AUTH] = None, conn_url: Optional[str] = None
) -> Endpoints:
    """get registered endpoints structs"""
    return f.get_endpoints(auth=auth, conn_url=conn_url)


def run_endpoint(
    hash: str,
    with_show: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
) -> Union[AppLogs, Any]:
    """run by endpoint, failed if `taskId`, `cfgId` not set or it is not active"""
    return f.run_endpoint(hash, with_show=with_show, auth=auth, conn_url=conn_url)


def create_endpoint(
    task_id: Optional[str] = None,
    cfg_id: Optional[str] = None,
    callback_url: Optional[str] = None,
    sla: Optional[str] = None,
    active: Optional[bool] = None,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
) -> str:
    """create endpoint, return hash, url - api/v1/endpoints/run/{hash}. fields may not be initialized - this will only cause an error at startup"""
    data = Endpoint(taskId=task_id, cfgId=cfg_id, callbackUrl=callback_url, sla=sla, active=active)
    return f.create_endpoint(data, wait=wait, auth=auth, conn_url=conn_url)


def update_endpoint(
    hash: str,
    task_id: Optional[str] = None,
    cfg_id: Optional[str] = None,
    callback_url: Optional[str] = None,
    sla: Optional[str] = None,
    active: Optional[bool] = None,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
) -> str:
    """update endpoint, return hash, url - api/v1/endpoints/run/{hash}. update field if it is not None"""
    data = Endpoint(hash=hash, taskId=task_id, cfgId=cfg_id, callbackUrl=callback_url, sla=sla, active=active)
    return f.update_endpoint(data, wait=wait, auth=auth, conn_url=conn_url)


def pause_endpoint(
    hash: str,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
) -> Alias.Info:
    return f.pause_endpoint(hash, wait=wait, auth=auth, conn_url=conn_url)


def resume_endpoint(
    hash: str,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
) -> Alias.Info:
    return f.resume_endpoint(hash, wait=wait, auth=auth, conn_url=conn_url)


def delete_endpoints(
    wait: bool = True, *, auth: Optional[AUTH] = None, conn_url: Optional[str] = None
) -> Alias.Info:
    """delete all endpoints"""
    return f.delete_endpoints(wait=wait, auth=auth, conn_url=conn_url)


def delete_endpoint(
    hash: str,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
) -> Alias.Info:
    """delete endpoint with `hash` """
    return f.delete_endpoint(hash, wait=wait, auth=auth, conn_url=conn_url)


# Scheme


def get_schemes(
    *, auth: Optional[AUTH] = None, conn_url: Optional[str] = None
) -> ResultOwnAndSharedIds:
    """return 2 list: own schemes ids and shared schemes ids"""
    return f.get_schemes(auth=auth, conn_url=conn_url)


def get_scheme(
    id: str, *, auth: Optional[AUTH] = None, conn_url: Optional[str] = None
) -> ResultScheme:
    """return scheme by `id` """
    return f.get_schemes_id(id, auth=auth, conn_url=conn_url)


def get_scheme_raw(
    id: str, *, auth: Optional[AUTH] = None, conn_url: Optional[str] = None
) -> Alias.Json:
    """return raw scheme data by `id` """
    return f.get_schemes_id_raw(id, auth=auth, conn_url=conn_url)


def get_schemes_mapping(
    scheme_from_id: str,
    scheme_to_id: str,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
) -> ResultMapping:
    """return mapping by schemes ids, does not assume if it is not"""
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
) -> Alias.Id:
    """create scheme\n
    `scheme_data` must be json or dict
    return `id` """
    assert re.fullmatch(SCHEME_PATTERN, name) is not None, f"wrong scheme name: {name}"
    scheme_json = to_json(scheme_data)
    scheme = SchemeWithName(data=scheme_json, name=name)
    return f.post_schemes(scheme, wait=wait, auth=auth, conn_url=conn_url)


def update_scheme(
    id: str,
    scheme_data: Union[Dict[str, Any], Alias.Json],
    name: str,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
) -> Alias.Id:
    """update scheme\n
    `scheme_data` must be json or dict
    return `id` """
    assert re.fullmatch(SCHEME_PATTERN, name) is not None, f"wrong scheme name: {name}"
    scheme_json = to_json(scheme_data)
    scheme = SchemeWithName(data=scheme_json, name=name)
    return f.post_schemes_id(id, scheme, wait=wait, auth=auth, conn_url=conn_url)


def create_schemes_mapping(
    scheme_from_id: str,
    scheme_to_id: str,
    mapping: Dict[str, str],
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
) -> Alias.Id:
    """save mapping between schemes with ids"""
    return f.post_schemes_mapping(
        SchemesFixMapping(
            schemeFromId=scheme_from_id, schemeToId=scheme_to_id, data=mapping
        ),
        wait=wait,
        auth=auth,
        conn_url=conn_url,
    )


def delete_schemes(
    wait: bool = True, *, auth: Optional[AUTH] = None, conn_url: Optional[str] = None
) -> Alias.Info:
    """delete all schemes"""
    return f.delete_schemes(wait=wait, auth=auth, conn_url=conn_url)


def delete_scheme(
    id: str,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
) -> Alias.Info:
    """delete scheme by `id` """
    return f.delete_schemes_id(id, wait=wait, auth=auth, conn_url=conn_url)


def delete_schemes_mapping(
    scheme_from_id: str,
    scheme_to_id: str,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
) -> Alias.Info:
    """delete mapping between schemes with ids"""
    return f.delete_schemes_mapping(
        SchemesIds(schemeFromId=scheme_from_id, schemeToId=scheme_to_id),
        wait=wait,
        auth=auth,
        conn_url=conn_url,
    )


# Common


def check_auth(
    *, auth: Optional[AUTH] = None, conn_url: Optional[str] = None
) -> Alias.Info:
    """check auth in core for current user"""
    return f.get_check_auth(auth=auth, conn_url=conn_url)


def ping(conn_url: Optional[str] = None) -> Alias.Info:
    """return `pong` """
    return f.get_ping(with_auth=False, conn_url=conn_url)


# def get_mappings(*, auth: Optional[AUTH]=None, conn_url: Optional[str]=None) -> ResultDocMappingsFull:
#     """outdate\n
#     return list: for each doc - map from scheme to mapping ids"""
#     return f.get_mapping(auth=auth, conn_url=conn_url)


# def get_mapping(id: str, *, auth: Optional[AUTH]=None, conn_url: Optional[str]=None) -> ResultMapping:
#     """return mapping by `id`"""
#     return f.get_mapping_id(id, auth=auth, conn_url=conn_url)


# def create_mapping(docs_ids: List[str], scheme_id: str, wait: bool = True, *, auth: Optional[AUTH]=None, conn_url: Optional[str]=None) -> Alias.Info:
#     """try to do and save mapping docs with `docs_ids` with scheme with `scheme_id`, ignore if failed"""
#     return f.post_mapping(DocsAndScheme(docsIds=docs_ids, schemeId=scheme_id), wait=wait, auth=auth, conn_url=conn_url)


# def delete_mapping(doc_id: str, wait: bool = True, *, auth: Optional[AUTH]=None, conn_url: Optional[str]=None) -> Alias.Info:
#     """delete mappings for doc with `doc_id`"""
#     return f.delete_mapping_id(doc_id, wait=wait, auth=auth, conn_url=conn_url)


# def delete_all(wait: bool = True, *, auth: Optional[AUTH]=None, conn_url: Optional[str]=None) -> Alias.Info:
#     """for admin: delete all"""
#     return f.delete_all(wait=wait, auth=auth, conn_url=conn_url)

# UserShare


def get_shared_collection(
    id: str, *, auth: Optional[AUTH] = None, conn_url: Optional[str] = None
) -> ResultLogins:
    """return list logins to which user has given access to the collection with `id` """
    return f.get_share_collection_id(id, auth=auth, conn_url=conn_url)


def get_shared_scheme(
    id: str, *, auth: Optional[AUTH] = None, conn_url: Optional[str] = None
) -> ResultLogins:
    """return list logins to which user has given access to the scheme with `id` """
    return f.get_share_scheme_id(id, auth=auth, conn_url=conn_url)


def get_shared_app(
    id: str, *, auth: Optional[AUTH] = None, conn_url: Optional[str] = None
) -> ResultLogins:
    """return list logins to which user has given access to the app with `id` """
    return f.get_share_userApp_id(id, auth=auth, conn_url=conn_url)


def get_shared_by_login(
    login: str, *, auth: Optional[AUTH] = None, conn_url: Optional[str] = None
) -> ResultSharedForLogin:
    """return structure with all info about share to user with `login` """
    return f.get_share_login(login, auth=auth, conn_url=conn_url)


def share_collection(
    id: str,
    user_logins: List[str],
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
) -> Alias.Info:
    """gives access to the collection with `id` to all users with `user_logins` """
    return f.post_share_collection_id(
        id,
        SharedWithUsers(userLogins=user_logins),
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
) -> Alias.Info:
    """gives access to the scheme with `id` to all users with `user_logins` """
    return f.post_share_scheme_id(
        id,
        SharedWithUsers(userLogins=user_logins),
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
) -> Alias.Info:
    """gives access to the app with `id` to all users with `user_logins` """
    return f.post_share_userApp_id(
        id,
        SharedWithUsers(userLogins=user_logins),
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
) -> Alias.Info:
    """gives access to everything listed to all users with `user_logins` """
    assert user_logins is not None, '"user_logins" is empty'
    collections_ids = [] if collections_ids is None else collections_ids
    schemes_ids = [] if schemes_ids is None else schemes_ids
    user_apps_ids = [] if user_apps_ids is None else user_apps_ids
    return f.post_share(
        Shared(
            userLogins=user_logins,
            collectionsIds=collections_ids,
            schemesIds=schemes_ids,
            userAppsIds=user_apps_ids,
        ),
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
) -> Alias.Info:
    """removes access to everything listed to all users with `user_logins` """
    assert user_logins is not None, '"user_logins" is empty'
    collections_ids = [] if collections_ids is None else collections_ids
    schemes_ids = [] if schemes_ids is None else schemes_ids
    user_apps_ids = [] if user_apps_ids is None else user_apps_ids
    return f.delete_share(
        Shared(
            userLogins=user_logins,
            collectionsIds=collections_ids,
            schemesIds=schemes_ids,
            userAppsIds=user_apps_ids,
        ),
        wait=wait,
        auth=auth,
        conn_url=conn_url,
    )


def delete_shared_all(
    wait: bool = True, *, auth: Optional[AUTH] = None, conn_url: Optional[str] = None
) -> Alias.Info:
    """removes access to everything for all for current user"""
    return f.delete_share_all(wait=wait, auth=auth, conn_url=conn_url)


# Registration


def get_user(
    login: str, *, auth: Optional[AUTH] = None, conn_url: Optional[str] = None
) -> Alias.Info:
    """admin: displays saved information about the user"""
    return f.get_register_login(login, auth=auth, conn_url=conn_url)


def get_users(
    *, auth: Optional[AUTH] = None, conn_url: Optional[str] = None
) -> ResultLogins:
    """admin: returns a list of all logins"""
    return f.get_register_all(auth=auth, conn_url=conn_url)


def create_user(
    *, auth: Optional[AUTH] = None, conn_url: Optional[str] = None
) -> Alias.Info:
    """create user in malevich-core, all operations will continue on his behalf"""
    return f.post_register(auth=auth, conn_url=conn_url)


def delete_user(
    *, auth: Optional[AUTH] = None, conn_url: Optional[str] = None
) -> Alias.Info:
    """delete current user, not raise if user not exist"""
    return f.delete_register(auth=auth, conn_url=conn_url)


def delete_user_login(
    login: str,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
) -> None:
    """admin: delete user by `login` """
    f.delete_register_login(login, wait=wait, auth=auth, conn_url=conn_url)


# UserApps


def get_apps(
    *, auth: Optional[AUTH] = None, conn_url: Optional[str] = None
) -> ResultOwnAndSharedIds:
    """return apps ids for current user"""
    return f.get_userApps(auth=auth, conn_url=conn_url)


def get_apps_real(
    *, auth: Optional[AUTH] = None, conn_url: Optional[str] = None
) -> ResultOwnAndSharedIds:
    """return apps real ids for current user"""
    return f.get_userApps_realIds(auth=auth, conn_url=conn_url)


def get_apps_map(
    *, auth: Optional[AUTH] = None, conn_url: Optional[str] = None
) -> ResultOwnAndSharedIdsMap:
    """return apps ids with real ids for current user"""
    return f.get_userApps_mapIds(auth=auth, conn_url=conn_url)


def get_app(
    id: str, *, auth: Optional[AUTH] = None, conn_url: Optional[str] = None
) -> UserApp:
    """return app by `id` """
    return f.get_userApps_id(id, auth=auth, conn_url=conn_url)


def get_app_real(
    id: str, *, auth: Optional[AUTH] = None, conn_url: Optional[str] = None
) -> UserApp:
    """return app by real `id` """
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
    collections_from: Optional[Dict[str, str]] = None,
    extra_collections_from: Optional[Dict[str, str]] = None,
    wait: bool = True,
    *,
    use_system_auth: bool = True,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
) -> Alias.Id:
    """create app\n
    `app_cfg` must be json or dict or None\n
    return `id` """
    assert (
        platform in POSSIBLE_APPS_PLATFORMS
    ), f"wrong platform: {platform}, possible platforms: {POSSIBLE_APPS_PLATFORMS}"
    assert image_ref is not None, "image_ref not set"
    app_cfg_json = None if app_cfg is None else to_json(app_cfg)
    image_user = image_auth[0] if image_auth is not None else Config.USERNAME if use_system_auth else None
    image_token = image_auth[1] if image_auth is not None else Config.TOKEN if use_system_auth else None
    if Config.WITH_WARNINGS and (image_user is None or image_token is None):
        Config.logger.warning("image_auth not set")
    json_image = JsonImage(ref=image_ref, user=image_user, token=image_token)
    app = UserApp(
        appId=app_id,
        inputId=input_id,
        processorId=processor_id,
        outputId=output_id,
        cfg=app_cfg_json,
        image=json_image,
        platform=platform,
        platformSettings=platform_settings,
        collectionsFrom=collections_from,
        extraCollectionsFrom=extra_collections_from,
    )
    return f.post_userApps(app, wait=wait, auth=auth, conn_url=conn_url)


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
    collections_from: Optional[Dict[str, str]] = None,
    extra_collections_from: Optional[Dict[str, str]] = None,
    wait: bool = True,
    *,
    use_system_auth: bool = True,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
) -> Alias.Info:
    """update app by `id`\n
    `app_cfg` must be json or dict or None"""
    assert (
        platform in POSSIBLE_APPS_PLATFORMS
    ), f"wrong platform: {platform}, possible platforms: {POSSIBLE_APPS_PLATFORMS}"
    assert image_ref is not None, "image_ref not set"
    app_cfg_json = None if app_cfg is None else to_json(app_cfg)
    image_user = image_auth[0] if image_auth is not None else Config.USERNAME if use_system_auth else None
    image_token = image_auth[1] if image_auth is not None else Config.TOKEN if use_system_auth else None
    if Config.WITH_WARNINGS and (image_user is None or image_token is None):
        Config.logger.warning("image_auth not set")
    json_image = JsonImage(ref=image_ref, user=image_user, token=image_token)
    app = UserApp(
        appId=app_id,
        inputId=input_id,
        processorId=processor_id,
        outputId=output_id,
        cfg=app_cfg_json,
        image=json_image,
        platform=platform,
        platformSettings=platform_settings,
        collectionsFrom=collections_from,
        extraCollectionsFrom=extra_collections_from,
    )
    return f.post_userApps_id(id, app, wait=wait, auth=auth, conn_url=conn_url)


def delete_apps(
    wait: bool = True, *, auth: Optional[AUTH] = None, conn_url: Optional[str] = None
) -> Alias.Info:
    """delete all user apps"""
    return f.delete_userApps(wait=wait, auth=auth, conn_url=conn_url)


def delete_app(
    id: str,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
) -> Alias.Info:
    """delete user app by `id` """
    return f.delete_userApps_id(id, wait=wait, auth=auth, conn_url=conn_url)


# UserTasks


def get_tasks(
    *, auth: Optional[AUTH] = None, conn_url: Optional[str] = None
) -> ResultIds:
    """return tasks ids for current user"""
    return f.get_userTasks(auth=auth, conn_url=conn_url)


def get_tasks_real(
    *, auth: Optional[AUTH] = None, conn_url: Optional[str] = None
) -> ResultIds:
    """return tasks real ids for current user"""
    return f.get_userTasks_realIds(auth=auth, conn_url=conn_url)


def get_tasks_map(
    *, auth: Optional[AUTH] = None, conn_url: Optional[str] = None
) -> ResultIdsMap:
    """return tasks ids with real ids for current user"""
    return f.get_userTasks_mapIds(auth=auth, conn_url=conn_url)


def get_task(
    id: str, *, auth: Optional[AUTH] = None, conn_url: Optional[str] = None
) -> UserTask:
    """return task by `id` """
    return f.get_userTasks_id(id, auth=auth, conn_url=conn_url)


def get_task_real(
    id: str, *, auth: Optional[AUTH] = None, conn_url: Optional[str] = None
) -> UserTask:
    """return task by real `id` """
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
) -> Alias.Id:
    """create task"""
    if synthetic:
        assert app_id is None, "app_id should be None for synthetic task"
    else:
        assert app_id is not None, "app_id should be not None for not synthetic task"
    if apps_depends is None:
        apps_depends = []
    if tasks_depends is None:
        tasks_depends = []
    task = UserTask(
        taskId=task_id,
        appId=app_id,
        appsDepends=apps_depends,
        tasksDepends=tasks_depends,
        synthetic=synthetic,
    )
    return f.post_userTasks(task, wait=wait, auth=auth, conn_url=conn_url)


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
) -> Alias.Info:
    """update task by `id` """
    if apps_depends is None:
        apps_depends = []
    if tasks_depends is None:
        tasks_depends = []
    task = UserTask(
        taskId=task_id,
        appId=app_id,
        appsDepends=apps_depends,
        tasksDepends=tasks_depends,
    )
    return f.post_userTasks_id(id, task, wait=wait, auth=auth, conn_url=conn_url)


def delete_tasks(
    wait: bool = True, *, auth: Optional[AUTH] = None, conn_url: Optional[str] = None
) -> Alias.Info:
    """delete all user tasks"""
    return f.delete_userTasks(wait=wait, auth=auth, conn_url=conn_url)


def delete_task(
    id: str,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
) -> Alias.Info:
    """delete user task by `id` """
    return f.delete_userTasks_id(id, wait=wait, auth=auth, conn_url=conn_url)


# UserCfgs


def get_cfgs(
    *, auth: Optional[AUTH] = None, conn_url: Optional[str] = None
) -> ResultIds:
    """return cfgs ids for current user"""
    return f.get_userCfgs(auth=auth, conn_url=conn_url)


def get_cfgs_real(
    *, auth: Optional[AUTH] = None, conn_url: Optional[str] = None
) -> ResultIds:
    """return cfgs real ids for current user"""
    return f.get_userCfgs_realIds(auth=auth, conn_url=conn_url)


def get_cfgs_map(
    *, auth: Optional[AUTH] = None, conn_url: Optional[str] = None
) -> ResultIdsMap:
    """return cfgs ids with real ids for current user"""
    return f.get_userCfgs_mapIds(auth=auth, conn_url=conn_url)


def get_cfg(
    id: str, *, auth: Optional[AUTH] = None, conn_url: Optional[str] = None
) -> ResultUserCfg:
    """return cfg by `id` """
    return f.get_userCfgs_id(id, auth=auth, conn_url=conn_url)


def get_cfg_real(
    id: str, *, auth: Optional[AUTH] = None, conn_url: Optional[str] = None
) -> ResultUserCfg:
    """return cfg by real `id` """
    return f.get_userCfgs_realId(id, auth=auth, conn_url=conn_url)


def __fix_cfg(cfg: Union[Dict[str, Any], Alias.Json, Cfg]) -> str:
    if isinstance(cfg, Cfg):
        for app_setting in cfg.app_settings:
            if isinstance(app_setting.saveCollectionsName, str):
                app_setting.saveCollectionsName = [app_setting.saveCollectionsName]
        cfg_json = cfg.json()
    else:
        if isinstance(cfg, Alias.Json):
            cfg = json.loads(cfg)
        assert isinstance(cfg, dict), "wrong cfg type"
        for app_setting in cfg["app_settings"]:
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
) -> Alias.Id:
    """create configuration file\n
    `cfg` must be json or dict or Cfg\n
    return `id` """
    user_cfg = UserCfg(cfgId=cfg_id, cfg=__fix_cfg(cfg))
    return f.post_userCfgs(user_cfg, wait=wait, auth=auth, conn_url=conn_url)


def update_cfg(
    id: str,
    cfg_id: str,
    cfg: Union[Dict[str, Any], Alias.Json, Cfg],
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
) -> Alias.Info:
    """update configuration file\n
    `cfg` must be json or dict or Cfg"""
    user_cfg = UserCfg(cfgId=cfg_id, cfg=__fix_cfg(cfg))
    return f.post_userCfgs_id(id, user_cfg, wait=wait, auth=auth, conn_url=conn_url)


def delete_cfgs(
    wait: bool = True, *, auth: Optional[AUTH] = None, conn_url: Optional[str] = None
) -> Alias.Info:
    """delete all user cfgs"""
    return f.delete_userCfgs(wait=wait, auth=auth, conn_url=conn_url)


def delete_cfg(
    id: str,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
) -> Alias.Info:
    """delete user cfg by `id` """
    return f.delete_userCfgs_id(id, wait=wait, auth=auth, conn_url=conn_url)


# OperationResults


def get_operations_results(
    *, auth: Optional[AUTH] = None, conn_url: Optional[str] = None
) -> ResultIds:
    """return list of operations ids"""
    return f.get_operationResults(auth=auth, conn_url=conn_url)


def get_operation_result(
    id: str, *, auth: Optional[AUTH] = None, conn_url: Optional[str] = None
) -> str:
    """return result by operation `id` if operation status is `OK` """
    return f.get_operationResults_id(id, auth=auth, conn_url=conn_url)


def delete_operations_results(
    wait: bool = True, *, auth: Optional[AUTH] = None, conn_url: Optional[str] = None
) -> Alias.Info:
    """delete all operations results"""
    return f.delete_operationResults(wait=wait, auth=auth, conn_url=conn_url)


def delete_operation_result(
    id: str,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
) -> Alias.Info:
    """delete operation result by `id` """
    return f.delete_operationResults_id(id, wait=wait, auth=auth, conn_url=conn_url)


# TempRun


def get_run_condition(
    id: str, *, auth: Optional[AUTH] = None, conn_url: Optional[str] = None
) -> Condition:
    """return run condition by operation `id` for running task"""
    return f.get_run_condition(id, auth=auth, conn_url=conn_url)


def get_run_active_runs(
    *, auth: Optional[AUTH] = None, conn_url: Optional[str] = None
) -> ResultIds:
    """return list running operationIds"""
    return f.get_run_activeRuns(auth=auth, conn_url=conn_url)


def get_run_main_task_cfg(
    id: str, *, auth: Optional[AUTH] = None, conn_url: Optional[str] = None
) -> MainTaskCfg:
    """return mainTaskCfg by operation `id` for running task"""
    return f.get_run_mainTaskCfg(id, auth=auth, conn_url=conn_url)


def get_task_runs(
    task_id: str,
    cfg_id: Optional[str] = None,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
) -> ResultIds:
    """return list running operationIds with `task_id` and `cfg_id` if specified"""
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
) -> AppLogs:
    """return task logs by operation `id` and `run_id` """
    task = LogsTask(operationId=id, runId=run_id)
    return f.get_manager_logs(task, with_show=with_show, auth=auth, conn_url=conn_url)


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
) -> AppLogs:
    """return app logs by operation `id`, `run_id`, `task_id` (that "null" if not exist) and `app_id` """
    task = LogsTask(
        operationId=id, runId=run_id, appId=app_id, taskId=task_id, force=force
    )
    return f.get_manager_logs(task, with_show=with_show, auth=auth, conn_url=conn_url)


def logs_clickhouse(
    *, auth: Optional[AUTH] = None, conn_url: Optional[str] = None
) -> Alias.Json:
    """return all clickhouse logs"""
    return f.get_clickhouse_all(auth=auth, conn_url=conn_url)


def logs_clickhouse_id(
    id: str, *, auth: Optional[AUTH] = None, conn_url: Optional[str] = None
) -> Alias.Json:
    """return clickhouse logs by operation `id` """
    return f.get_clickhouse_id(id, auth=auth, conn_url=conn_url)


def get_dag_key_value(
    id: str, *, auth: Optional[AUTH] = None, conn_url: Optional[str] = None
) -> Alias.Json:
    """return key-value cfg from dag by operation `id` """
    return f.get_manager_dagKeyValue_operationId(id, auth=auth, conn_url=conn_url)


def update_dag_key_value(
    data: Dict[str, str],
    operationId: str,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
) -> None:
    """update key-value cfg from dag by operation `id` and `data` """
    return f.post_manager_dagKeyValue(
        KeysValues(data=data, operationId=operationId),
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
) -> Union[Alias.Json, AppFunctionsInfo]:
    """return json with functions app info, `id` is appId"""
    return f.get_app_info(id, parse=parse, auth=auth, conn_url=conn_url)


def get_app_info_by_real_id(
    id: str,
    parse: bool = False,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
) -> Union[Alias.Json, AppFunctionsInfo]:
    """return json with functions app info, `id` is real id for app"""
    return f.get_app_info_by_real_id(id, parse=parse, auth=auth, conn_url=conn_url)


def get_image_info(
    image_ref: str,
    image_auth: Optional[AUTH] = None,
    parse: bool = False,
    *,
    use_system_auth: bool = False,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
) -> Union[Alias.Json, AppFunctionsInfo]:
    """return json with functions image info"""
    image_user = image_auth[0] if image_auth is not None else Config.USERNAME if use_system_auth else None
    image_token = image_auth[1] if image_auth is not None else Config.TOKEN if use_system_auth else None
    if Config.WITH_WARNINGS and (image_user is None or image_token is None):
        Config.logger.warning("image_auth not set")
    json_image = JsonImage(ref=image_ref, user=image_user, token=image_token)
    return f.get_image_info(json_image, parse=parse, auth=auth, conn_url=conn_url)


def get_task_schedules(
    operation_id: str,
    with_show: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
) -> Schedules:
    """return schedule ids by `operation_id` """
    operation = Operation(operationId=operation_id)
    return f.get_task_schedules(
        operation, with_show=with_show, auth=auth, conn_url=conn_url
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
) -> AppLogs:
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
    if scaleInfo is None:
        scaleInfo = []
    if component is None:
        component = TaskComponent()
    if policy is None:
        policy = TaskPolicy()
    if restrictions is None:
        restrictions = Restrictions()
    task = MainTask(
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
        scaleInfo=scaleInfo,
        component=component,
        policy=policy,
        schedule=schedule,
        restrictions=restrictions,
    )
    return f.post_manager_task(
        task,
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
) -> AppLogs:
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
    task = MainTask(
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
        profileMode=profile_mode,
        scaleInfo=scaleInfo,
        component=component,
        policy=policy,
        restrictions=restrictions,
    )
    return f.post_manager_task(
        task,
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
) -> Optional[AppLogs]:
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
    if run_id is None:
        run_id = rand_str(15)
    if with_show is None:
        with_show = with_logs
    task = RunTask(
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
    return f.post_manager_task_run(
        task,
        with_show=with_show,
        long=long,
        long_timeout=long_timeout,
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
) -> Alias.Info:
    """unschedule task by `schedule_id` """
    operation = UnscheduleOperation(scheduleId=schedule_id)
    return f.post_manager_task_unschedule(
        operation, with_show=with_show, wait=wait, auth=auth, conn_url=conn_url
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
) -> Optional[AppLogs]:
    """stop task by `operation_id`

    Args:
       operation_id (str): `operation_id`, that returned from 'task_prepare', or just operation_id for runned task
       with_logs (bool): return logs for task if True
       info_url (Optional[str]): send also result to info_url if it exist and 'with_logs=True'
       with_show (bool): show result (like for each operation, default equals with_logs arg)
       wait (bool): is it worth waiting for the result or immediately return `operation_id`
       auth (Optional[AUTH]): redefined auth if not None"""
    if with_show is None:
        with_show = with_logs
    task = StopOperation(operationId=operation_id, withLogs=with_logs, infoUrl=info_url)
    return f.post_manager_task_stop(
        task, with_show=with_show, wait=wait, auth=auth, conn_url=conn_url
    )


def task_stop_all(
    with_logs: bool = False,
    info_url: Optional[str] = None,
    with_show: bool = True,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
) -> Alias.Json:
    """stop all tasks"""
    task = StopOperationMany(withLogs=with_logs, infoUrl=info_url)
    return f.post_manager_task_stop_all(
        task, with_show=with_show, wait=wait, auth=auth, conn_url=conn_url
    )


def task_resume(
    operation_id: str,
    with_show: bool = True,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
) -> Alias.Empty:
    """resume task by `operation_id` """
    task = Operation(operationId=operation_id)
    return f.post_manager_task_resume(
        task, with_show=with_show, wait=wait, auth=auth, conn_url=conn_url
    )


def task_pause(
    operation_id: str,
    with_show: bool = True,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
) -> Alias.Empty:
    """pause task by `operation_id` """
    task = Operation(operationId=operation_id)
    return f.post_manager_task_pause(
        task, with_show=with_show, wait=wait, auth=auth, conn_url=conn_url
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
) -> Alias.Empty:
    """stop app by `operation_id`, `task_id` and `app_id` """
    app_manage = AppManage(
        operationId=operation_id, taskId=task_id, appId=app_id, runId=run_id
    )
    return f.post_manager_app_stop(
        app_manage, with_show=with_show, wait=wait, auth=auth, conn_url=conn_url
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
) -> Alias.Empty:
    """resume app by `operation_id`, `task_id` and `app_id` """
    app_manage = AppManage(
        operationId=operation_id, taskId=task_id, appId=app_id, runId=run_id
    )
    return f.post_manager_app_resume(
        app_manage, with_show=with_show, wait=wait, auth=auth, conn_url=conn_url
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
) -> Alias.Empty:
    """pause app by `operation_id`, `task_id` and `app_id` """
    app_manage = AppManage(
        operationId=operation_id, taskId=task_id, appId=app_id, runId=run_id
    )
    return f.post_manager_app_pause(
        app_manage, with_show=with_show, wait=wait, auth=auth, conn_url=conn_url
    )


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
) -> Union[Alias.Info, KafkaMsg]:  # TODO add tl
    """send msg to kafka for task by `operation_id`, `run_id` and `data` """
    assert data is not None, "data should exists in kafka_send"
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
    kafka_msg = KafkaMsg(
        operationId=operation_id, runId=run_id, data=data, metadata=real_metadata
    )
    return await f.kafka_send(
        kafka_msg, with_show=with_show, auth=auth, conn_url=conn_url
    )


# other


def create_collection_from_file(
    filename: str,
    name: Optional[str] = None,
    metadata: Optional[Union[Dict[str, Any], str]] = None,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
) -> Alias.Id:
    """create collection\n
    return collection id"""
    return fh.create_collection_from_file_df(
        filename, name, metadata, auth=auth, conn_url=conn_url
    )


def create_collection_from_df(
    data: pd.DataFrame,
    name: Optional[str] = None,
    metadata: Optional[Union[Dict[str, Any], str]] = None,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
) -> Alias.Id:
    """create collection\n
    return collection id"""
    return fh.create_collection_from_df(
        data, name, metadata, auth=auth, conn_url=conn_url
    )


def get_collection_to_df(
    id: str,
    offset: int = 0,
    limit: int = -1,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
) -> pd.DataFrame:
    """return df from collection by `id`, pagination: unlimited - `limit` < 0"""
    collection = get_collection(id, offset, limit, auth=auth, conn_url=conn_url)
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
) -> pd.DataFrame:
    """return df from collection by `name` and mb also `operation_id` and `run_id` with which it was saved. raise if there are multiple collections, pagination: unlimited - `limit` < 0"""
    collection = get_collection_by_name(
        name, operation_id, run_id, offset, limit, auth=auth, conn_url=conn_url
    )
    records = list(map(lambda x: json.loads(x.data), collection.docs))
    return pd.DataFrame.from_records(records)


def create_schemes_by_path(
    path: str,
    wait: bool = True,
    *,
    auth: Optional[AUTH] = None,
    conn_url: Optional[str] = None,
) -> Dict[str, Alias.Id]:
    """schemes are created from json along the path to the directory, scheme_name - is the name of the file without '.json', returned a dict from the name of the created scheme to id"""
    res = dict()
    for filename in os.listdir(path):
        if filename.endswith(".json"):
            name = filename[:-5]
            with open(f"{path}/{filename}") as f:
                data = f.read()
            res[name] = create_scheme(
                data, name, wait=wait, auth=auth, conn_url=conn_url
            )
    return res


def create_app_settings(
    app_id: str,
    task_id: Optional[str] = None,
    save_collections_names: Optional[Union[str, List[str]]] = None,
) -> AppSettings:  # FIXME
    return AppSettings(
        appId=app_id, taskId=task_id, saveCollectionsName=save_collections_names
    )
