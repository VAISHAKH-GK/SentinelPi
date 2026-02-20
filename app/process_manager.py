"""
SentinelPi — Process Manager
Runs module scripts as subprocesses with live output and safe teardown.
"""

import subprocess
import threading
import os
import signal


class ProcessManager:
    def __init__(self):
        self._processes: dict = {}

    def start(self, name: str, script_path: str, args: list = None,
              on_output=None, on_exit=None) -> tuple:
        if self.is_running(name):
            return False, "Already running"

        cmd = ["python3", "-u", script_path] + (args or [])
        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                preexec_fn=os.setsid,
            )
            self._processes[name] = proc
            threading.Thread(
                target=self._reader,
                args=(name, proc, on_output, on_exit),
                daemon=True,
            ).start()
            return True, f"Started PID {proc.pid}"
        except FileNotFoundError:
            return False, f"Script not found: {script_path}"
        except Exception as e:
            return False, str(e)

    def stop(self, name: str) -> bool:
        proc = self._processes.get(name)
        if not proc or proc.poll() is not None:
            return False
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
        except Exception:
            pass
        return True

    def is_running(self, name: str) -> bool:
        p = self._processes.get(name)
        return p is not None and p.poll() is None

    def stop_all(self):
        for name in list(self._processes):
            self.stop(name)

    def _reader(self, name, proc, on_output, on_exit):
        if proc.stdout:
            for line in proc.stdout:
                if on_output:
                    on_output(line.rstrip())
        proc.wait()
        if on_exit:
            on_exit(proc.returncode)


process_manager = ProcessManager()
