#!/usr/bin/env python3

import os
import time
import yaml
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Updated base paths
BASE_DIR = "/opt/opsydian"
TASK_DIR = os.path.join(BASE_DIR, "jobs/tasks/")
LOG_FILE = os.path.join(BASE_DIR, "logs/job_watcher.log")

PENDING_JOBS = []

def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}\n")

class JobHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path.endswith(".yaml") and not event.is_directory:
            job_file = os.path.basename(event.src_path)
            PENDING_JOBS.append(job_file)
            msg = f"📥 New job detected: {job_file}"
            print(msg)
            log(msg)
            notify_user()

def notify_user():
    if not PENDING_JOBS:
        return

    print("\nThe following jobs are pending to be executed:")
    log("Pending jobs:")
    for idx, job in enumerate(PENDING_JOBS, start=1):
        line = f"{idx}. {job}"
        print(line)
        log(line)

    log("Waiting for external execution confirmation (via opsydianctl or supervisor).")

def start_watcher():
    if not os.path.exists(LOG_FILE):
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        open(LOG_FILE, "w").close()

    print(f"📡 Watching for jobs in: {TASK_DIR}")
    log(f"Watcher started on: {TASK_DIR}")

    event_handler = JobHandler()
    observer = Observer()
    observer.schedule(event_handler, path=TASK_DIR, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_watcher()

