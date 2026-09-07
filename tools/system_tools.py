"""System tools: time, status, app/url launcher, shell with safety."""

import datetime
import os
import shutil
import subprocess
import webbrowser

import psutil

import config


class SystemTools:
    def __init__(self, mongo=None):
        self.mongo = mongo

    # ------------------------------------------------------------------ time
    def get_time(self):
        now = datetime.datetime.now()
        return {
            "datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
            "weekday": now.strftime("%A"),
        }

    # ------------------------------------------------------------- system info
    def system_status(self):
        cpu = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory()
        drive = os.path.splitdrive(os.path.abspath("."))[0] + os.sep
        disk = psutil.disk_usage(drive)
        battery = psutil.sensors_battery()
        return {
            "cpu_percent": cpu,
            "ram_percent": mem.percent,
            "ram_used_gb": round(mem.used / 1024 ** 3, 2),
            "ram_total_gb": round(mem.total / 1024 ** 3, 2),
            "disk_percent": disk.percent,
            "disk_free_gb": round(disk.free / 1024 ** 3, 2),
            "battery_percent": battery.percent if battery else None,
            "battery_plugged": battery.power_plugged if battery else None,
        }

    # ---------------------------------------------------------------- launchers
    def open_application(self, name):
        name = (name or "").strip().lower()
        if not name:
            return {"error": "No application name given."}
        known = {
            "notepad": ["notepad.exe", None],
            "calculator": ["calc.exe", None],
            "paint": ["mspaint.exe", None],
            "cmd": ["cmd.exe", None],
            "powershell": ["powershell.exe", None],
            "explorer": ["explorer.exe", None],
            "task manager": ["taskmgr.exe", None],
            "chrome": ["start", "chrome"],
            "edge": ["start", "msedge"],
            "firefox": ["start", "firefox"],
            "word": ["start", "winword"],
            "excel": ["start", "excel"],
            "settings": ["start", "ms-settings:"],
        }
        if name in known:
            exe_or_args = known[name]
            if exe_or_args[0] == "start":
                subprocess.Popen(exe_or_args, shell=True)
            else:
                os.startfile(exe_or_args[0])
            return {"opened": name}
        # Fallback: ask Windows to resolve the app by its name.
        try:
            os.startfile(name)
            return {"opened": name}
        except Exception as exc:
            return {"error": f"Could not open application '{name}': {exc}"}

    def open_url(self, url):
        url = (url or "").strip()
        if not url:
            return {"error": "No URL given."}
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        webbrowser.open(url)
        return {"opened_url": url}

    # ------------------------------------------------------------- run command
    def run_command(self, command):
        command = (command or "").strip()
        if not command:
            return {"error": "Empty command."}
        if config.pattern_matches(config.DENY_PATTERNS, command):
            self._log(command, "DENIED")
            return {"error": "Command denied by JARVIS safety policy."}
        if config.pattern_matches(config.CONFIRM_PATTERNS, command):
            print(f"\n[SAFETY] This command needs confirmation:\n    {command}")
            ans = input("    Run it? [y/N]: ").strip().lower()
            if ans not in ("y", "yes"):
                self._log(command, "CANCELLED")
                return {"cancelled": "Command was cancelled by the user."}
        return self._exec(command)

    def execute_managed(self, command, confirmed=False):
        """Voice/agent-safe command runner.

        Returns a dict that the LLM can act on:
          * DENY  -> refused outright
          * needs_confirmation -> ask the user; re-call with confirmed=True
          * otherwise -> {exit_code, stdout, stderr}
        """
        command = (command or "").strip()
        if not command:
            return {"error": "Empty command."}
        if config.pattern_matches(config.DENY_PATTERNS, command):
            self._log(command, "DENIED")
            return {"error": "Command denied by JARVIS safety policy.",
                    "denied": True}
        if config.pattern_matches(config.CONFIRM_PATTERNS, command):
            if not confirmed:
                self._log(command, "PENDING_CONFIRM")
                return {"needs_confirmation": True,
                        "message": "This action is sensitive. Ask the user to "
                                   "confirm out loud, then re-run with "
                                   "confirmed=True."}
        return self._exec(command)

    def _exec(self, command):
        try:
            proc = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=60
            )
            out = (proc.stdout or "")[:2000]
            err = (proc.stderr or "")[:2000]
            status = "OK" if proc.returncode == 0 else "ERROR"
            self._log(command, status, out[:500])
            return {"exit_code": proc.returncode, "stdout": out, "stderr": err}
        except subprocess.TimeoutExpired:
            self._log(command, "TIMEOUT")
            return {"error": "Command timed out after 60 seconds."}
        except Exception as exc:
            self._log(command, "ERROR")
            return {"error": str(exc)}

    def _log(self, command, status, detail=""):
        if self.mongo is not None:
            try:
                self.mongo.log_command(command, status, detail)
            except Exception:
                pass