import json
import re
import sys
from typing import Any, Dict, List, Optional, Union


def numeric_version(version_str):  # noqa: ANN201
    try:
        # Split the version string by the period
        major, minor, patch = version_str.split(".")

        # Pad each part with leading zeros to make it 3 digits
        major = major.zfill(3)
        minor = minor.zfill(3)
        patch = patch.zfill(3)

        # Concatenate the padded parts
        numeric_version_str = f"{major}{minor}{patch}"

        # Convert the concatenated string to an integer
        result = int(numeric_version_str)
        # print(result)
        return result

    except ValueError:
        print("Invalid version string format. Expected format: X.X.X")
        return None


# from https://raw.githubusercontent.com/vast-ai/vast-python/master/vast.py
def parse_query(query_str: str, res: Dict = None) -> Dict:
    """
    Basically takes a query string (like the ones in the examples of commands for the search__offers function) and
    processes it into a dict of URL parameters to be sent to the server.

    :param str query_str:
    :param Dict res:
    :return Dict:
    """
    if res is None:
        res = {}
    if isinstance(query_str, list):
        query_str = " ".join(query_str)
    query_str = query_str.strip()
    opts = re.findall(
        "([a-zA-Z0-9_]+)( *[=><!]+| +(?:[lg]te?|nin|neq|eq|not ?eq|not ?in|in) )?( *)(\[[^\]]+\]|[^ ]+)?( *)",  # noqa: W605
        query_str,
    )

    # print(opts)
    # res = {}
    op_names = {
        ">=": "gte",
        ">": "gt",
        "gt": "gt",
        "gte": "gte",
        "<=": "lte",
        "<": "lt",
        "lt": "lt",
        "lte": "lte",
        "!=": "neq",
        "==": "eq",
        "=": "eq",
        "eq": "eq",
        "neq": "neq",
        "noteq": "neq",
        "not eq": "neq",
        "notin": "notin",
        "not in": "notin",
        "nin": "notin",
        "in": "in",
    }
    field_alias = {
        "cuda_vers": "cuda_max_good",
        "display_active": "gpu_display_active",
        "reliability": "reliability2",
        "dlperf_usd": "dlperf_per_dphtotal",
        "dph": "dph_total",
        "flops_usd": "flops_per_dphtotal",
    }
    field_multiplier = {
        "cpu_ram": 1000,
        "gpu_ram": 1000,
        "duration": 24.0 * 60.0 * 60.0,
    }

    fields = {
        "bw_nvlink",
        "compute_cap",
        "cpu_cores",
        "cpu_cores_effective",
        "cpu_ram",
        "cuda_max_good",
        "datacenter",
        "direct_port_count",
        "driver_version",
        "disk_bw",
        "disk_space",
        "dlperf",
        "dlperf_per_dphtotal",
        "dph_total",
        "duration",
        "external",
        "flops_per_dphtotal",
        "gpu_display_active",
        # "gpu_ram_free_min",
        "gpu_mem_bw",
        "gpu_name",
        "gpu_ram",
        "gpu_display_active",
        "has_avx",
        "host_id",
        "id",
        "inet_down",
        "inet_down_cost",
        "inet_up",
        "inet_up_cost",
        "machine_id",
        "min_bid",
        "mobo_name",
        "num_gpus",
        "pci_gen",
        "pcie_bw",
        "reliability2",
        "rentable",
        "rented",
        "storage_cost",
        "static_ip",
        "total_flops",
        "verification",
        "verified",
        "geolocation",
    }
    joined = "".join("".join(x) for x in opts)
    if joined != query_str:
        raise ValueError(
            "Unconsumed text. Did you forget to quote your query? "
            + repr(joined)
            + " != "
            + repr(query_str)
        )

    for field, op, _, value, _ in opts:
        value = value.strip(",[]")
        v = res.setdefault(field, {})
        op = op.strip()
        op_name = op_names.get(op)

        if field in field_alias:
            field = field_alias[field]

        if (field == "driver_version") and ("." in value):
            value = numeric_version(value)

        if field not in fields:
            print(
                f"Warning: Unrecognized field: {field}, see list of recognized fields.",
                file=sys.stderr,
            )
        if not op_name:
            raise ValueError(
                "Unknown operator. Did you forget to quote your query? "
                + repr(op).strip("u")
            )
        if op_name in ["in", "notin"]:
            value = [x.strip() for x in value.split(",") if x.strip()]
        if not value:
            raise ValueError(
                "Value cannot be blank. Did you forget to quote your query? "
                + repr((field, op, value))
            )
        if not field:
            raise ValueError(
                "Field cannot be blank. Did you forget to quote your query? "
                + repr((field, op, value))
            )
        if value in ["?", "*", "any"]:
            if op_name != "eq":
                raise ValueError("Wildcard only makes sense with equals.")
            if field in v:
                del v[field]
            if field in res:
                del res[field]
            continue

        if field in field_multiplier:
            value = float(value) * field_multiplier[field]

            if isinstance(value, str):
                v[op_name] = value.replace("_", " ")
            else:
                v[op_name] = value

        else:
            # print(value)
            if value == "true":
                v[op_name] = True
            elif value == "False":
                v[op_name] = False
            elif isinstance(value, str):
                v[op_name] = value.replace("_", " ")
            else:
                # v[op_name] = [v.replace('_', ' ') for v in value]
                v[op_name] = value

        res[field] = v

    return res


