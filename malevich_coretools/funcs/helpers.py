import json
from typing import Any, Dict, Optional, Union

import pandas as pd

from malevich_coretools.abstract.abstract import Alias, DocsDataCollection
from malevich_coretools.funcs.funcs import post_collections_data
from malevich_coretools.secondary import Config


def create_collection_from_file_df(file: str, name: Optional[str], metadata: Optional[Union[Dict[str, Any], str]], *args, **kwargs) -> Alias.Id:
    data = pd.read_csv(file)
    if name is None:
        name = file
    return create_collection_from_df(data, name=file, metadata=metadata, *args, **kwargs)


def create_collection_from_df(data: pd.DataFrame, name: Optional[str], metadata: Optional[Union[Dict[str, Any], str]], *args, **kwargs) -> Alias.Id:
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
    return post_collections_data(DocsDataCollection(data=[row.to_json() for _, row in data.iterrows()], name=name, metadata=metadata), *args, **kwargs)
