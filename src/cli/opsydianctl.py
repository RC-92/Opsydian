#!/usr/bin/env python3


import os
import sys
import yaml
import time

TASK_DIR = "/opt/opsydian/jobs/tasks/"
RUN_DIR = "/opt/opsydian/jobs/.run/"
SEEN_FILE = "/opt/opsydian/.opsydian_seen_jobs"

def log(msg):
    print(msg)

def save_seen(jobs):
    try:
        with open(SEEN_FILE, "w") as f:
            for j in jobs:
                f.write(j + "\n")
    except Exception as e:
        log(f"⚠️ Failed to write seen file: {e}")

def load_seen():
    if not os.path.exists(SEEN_FILE):
        return set()
    try:
        with open(SEEN_FILE, "r") as f:
            return set(line.strip() for line in f)
    except Exception as e:
        log(f"⚠️ Failed to read seen file: {e}")
        return set()

def list_jobs(show_new=False):
    jobs = sorted(f for f in os.listdir(TASK_DIR) if f.endswith(".yaml"))
    seen = load_seen()
    if not jobs:
        print("✅ No pending jobs.")
        return []

    print("\n📋 Pending Jobs:")
    for idx, job in enumerate(jobs, 1):
        tag = "  " + ("🆕 New!" if show_new and job not in seen else "")
        print(f"{idx}. {job}{tag}")

    return jobs

def load_job(jobfile):
    path = os.path.join(TASK_DIR, jobfile)
    with open(path) as f:
        return yaml.safe_load(f)

def run_job(jobfile):
    src = os.path.join(TASK_DIR, jobfile)
    dest = os.path.join(RUN_DIR, jobfile)

    if not os.path.exists(src):
        print(f"❌ Job not found in tasks/: {jobfile}")
        return

    try:
        os.rename(src, dest)
        print(f"All jobs scheduled to be excecuted at the next available window")
    except Exception as e:
        print(f"❌ Failed to move job: {e}")

def delete_job(jobfile):
    try:
        os.remove(os.path.join(TASK_DIR, jobfile))
        print(f"🗑️ Deleted: {jobfile}")
    except Exception as e:
        print(f"❌ Failed to delete job: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  opsydianctl.py status")
        print("  opsydianctl.py list")
        print("  opsydianctl.py run <jobid|all>")
        print("  opsydianctl.py delete <jobid|all>")
        sys.exit(1)

    cmd = sys.argv[1].lower()

    if cmd == "list":
        list_jobs()

    elif cmd == "status":
        jobs = list_jobs(show_new=True)
        save_seen(jobs)

    elif cmd == "run":
        if len(sys.argv) < 3:
            print("⚠️ Specify job name or 'all'")
            return
        arg = sys.argv[2]
        if arg == "all":
            for job in list_jobs():
                run_job(job)
        else:
            run_job(arg)

    elif cmd == "delete":
        if len(sys.argv) < 3:
            print("⚠️ Specify job name or 'all'")
            return
        arg = sys.argv[2]
        if arg == "all":
            for job in list_jobs():
                delete_job(job)
        else:
            delete_job(arg)

    else:
        print("❌ Unknown command.")

if __name__ == "__main__":
    main()

