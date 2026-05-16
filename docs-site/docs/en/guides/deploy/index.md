---
title: Deploy & Ops Guide
description: A complete guide to deploying repositories using the PEtFiSh deploy skill pack.
---

# Deploy & Ops Guide

The **deploy** pack provides a complete suite of skills for reading a repository, deploying it to a target host, verifying its functionality, and maintaining it over time. 

Rather than assuming a one-size-fits-all deployment strategy, this pack acts as an intelligent DevOps engineer. It analyzes your codebase to understand *how* it should run, checks your infrastructure to ensure it *can* run, forms a deterministic plan, executes the deployment with safety gates, and strictly verifies the result before calling the job done.

This pack bridges the gap between local development and production reality. Whether you are spinning up a quick Docker Compose stack on your laptop, or performing a zero-downtime Blue/Green deployment to a remote Ubuntu server, the deploy pack ensures consistency, safety, and operational rigor.

```bash
# Install the deploy pack (macOS / Linux)
curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh | bash -s -- --pack deploy

# Install the deploy pack (Windows PowerShell)
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack deploy
```

---

## Overview

The deploy pack is designed for tasks ranging from "spin this up locally" to "deploy this GitHub repository to my staging server." It excels at intelligent discovery, safe execution, real smoke testing, and day-2 operations.

### What's in the Pack

The deploy pack is modular. While the orchestrator ties everything together, each skill is a standalone tool capable of performing deep operations in its specific domain.

| Skill | Purpose | Role in Pipeline |
|---|---|---|
| **`repo-service-lifecycle`** | The end-to-end orchestrator that chains all other skills together. It understands the full lifecycle and passes context (like the discovered tech stack and target host) from one step to the next seamlessly. | **Orchestrator** |
| **`repo-runtime-discovery`** | Scans the codebase, detects the tech stack, identifies build steps, locates database requirements, and maps out required environment variables. It builds the foundational "Deployment Brief." | **Step 1: Discover** |
| **`target-host-readiness`** | Checks the target server's OS architecture, available CPU/RAM, disk space, port conflicts, and required runtimes (like Docker, Node, Python). It acts as a safety gate. | **Step 2: Check** |
| **`deployment-executor`** | Performs the actual rollout. It safely applies the changes, injects secrets, manages systemd or docker-compose processes, and creates strict rollback points before any destructive action. | **Step 3: Execute** |
| **`deployment-verifier`** | Proves the service is functional. It performs HTTP health checks, core API smoke tests, log inspection for startup errors, and database connection verification. | **Step 4: Verify** |
| **`service-operations`** | Acts as your day-2 SRE. It handles routine maintenance, log rotation, resource profiling, dependency upgrades, and SSL/TLS certificate renewals without downtime. | **Step 5: Maintain** |
| **`incident-rollback`** | Triages failures, stabilizes broken services, and executes hard rollbacks to the last known safe state when critical SEV-1 outages occur. | **Failure Handling** |

### When to Use This Pack vs. When NOT to Use

**Use this pack when:**

- **Deploying to VMs or Bare Metal:** You have a traditional repository (Node, Python, Go, Java, Rust) and need it running on a Virtual Private Server (AWS EC2, DigitalOcean Droplet, local Proxmox VM) or local Docker environment.
- **Provisioning from Scratch:** You are setting up a new staging or production server and need an intelligent agent to ensure all prerequisites (like specific Node versions, Docker daemon, or Nginx) are met before attempting to copy code.
- **Requiring Verifiable Deployments:** You need a structured deployment process that guarantees the service is actually answering requests (via HTTP smoke tests and log tailing) before calling the job "done."
- **Managing Production Incidents:** You are responding to a production outage (e.g., a 502 Bad Gateway) and need to safely triage, stabilize, or roll back the deployment to the last known working Git commit.
- **Performing Routine Day-2 Maintenance:** You want to maintain a service over time. This includes checking application logs for slow queries, preparing for dependency upgrades, renewing SSL certificates, and managing disk space.

**Do NOT use this pack when:**

- **Using Fully Managed PaaS:** You are relying entirely on a managed Platform-as-a-Service (PaaS) like Vercel, Heroku, Render, or Netlify. These platforms already handle runtime discovery, build execution, and traffic shifting internally.
- **Developing Features:** You are looking to write or debug application code. This pack strictly handles DevOps, infrastructure, and operations. If you need to write features, use the default OpenCode development skills.
- **Bypassing Safety Checks:** You want to blindly run a destructive script without verifying success. This pack mandates safety gates, rollback points, and verification steps. If you want to circumvent these, use the basic `bash` tool directly.

---

## The Deployment Chain

The pack operates through a strict, deterministic pipeline designed to eliminate the guesswork from deployments. If you use the `repo-service-lifecycle` orchestrator, it automatically routes context and state through these steps sequentially. If you manually request a specific action (e.g., "Just verify this endpoint"), the agent bypasses the orchestrator and loads the corresponding individual skill.

```text
User Request ("Deploy this to production")
    │
    ▼
[ repo-service-lifecycle ] (Central Orchestrator)
    │
    ├─ Step 1: repo-runtime-discovery (Analyze the codebase)
    │          ↳ Output: Deployment Brief (Tech stack, Env vars, Build steps)
    │
    ├─ Step 2: target-host-readiness  (Check the target server)
    │          ↳ Output: Readiness Report (CPU, Port conflicts, Runtimes)
    │          ↳ Blocks if prerequisites are missing.
    │
    ├─ Step 3: deployment-executor    (Run the actual deployment)
    │          ↳ Output: Execution Log & Rollback Point
    │          ↳ Backs up previous state, injects secrets, restarts processes.
    │
    ├─ Step 4: deployment-verifier    (Prove the service is running)
    │          ↳ Output: Verification Report (Smoke tests, Log checks)
    │          ↳ Ensures HTTP 200 OK and database connectivity.
    │
    └─ Step 5: service-operations     (Record state & ongoing maintenance)
               ↳ Output: Ops Baseline (Version tracking, Resource profiling)
               │
          (If Step 3 or 4 fails critically)
               │
               └─ incident-rollback   (Revert & stabilize)
                  ↳ Output: Incident Record
                  ↳ Restores the backup created in Step 3.
```