# from https://raw.githubusercontent.com/vast-ai/vast-python/master/vast.py
def parse(
    search_query: str,
    show_order: str = "score-",
    no_default: bool = False,
    instance_type="on-demand",
) -> Dict[str, Any]:
    """Query syntax:

            query = comparison comparison...
            comparison = field op value
            field = <name of a field>
            op = one of: <, <=, ==, !=, >=, >, in, notin
            value = <bool, int, float, etc> | 'any'
            bool: True, False

    note: to pass '>' and '<' on the command line, make sure to use quotes
    note: to encode a string query value (ie for gpu_name), replace any spaces ' ' with underscore '_'


    Examples:

            # search for somewhat reliable single RTX 3090 instances, filter out any duplicates or offers that conflict with our existing stopped instances
            ./vast search offers 'reliability > 0.98 num_gpus=1 gpu_name=RTX_3090 rented=False'

            # search for datacenter gpus with minimal compute_cap and total_flops
            ./vast search offers 'compute_cap > 610 total_flops > 5 datacenter=True'

            # search for reliable machines with at least 4 gpus, unverified, order by num_gpus, allow duplicates
            ./vast search offers 'reliability > 0.99  num_gpus>=4 verified=False rented=any' -o 'num_gpus-'


    Available fields:

                    Name				  Type	   Description

            bw_nvlink			   float	 bandwidth NVLink
            compute_cap:			int	   cuda compute capability*100  (ie:  650 for 6.5, 700 for 7.0)
            cpu_cores:			  int	   # virtual cpus
            cpu_cores_effective:	float	 # virtual cpus you get
            cpu_ram:				float	 system RAM in gigabytes
            cuda_vers:			  float	 machine max supported cuda version (based on driver version)
            datacenter:			 bool	  show only datacenter offers
            direct_port_count	   int	   open ports on host's router
            disk_bw:				float	 disk read bandwidth, in MB/s
            disk_space:			 float	 disk storage space, in GB
            dlperf:				 float	 DL-perf score  (see FAQ for explanation)
            dlperf_usd:			 float	 DL-perf/$
            dph:					float	 $/hour rental cost
            driver_version		  string	machine's nvidia driver version as 3 digit string ex. "535.86.05"
            duration:			   float	 max rental duration in days
            external:			   bool	  show external offers in addition to datacenter offers
            flops_usd:			  float	 TFLOPs/$
            geolocation:			string	Two letter country code. Works with operators =, !=, in, not in (e.g. geolocation not in [XV,XZ])
            gpu_mem_bw:			 float	 GPU memory bandwidth in GB/s
            gpu_name:			   string	GPU model name (no quotes, replace spaces with underscores, ie: RTX_3090 rather than 'RTX 3090')
            gpu_ram:				float	 GPU RAM in GB
            gpu_frac:			   float	 Ratio of GPUs in the offer to gpus in the system
            gpu_display_active:	 bool	  True if the GPU has a display attached
            has_avx:				bool	  CPU supports AVX instruction set.
            id:					 int	   instance unique ID
            inet_down:			  float	 internet download speed in Mb/s
            inet_down_cost:		 float	 internet download bandwidth cost in $/GB
            inet_up:				float	 internet upload speed in Mb/s
            inet_up_cost:		   float	 internet upload bandwidth cost in $/GB
            machine_id			  int	   machine id of instance
            min_bid:				float	 current minimum bid price in $/hr for interruptible
            num_gpus:			   int	   # of GPUs
            pci_gen:				float	 PCIE generation
            pcie_bw:				float	 PCIE bandwidth (CPU to GPU)
            reliability:			float	 machine reliability score (see FAQ for explanation)
            rentable:			   bool	  is the instance currently rentable
            rented:				 bool	  allow/disallow duplicates and potential conflicts with existing stopped instances
            storage_cost:		   float	 storage cost in $/GB/month
            static_ip:			  bool	  is the IP addr static/stable
            total_flops:			float	 total TFLOPs from all GPUs
            verified:			   bool	  is the machine verified
    """
    field_alias = {
        "cuda_vers": "cuda_max_good",
        "reliability": "reliability2",
        "dlperf_usd": "dlperf_per_dphtotal",
        "dph": "dph_total",
        "flops_usd": "flops_per_dphtotal",
    }
    try:
        if no_default:
            query = {}
        else:
            query = {
                "verified": {"eq": True},
                "external": {"eq": False},
                "rentable": {"eq": True},
                "rented": {"eq": False},
            }
            # query = {"verified": {"eq": True}, "external": {"eq": False}, "rentable": {"eq": True} }

        if search_query is not None:
            query = parse_query(search_query, query)

        order = []
        for name in show_order.split(","):
            name = name.strip()
            if not name:
                continue
            direction = "asc"
            if name.strip("-") != name:
                direction = "desc"
            field = name.strip("-")
            if field in field_alias:
                field = field_alias[field]
            order.append([field, direction])

        query["order"] = order
        query["type"] = instance_type
        # For backwards compatibility, support --type=interruptible option
        if query["type"] == "interruptible":
            query["type"] = "bid"
    except ValueError as e:
        print("Error: ", e)
        return None
    return query


