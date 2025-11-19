# DigiPraman Universal Loan Verification System

## Overview

DigiPraman is a Universal Loan Verification System designed to streamline the government loan utilization verification process. The system leverages a mobile app for beneficiaries and a web portal for officers, integrating AI for enhanced fraud detection and risk assessment.

## Project Structure

The project is organized as follows:

```
digipraman-backend
├── src
│   ├── app.ts                # Entry point of the application
│   ├── config                 # Configuration settings
│   │   └── index.ts
│   ├── controllers            # Business logic for routes
│   │   └── index.ts
│   ├── db                    # Database related files
│   │   ├── migrations         # Database schema migrations
│   │   └── seeds              # Seed data for testing
│   ├── models                 # Data models for entities
│   │   └── index.ts
│   ├── routes                 # Route definitions
│   │   └── index.ts
│   ├── services               # Logic for external interactions
│   │   └── index.ts
│   └── types                  # TypeScript types and interfaces
│       └── index.ts
├── package.json               # npm configuration
├── tsconfig.json              # TypeScript configuration
└── README.md                  # Project documentation
```

## Setup Instructions

1. **Clone the repository:**

   ```
   git clone <repository-url>
   cd digipraman-backend
   ```

2. **Install dependencies:**

   ```
   npm install
   ```

3. **Database Configuration:**
   Update the database connection settings in `src/config/index.ts` to match your PostgreSQL setup.

4. **Provision Database:**

   ```powershell
   psql -U postgres -c "CREATE DATABASE digipraman;"
   psql -U postgres -d digipraman -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"
   psql -U postgres -d digipraman -c "CREATE EXTENSION IF NOT EXISTS postgis;"
   psql -U postgres -d digipraman -f src/db/migrations/001_initial_schema.sql
   ```

   This creates all enums, tables, and indexes outlined in the data model (organizations, users, loan_applications, verification_requests, evidence_items, VIDYA outputs, etc.).

5. **Seed the Database:**
   Populate the database with initial data using the seed files located in `src/db/seeds`.

6. **Start the Application:**
   ```
   npm start
   ```

## Environment Variables

Create a `.env` file in the project root containing at least:

```
APP_PORT=3000
DB_HOST=localhost
DB_PORT=5432
DB_NAME=digipraman
DB_USER=postgres
DB_PASSWORD=postgres
JWT_SECRET=replace-me
DEFAULT_ORG_ID=<optional UUID if you want auto-provisioned beneficiaries to attach to an org>
```

## Usage

- The mobile app allows beneficiaries to submit verification requests.
- Officers can review cases through the web portal, utilizing AI-assisted risk analysis.
- Admins can manage configurations and audit logs.

Complementary docs live under `docs/`:

- `docs/api/openapi.yaml` – minimal OpenAPI contract for OTP auth, evidence flows, and officer decisions.
- `docs/design/wireframes.md` – quick-reference wireframes covering beneficiary, capture, and officer experiences.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for discussion.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
