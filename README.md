# docker-workshop

Workshop code base — a collection of Python examples and supporting infrastructure for a Docker-based workshop.

## Contents

- pipeline/ — CI/CD or pipeline examples (if present).
- terraform-local/ — local Terraform examples (if present).
- test/ — test code and test data.

## Prerequisites

- Docker (Engine) installed and running. On macOS/Windows use Docker Desktop.
- Optional: docker-compose (if you use compose files).
- A modern web browser for Jupyter notebooks (if used).

## Quick start — build and run with Docker

1. Open Docker
   - Start Docker Desktop (macOS/Windows) or ensure the Docker daemon is running (Linux):
     - macOS/Windows: open `Docker Desktop` from Applications and wait until it reports "Docker is running".
     - Linux: run `sudo systemctl start docker` (or the appropriate service manager command).

2. Build the Docker image (run from the repository root)

```bash
# build an image tagged `docker-workshop`
docker build -t docker-workshop .
```

3. Run the container and open an interactive shell

```bash
# start a container and drop to a shell, mounting the repo into /app
docker run --rm -it -v "$PWD":/app -w /app docker-workshop bash
```

4. Run Jupyter Notebook / Lab (if notebooks are included)

```bash
# run Jupyter Notebook inside the container and expose it on port 8888
docker run --rm -p 8888:8888 -v "$PWD":/app -w /app docker-workshop \
  jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root
```

- After the notebook starts it will print a URL with a token. Open `http://localhost:8888` in your browser and paste the token if necessary.

## Running Python code or tests

- From inside the running container (shell), run Python scripts as usual:

```bash
python path/to/script.py
```

- If the repository includes a `requirements.txt` (or similar), install dependencies inside the container or in a virtualenv:

```bash
pip install -r requirements.txt
```

- Run tests (if using pytest):

```bash
pytest -q
```

## Working with volumes and persisted data

- The examples above mount the current repository into `/app` inside the container using `-v "$PWD":/app`. This makes your local files available to the container and lets you edit code on the host while running it in Docker.
- To persist data produced by the container, use named volumes or bind mounts to a host directory.

## Environment variables and configuration

- Pass environment variables into the container with `-e VAR=value` or use an env file with `--env-file .env`.

Example:

```bash
docker run --rm -e MY_VAR=foo -v "$PWD":/app -w /app docker-workshop python script.py
```

## Helpful Docker commands

- List running containers: `docker ps`
- List all containers: `docker ps -a`
- View logs: `docker logs <container-id-or-name>`
- Execute a shell in a running container: `docker exec -it <container-id-or-name> bash`
- Stop a container: `docker stop <container-id-or-name>`
- Remove dangling images: `docker image prune -f`

## If you use docker-compose

If the repository includes a `docker-compose.yml`, start the services with:

```bash
docker-compose up --build
```

Stop and remove containers with:

```bash
docker-compose down
```

## Repository notes

- The repo primarily contains Python code. Look in the repository root and the `test/` directory for runnable scripts and tests.
- `pipeline/` and `terraform-local/` appear to contain infrastructure or CI-related examples — check those directories for README or usage notes specific to them.

## Troubleshooting

- Permission denied when mounting volumes on Linux: ensure your user is in the `docker` group or run the container with `sudo`.
- Port already in use: change the host port when mapping (for example `-p 8889:8888`).
- Build fails due to missing dependencies: inspect the Dockerfile (if present) and the repository dependency files (`requirements.txt`, `pyproject.toml`).

## Contributing

Please open issues or pull requests for improvements. Provide steps to reproduce and specify environment (OS, Docker version).

## Contact

If you need further help, open an issue in this repository or contact the repository owner.