### Context Passing
Each skill in the chain passes its output to the next. For example, `target-host-readiness` doesn't just check generic metrics; it specifically checks for the exact Node.js version and database ports identified by `repo-runtime-discovery` in the previous step. This tight coupling ensures the deployment is hyper-specific to your exact repository.

---

## Lifecycle Orchestrator

The `repo-service-lifecycle` skill is the "just tell it to do everything" entry point. When you provide a broad deployment or operational request, the agent loads this orchestrator to manage the entire pipeline from discovery to verification.

### How It Chains Steps

The orchestrator does not perform the deployment itself. Instead, it acts as a manager that delegates to the specialized skills in order:

1. It triggers `repo-runtime-discovery` to build a deployment brief.
2. It passes that brief to `target-host-readiness` to validate the environment.
3. It hands the verified plan to `deployment-executor`.
4. It commands `deployment-verifier` to prove the service is running.
5. It uses `service-operations` or `incident-rollback` depending on the verification outcome.

### Example Prompts

=== "Deploy and Verify"

    ```text
    Please deploy this repository to my local machine and verify that it's working.
    ```

=== "Remote Provision and Deploy"

    ```text
    Help me deploy this GitHub repo to ubuntu@10.0.0.5. Make sure the server has what it needs first, then get it online and verified.
    ```

=== "Ongoing Maintenance"

    ```text
    Take ownership of the service running on port 8080. Verify its health, check the recent logs, and establish a baseline for continuous operations.
    ```

---

## Quick Start

### Example 1: Local Docker Deployment

If you just want to get a project running locally using its existing Docker configuration for testing or development:

=== "Prompt"

    ```text
    Deploy the current repository to my local Docker environment and verify it works.
    ```

=== "Expected Behavior"

    1. The agent loads `repo-service-lifecycle`.
    2. It scans your repository to find the `Dockerfile` or `docker-compose.yml`.
    3. It checks if Docker is running locally and ensures port 80/443 (or the target ports) are not occupied by your host OS.
    4. It builds the container image (`docker build -t myapp .`) and starts the container (`docker run -d`).
    5. It aggressively curls the local endpoint (`http://localhost:8080/health`) until the application stops returning `502` and returns `200 OK`.
    6. It provides a structured summary of the deployment, the mapped ports, and the command needed to tail the logs (e.g., `docker logs -f myapp`).

### Example 4: Post-Deploy Verification

Sometimes you deploy code manually, but want the agent to handle the rigorous verification phase.

=== "Prompt"

    ```text
    I just deployed the new backend to production. Run a deep verification on https://api.example.com to ensure everything is stable.
    ```

=== "Expected Behavior"

    1. The agent loads `deployment-verifier` directly (bypassing discovery and execution).
    2. It performs an HTTP check on the provided URL, verifying the SSL certificate validity.
    3. It runs a few basic API calls (like `GET /api/v1/status`) to check the JSON response structure.
    4. It connects to the host via SSH (if credentials are provided in context) to check the application logs for silent errors.
    5. It compiles a "Verification Report" confirming the system is fully operational.

### Example 2: Remote SSH Deployment

When deploying to a remote server, you must provide the target host and user. The agent uses your local machine's existing SSH configuration (e.g., `~/.ssh/config` or loaded identities in `ssh-agent`) to securely connect.

=== "Prompt"

    ```text
    Deploy this repository to staging-user@192.168.1.50. You can use my local SSH keys. We need it running on port 3000.
    ```

=== "Expected Behavior"

    1. The agent connects to `192.168.1.50` via SSH.
    2. It verifies that Node.js or Docker is installed on the remote host.
    3. It checks if port `3000` is available.
    4. It copies the code via `rsync` or clones via `git`.
    5. It installs dependencies, builds the project, and starts the service.
    6. It runs a remote verification script to ensure the port is responding.

### Example 3: Blue-Green / Zero-Downtime Deployment

For production systems, you often cannot afford even a few seconds of downtime while a process restarts. The agent can orchestrate zero-downtime rollouts.

=== "Prompt"

    ```text
    Execute a zero-downtime deployment for this Python API. Start the new version on a temporary port, wait for it to be healthy, and then hot-swap the Nginx upstream to point to the new port before stopping the old version.
    ```

=== "Expected Behavior"

    1. The agent reads the current Nginx config to find the active port (e.g., `8001`).
    2. It deploys the new codebase and starts the new process on a secondary port (e.g., `8002`).
    3. It aggressively polls `localhost:8002/health` until it returns 200 OK.
    4. Once healthy, it modifies `/etc/nginx/sites-available/api` to point to `:8002`.
    5. It executes `nginx -t` to validate syntax, then `systemctl reload nginx` for a seamless traffic shift.
    6. It safely terminates the old process on `8001`.

??? example "What Just Happened? (The Chain Explained)"
    When you issued the command, the agent didn't just run `docker compose up`. It followed the strict discipline required by the pack:
    
    - It ran **Discovery** to ensure it knew *how* the app builds.
    - It ran **Readiness** to ensure the remote host had the right architecture and wasn't out of disk space.
    - It ran **Executor** to apply the changes, making sure to log the git commit hash it was deploying.
    - It ran **Verifier** to confirm the application was actually answering HTTP requests, rather than just checking if the process ID existed.

!!! tip "Be specific about the target"
    The agent cannot magically know your server credentials. If deploying remotely, provide the SSH host and ensure your environment has the necessary SSH keys configured. 
    Example: `Deploy this to user@10.0.0.5`

---

## Step 1: Discover Your Repo

Before touching any servers, the agent must understand what it is deploying. This is handled by **`repo-runtime-discovery`**.

It scans the local or remote repository to identify the tech stack, entry points, configuration needs, database dependencies, and health endpoints. It will flag if required environment variables are missing from the project.

