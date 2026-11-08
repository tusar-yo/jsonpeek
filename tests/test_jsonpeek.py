import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from jsonpeek import describe, render
from jsonpeek.cli import main


class DescribeTests(unittest.TestCase):
    def test_scalars(self):
        self.assertEqual(describe(1), "int")
        self.assertEqual(describe(1.5), "float")
        self.assertEqual(describe("x"), "string")
        self.assertEqual(describe(True), "bool")
        self.assertEqual(describe(None), "null")

    def test_bool_is_not_int(self):
        self.assertEqual(describe([True, 1])["of"], {"__union__": ["bool", "int"]})

    def test_empty_list(self):
        self.assertEqual(describe([]), {"__list__": 0, "of": None})

    def test_list_of_objects_merges_keys(self):
        d = describe([{"a": 1, "b": "x"}, {"a": 2, "c": None}])
        self.assertEqual(d["__list__"], 2)
        self.assertEqual(d["of"], {"a": "int", "b?": "string", "c?": "null"})

    def test_mixed_list(self):
        d = describe([1, "a", 2])
        self.assertEqual(d["of"], {"__union__": ["int", "string"]})

    def test_nested(self):
        d = describe({"users": [{"id": 1, "tags": ["a", "b"]}]})
        self.assertEqual(d["users"]["of"]["tags"], {"__list__": 2, "of": "string"})


class RenderTests(unittest.TestCase):
    def test_render_object(self):
        out = render(describe({"a": 1, "b": [1, 2]}))
        self.assertIn("a: int", out)
        self.assertIn("b: list[2] of int", out)

    def test_union_render(self):
        self.assertEqual(render(describe([1, "x"])), "list[2] of int | string")

    def test_depth_limit(self):
        out = render(describe({"a": {"b": {"c": 1}}}), max_depth=1)
        self.assertIn("{...}", out)
        self.assertNotIn("c: int", out)


class CliTests(unittest.TestCase):
    def test_file(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        self.addCleanup(os.remove, path)
        json.dump({"name": "x", "n": 3}, open(path, "w"))
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(main([path]), 0)
        self.assertIn("name: string", out.getvalue())

    def test_invalid_json(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        self.addCleanup(os.remove, path)
        open(path, "w").write("{nope")
        self.assertEqual(main([path]), 2)

    def test_missing_file(self):
        self.assertEqual(main(["/nonexistent.json"]), 2)


if __name__ == "__main__":
    unittest.main()
