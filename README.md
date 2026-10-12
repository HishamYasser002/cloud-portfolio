# cloud-portfolio

**🌐 Live site: [sthishamportfolio.z1.web.core.windows.net](https://sthishamportfolio.z1.web.core.windows.net/)**

My personal portfolio, hosted on Microsoft Azure and deployed automatically with GitHub Actions. I'm building it step by step while studying for the Azure Administrator (AZ-104) certification.

## Architecture

```
GitHub push (main) ──> GitHub Actions ──OIDC login──> Azure
                                                │
                                                ▼
                           Azure Storage account (Germany West Central)
                           └── $web container ──> static website (HTTPS)
```

- **Hosting:** Azure Blob Storage static website, Standard LRS, Germany West Central
- **Security:** HTTPS only, minimum TLS 1.2, no public blob access
- **Access control:** least-privilege RBAC (*Storage Blob Data Contributor*, scoped to this storage account only)
- **CI/CD:** GitHub Actions deploys `frontend/` on every push to `main`
- **Authentication:** OIDC workload identity federation, so no passwords or keys are stored in GitHub

## Repository structure

```
frontend/              Website (HTML, CSS, JS)
api/                   Visitor counter API (coming next)
infra/                 Infrastructure config (Terraform coming next)
.github/workflows/     Deployment pipeline
```

## Problems I hit and how I fixed them

**1. Region blocked by Azure Policy**
Creating an Azure Static Web App failed with `RequestDisallowedByAzure`. My Azure for Students subscription has an *Allowed resource deployment regions* policy limited to five European regions, and Static Web Apps isn't available in any of them. I found the allowed list with `az policy assignment list` and switched to hosting the site on Blob Storage in Germany West Central.

**2. `SubscriptionNotFound` when creating the storage account**
The subscription did exist; the `Microsoft.Storage` resource provider just wasn't registered on it yet. Fixed with `az provider register --namespace Microsoft.Storage`.

**3. No permission to upload files, even as subscription owner**
Owner covers the management plane (creating and configuring resources) but not the data plane (reading and writing blobs). I assigned myself *Storage Blob Data Contributor*, scoped only to this storage account.

**4. GitHub Actions login failed with `AADSTS700213`**
GitHub now sends OIDC subjects that include the owner and repository IDs (`repo:owner@id/repo@id:ref:...`), so the federated credential I created with the old format didn't match. I recreated it with the exact subject shown in the error message.

## Roadmap

- [x] Static website on Azure Storage
- [x] Automated deployment with GitHub Actions and OIDC
- [ ] Visitor counter API (Azure Functions + Table Storage)
- [ ] Tests in the pipeline
- [ ] Infrastructure as code with Terraform
- [ ] Monitoring and alerts with Application Insights

## Connect

[LinkedIn](https://www.linkedin.com/in/hisham-abuhishmeh-58b825265) · [GitHub](https://github.com/HishamYasser002)
