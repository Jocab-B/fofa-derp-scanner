import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "extract_success.py"


def probe_row(region_id, probe_class, status, latest, results, recent):
    mean = results.split().count("true") / len(results.split())
    return (
        f"<tr><td>{probe_class}</td>"
        f"<td>{probe_class} class={probe_class} region_id={region_id}</td>"
        "<td>15s</td><td>now</td><td>now</td>"
        f"<td>{status} Recent: [{results}] Mean: {mean}</td>"
        f"<td>{latest} Recent: [{recent}] Median: 1ms</td><td></td></tr>"
    )


class ExtractSuccessTest(unittest.TestCase):
    def test_missing_input_exits_nonzero(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            result = subprocess.run(
                [sys.executable, SCRIPT, "--html", directory / "missing.html",
                 "--json", directory / "missing.json"],
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(result.returncode, 0)

    def test_runs_without_third_party_html_parser(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            html = directory / "report.html"
            source = directory / "derp.json"
            output = directory / "success.json"
            html.write_text(
                "<table><tr>"
                "<td>mesh</td><td>derp_mesh class=derp_mesh region_id=900</td>"
                "<td>15s</td><td>now</td><td>now</td>"
                "<td>succeeded Recent: [true] Mean: 1</td>"
                "<td>50ms Recent: [50ms] Median: 50ms</td><td></td>"
                "</tr></table>",
                encoding="utf-8",
            )
            source.write_text(json.dumps({"Regions": {"900": {"RegionID": 900}}}), encoding="utf-8")

            result = subprocess.run(
                [sys.executable, SCRIPT, "--html", html, "--json", source, "--output", output,
                 "--start", "900"],
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(list(json.loads(output.read_text(encoding="utf-8"))["Regions"]), ["900"])

    def test_renumbers_filtered_regions_in_latency_order(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            html = directory / "report.html"
            source = directory / "derp.json"
            output = directory / "success.json"
            html.write_text(
                "<table>" + "".join([
                    probe_row(900, "derp_mesh", "succeeded", "90ms", "true true", "80ms 95ms"),
                    probe_row(901, "derp_udp", "succeeded", "10ms", "true true", "10ms 10ms"),
                    probe_row(902, "derp_mesh", "succeeded", "100ms", "true true", "80ms 90ms"),
                    probe_row(903, "derp_mesh", "succeeded", "80ms", "true false", "80ms"),
                    probe_row(904, "derp_mesh", "succeeded", "80ms", "true true", "80ms 120ms 150ms"),
                    probe_row(905, "derp_mesh", "succeeded", "60ms", "true true", "50ms 70ms"),
                    probe_row(906, "derp_mesh", "failed", "50ms", "false false", ""),
                ]) + "</table>",
                encoding="utf-8",
            )
            source.write_text(
                json.dumps({"Regions": {
                    str(region): {
                        "RegionID": region,
                        "RegionCode": f"custom{region}",
                        "Nodes": [{"Name": f"{region}-node", "RegionID": region}],
                    }
                    for region in range(900, 907)
                }}),
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, SCRIPT, "--html", html, "--json", source, "--output", output,
                 "--start", "1000"],
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            regions = json.loads(output.read_text(encoding="utf-8"))["Regions"]
            self.assertEqual(list(regions), ["1000", "1001"])
            self.assertEqual(regions["1000"], {
                "RegionID": 1000,
                "RegionCode": "custom1000",
                "Nodes": [{"Name": "1000-node", "RegionID": 1000}],
            })
            self.assertEqual(regions["1001"], {
                "RegionID": 1001,
                "RegionCode": "custom1001",
                "Nodes": [{"Name": "1001-node", "RegionID": 1001}],
            })
