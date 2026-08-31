import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.convert_assets import convert_asset_to_derp


SCRIPT = Path(__file__).parents[1] / "scripts" / "convert_assets.py"


class ConvertAssetsTest(unittest.TestCase):
    def test_converts_single_record_export(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "assets.json"
            output = Path(directory) / "derp.json"
            source.write_text(
                '{"ip":"1.1.1.1","port":"443","domain":"","city":"A"}\n',
                encoding="utf-8",
            )

            convert_asset_to_derp(source, output)

            self.assertEqual(list(json.loads(output.read_text())["Regions"]), ["900"])

    def test_converts_ndjson_export(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "assets.json"
            output = Path(directory) / "derp.json"
            source.write_text(
                '{"ip":"1.1.1.1","port":"443","domain":"","city":"A"}\n'
                '{"ip":"2.2.2.2","port":"8443","domain":"","city":"B"}\n',
                encoding="utf-8",
            )

            convert_asset_to_derp(source, output)

            self.assertTrue(output.exists())
            self.assertEqual(list(json.loads(output.read_text())["Regions"]), ["900", "901"])

    def test_converts_json_array_export(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "assets.json"
            output = Path(directory) / "derp.json"
            source.write_text(
                '[{"ip":"1.1.1.1","port":"443","domain":"","city":"A"}]',
                encoding="utf-8",
            )

            convert_asset_to_derp(source, output)

            self.assertEqual(list(json.loads(output.read_text())["Regions"]), ["900"])

    def test_missing_input_exits_nonzero(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [sys.executable, SCRIPT, "--input", Path(directory) / "missing.json"],
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(result.returncode, 0)
