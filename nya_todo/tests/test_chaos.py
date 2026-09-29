import importlib
import os
import shutil
import subprocess
import tempfile
import threading
import unittest
from pathlib import Path

from nya_todo import temporary_permanent
from nya_todo.dumb_chess import DumbChess
from nya_todo.math_kilometers import KILOMETERS, pointlessMathPipeline
from nya_todo.parity_validator import validateParity
from nya_todo.raw_syscalls import rawGetpid, rawWrite
from nya_todo.server import makeServer
from nya_todo.tests.test_nya import call

ROOT = Path(__file__).resolve().parents[2]
layer = importlib.import_module("nya_todo.бурят_猫_layer")


class Parity(unittest.TestCase):
    def test_values(self):
        for n in [0, 1, 2, 13, 14, 15, 99, 100, -7, -8, 5000]:
            self.assertEqual(validateParity(n), "парное" if n % 2 == 0 else "непарное", n)

    def test_rejects_junk(self):
        for bad in [True, 1.5, "2", 5001]:
            with self.assertRaises(ValueError):
                validateParity(bad)


class Chess(unittest.TestCase):
    def test_opening(self):
        g = DumbChess()
        self.assertEqual(g.play("e2e4"), (True, "ok"))
        self.assertEqual(g.play("e2e4")[0], False)  # black to move, empty square
        self.assertEqual(g.play("g8f6"), (True, "ok"))
        self.assertFalse(g.play("f1f5")[0])  # blocked by own pawn
        self.assertTrue(g.play("f1c4")[0])

    def test_illegal(self):
        g = DumbChess()
        self.assertFalse(g.play("e2e5")[0])
        self.assertFalse(g.play("a1a3")[0])
        self.assertFalse(g.play("zz")[0])
        self.assertFalse(g.play("e7e5")[0])  # not black's turn

    def test_scholars_mate_ends_by_king_capture(self):
        g = DumbChess()
        for m in ["e2e4", "e7e5", "f1c4", "b8c6", "d1h5", "g8f6", "h5f7", "e8f7"]:
            self.assertTrue(g.play(m)[0], m)
        # black king took the queen; keep going until a king is captured
        g = DumbChess()
        for m in ["e2e4", "f7f6", "d1h5", "a7a6", "h5e8"]:
            self.assertTrue(g.play(m)[0], m)
        self.assertEqual(g.winner, "white")
        self.assertEqual(g.play("a6a5"), (False, "game over"))


class Pointless(unittest.TestCase):
    def test_kilometers_do_nothing(self):
        self.assertGreater(len(KILOMETERS), 400)
        for x in [-1000, -1, 0, 1, 29, 12345]:
            self.assertEqual(pointlessMathPipeline(x), x)


class Syscalls(unittest.TestCase):
    def test_getpid_matches_os(self):
        self.assertEqual(rawGetpid(), os.getpid())

    def test_rawwrite_writes(self):
        r, w = os.pipe()
        self.assertEqual(rawWrite(w, "нюдэ 猫"), len("нюдэ 猫".encode()))
        os.close(w)
        self.assertEqual(os.read(r, 100).decode(), "нюдэ 猫")
        os.close(r)


class Relay(unittest.TestCase):
    def setUp(self):
        self.log = tempfile.NamedTemporaryFile(delete=False)
        self.log.close()
        os.environ["NYA_RELAY_LOG"] = self.log.name

    def tearDown(self):
        os.environ.pop("NYA_RELAY_LOG", None)
        os.unlink(self.log.name)

    def lines(self):
        return Path(self.log.name).read_text().splitlines()

    def test_python_relays_through_shell(self):
        self.assertEqual(layer.shellPythonRelay("unit", 1, 2), 0)
        self.assertIn("tag=unit", self.lines()[0])

    def test_creating_a_todo_reaches_the_relay(self):
        temporary_permanent.resetForTests()
        server = makeServer("127.0.0.1", 0)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            base = "http://127.0.0.1:%d" % server.server_address[1]
            call(base, "POST", "/api/todo", {"title": "relay me"})
            status, body = call(base, "GET", "/api/relay")
            self.assertEqual((status, body["exit"]), (200, 0))
            self.assertEqual(call(base, "GET", "/api/parity?n=41")[1]["parity"], "непарное")
            self.assertEqual(call(base, "GET", "/api/parity?n=x")[0], 400)
            self.assertEqual(call(base, "POST", "/api/chess", {"move": "e2e4"})[0], 200)
            self.assertEqual(call(base, "POST", "/api/chess", {"move": "e2e4"})[0], 422)
        finally:
            server.shutdown()
            server.server_close()
        tags = "\n".join(self.lines())
        self.assertIn("tag=python-create", tags)
        self.assertIn("tag=http", tags)

    @unittest.skipUnless(shutil.which("as") and shutil.which("ld") and os.uname().machine == "x86_64",
                         "no assembler, no assembly")
    def test_assembly_calls_python_via_execve(self):
        with tempfile.TemporaryDirectory() as d:
            exe = os.path.join(d, "nya")
            subprocess.check_call([str(ROOT / "nya_todo/scripts/build_asm.sh"), exe], cwd=ROOT)
            r = subprocess.run([exe], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0)
        self.assertIn("Сайн байна", r.stdout)
        self.assertIn("tag=asm", "\n".join(self.lines()))

    @unittest.skipUnless(shutil.which("node"), "no node")
    def test_javascript_calls_python_via_shell(self):
        r = subprocess.run(["node", str(ROOT / "nya_todo/js/nya_relay.js"), "7"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0)
        self.assertIn("你好", r.stdout)
        self.assertIn("tag=js", "\n".join(self.lines()))


if __name__ == "__main__":
    unittest.main()