### What Gets Detected

When `repo-runtime-discovery` runs, it looks for specific files and patterns to determine how the application should be built and executed. Here is exactly what the agent looks for during the discovery phase:

- **`Dockerfile` / `.dockerignore`**: Indicates the project is containerized. The agent will inspect the base image, exposed ports, and the entrypoint command. It will also look for multi-stage builds to optimize the final image size.
- **`docker-compose.yml` / `compose.yaml`**: Suggests a multi-container stack. The agent parses this to understand service dependencies (like needing Redis or PostgreSQL), named volumes for persistence, and custom network bridging.
- **`package.json` / `yarn.lock` / `pnpm-lock.yaml`**: Identifies a Node.js project. The agent reads the `scripts` block to find the `build`, `start`, and `test` commands. It checks for frameworks like Next.js, NestJS, or Express to determine the runtime requirements.
- **`requirements.txt` / `pyproject.toml` / `Pipfile`**: Identifies a Python application. The agent checks for frameworks like Django, Flask, or FastAPI to determine the best WSGI/ASGI server (e.g., gunicorn, uvicorn).
- **`go.mod` / `go.sum`**: Identifies a Go project. The agent looks for the `main` package location for compilation, and checks if CGO is required.
- **`build.gradle` / `pom.xml`**: Identifies a Java/Kotlin project. The agent looks for Spring Boot or Quarkus signatures to define the Maven/Gradle build commands and the final `.jar` artifact location.
- **`Makefile`**: A universal task runner. If present, the agent will look for standard targets like `make build`, `make run`, and `make clean`.
- **Systemd Units (`*.service`)**: If `.service` files are committed to the repository, the agent assumes you want to deploy directly to the host OS using Systemd, parsing the `ExecStart` and `EnvironmentFile` directives.
- **Kubernetes Manifests (`k8s/`, `helm/`, `*.yaml`)**: Indicates a Kubernetes deployment strategy. The agent will read Deployments, Services, and Ingresses to map the cluster topology.
- **`Procfile`**: Often used by Heroku or PM2 to define process types (e.g., `web`, `worker`).

!!! info "Custom Configuration Files"
    The discovery phase also scans for common configuration files like `.env.example`, `config.yml`, `nginx.conf`, and `prometheus.yml`. It cross-references these with the application code to identify required environment variables and alert you to missing secrets before the deployment even begins.

### Handling Specific Frameworks

The discovery skill applies tailored logic for modern frameworks to ensure optimal deployments:

- **Next.js / Nuxt.js**: Detects if the app is configured for static export (`next export`) or requires a Node.js server. It ensures `npm run build` is called before deployment.
- **Django / Flask**: Looks for `wsgi.py` or `asgi.py` and recommends Gunicorn or Uvicorn over the built-in development server. It checks for `manage.py migrate` requirements.
- **Spring Boot**: Identifies the `.jar` location and ensures the `java -jar` command includes standard production flags (like memory limits `-Xmx`).
- **React / Vue / Vite**: If a purely frontend project is detected, it recommends a static serving strategy (like deploying via Nginx) rather than running a Node.js process.

### Example Prompts

=== "Analyze Local"

    ```text
    Analyze this repository and tell me what we need to deploy it.
    ```

=== "Analyze Remote GitHub"

    ```text
    Look at the repository https://github.com/example/api-service. What is required to run it in production?
    ```

=== "Find Config Gaps"

    ```text
    Review our current codebase. What environment variables or configuration files are missing before we can deploy this?
    ```

??? example "Sample Output"

    ```markdown
    ## Deployment Brief: `api-service`
    
    ### Tech Stack
    - **Language:** TypeScript / Node.js (v18+)
    - **Framework:** Express
    - **Database:** PostgreSQL
    
    ### Entry Points
    - **Build:** `npm run build` (compiles to `./dist`)
    - **Run:** `npm start` (executes `node dist/index.js`)
    - **Dev:** `npm run dev`
    
    ### Dependencies & Configuration
    - **Database:** Requires a PostgreSQL instance.
    - **Environment Variables Required:**
      - `DATABASE_URL` (Missing)
      - `JWT_SECRET` (Missing)
      - `PORT` (Defaults to 3000)
    
    ### Health Endpoints
    - `/api/health` returns `{"status": "ok"}`
    
    ### Proposed Deployment Strategy
    The repository contains a `docker-compose.yml` that defines both the API and a PostgreSQL database. The recommended approach is to deploy using Docker Compose.
    ```

!!! tip "Feed it documentation"
    If your repository has a `DEPLOY.md` or architecture diagram, point the agent to it during discovery. It will incorporate your custom instructions into the Deployment Brief.

---

## Step 2: Check Host Readiness

Once the deployment strategy is clear, the agent checks if the target server is actually capable of running the code using **`target-host-readiness`**.

It verifies OS architecture, CPU/RAM/Disk space, port conflicts, required runtimes (Docker, Node, Python, Systemd), and write permissions.

### What Gets Checked

When `target-host-readiness` runs, it behaves like an experienced sysadmin ensuring the server won't buckle under the deployment. Here are the precise checks performed:

- **System Resources**:
    - **CPU & Load Average**: Checks `uptime` and `top`. If the server is already sitting at 99% CPU utilization, the agent warns you that adding a new process might crash the host.
    - **Memory (RAM)**: Runs `free -m`. It calculates if the available memory can comfortably support the new application, particularly Java or Node.js apps which have high baseline overheads.
    - **Disk Space**: Runs `df -h`. A deployment that requires extracting a 2GB Docker image will fail if only 1GB is free. The agent blocks the deployment to prevent corrupting the server's root filesystem.
- **Port Availability**: Uses `ss -tulpn` or `lsof -i` to verify the target ports (e.g., `80`, `443`, `3000`) are actually free. It identifies conflicting processes (like an old Nginx process hanging onto port 80).
- **Runtimes & Dependencies**:
    - **Docker**: Verifies `docker version` and `docker compose version`. Checks if the current user has permission to connect to the Docker daemon (`docker ps`).
    - **Language Runtimes**: Runs `node -v`, `python3 --version`, or `go version`. It strictly compares these against the versions required in the deployment brief.
    - **Service Managers**: Checks if `systemd` or `pm2` are installed and functioning.
