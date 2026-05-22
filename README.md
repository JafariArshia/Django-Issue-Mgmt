# Issue Tracker - Internal Ticket Management System

A full-stack internal issue and task management system built with Python Django, designed and deployed for **Feizy Rugs** (Texas, United States) as a tailored replacement for their existing Jira workflow. This repository is a cleaned-up version of the production codebase used internally by the company.

---

## 1. Background

Feizy Rugs needed an internal ticketing system built specifically around their team's workflow. While they had previously used Jira, they wanted a self-hosted solution that matched their exact processes, kept data internal to the company, and removed the overhead of a general-purpose tool. The system was deployed on an internal IIS server, making it accessible to all team members over the company's local network.

The result was a measurable improvement in how the team tracked and resolved issues:

- **70% improvement** in operational efficiency through automated scheduling and notifications
- **40% reduction** in issue resolution time through structured tracking and priority management
- **80% increase** in information flow speed across the organization via Microsoft Power Automate integration

---

## 2. Features

### 2.1 Ticket Management
- Create, edit, update, and close issues with full lifecycle tracking
- Priority levels (e.g. Normal, Important, Urgent) to help teams triage work effectively
- Ticket visibility rules: only the ticket creator and the assigned recipient can view a given ticket - other users cannot see tickets they are not part of, keeping sensitive task data appropriately scoped

### 2.2 Automated Notifications
- Configurable scheduled email alerts to notify the assigned recipient that a task is due
- Notification intervals are flexible - per minute, hourly, daily, or any custom cadence
- Built using **Microsoft Power Automate** for the email delivery layer
- Full alert history log per ticket, allowing users to see all past notifications sent for an issue

### 2.3 Comments
- Each ticket has a comment thread where the creator and recipient can discuss the issue
- Used for status updates, clarifications, resolution notes, or any relevant back-and-forth communication

### 2.4 Excel Migration Tool
- Since the team previously tracked tasks and issues entirely in Excel spreadsheets, a dedicated import tool was built to allow seamless migration of existing data
- Column mapping interface aligns Excel fields to the system's data model, so historical records could be moved into the platform without manual re-entry

### 2.5 Role-Based Access & Multi-User Support
- Supports multiple concurrent users across the organization
- Authentication and access control implemented using Django's middleware and permission system
- Users are segmented by role, with data access scoped accordingly

---

## 3. Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Django |
| Frontend | Django Templates (server-rendered) |
| Database | Relational DB via Django ORM |
| Task Scheduling | Django task scheduler |
| Email Automation | Microsoft Power Automate |
| Deployment | IIS (Windows Server, internal network) |
| Auth | Django authentication middleware, RBAC |

---

## 4. Architecture Overview

The application follows a standard Django MVT (Model-View-Template) architecture with a few additional layers:

**Models** define the core data structures: Users, Tickets, Comments, Notifications, and AlertLogs. Ticket visibility is enforced at the query level, ensuring users can only retrieve records they are authorized to see.

**Views** handle all business logic - ticket creation and updates, comment submission, notification triggering, and the Excel import pipeline. RESTful API patterns were applied where appropriate for clean separation between data handling and presentation.

**Templates** provide the frontend UI, keeping the interface functional and straightforward for non-technical staff at the company.

**Scheduler** runs as a background service, evaluating active tickets and firing notification events based on each ticket's configured alert interval. These events are handed off to Microsoft Power Automate, which handles the actual email delivery.

**Excel Importer** reads uploaded `.xlsx` files, presents a column-mapping interface to the user, and writes the mapped rows into the database using validated Django model forms, including error handling for malformed or missing fields.

---

## 5. Deployment

The system was deployed on an **IIS (Internet Information Services)** server on one of the company's internal machines, making it accessible to all employees within the company's local network without requiring internet exposure. This kept all ticket data fully internal to the organization.

---

## 6. Notes

This repository is a cleaned-up and anonymized version of the production system delivered to Feizy Rugs. Some company-specific configuration values, credentials, and internal data have been removed or replaced with placeholders.

---

*Built by Arshia Jafari - Python Django Developer Intern, Feizy Rugs (Aug-Nov 2024)*
