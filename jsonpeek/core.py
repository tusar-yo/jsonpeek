from typing import Any, List

_NAMES = {type(None): "null", bool: "bool", int: "int", float: "float", str: "string"}


def _scalar(v: Any) -> str:
    return _NAMES.get(type(v), type(v).__name__)


def describe(value: Any) -> Any:
    """Return a structural description.

    Scalars -> type-name string. Dict -> {key: description}.
    List -> {"__list__": n, "of": merged element description or None}.
    Mixed alternatives -> {"__union__": [descriptions]}.
    """
    if isinstance(value, dict):
        return {k: describe(v) for k, v in value.items()}
    if isinstance(value, list):
        merged = None
        for item in value:
            merged = _merge(merged, describe(item)) if merged is not None else describe(item)
        return {"__list__": len(value), "of": merged}
    return _scalar(value)


def _union_members(d: Any) -> List[Any]:
    return d["__union__"] if isinstance(d, dict) and "__union__" in d else [d]


def _kind(d: Any) -> str:
    if isinstance(d, str):
        return d
    if "__list__" in d:
        return "list"
    return "object"


def _merge(a: Any, b: Any) -> Any:
    """Merge two descriptions; objects merge key-wise (missing keys become optional '?')."""
    members: List[Any] = []
    for m in _union_members(a) + _union_members(b):
        for i, existing in enumerate(members):
            if _kind(existing) == _kind(m):
                members[i] = _merge_same(existing, m)
                break
        else:
            members.append(m)
    return members[0] if len(members) == 1 else {"__union__": members}


def _merge_same(a: Any, b: Any) -> Any:
    if isinstance(a, str):
        return a
    if "__list__" in a:
        of = a["of"] if b["of"] is None else (b["of"] if a["of"] is None else _merge(a["of"], b["of"]))
        return {"__list__": a["__list__"] + b["__list__"], "of": of}
    out = {}
    for k in list(a) + [k for k in b if k not in a]:
        ka = k if k in a else None
        kb = k if k in b else None
        if ka and kb:
            out[k] = _merge(a[k], b[k])
        else:
            out[k.rstrip("?") + "?"] = a[k] if ka else b[k]
    return out


def render(desc: Any, max_depth: int = 8, indent: int = 0) -> str:
    pad = "  " * indent
    if isinstance(desc, str):
        return desc
    if "__union__" in desc:
        return " | ".join(render(m, max_depth, indent) for m in desc["__union__"])
    if "__list__" in desc:
        n, of = desc["__list__"], desc["of"]
        if of is None:
            return "list (empty)"
        inner = render(of, max_depth, indent)
        return f"list[{n}] of {inner}"
    if indent >= max_depth:
        return "{...}"
    if not desc:
        return "{}"
    lines = ["{"]
    for k, v in desc.items():
        lines.append(f"{pad}  {k}: {render(v, max_depth, indent + 1)}")
    lines.append(f"{pad}}}")
    return "\n".join(lines)