- **Permissions**: Verifies that the deployment user has write access to the target deployment directory (e.g., `/opt/myapp`) and permission to restart services or reload proxies via `sudo`.

!!! warning "Strict Mode Readiness"
    The deploy pack operates in a fail-safe mode. If a critical prerequisite (like a missing runtime or port conflict) is detected, the agent will **block** the deployment. It will not attempt to randomly guess how to install dependencies unless explicitly instructed to do so.

### Example Prompts

=== "Check Remote Requirements"

    ```text
    Check if 192.168.1.100 is ready for our Node.js deployment. We need port 3000 and Node v18.
    ```

=== "Pre-flight Docker Check"

    ```text
    Verify the local machine can run our docker-compose stack. Make sure ports 80 and 443 are free.
    ```

=== "Capacity Planning"

    ```text
    Assess the production server at user@prod.internal. Do we have enough disk space and memory to deploy a new Java Spring Boot container?
    ```

??? example "Sample Output"

    ```markdown
    ## Host Readiness Report: `192.168.1.100`
    
    ### System Resources
    - **OS:** Ubuntu 22.04 LTS (x86_64)
    - **CPU:** 4 Cores (Load average: 0.45) - **PASS**
    - **Memory:** 8GB total, 4.2GB available - **PASS**
    - **Disk Space:** 50GB total, 4.1GB available - **WARNING** (Low disk space)
    
    ### Runtimes & Dependencies
    - **Node.js:** v14.19.0 installed - **BLOCKER** (v18+ required by codebase)
    - **NPM:** v6.14.16 installed - **BLOCKER**
    - **Docker:** v24.0.5 installed - **PASS**
    
    ### Network & Ports
    - **Port 3000:** IN USE by PID 1452 (node) - **BLOCKER**
    
    ### Conclusion
    The host is **NOT READY** for deployment.
    
    **Required Actions Before Execution:**
    1. Upgrade Node.js to v18.
    2. Free up or reassign port 3000 (currently used by another Node process).
    3. Monitor disk space.
    
    Would you like me to attempt fixing these blockers?
    ```

!!! warning "Do not ignore Blockers"
    If the agent flags a Blocker, do not force it to proceed. Have the agent resolve the blocker (e.g., "Kill the process on port 3000 and install Node 18") before moving to the execution phase.

---

## Step 3: Execute Deployment

With a plan in hand and a ready host, **`deployment-executor`** performs the actual rollout.

It follows a strict `Plan → Validate → Execute` loop. It records the current state, creates a rollback point, pushes the code, injects configurations, and starts the service.

### Rollback Points and State Recording

Before executing any destructive command, the agent creates a rollback point. This usually involves:

- Copying the existing binary or release directory to a backup folder (e.g., `release_backup_20260515/`).
- Exporting the current database schema state if migrations are planned.
- Saving the exact Git commit hash of the *previous* deployment.
- Logging the exact commands used so they can be reversed.

### Deployment Strategies

The agent automatically selects the best deployment strategy based on the discovery phase, but you can explicitly request a specific approach. Each strategy comes with its own set of validation checks and rollback procedures.

=== "Docker Compose"
    The preferred method for multi-container stacks.
    
    ```text
    Execute the deployment using docker-compose. Rebuild the images and recreate the containers without dropping the database volume.
    ```
    
    ```markdown
    **Agent Action:**
    1. Validates the `docker-compose.yml` syntax using `docker compose config`.
    2. Runs `docker compose pull` to fetch any updated base images from registries.
    3. Runs `docker compose build --pull` to compile the application image.
    4. Runs `docker compose up -d --remove-orphans` to start the new containers.
    5. Verifies container health states using `docker compose ps`.
    
    *Rollback Strategy:* The agent tags the previous image and can instantly revert by running `docker compose up -d` with the old tag.
    ```

=== "Systemd Service"
    The best approach for bare-metal binaries (like Go, Rust) or direct host deployments without container overhead.
    
    ```text
    Deploy the compiled binary to /opt/myapp and set it up as a systemd service named myapp.service. Make sure it runs as a non-root user.
    ```
    
    ```markdown
    **Agent Action:**
    1. Creates a dedicated service user: `useradd -r -s /bin/false myapp_user`.
    2. Copies the compiled binary to `/opt/myapp/myapp` and sets ownership.
    3. Generates `/etc/systemd/system/myapp.service` with `User=myapp_user` and `Restart=always`.
    4. Runs `systemctl daemon-reload` to register the service.
    5. Runs `systemctl restart myapp` to apply changes.
    6. Runs `systemctl enable myapp` to ensure it starts on boot.
    
    *Rollback Strategy:* The agent moves the old binary to `/opt/myapp/backups/myapp_old` before copying the new one, allowing a simple file swap and restart if the new binary fails.
    ```

=== "PM2 / Process Manager"
    Common for Node.js applications running directly on the host, providing clustering and automatic restarts.
    
    ```text
    Use PM2 to deploy the Node.js app. Make sure it runs in cluster mode with 4 instances to utilize all CPU cores.
    ```
    
    ```markdown
    **Agent Action:**
    1. Verifies PM2 is installed globally (`pm2 -v`).
    2. Runs `npm ci` to cleanly install dependencies without modifying the lockfile.
    3. Runs `npm run build` to compile TypeScript or bundle assets.
    4. Executes `pm2 start ecosystem.config.js --env production -i 4` or `pm2 start dist/index.js -i 4 --name "api"`.
    5. Runs `pm2 save` to persist the process list across system reboots.
    
    *Rollback Strategy:* The agent can issue a `pm2 reload api` to perform a zero-downtime reload, or revert to a previous Git commit and run the build steps again.
    ```

