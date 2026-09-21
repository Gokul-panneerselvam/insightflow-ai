# Insightflow AI

Full-stack enterprise AI research and decision intelligence platform built with React, FastAPI, LangChain, LangGraph, LangSmith, PostgreSQL, pgvector, Redis, and MCP.

---

## Getting Started

### Prerequisites
- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (fast Python package manager)
- [Docker](https://www.docker.com/) (optional, for containerization)

### Installation

```bash
# Sync dependencies and create virtual environment
uv sync
```

### Running the Backend Server

```bash
# Start development server with hot-reloading on http://localhost:8000
uv run uvicorn src.app.main:app --reload --port 8000
```

Alternatively:
```bash
uv run python -m src.main
```

---

## API Endpoints

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/` | `GET` | Service overview, status, and API routes |
| `/healthz` | `GET` | Root-level health check alias for cloud load balancers |
| `/api/v1/health` | `GET` | Detailed health check (app name, version, environment, timestamp) |
| `/api/v1/livez` | `GET` | Container liveness probe |
| `/api/v1/readyz` | `GET` | Container readiness probe |
| `/docs` | `GET` | Interactive Swagger / OpenAPI documentation |
| `/redoc` | `GET` | ReDoc API documentation |

---

## Code Quality & Local Checks

Run the automated checks locally before committing or opening a pull request:

```powershell
# 1. Ruff Linting
uv run ruff check .

# 2. Ruff Formatting
uv run ruff format --check .

# 3. Mypy Static Type Checking
uv run mypy src tests

# 4. Pytest with Coverage
uv run pytest --cov=src --cov-report=term-missing
```

---

## Docker Containerization

```bash
# Build the production Docker container
docker build -t insightflow-ai:latest .

# Run container locally on port 8000
docker run -p 8000:8000 insightflow-ai:latest
```

---

## CI/CD Pipeline (Azure Container Apps)

The repository uses GitHub Actions configured in [ci-cd.yml](.github/workflows/ci-cd.yml) with a 2-phase architecture:

```
[Commit / PR Push] ──> Phase 1: CI Checks (Ruff + Mypy + Pytest Coverage)
                                  │
                                  ▼
[Merge to main]    ──> Phase 2: CD Deploy (Build Image ──> Push to ACR ──> Deploy to Azure Container Apps)
```

### 1. Phase 1: Continuous Integration (CI)
- Triggers on: Any push or pull request targeting `main`.
- Runs:
  - **Ruff**: Linting and formatting validation.
  - **Mypy**: Static type validation across `src/` and `tests/`.
  - **Pytest**: Automated test suite execution with minimum coverage enforcement.

### 2. Phase 2: Continuous Deployment (CD)
- Triggers on: Push / merge directly into `main` after CI checks pass.
- Authenticates with Azure and Azure Container Registry (ACR).
- Builds multi-stage optimized container image and pushes to ACR with `${{ github.sha }}` and `latest` tags.
- Deploys the container to Azure Container Apps with zero-downtime rolling update.

---

### Azure Infrastructure Setup (One-time)

Run these Azure CLI commands to provision the initial cloud resources:

```bash
# Set variables
RESOURCE_GROUP="rg-insightflow-prod"
LOCATION="eastus"
ACR_NAME="acrinsightflow"
ACA_ENV="env-insightflow"
APP_NAME="app-insightflow-backend"

# 1. Create Resource Group
az group create --name $RESOURCE_GROUP --location $LOCATION

# 2. Create Azure Container Registry (ACR)
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --admin-enabled true

# 3. Create Container Apps Managed Environment
az containerapp env create --name $ACA_ENV --resource-group $RESOURCE_GROUP --location $LOCATION

# 4. Create initial Azure Container App
az containerapp create \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --environment $ACA_ENV \
  --image mcr.microsoft.com/k8se/quickstart:latest \
  --target-port 8000 \
  --ingress external \
  --min-replicas 1 \
  --max-replicas 3

# 5. Create Azure Service Principal for GitHub Actions
az ad sp create-for-rbac \
  --name "sp-insightflow-github" \
  --role "Contributor" \
  --scopes "/subscriptions/<SUBSCRIPTION_ID>/resourceGroups/$RESOURCE_GROUP" \
  --json-auth
```

---

### Required GitHub Secrets

Configure these in your GitHub Repository under **Settings > Secrets and variables > Actions**:

| Secret Name | Description | Example / Source |
| :--- | :--- | :--- |
| `AZURE_CREDENTIALS` | JSON output from `az ad sp create-for-rbac` | `{"clientId": "...", "clientSecret": "...", ...}` |
| `AZURE_CONTAINER_REGISTRY` | Full ACR login server | `acrinsightflow.azurecr.io` |
| `AZURE_ACR_NAME` | ACR name | `acrinsightflow` |
| `AZURE_REGISTRY_USERNAME` | ACR admin username / SP client ID | `acrinsightflow` |
| `AZURE_REGISTRY_PASSWORD` | ACR admin password / SP secret | `<acr-admin-password>` |
| `AZURE_RESOURCE_GROUP` | Target Azure Resource Group | `rg-insightflow-prod` |
| `AZURE_CONTAINER_APP_NAME` | Target Azure Container App name | `app-insightflow-backend` |
