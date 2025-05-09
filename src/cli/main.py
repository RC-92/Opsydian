#!/usr/bin/env python3

import os
import sys
import yaml
import logging
import requests
import datetime

DEBUG = "-d" in sys.argv

logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# Updated paths
BASE_DIR = "/opt/opsydian"
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"

SYSTEM_PROMPT_PATH = os.path.join(BASE_DIR, "src/llm/systemprompt.txt")
HOSTS_DIR = os.path.join(BASE_DIR, "data/hosts/")
JOBS_DIR = os.path.join(BASE_DIR, "jobs/tasks/")

def load_hosts_from_disk():
    hosts = []
    for file in os.listdir(HOSTS_DIR):
        if file.endswith(".yaml"):
            with open(os.path.join(HOSTS_DIR, file)) as f:
                try:
                    data = yaml.safe_load(f)
                    hosts.append({
                        "hostname": data.get("hostname"),
                        "environment": data.get("environment"),
                        "grouping": data.get("grouping")
                    })
                except Exception as e:
                    logging.warning(f"Invalid YAML in {file}: {e}")
    return hosts

def parse_prompt_sections():
    with open(SYSTEM_PROMPT_PATH, "r") as f:
        content = f.read()

    if "## INVENTORY" not in content:
        base = content.strip()
        inventory = []
    else:
        base, inventory_block = content.split("## INVENTORY", 1)
        try:
            inventory_data = yaml.safe_load(inventory_block)
            inventory = inventory_data.get("known_hosts") or []
        except Exception as e:
            logging.warning(f"Failed to parse inventory block: {e}")
            inventory = []

    return base.strip(), inventory

def update_inventory_prompt(base_prompt, current_inventory):
    inventory_block = yaml.dump({"known_hosts": current_inventory}, default_flow_style=False)
    new_prompt = f"{base_prompt}\n\n## INVENTORY\n{inventory_block}"
    with open(SYSTEM_PROMPT_PATH, "w") as f:
        f.write(new_prompt)
    return new_prompt

def refresh_and_load_system_prompt():
    base_prompt, existing_inventory = parse_prompt_sections()
    disk_inventory = load_hosts_from_disk()

    known_hostnames = {h['hostname'] for h in existing_inventory}
    new_hosts = [h for h in disk_inventory if h["hostname"] not in known_hostnames]

    if new_hosts:
        logging.info(f"Found {len(new_hosts)} new hosts, updating system prompt.")
        updated_inventory = existing_inventory + new_hosts
        return update_inventory_prompt(base_prompt, updated_inventory)
    else:
        logging.debug("No new hosts found.")
        return update_inventory_prompt(base_prompt, existing_inventory)

def query_ollama(prompt, system_prompt):
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "system": system_prompt,
        "stream": False
    }

    logging.debug(f"Sending payload: {payload}")
    response = requests.post(OLLAMA_URL, json=payload)
    response.raise_for_status()
    output = response.json().get("response", "").strip()
    logging.debug(f"Received response: {output}")
    return output

def create_job_yaml(response_text):
    try:
        yaml_lines = []
        for line in response_text.splitlines():
            if ":" in line and not line.strip().startswith("You "):
                yaml_lines.append(line)
            elif yaml_lines:
                break

        parsed_yaml = "\n".join(yaml_lines)

        for key in ["intent", "intended_host", "subject"]:
            broken = f"{key}: {key}:"
            if broken in parsed_yaml:
                parsed_yaml = parsed_yaml.replace(broken, f"{key}:")

        logging.debug(f"Parsed YAML block:\n{parsed_yaml}")
        job_data = yaml.safe_load(parsed_yaml)

        intent = job_data["intent"]
        target = job_data["intended_host"]
        subject = job_data.get("subject", "unknown")
        timestamp = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
        job_id = f"{intent}-{target}-{timestamp}"
        job_file = os.path.join(JOBS_DIR, f"{job_id}.yaml")

        job_payload = {
            "job_id": job_id,
            "intent": intent,
            "target": target,
            "subject": subject,
            "status": "pending",
            "created_by": "cli"
        }

        with open(job_file, "w") as f:
            yaml.dump(job_payload, f)

        print(f"✅ Job created: {job_file}")
        logging.info(f"Job YAML written to: {job_file}")
    except Exception as e:
        print("❌ Failed to parse YAML or create job.")
        logging.error(f"Job creation error: {e}")

def main():
    logging.info("Opsydian CLI Chatbot started (API mode)")
    system_prompt = refresh_and_load_system_prompt()
    print("Opsydian CLI Chatbot (type 'exit' to quit)")

    last_response = None

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "exit":
            logging.info("User exited chatbot")
            break

        if user_input.lower() == "yes" and last_response:
            print("✅ Confirmed. Proceeding with job:")
            print(last_response)
            create_job_yaml(last_response)
            last_response = None
            continue

        logging.debug(f"User input: {user_input}")
        response = query_ollama(user_input, system_prompt)
        print(f"LLM: {response}")
        last_response = response

if __name__ == "__main__":
    main()