=== "Manual / Custom Script"
    If your repository has a highly specific deployment script (e.g., Ansible, Capistrano, or Bash), instruct the agent to use it.
    
    ```text
    Deploy using the ./scripts/deploy-prod.sh script. Pass the `--force` flag.
    ```
    
    ```markdown
    **Agent Action:**
    1. Grants execute permissions: `chmod +x ./scripts/deploy-prod.sh`.
    2. Analyzes the script to understand its side effects before running.
    3. Executes `./scripts/deploy-prod.sh --force`.
    4. Captures `stdout` and `stderr`, tracking the exit code.
    
    *Rollback Strategy:* Depends entirely on the custom script. The agent will ask you for a rollback script (e.g., `./scripts/rollback-prod.sh`) before proceeding.
    ```

### Permissions and Authentication

The executor needs sufficient privileges to modify the host system. Depending on your deployment strategy, the agent handles permissions automatically:

- **Sudo Access**: When modifying `/etc/systemd/system/` or `/etc/nginx/`, the agent will prefix commands with `sudo`. You must ensure the connecting user has `sudo` privileges without a password prompt, or the deployment will stall.
- **Docker Group**: If deploying via Docker, the connecting user should be a member of the `docker` group to avoid needing `sudo` for every `docker` command.
- **Remote Registries**: If pulling images from private registries (like AWS ECR or GitHub Container Registry), the agent can execute the required `docker login` step, provided you pass the credentials securely in your initial prompt.
- **SSH Forwarding**: If the agent needs to clone a private Git repository directly on the remote server, it uses your local `ssh-agent` forwarding by default, eliminating the need to copy private keys to the server.

### Example Prompts

=== "Execute Docker Compose"

    ```text
    Execute the deployment to the staging server using docker-compose. Use the existing config.
    ```

=== "Zero-Downtime Rollout"

    ```text
    Deploy the latest master branch to the production VM. Use a blue-green strategy with Nginx so we don't drop traffic.
    ```

=== "Inject Secrets"

    ```text
    Deploy the worker service. Inject the secrets from the local `.env.prod` file into the target host before starting the systemd service.
    ```

??? example "Sample Output"

    ```markdown
    ## Execution Plan
    
    1. **Rollback Point:** Create a tarball of `/opt/api-service/current` to `/opt/api-service/backups/release_20260515.tar.gz`.
    2. **Transfer:** Rsync local `./dist` to remote `/opt/api-service/new`.
    3. **Config:** Write injected `DATABASE_URL` to `/opt/api-service/new/.env`.
    4. **Execute:** Stop current service, swap symlinks, restart systemd service `api-service`.
    
    *Executing...*
    
    ## Execution Result
    
    - **Status:** SUCCESS
    - **Deployed Version:** Git commit `a1b2c3d4`
    - **Rollback Point:** `/opt/api-service/backups/release_20260515.tar.gz`
    - **Commands run:** `systemctl restart api-service`
    
    The service has been started. Proceeding to verification.
    ```

!!! tip "Review the Plan"
    When using `deployment-executor`, the agent will usually output a plan before running commands. Take a moment to read it before confirming "go ahead," especially in production environments.

---

## Step 4: Verify

A deployment isn't finished just because the process didn't crash immediately. **`deployment-verifier`** proves the service is actually usable.

It performs health/readiness checks, core API smoke tests, log inspection, and dependency verification (checking if it successfully connected to Redis/DB).

### What Gets Verified

Verification is more than just checking if the process ID exists. The `deployment-verifier` skill performs multi-layered checks to ensure true service availability:

- **Process & Service State**: Checks `systemctl status`, `pm2 list`, or `docker ps` to ensure the process is running, not continually restarting, and hasn't exited with an error code.
- **Port Binding**: Runs `netstat`, `ss`, or `lsof` to confirm the application has successfully bound to the expected port (e.g., `3000`).
- **HTTP Smoke Tests**: Issues `curl` or `wget` requests to health endpoints (`/health`, `/ping`, `/api/status`). It checks for `200 OK` status codes and parses JSON responses to confirm deep health (e.g., `{"database": "connected"}`).
- **Log Inspection**: Reads the tail of the application logs (via `journalctl`, `docker logs`, or file tails). It uses pattern matching to look for fatal errors, missing modules, or unhandled exceptions that occurred during startup.
- **Dependency Handshakes**: Checks logs or runs specific commands to ensure the app successfully connected to its database (PostgreSQL, MySQL), cache (Redis, Memcached), or message broker (RabbitMQ, Kafka).
- **Reverse Proxy Routing**: If Nginx or Traefik is involved, it verifies the proxy is successfully routing external requests to the newly deployed application without returning `502 Bad Gateway`.

### Example Prompts

=== "Standard Verification"

    ```text
    Verify the deployment we just did.
    ```

=== "Custom Smoke Test"

    ```text
    Run a smoke test on the new deployment. Check the `/api/health` endpoint and verify that the `/api/users` endpoint returns a 200 OK.
    ```

=== "Log Verification"

    ```text
    Verify the service started cleanly by checking the systemd logs. Make sure there are no database connection errors.
    ```

=== "Deep Dependency Check"

    ```text
    Perform a deep verification. Ensure the API returns 200, check the last 100 lines of logs for any memory warnings, and confirm the Redis connection is established by running `redis-cli ping` inside the cache container.
    ```

