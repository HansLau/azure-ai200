# Ticket Triage – AI Helpdesk Assistant

## 1. Project Overview

Ticket Triage is a web-based helpdesk application developed as part of the Azure AI-200 Capstone Project.

The system allows users to submit support tickets and receive an automatic category suggestion. Administrators can review submitted tickets, filter the ticket list, and update ticket statuses.

The application uses Azure services for frontend hosting, backend API processing, AI-based classification, secure secret management, and ticket storage.

---

## 2. Setup Instructions
The Ticket Triage application is deployed on Microsoft Azure.

To access the application:

1. Sign in to the Azure Portal.
2. Navigate to the `ai200` resource group.
3. Select the `ticket-triage` Azure Static Web App.
4. On the Overview page, click **Browse** to open the deployed application.
5. The Ticket Triage user portal will be displayed.
6. Users can submit a support ticket through the portal.
7. Administrators can access the Admin Portal to review submitted tickets, filter tickets, and update ticket statuses.

---

## 3. Deployment Steps

1. The project source code is in GitHub.
2. The frontend is deployed to Azure Static Web Apps.
3. The backend is deployed to Azure Functions.
4. GitHub Actions is used to automate deployment.
5. Azure Cosmos DB is configured for ticket storage.
6. Azure AI Language is configured for ticket classification.
7. Azure Key Vault is configured to securely store sensitive credentials.
8. The Azure Function App uses a managed identity to access the required Key Vault secrets.

---
## 4. Environment Variables

The backend requires the following environment variables:

| Variable | Purpose |
|---|---|
| `COSMOS_DB_URI` | Connection URI for Azure Cosmos DB |
| `COSMOS_DB_KEY` | Authentication key for Azure Cosmos DB |
| `COSMOS_DB_NAME` | Name of the Cosmos DB database |
| `COSMOS_CONTAINER_NAME` | Name of the Cosmos DB container |
| `AZURE_LANGUAGE_ENDPOINT` | Endpoint for Azure AI Language |
| `AZURE_LANGUAGE_KEY` | Authentication key for Azure AI Language |

The sensitive environment variables, including the Cosmos DB credentials and Azure AI Language key, are stored in Azure Key Vault securely.
The Azure Function App uses a system-assigned managed identity with permission to access the required Key Vault secrets.
No secret values are stored directly in the GitHub repository.

---

## 5. Test Instructions

1. Open the Ticket Triage web portal in a browser.
2. Enter your **Full Name**, **Email**, **Subject**, and **Detailed Description**.
3. Click **Suggest with AI** to receive a suggested ticket category.
4. Click **Submit Ticket** to submit the support request.
5. Open the Admin Portal to verify that the submitted ticket appears in the Helpdesk Queue.

---

## 6. Limitations and Future Improvements

| Current Limitation | Future Improvement |
|---|---|
| AI classification may not always correctly classify complex or unclear tickets. | Improve the AI classification model and train it with more ticket examples. |
| The Admin Portal has basic ticket management features. | Add more advanced dashboard features, such as ticket statistics and analytics. |
| The system currently has basic user and admin access control. | Implement Microsoft Entra ID authentication and role-based access control. |
| The system does not currently provide notifications when a ticket status changes. | Add email notifications to keep users updated on their ticket status. |
| The application is mainly designed for the capstone demonstration and uses Azure free-tier services. | Scale the Azure services and resources for a larger number of users and tickets. |

