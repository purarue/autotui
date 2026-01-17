import json
from io import StringIO

from typing import Any, TextIO, Literal
from collections.abc import Callable

from .serialize import serialize_namedtuple, deserialize_namedtuple, PrimitiveType
from .typehelpers import NT, T


Format = Literal["json", "yaml"]


def _pretty_print(kwargs: dict[str, Any]) -> dict[str, Any]:
    if "indent" not in kwargs:
        kwargs["indent"] = "    "
    return kwargs


def namedtuple_sequence_dumps(
    nt_items: list[NT],
    *,
    attr_serializers: dict[str, Callable[[T], PrimitiveType]] | None = None,
    type_serializers: dict[type, Callable[[Any], PrimitiveType]] | None = None,
    format: Format | None = "json",
    **kwargs: Any,
) -> str:
    """
    Dump the list of namedtuples to a JSON string
    """
    s_obj: list[dict[str, Any]] = []
    for nt in nt_items:
        s_obj.append(serialize_namedtuple(nt, attr_serializers, type_serializers))
    if format == "json":
        return json.dumps(s_obj, **_pretty_print(kwargs))
    elif format == "yaml":
        from yaml import safe_dump

        buf = StringIO()
        safe_dump(s_obj, buf, **kwargs)
        return buf.getvalue()
    else:
        raise ValueError(
            f"Format is None while trying to dump {nt_items[0] if len(nt_items) > 0 else nt_items}"
        )


def namedtuple_sequence_dump(
    nt_items: list[NT],
    fp: TextIO,
    *,
    attr_serializers: dict[str, Callable[[T], PrimitiveType]] | None = None,
    type_serializers: dict[type, Callable[[Any], PrimitiveType]] | None = None,
    format: Format | None = "json",
    **kwargs: Any,
) -> None:
    """
    Dump the list of namedtuples to a file-like object as JSON
    """
    # dump to string first, so JSON serialization errors dont cause data losses
    dumped: str = namedtuple_sequence_dumps(
        nt_items,
        attr_serializers=attr_serializers,
        type_serializers=type_serializers,
        format=format,
        **kwargs,
    )
    fp.write(dumped)


def _load_json(nt_string: str) -> Any:
    try:
        # speedup load if orjson is installed
        import orjson

        return orjson.loads(nt_string)
    except ImportError:
        pass
    return json.loads(nt_string)


def namedtuple_sequence_loads(
    nt_string: str,
    to: type[NT],
    *,
    attr_deserializers: dict[str, Callable[[PrimitiveType], Any]] | None = None,
    type_deserializers: dict[type, Callable[[PrimitiveType], Any]] | None = None,
    format: Format | None = "json",
) -> list[NT]:
    """
    Load a list of namedtuples specified by 'to' from a JSON string
    """

    if format == "json":
        loaded_obj = _load_json(nt_string)
    elif format == "yaml":
        from yaml import safe_load

        loaded_obj = safe_load(nt_string)
    else:
        raise ValueError("unset format while trying to dump")
    if not isinstance(loaded_obj, list):
        raise TypeError(
            f"{loaded_obj} is a {type(loaded_obj).__name__}, expected a top-level list from JSON source"
        )
    ds_items: list[NT] = []
    for lo in loaded_obj:
        ds_items.append(
            deserialize_namedtuple(
                lo,
                to,
                attr_deserializers=attr_deserializers,
                type_deserializers=type_deserializers,
            )
        )
    return ds_items


def namedtuple_sequence_load(
    fp: TextIO,
    to: type[NT],
    *,
    attr_deserializers: dict[str, Callable[[PrimitiveType], Any]] | None = None,
    type_deserializers: dict[type, Callable[[PrimitiveType], Any]] | None = None,
    format: Format | None = "json",
) -> list[NT]:
    """
    Load a list of namedtuples to the namedtuple specified by 'to'
    from a file-like object containing JSON
    """
    return namedtuple_sequence_loads(
        fp.read(),
        to,
        attr_deserializers=attr_deserializers,
        type_deserializers=type_deserializers,
        format=format,
    )