??? example "Sample Output"

    ```markdown
    ## Verification Report
    
    ### Process Health
    - **Systemd Service:** `api-service.service` is **ACTIVE (running)**.
    - **PID:** 4512
    
    ### Network & API Smoke Test
    - **Port Check:** Port 3000 is listening.
    - **Health Endpoint:** `GET http://localhost:3000/api/health` returned `200 OK`.
      - Response body: `{"status":"healthy","db":"connected"}`
    
    ### Log Verification
    - Scanned last 50 lines of journalctl for `api-service`.
    - Found expected startup line: `Server listening on port 3000`.
    - **No ERROR or FATAL log entries found.**
    - Database connection verified in logs: `Connected to PostgreSQL pool`.
    
    ### Conclusion
    The deployment is **VERIFIED AND SUCCESSFUL**. Service is fully operational.
    ```

!!! warning "Do not skip verification"
    If you manually interrupt the agent after Step 3, you are flying blind. Always let the agent run the verifier to ensure a clean handoff and catch configuration errors early.

---

## Step 5: Ongoing Operations

For day-2 tasks, **`service-operations`** acts as your Site Reliability Engineer (SRE).

It handles continuous maintenance, tracking version history, inspecting health, managing certificates, and preparing for future upgrades.

### Day-2 Responsibilities

- **Log Review**: Scanning application logs for anomalies, memory leaks, or slow queries.
- **Upgrade Prep**: Verifying current versions and dependencies before attempting a patch.
- **Certificate Checks**: Ensuring SSL/TLS certificates (e.g., Let's Encrypt) are valid and renewing them if they are close to expiration.
- **Resource Profiling**: Checking if the service is creeping up in memory usage or exhausting file descriptors.

### Common Operations Recipes

Once a service is stable in production, you will routinely need to perform maintenance. Use these recipes to guide the agent through day-2 operations, ensuring high availability and system health.

??? example "Recipe: Log Rotation and Disk Cleanup"
    Servers often crash because application logs fill up the disk. You can proactively instruct the agent to clear space safely.
    
    **Prompt:**
    ```text
    The server disk space is at 85%. Please find old application logs in /var/log/myapp, compress them, delete anything older than 30 days, and run `docker system prune -a --volumes` to clear unused Docker images.
    ```
    
    **Agent Behavior:**
    The agent will locate the logs, execute the compression (`tar -czf`), delete old files safely (`find /var/log/myapp -name "*.log" -mtime +30 -delete`), and clear the Docker cache. It will then report the recovered disk space.
    
    **Sample Output:**
    ```markdown
    - Compressed 14 log files into `archive-2026-05.tar.gz`.
    - Deleted 28 files older than 30 days.
    - Cleared 3.4GB of dangling Docker images and stopped containers.
    - **Result:** Disk usage reduced from 85% to 62%.
    ```

??? example "Recipe: Non-Disruptive Dependency Update"
    When a security patch is released, you need to update dependencies without taking the system down.
    
    **Prompt:**
    ```text
    We need to update the `express` package to v4.21.0 due to a CVE. Review the package.json, perform the update locally, run the unit tests, and if they pass, draft a plan to deploy the updated container to production without downtime.
    ```
    
    **Agent Behavior:**
    The agent acts as a developer-SRE hybrid. It modifies the `package.json`, reinstalls dependencies, executes `npm test`, and formats a zero-downtime deployment plan using Docker Compose or Nginx upstream switching. It ensures the new container is healthy before terminating the old one.

??? example "Recipe: Backup Verification and Data Restoration"
    Backups are useless if they cannot be restored. Regular verification is a crucial ops task.
    
    **Prompt:**
    ```text
    Test our database backup strategy. Download the latest PostgreSQL dump from AWS S3, spin up a temporary local PostgreSQL container, restore the dump, and verify that the `users` table has data.
    ```
    
    **Agent Behavior:**
    1. Downloads the `.sql.gz` file using AWS CLI.
    2. Launches `docker run -d --name test-db -e POSTGRES_PASSWORD=test postgres:15`.
    3. Streams the dump into the container using `gunzip -c dump.sql.gz | docker exec -i test-db psql -U postgres`.
    4. Runs a `SELECT count(*) FROM users` query to prove the backup is viable.
    5. Tears down the temporary container.

??? example "Recipe: Capacity Scaling and Load Balancing"
    When traffic increases, the service needs more resources.
    
    **Prompt:**
    ```text
    Traffic is spiking. Scale the `api_worker` service in docker-compose from 2 replicas to 6 replicas. Verify that the Nginx load balancer recognizes the new instances.
    ```
    
    **Agent Behavior:**
    The agent executes `docker compose up -d --scale api_worker=6`. It then checks the Nginx or Traefik logs to confirm the new upstream targets have been registered and are receiving HTTP requests. It monitors CPU and memory usage post-scaling to ensure the host machine isn't overwhelmed.

??? example "Recipe: Renewing SSL/TLS Certificates"
    Expired certificates cause immediate downtime and browser security warnings.
    
    **Prompt:**
    ```text
    Check the Let's Encrypt certificates managed by Certbot. If any expire in the next 15 days, force a renewal and reload the Nginx service.
    ```
    
    **Agent Behavior:**
    The agent runs `certbot certificates` to parse expiration dates. If a renewal is needed, it runs `certbot renew`. Finally, it executes `systemctl reload nginx` to apply the new certificates without dropping active connections.

### Example Prompts

=== "Routine SRE Check"

    ```text
    Do a routine check on the production service. Grab the latest logs and check resource usage.
    ```

=== "Prepare for Upgrade"

    ```text
    We need to upgrade the database next week. Review the current operations state, check the exact versions running, and give me an upgrade prep report.
    ```

=== "Certificate and Config Check"

    ```text
    Check the SSL certificates for the Nginx proxy. Are they expiring soon? Also verify the configuration syntax is valid.
    ```

??? example "Sample Output"

    ```markdown
    ## Operations Inspection Report
    
    ### Service State
    - **Target:** `api-service` (Docker container)
    - **Uptime:** 14 days, 3 hours
    - **Current Version:** `v1.2.4` (Commit `f8e9d0c`)
    
    ### Resource Utilization
    - **CPU:** Normal (0.2%)
    - **Memory:** 450MB / 1GB Limit - **Stable**
    - **Disk I/O:** Normal
    
    ### Log Anomalies
    - Scanned last 24 hours of logs.
    - **Notice:** Found 14 occurrences of `WARN: API rate limit exceeded for IP`. This is normal traffic behavior but might warrant adjusting rate limits.
    - No critical crashes or restarts detected.
    
    ### Certificate Status
    - **Domain:** `api.example.com`
    - **Issuer:** Let's Encrypt
    - **Expires In:** 45 days (Renewal not yet required).
    
    ### Recommendations
    Service is healthy. No immediate operational actions required.
    ```

!!! tip "Schedule routine checks"
    Make it a habit to ask the agent to "run a routine operations check" once a week on your critical services. It will often spot creeping memory usage or disk space issues before they cause an outage.

---

## Handling Failures

If a deployment fails, or if a service crashes in production, the **`incident-rollback`** skill takes over. It emphasizes stabilization over deep debugging. 

### Severity Levels and Triage Flow

When invoked, the agent triages the issue based on severity. It uses a structured decision tree to determine if it should debug the issue in place, or execute a hard rollback immediately.

1. **Critical Outage (SEV-1):** 
    - **Symptoms:** Service is entirely unresponsive, returning 502/503/504 errors, container is in a rapid crash loop, or the host machine has run out of memory.
    - **Agent Action:** Immediate rollback to the previous stable state. The agent prioritizes restoring service over finding the root cause. Once the service is stable on the old version, the agent will download the failing logs for offline analysis.
2. **Degraded Performance (SEV-2):** 
    - **Symptoms:** Service is up but responding slowly, certain API routes are returning 500s, or the database connection pool is exhausted.
    - **Agent Action:** Attempt quick stabilization before a full rollback. The agent might restart the service, clear a bloated cache, scale up replicas, or revert a specific config file (like an Nginx routing rule). If stabilization fails within 2 minutes, it escalates to SEV-1 and rolls back.
3. **Minor Issue (SEV-3):** 
    - **Symptoms:** Non-critical bugs, minor UI glitches, or isolated warnings in the logs that do not affect the critical path.
    - **Agent Action:** Standard debugging. The agent will read the logs, propose a patch, and execute a hotfix deployment without dropping the current live state.

### Automatic vs. Manual Rollback

If the orchestrator is running a deployment and Step 4 (Verifier) fails completely (e.g., the health check returns 500), the agent will automatically trigger the rollback sequence. If you notice an issue hours later, you can manually invoke it.

### Troubleshooting Common Failures

When a deployment fails, the agent will attempt to diagnose the issue. Here are the most common failure patterns the `incident-rollback` skill handles, and how you can guide it.

| Error Pattern | Likely Cause | Recommended Agent Action |
|---|---|---|
| **`502 Bad Gateway`** on health check | The application process crashed immediately after starting, or the reverse proxy is misconfigured. | *"Check the application container logs for immediate crashes. If none, check the Nginx error logs for upstream connection issues."* |
| **`Connection Refused`** to database | The database container isn't ready, credentials are wrong, or network bridge is missing. | *"Verify the database host is resolvable from the app container. Check if the database migration ran successfully, and ensure the DB port is exposed."* |
| **`ENOSPC: no space left on device`** | The host disk is 100% full, preventing new logs, builds, or containers. | *"Abort deployment. Run `df -h` and `docker system prune -a --volumes` to clear space. Check `/var/log` for bloated log files, then retry."* |
| **`EADDRINUSE: port is already allocated`** | An old version of the app is still running, or another service hijacked the port. | *"Find the PID using port 3000 (`lsof -i :3000`), kill it gracefully (`kill -15`), and restart the service."* |
| **`Invalid signature` / `Unauthorized`** | Missing or incorrect environment variables (e.g., missing API keys or wrong JWT secret). | *"Check if the `.env` file was successfully injected. Compare the remote `.env` keys with the local template to identify missing secrets."* |
| **`OOMKilled` (Out of Memory)** | The application consumed more memory than the container or host allows. | *"Check `dmesg -T \| grep -i oom`. If confirmed, increase the memory limit in `docker-compose.yml` or allocate swap space on the host."* |
| **`Error: ENOTFOUND`** | DNS resolution failed, usually due to a misconfigured Docker bridge network or missing `/etc/hosts` entry. | *"Ping the target hostname from within the container. Verify the Docker network configuration and custom DNS settings."* |

### Post-Incident Review (PIR)

After a successful stabilization or rollback, the agent doesn't just stop. It automatically generates an Incident Record summarizing what went wrong, what actions were taken, and what needs to be fixed before the next deployment attempt. This record serves as the foundation for your team's Post-Incident Review.

It will also flag if the failure was due to infrastructure (e.g., ran out of memory) versus application logic (e.g., a missing environment variable).

### Example Prompts

=== "Manual Rollback"

    ```text
    The site is returning 502s after the last deploy. Fix it or roll it back.
    ```

=== "Triage Production Incident"

    ```text
    Users are reporting the login API is timing out. Investigate the incident and stabilize the service immediately.
    ```

=== "Revert Configuration"

    ```text
    The new Nginx config we applied is dropping traffic. Roll back to the previous configuration backup immediately.
    ```

??? example "Sample Output (Incident Record)"

    ```markdown
    ## Incident Record & Rollback
    
    ### Incident Triage
    - **Issue:** Health check on `/api/health` failing with `502 Bad Gateway`.
    - **Logs:** App container is in a crash loop. Error: `Missing environment variable: STRIPE_API_KEY`.
    - **Severity:** CRITICAL (Service Down).
    
    ### Actions Taken (Stabilization)
    - Attempted to inject missing key, but key was not available in context.
    - **Decision:** Executing rollback to previous stable state to restore service.
    
    ### Rollback Execution
    1. Stopped failing container `api-service-v1.3.0`.
    2. Restored previous container `api-service-v1.2.9` from backup image.
    3. Reverted Nginx routing.
    
    ### Current State
    - **Status:** RESTORED
    - Service is back online running previous version (`v1.2.9`). 
    - Smoke tests pass.
    
    ### Follow-up Required
    The deployment failed due to a missing `STRIPE_API_KEY` in the production environment. Please provide this key securely before attempting the deployment again.
    ```

---

## Tips & Best Practices

??? example "Handling Private Repositories"
    If the agent needs to deploy a private GitHub repository to a remote server, it will need access. You can either use ssh-agent forwarding, or explicitly tell the agent: 
    *"Use a Personal Access Token stored in the `$GITHUB_TOKEN` environment variable on the server to clone the repo."*

??? example "Network Retries"
    Network operations fail. The deploy pack is instructed to **retry transient network failures** (SSH timeouts, `apt install` hangs, `docker pull` errors) at least twice before giving up or changing the deployment strategy. Do not panic if the first SSH attempt times out.

??? example "Multi-service Deployments"
    When dealing with microservices, instruct the agent clearly. 
    *"Deploy the backend service first, verify its database connection, and only then deploy the frontend React application."* 
    The orchestrator will handle the dependencies sequentially.

??? example "Handling Database Migrations Safely"
    Never let the agent run destructive migrations blindly in a production environment. 
    *"Run the deployment, but pause before running Prisma migrations. I want to review the SQL output first. Once I approve, you can execute the migration and verify."*
    By setting this boundary, you ensure schema changes do not inadvertently drop tables, rename critical columns, or lock the database during peak hours. You can also instruct the agent to run a database backup *before* the migration executes.

??? example "Environment Variable Management"
    Do not paste production secrets into the chat window. It is insecure and leaves secrets in your chat history.
    *"The secrets are located in `/etc/secrets/.env.prod` on the remote host. Inject them during the deployment step."* 
    Alternatively, use a secret manager: *"Fetch the database credentials from AWS Secrets Manager using the IAM role, and export them as environment variables before starting the Systemd service."*

??? example "Combining with CI/CD"
    The deploy pack does not replace GitHub Actions, GitLab CI, or Jenkins; it complements them. You can use the pack to provision the initial server, set up the Docker environment, configure the firewall, and register the GitHub Actions runner. Once the infrastructure is solid, you can let your traditional CI/CD pipeline take over daily code pushes, reserving the deploy pack for complex maintenance and incident triage.

??? example "Working with Monorepos"
    If your repository contains multiple services (e.g., a frontend React app in `apps/web` and a backend Node.js API in `apps/api`), tell the agent exactly which directory to focus on to avoid confusion.
    *"Deploy the backend service located in `apps/api`. Ignore the `apps/web` directory for now. Look for the `Dockerfile` inside `apps/api` and ensure the build context is the repository root."*

??? example "Deploying Behind a Reverse Proxy"
    If you are deploying a service that needs to be exposed to the internet via Nginx, Traefik, or Caddy, instruct the agent to handle the routing configuration alongside the application deployment.
    *"Deploy the service to port 8080 locally. Then, create an Nginx server block in `/etc/nginx/sites-available/api` for `api.example.com` that proxies traffic to `127.0.0.1:8080`. Test the Nginx config, create the symlink, and reload Nginx."*

??? example "Zero-Downtime Deployments"
    For critical services, instruct the agent to use zero-downtime deployment strategies rather than stopping and starting the service abruptly.
    *"Deploy the new Docker container on a new port (e.g., 8081). Wait for its health check to pass at `/api/health`. Once healthy, update the Nginx configuration to point to the new port, reload Nginx gracefully, and then stop the old container on port 8080."*
    This explicit instruction ensures the agent avoids taking the application offline during the deployment process.

??? example "Log Rotation and Management"
    Applications can quickly exhaust disk space if logs are left unmanaged. You can incorporate log rotation setup into the deployment request.
    *"Set up logrotate for the application logs located in `/var/log/myapp/`. Ensure logs are rotated daily, compressed, and kept for 14 days. Create the config file at `/etc/logrotate.d/myapp` and test it."*
    Handling this during deployment prevents late-night incidents caused by full disks.

---

## Skill Reference

The skills in this pack are modular. You can invoke the entire pipeline via the orchestrator, or call specific skills by using the trigger phrases below.

| Skill Name | Detailed Description | Common Trigger Phrases |
|---|---|---|
| **`repo-service-lifecycle`** | The end-to-end orchestrator for complete deployment pipelines. It manages the context handover between discovery, host checking, execution, verification, and operations. Use this for all general "get this running" requests. | *"Deploy this repo"*<br>*"Spin this up and manage it"*<br>*"Get this online"*<br>*"Take this repo to production"* |
| **`repo-runtime-discovery`** | Analyzes local or remote codebases to determine deployment requirements. It outputs a Deployment Brief detailing the tech stack, build commands, and missing configuration variables. | *"Analyze this repo"*<br>*"What do we need to deploy this?"*<br>*"Check the tech stack"*<br>*"Find missing env vars"* |
| **`target-host-readiness`** | Validates target infrastructure and prerequisites. It checks CPU, memory, disk space, port conflicts, and required language runtimes before allowing a deployment to proceed. | *"Check the server"*<br>*"Is the host ready?"*<br>*"Verify port availability"*<br>*"Check disk space on prod"* |
| **`deployment-executor`** | Safely executes deployments with strict rollback points. It handles the actual code transfer, container building, service restarting, and configuration injection. | *"Run the deployment"*<br>*"Apply the changes"*<br>*"Execute the rollout"*<br>*"Update the systemd service"* |
| **`deployment-verifier`** | Proves the service is functional via HTTP smoke tests, log inspection, and dependency validation. It ensures the application is actually serving traffic, not just running as a dead process. | *"Verify the deployment"*<br>*"Run a smoke test"*<br>*"Check if it's healthy"*<br>*"Validate the API endpoint"* |
| **`service-operations`** | Acts as a day-2 SRE. It handles routine maintenance, application log review, resource profiling, dependency updates, and SSL/TLS certificate renewals. | *"Check production logs"*<br>*"Prepare for upgrade"*<br>*"Routine SRE check"*<br>*"Check SSL certificates"* |
| **`incident-rollback`** | Stabilizes broken services and reverts to safe states during critical outages. It triages failures (SEV-1 vs SEV-3) and executes immediate rollbacks if the application crashes. | *"Site is down"*<br>*"Roll back the deploy"*<br>*"Fix the 502 error"*<br>*"Triage production incident"* |