def vast_settings(
    id: Optional[int] = None, query: Optional[Union[str, Dict[str, Any]]] = None, api_key: Optional[str] = None, disk: Optional[int] = None, assets: Optional[List[str]] = None
) -> str:
    """
    Platform settings for create app:\n
            by nothing - use default query inside\n
            by offer id - try use this id for app\n
            by query - use this query inside\n

    Examples:\n
            vast_settings()\n
            vast_settings(id="<id, that found with vast (vastai search offers)>")\n
            vast_settings(query={"dph": {"lt": "0.1"}})\n
            vast_settings(query="dph<0.1")\n
    """
    res = {}
    if id is not None:
        assert isinstance(id, int), "wrong id type"
        assert query is None, "id and query set"
        res["id"] = id
    elif query is not None:
        if isinstance(query, str):
            res["query"] = parse(query, no_default=True)  # run only with this options
        else:
            assert isinstance(query, dict), "wrong query type: it should be str or dict"
            res["query"] = query
    if api_key is not None:
        assert isinstance(api_key, str), "wrong api_key type"
        res["apiKey"] = api_key
    if disk is not None:
        assert isinstance(disk, int), "wrong disk type"
        res["disk"] = disk
    if assets is not None:
        res["assets"] = assets
    return json.dumps(res)
