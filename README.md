# jsonpeek

Get the *shape* of a big JSON file without scrolling through it. Zero dependencies, pure Python.

Arrays of objects are merged into one description. Keys that only appear in some items are marked optional with `?`.

```
$ jsonpeek users.json
{
  total: int
  users: list[3] of {
    id: int
    name: string
    tags: list[2] of string
    email?: string
  }
}
```

## Install

```
pip install git+https://github.com/tusar-yo/jsonpeek.git
```

## Usage

```
jsonpeek data.json
curl -s https://api.example.com/items | jsonpeek
jsonpeek data.json --max-depth 2
```

Mixed types show as unions, e.g. `list[4] of int | string`. Exit code `2` on unreadable or invalid JSON.

## Develop

```
python -m unittest discover -s tests -v
```

MIT licensed.
