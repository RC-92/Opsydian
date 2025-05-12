# Overview
Opsydian is an AI-powered agent designed to automate system administrative tasks across a variety of UNIX-based systems. It leverages natural language processing to translate user instructions into actionable jobs that can be executed upon confirmation. Opsydian bridges the gap between AI-driven instruction parsing and secure, auditable task execution in production environments.

# Target Users
* System Administrators
* DevOps Engineers
* Site Reliability Engineers (SREs)
* Infrastructure Engineers managing hybrid or legacy systems (e.g., AIX, Solaris

# Core Features
* Converts natural language prompts into actionable tasks
* Multi-role support with approval flows
* Cross-platform execution (Linux, Solaris*, AIX*, Mainframe.)
* Modular architecture with shell-scripted task handlers
* SSH-based secure communication and remote execution


_Note: OS Indicated with * are still in the process of being developed, it will be available in future releases_

# High-level system diagram
![image](https://github.com/user-attachments/assets/b8e725b8-24b3-44b0-ae20-64e6e416e30a)



# Major Components:
Opsydian is composed of a collection of tightly scoped components that operate together to deliver reliable automation. These components are modular and purpose-built to handle specific stages of job management. Each module is designed with simplicity, extensibility, and security in mind. Further implementation details are intentionally abstracted to protect the internal mechanics of the application.

# Flow
1. User provides a task in natural language.
2. Opsydian interprets the task and creates a structured job.
3. After user approval, the job is executed on relevant systems.
4. Task status is logged and classified for audit and tracking purposes.

# Directory Layout

```
/opt/opsydian/
├── data/
│   └── hosts/                # YAML files per host
│   └── host_keys/            # SSH keys for authentication
├── jobs/
│   ├── task/                 # Generated jobs awaiting confirmation
│   ├── .run/                 # Jobs ready for execution
│   ├── done/                 # Successfully completed
│   ├── error/                # Failed executions
│   └── retry/                # Marked for retry
├── src/
│   ├── cli/                  # Main interface (opsydianctl.py)
│   ├── llm/                  # LLM system prompt
│   ├── executor/             # Execution engine
│   ├── watchers/             # Job watchers
│   └── scheduler/            # Optional scheduling
/var/log/opsydian/
├── llm/opsydianllm.log
├── jobs/executor.log
├── jobs/watcher.log
```

# Users
**opsydian**: Full privileges, able to trigger execution of task/kjobs
**other users**: Is only able to create a task/jobs

# Roles
* Job Creator: Allowed to interact with the CLI and generate task YAMLs
* Executor: Typically a background process or daemon with rights to execute scripts on remote systems

# Pre-requisites
Opsydian has been tested and verified on the following operating systems and versions:
Ensure the following are met prior to installation of the application

## Server (Controller)
- Ubuntu 24.04 LTS
- CentOS Stream 9

## Client (Managed Hosts)
- Ubuntu 24.04 LTS
- CentOS Stream 9

# Language Model (LLM Backend)
- Ollama: Gemma 3 model

Note: Opsydian relies on passwordless SSH or pre-provisioned credentials to execute tasks on client systems. Ensure host configurations are appropriately secured and consistent.


# Installation: 
## 1. Clone the Repo
``git clone https://github.com/RC-92/Opsydian.git /opt/opsydian``

## 2. As user with SUDO rights, execute install.sh
``./install.sh``

# CLI
## Non Opsydian Admin User
### 1. List all pulled Ollama models
`` opsydian list models``

![image](https://github.com/user-attachments/assets/0e9a472a-618c-4d78-8a90-8abbc710b07b)

### 2. Check status of Opsydian:
``opsydian status``

![image](https://github.com/user-attachments/assets/b3a9d5b2-5ff7-47d9-a750-4bb8ecbd6bf9)

### 3. Start Opsydian and create a new task

`` opsydian start``

![image](https://github.com/user-attachments/assets/63c179fe-6a29-4255-a385-fe455b25a9ba)


![image](https://github.com/user-attachments/assets/be665cc8-f8d3-4986-8f24-292c5996bfa0)


### when prompted, indicate Yes, or No. 
![image](https://github.com/user-attachments/assets/e1714e86-cda4-4a55-829d-56985537b2a5)


##  Opsydian Admin User: 

### 1. List hosts on system 

``opsydian-list-hosts``

![image](https://github.com/user-attachments/assets/63ed5251-5cd9-46f4-9db9-64dae3917591)

### 2. Add new hosts to host files

``opsydian-add-host $HOSTNAME $IP_ADDRESS_OF_NEW_HOSTS```

![image](https://github.com/user-attachments/assets/5fbdc113-242f-4720-a8bb-835e31bb0985)

### 3. Montior tasks/jobs

``opsydian-monitor``

![image](https://github.com/user-attachments/assets/e87ef37a-e961-4137-9340-b18ff51c8ba4)

### 4. Run all task/jobs

``opsydian run task all``

![image](https://github.com/user-attachments/assets/b653a8a8-88a5-4bb2-9083-0c41c767703c)

### 5. Run Specific tasks:

``opsydian run task $TASKID``


### 6. List pending tasks

``opsydian list tasks``

![image](https://github.com/user-attachments/assets/581a4ee8-8c38-45f7-bbc6-785646b46ca4)



If you wish to get in touch with me, please feel free to contact me at: 

Email: rc140592@pm.me


All pull request are welcome. 
I am also open to all and any suggestions
