#!/usr/bin/env python3

import os
import time
import yaml
import subprocess
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

RUN_DIR = "/opt/opsydian/jobs/.run/"
HOSTS_DIR = "/opt/opsydian/data/hosts/"
DONE_DIR = "/opt/opsydian/jobs/done/"
ERROR_DIR = "/opt/opsydian/jobs/error/"
LOG_FILE = "/opt/opsydian/logs/exec.log"
SCRIPT_BASE = "/opt/opsydian/bin"
KEY_FILE = "/opt/opsydian/data/hosts/.hostkeys/opsydian_ed25519"


def log(msg):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"{timestamp} {msg}\n")
    print(f"{timestamp} {msg}")


def load_hosts():
    hosts = []
    for file in os.listdir(HOSTS_DIR):
        if file.endswith(".yaml"):
            path = os.path.join(HOSTS_DIR, file)
            with open(path) as f:
                try:
                    data = yaml.safe_load(f)
                    hosts.append({
                        "hostname": data.get("hostname"),
                        "ip": data.get("ip"),
                        "os": data.get("os"),
                        "environment": data.get("environment"),
                        "grouping": data.get("grouping"),
                        "username": data.get("username"),
                    })
                except Exception as e:
                    log(f"⚠️ Failed to parse {file}: {e}")
    return hosts


def resolve_targets(job_target, all_hosts):
    job_target = job_target.lower()
    if job_target == "all":
        return all_hosts
    elif job_target in ["production", "staging"]:
        return [h for h in all_hosts if h.get("environment", "").lower() == job_target]
    elif job_target in ["frontend", "backend", "database"]:
        return [h for h in all_hosts if h.get("grouping", "").lower() == job_target]
    else:
        return [h for h in all_hosts if h.get("hostname", "") == job_target]


def is_host_online(ip):
    try:
        result = subprocess.run(["ping", "-c", "1", "-W", "2", ip],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        return result.returncode == 0
    except Exception:
        return False


def run_host_script(intent, osname, ip, username, subject):
    os_id = osname.lower().split(" ")[0]
    if os_id.startswith("rhel"):
        os_id = "rhel"
    elif os_id.startswith("ubuntu"):
        os_id = "ubuntu"
    elif os_id.startswith("solaris"):
        os_id = "solaris"

    script = f"{SCRIPT_BASE}/{intent.lower()}-{os_id}.sh"

    if not os.path.exists(script):
        log(f"❌ Script not found: {script}")
        return False

    try:
        ssh_command = [
            "ssh", "-i", KEY_FILE,
            "-o", "StrictHostKeyChecking=no",
            f"{username}@{ip}",
            f"bash -s"
        ]
        with open(script, 'rb') as script_file:
            result = subprocess.run(
                ssh_command,
                input=script_file.read(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=60
            )

        log(f"📥 STDOUT from {ip}:\n{result.stdout.decode().strip()}")
        log(f"📥 STDERR from {ip}:\n{result.stderr.decode().strip()}")

        if result.returncode == 0:
            log(f"✅ Success on {ip} using {script}: {subject}")
            return True
        else:
            log(f"❌ Failed on {ip} using {script}")
            return False
    except Exception as e:
        log(f"❌ Exception on {ip} using {script}: {e}")
        return False


def handle_job(job_path):
    jobfile = os.path.basename(job_path)
    log(f"🚀 Executing job: {jobfile}")

    try:
        with open(job_path) as f:
            job = yaml.safe_load(f)
        intent = job.get("intent")
        subject = job.get("subject")
        target = job.get("target")

        if not intent or not subject or not target:
            raise ValueError("Missing intent/subject/target in job")

        hosts = load_hosts()
        targets = resolve_targets(target, hosts)
        if not targets:
            raise ValueError("No matching hosts found")

        all_success = True
        for host in targets:
            if not is_host_online(host["ip"]):
                log(f"⚠️ Host {host['ip']} unreachable. Skipping.")
                all_success = False
                continue

            success = run_host_script(
                intent, host["os"], host["ip"],
                host["username"], subject
            )
            all_success = all_success and success

        dest = DONE_DIR if all_success else ERROR_DIR
        shutil.move(job_path, os.path.join(dest, jobfile))
        log(f"📦 Job moved to: {dest}")

    except Exception as e:
        log(f"❌ Job processing failed: {e}")
        shutil.move(job_path, os.path.join(ERROR_DIR, jobfile))


class RunJobHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path.endswith(".yaml") and not event.is_directory:
            time.sleep(1)
            handle_job(event.src_path)


def start_executor():
    log("🔁 Opsydian Executor started.")
    observer = Observer()
    observer.schedule(RunJobHandler(), path=RUN_DIR, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    start_executor()

