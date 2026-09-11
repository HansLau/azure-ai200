# Ticket Triage – AI Helpdesk Assistant

## 1. Project Overview

Ticket Triage is a web-based helpdesk application developed as part of the Azure AI-200 Capstone Project.

The system allows users to submit support tickets and receive an automatic category suggestion. Administrators can review submitted tickets, filter the ticket list, and update ticket statuses.

The application uses Azure services for frontend hosting, backend API processing, AI-based classification, secure secret management, and ticket storage.

---

## 2. Main Features

### User Portal

- Submit a support ticket
- Enter user name and email
- Provide a ticket title and description
- Select ticket priority
- Receive an AI-suggested ticket category
- Submit the ticket to the backend

### AI Classification

The system automatically suggests a category based on the submitted ticket.

Supported categories:

- IT Support
- Facilities
- Course Registration
- Student Finance
- Library Services
- General Enquiry

The application uses Azure AI Language for classification with a keyword-based classification logic available as a fallback.

### Admin Portal

Administrators can:

- View submitted tickets
- Review ticket details
- Filter tickets by category
- Filter tickets by status
- Filter tickets by email
- Update ticket status

Supported ticket statuses include:

- New
- Categorised
- In Progress
- Resolved

---
