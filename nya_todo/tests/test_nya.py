import json
import subprocess
import threading
import unittest
import urllib.error
import urllib.request

from nya_todo import final, temporary_permanent
from nya_todo.cat_engine_bridge import CatEngineBridge, pythonCatgirlFallback
from nya_todo.config import CatConfigurationResolver
from nya_todo.legacy_compatibility_layer import PHASES, nextPhase
from nya_todo.server import makeServer


def call(base, method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(base + path, data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            raw = r.read()
            return r.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        raw = e.read()
        return e.code, json.loads(raw) if raw else None


class ImportantThings(unittest.TestCase):
    def setUp(self):
        temporary_permanent.resetForTests()
        self.server = makeServer("127.0.0.1", 0)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.base = "http://127.0.0.1:%d" % self.server.server_address[1]

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()

    def test_create_list_delete(self):
        status, item = call(self.base, "POST", "/api/todo", {"title": "buy milk", "priority": 2})
        self.assertEqual(status, 201)
        self.assertEqual(item["cat"]["score"], 29)
        _, listing = call(self.base, "GET", "/api/todo")
        self.assertEqual(listing["count"], 1)
        self.assertEqual(call(self.base, "DELETE", "/api/todo?id=%d" % item["id"])[0], 204)
        self.assertEqual(call(self.base, "GET", "/api/todo")[1]["count"], 0)

    def test_phase_cycle_returns_to_todo_and_flips_done(self):
        _, item = call(self.base, "POST", "/api/todo", {"title": "launch invoice"})
        seen = []
        for _ in range(3):
            _, item = call(self.base, "POST", "/api/todo/todo", {"id": item["id"]})
            seen.append(item["phase"])
        self.assertEqual(seen, ["accounting", "space", "todo"])
        self.assertTrue(item["done"])

    def test_accounting_and_space_views(self):
        _, item = call(self.base, "POST", "/api/todo", {"title": "x", "priority": 1})
        _, acc = call(self.base, "POST", "/api/todo/todo", {"id": item["id"]})
        self.assertEqual(acc["ledger"]["currency"], "kbps")
        _, space = call(self.base, "POST", "/api/todo/todo", {"id": item["id"]})
        self.assertGreater(space["orbit"]["period_min"], 80)  # physics: nothing orbits faster than LEO
        self.assertEqual(space["orbit"]["downlink_udp_port"], 5600 + item["id"])

    def test_bad_input(self):
        self.assertEqual(call(self.base, "POST", "/api/todo", {"title": "  "})[0], 400)
        self.assertEqual(call(self.base, "POST", "/api/todo/todo", {"id": 999})[0], 404)
        self.assertEqual(call(self.base, "GET", "/api/nope")[0], 404)

    def test_teapots(self):
        self.assertEqual(call(self.base, "GET", "/api/why")[0], 418)
        self.assertEqual(call(self.base, "GET", "/api/cat?brew=coffee")[0], 418)
        self.assertEqual(call(self.base, "GET", "/api/cat")[0], 200)

    def test_user_endpoints_agree(self):
        _, a = call(self.base, "GET", "/api/final-user")
        _, b = call(self.base, "GET", "/api/legacy-final-user-manager")
        self.assertEqual(b["userUser"]["actualUser"], a)

    def test_python_and_rust_cats_agree_if_rust_exists(self):
        bridge = CatEngineBridge()
        binary = bridge.binaryPath()
        if binary is None:
            self.skipTest("cat_engine not built; the Python cat has no one to disagree with")
        for title, pr in [("", 0), ("buy milk", 2), ("refactor the entire universe today", 10)]:
            out = json.loads(subprocess.run([str(binary), str(pr), title], capture_output=True, text=True).stdout)
            self.assertEqual(out, pythonCatgirlFallback(title, pr))


class ImportantSounding(unittest.TestCase):
    def test_list_exists(self):
        temporary_permanent.resetForTests()
        self.assertIsInstance(final.doNotTouchThis().list(), list)

    def test_cat_has_name(self):
        self.assertTrue(final.catEngineName())

    def test_banana_final2_is_not_banana_final2_real(self):
        self.assertNotEqual(final.bananaFinal2, final.bananaFinal2_REAL)

    def test_server_survives_existence_of_user(self):
        server = makeServer("127.0.0.1", 0)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            status, user = call("http://127.0.0.1:%d" % server.server_address[1], "GET", "/api/final-user")
            self.assertEqual(status, 200)
            self.assertEqual(user["name"], "actualUser")
        finally:
            server.shutdown()
            server.server_close()

    def test_phases_are_a_cycle(self):
        p = PHASES[0]
        for _ in PHASES:
            p = nextPhase(p)
        self.assertEqual(p, PHASES[0])

    def test_env_is_excessive(self):
        self.assertGreater(len(CatConfigurationResolver().resolve()), 40)


if __name__ == "__main__":
    unittest.main()
