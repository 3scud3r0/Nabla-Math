import json
from pathlib import Path
import tempfile
import threading
import unittest
from urllib.request import Request, urlopen
from urllib.error import HTTPError

from nablamath.desktop.app import make_server


class DesktopTests(unittest.TestCase):
    def test_browser_routes_store_and_export_with_local_session(self):
        with tempfile.TemporaryDirectory() as directory:
            server, _ = make_server(Path(directory))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            url = f"http://127.0.0.1:{server.server_port}"
            try:
                with urlopen(url + "/") as response:
                    page = response.read().decode("utf-8")
                    self.assertIn("Seu laboratório matemático", page)
                    token = page.split("const auth='")[1].split("'")[0]
                def request(route, data=None, key=token):
                    raw = json.dumps(data).encode() if data is not None else None
                    headers = {"X-Nabla-Token": key, "Origin": url, "Content-Type": "application/json"}
                    with urlopen(Request(url + "/api/" + route, raw, headers)) as response:
                        return json.load(response)
                with self.assertRaises(HTTPError) as bad:
                    request("status", key="wrong")
                self.assertEqual(bad.exception.code, 403)
                calc = request("run", {"expression": "(x+x)/x", "values": {"x": "3"}})
                self.assertEqual(calc["result"]["value"], "2")
                self.assertGreaterEqual(len(calc["result"]["steps"]), 1)
                self.assertIn("x != 0", calc["result"]["assumptions"])
                self.assertEqual(request("status")["records"], 1)
                report = request("report", {"expression": "(x+x)/x", "values": {"x": "3"}})
                self.assertTrue(Path(report["path"]).is_file())
                exported = request("export", {})
                self.assertEqual(exported["records"], 1)
                self.assertTrue(Path(exported["path"]).is_file())
                with self.assertRaises(HTTPError) as bad_upload:
                    request("upload", {"consent": False, "redistributable": False})
                self.assertEqual(bad_upload.exception.code, 400)
                self.assertEqual(request("orbit", {"altitude_m": 400000})["formal_proof"], None)
                self.assertTrue(request("fluid", {"radius_m": .01, "length_m": 2, "pressure_pa": 5})["laminar_regime_compatible"])
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=2)

    def test_bounded_loop_stops_and_deduplicates(self):
        with tempfile.TemporaryDirectory() as directory:
            server, research = make_server(Path(directory))
            server.server_close()
            research.start(max_examples=5, interval_seconds=.1)
            research.worker.join(timeout=3)
            self.assertEqual(research.status()["attempted_this_session"], 5)
            self.assertEqual(research.count(), 5)
            with self.assertRaises(ValueError):
                research.start(max_examples=1001, interval_seconds=.1)
            self.assertEqual(research.curate_local("CC0-1.0", "my local calculations")["records"], 5)
