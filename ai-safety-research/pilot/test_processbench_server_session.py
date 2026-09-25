"""Offline lifecycle checks: all socket, process and signal operations are mocked."""
import io
import shlex
import signal
import unittest
from unittest.mock import MagicMock, patch

import processbench_server_session as session


class ServerSessionTests(unittest.TestCase):
    def simulate(self, data=b"STOP\n", poll=None, busy=False, watchdog=False,
                 persistent=False, cache_ram_mib=None):
        child = MagicMock(pid=43210, returncode=0)
        child.poll.return_value = poll
        socket = MagicMock()
        socket.__enter__.return_value = socket
        if busy:
            socket.bind.side_effect = OSError("occupied")
        selector = MagicMock()
        selector.select.return_value = [True]
        output = io.StringIO()
        clock = [0]

        def now():
            clock[0] += 6000 if watchdog else 1
            return clock[0]

        def kill(pid, sig):
            self.assertEqual(pid, 43210, "Never target an unowned process group")
            if sig == 0 and not persistent:
                raise ProcessLookupError

        with patch("socket.socket", return_value=socket), \
                patch("os.access", return_value=True), \
                patch("subprocess.Popen", return_value=child) as start, \
                patch("selectors.DefaultSelector", return_value=selector), \
                patch("signal.signal"), \
                patch("os.read", return_value=data), \
                patch("os.killpg", side_effect=kill) as killed, \
                patch("time.monotonic", side_effect=now), \
                patch("time.sleep"), \
                patch("sys.stdin", MagicMock()), \
                patch("sys.argv", ["python"]), \
                patch("sys.stdout", output):
            if busy:
                with self.assertRaises(OSError):
                    exec(session.remote_code(cache_ram_mib), {})
                start.assert_not_called()
                killed.assert_not_called()
            elif persistent:
                with self.assertRaisesRegex(RuntimeError, "still present"):
                    exec(session.remote_code(cache_ram_mib), {})
                killed.assert_any_call(43210, signal.SIGKILL)
                self.assertIn('"owned_group_absent": false', output.getvalue())
            else:
                exec(session.remote_code(cache_ram_mib), {})
                self.assertTrue(start.call_args.kwargs["start_new_session"])
                self.assertEqual(start.call_args.args[0], [
                    "/Applications/Ollama.app/Contents/Resources/ollama", "serve"])
                self.assertEqual(start.call_args.kwargs["env"]["OLLAMA_HOST"],
                                 "127.0.0.1:11435")
                self.assertEqual(start.call_args.kwargs["env"]["OLLAMA_NOPRUNE"], "1")
                if cache_ram_mib == 0:
                    self.assertEqual(start.call_args.kwargs['env']['LLAMA_ARG_CACHE_RAM'], '0')
                    self.assertIn('"LLAMA_ARG_CACHE_RAM": "0"', output.getvalue())
                killed.assert_any_call(43210, signal.SIGTERM)
                self.assertIn('"owned_group_absent": true', output.getvalue())
        return output.getvalue()

    def test_stop(self):
        self.assertIn("requested_stop", self.simulate())

    def test_eof(self):
        self.assertIn("stdin_eof", self.simulate(b""))

    def test_server_exit(self):
        self.assertIn("server_exited", self.simulate(poll=1))

    def test_busy_port_refusal(self):
        self.simulate(busy=True)

    def test_watchdog(self):
        self.assertIn("watchdog", self.simulate(watchdog=True))

    def test_persistent_group_fails_after_kill(self):
        self.simulate(persistent=True)

    def test_cache_disable_only_owned_service_environment(self):
        self.simulate(cache_ram_mib=0)
        command = session.ssh_command(0)
        self.assertEqual(shlex.split(command[-1]), ['python3', '-B', '-c', session.remote_code(0)])
        self.assertIn('CACHE_RAM_MIB = 0', session.remote_code(0))
        for invalid in (-1, 1, 8192, '0', False):
            with self.assertRaises(ValueError):
                session.ssh_command(invalid)

    def test_ssh_quoting_and_options(self):
        command = session.ssh_command()
        self.assertEqual(shlex.split(command[-1]),
                         ["python3", "-B", "-c", session.REMOTE_CODE])
        self.assertEqual(command[-2], "prabs@100.74.220.25")
        for option in ("BatchMode=yes", "StrictHostKeyChecking=yes",
                       "ControlMaster=no", "ControlPath=none"):
            self.assertIn(option, command)


if __name__ == "__main__":
    unittest.main()
