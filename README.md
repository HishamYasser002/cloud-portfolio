# cloud-portfolio

**🌐 Live site: [sthishamportfolio.z1.web.core.windows.net](https://sthishamportfolio.z1.web.core.windows.net/)**

My personal portfolio, hosted on Microsoft Azure, with a serverless visitor counter and automatic deployment through GitHub Actions. I'm building it step by step while studying for the Azure Administrator (AZ-104) certification.

## Architecture

```
                         GitHub push (main)
                                │
                                ▼
                 GitHub Actions ──OIDC login──> Azure
                                │
                                ▼
 Browser ──> Storage static website ($web)          (Germany West Central)
    │
    │  POST /api/visits
    ▼
 Azure Function (Python, Flex Consumption)
    │  managed identity, no keys
    ▼
 Table Storage ("visits" table)  ──>  {"count": 42}
```

- **Website:** Azure Blob Storage static website, Standard LRS, Germany West Central
- **Visitor counter:** Python Azure Function on the Flex Consumption plan, storing the count in Azure Table Storage
- **No secrets anywhere:** the function reaches the table with a **managed identity**, and GitHub Actions logs in to Azure with **OIDC**. There are no connection strings, keys or passwords in the code or in GitHub.
- **Least privilege:** each identity has only the role it needs, scoped to this one storage account (*Storage Blob Data Contributor* for deployment, *Storage Table Data Contributor* for the function)
- **CORS:** the API only accepts browser requests from this site
- **Security baseline:** HTTPS only, minimum TLS 1.2, no public blob access

## How the visitor counter works

1. The page calls `POST /api/visits`.
2. The function reads the counter row, adds 1 and writes it back **only if nobody changed it in the meantime**. It uses the row's ETag with an `If-Match` condition (optimistic concurrency). If two visitors arrive at the same moment, the losing update is retried instead of a visit being lost.
3. It returns `{"count": n}`, and the page shows it.

The logic lives in `api/counter.py`, separate from the Azure Functions code, so it can be unit tested with a fake in-memory table (`api/tests/`), including the concurrent-update case.

## Repository structure

```
frontend/              Website (HTML, CSS, JS)
api/                   Visitor counter: Azure Function (Python) + tests
infra/                 Infrastructure config (Terraform coming next)
.github/workflows/     Deployment pipeline
```

## Run the API locally

Requires Python 3.12, Azure Functions Core Tools and the Azure CLI (`az login`).

```bash
cd api
python -m venv .venv
.venv\Scripts\activate        # Windows (source .venv/bin/activate on Linux/macOS)
pip install -r requirements-dev.txt
pytest
func start                    # then open http://localhost:7071/api/visits
```

Locally, the function signs in with your `az login`. In Azure it uses its managed identity, with the same code.

## Problems I hit and how I fixed them

**1. Region blocked by Azure Policy**
Creating an Azure Static Web App failed with `RequestDisallowedByAzure`. My Azure for Students subscription has an *Allowed resource deployment regions* policy limited to five European regions, and Static Web Apps isn't available in any of them. I found the allowed list with `az policy assignment list` and switched to hosting the site on Blob Storage in Germany West Central.

**2. `SubscriptionNotFound` when creating the storage account**
The subscription did exist; the `Microsoft.Storage` resource provider just wasn't registered on it yet. Fixed with `az provider register --namespace Microsoft.Storage`. The same applied later to `Microsoft.Web` for Azure Functions.

**3. No permission to upload files, even as subscription owner**
Owner covers the management plane (creating and configuring resources) but not the data plane (reading and writing blobs and tables). I assigned myself *Storage Blob Data Contributor*, and later *Storage Table Data Contributor*, scoped only to this storage account.

**4. GitHub Actions login failed with `AADSTS700213`**
GitHub now sends OIDC subjects that include the owner and repository IDs (`repo:owner@id/repo@id:ref:...`), so the federated credential I created with the old format didn't match. I recreated it with the exact subject shown in the error message.

**5. Choosing a region for the Function App**
Because of the region policy, I checked which allowed regions support the Flex Consumption plan (`az functionapp list-flexconsumption-locations`) before creating anything. Germany West Central supports it, so the function runs in the same region as its storage.

## Roadmap

- [x] Static website on Azure Storage
- [x] Automated deployment with GitHub Actions and OIDC
- [x] Visitor counter API (Azure Functions + Table Storage, managed identity)
- [x] Deploy the API from GitHub Actions, with tests running first
- [ ] Infrastructure as code with Terraform
- [x] Monitoring and alerts with Application Insights

## Connect

[LinkedIn](https://www.linkedin.com/in/hisham-abuhishmeh-58b825265) · [GitHub](https://github.com/HishamYasser002)
