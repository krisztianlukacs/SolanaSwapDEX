# Data/Index

## Core Functionalities

### Postgres for User State and History
- Utilize a PostgreSQL database to store:
  - **User State**: Persist user-specific configurations and statuses.
  - **Transaction History**: Maintain a detailed record of all user transactions for auditing and analytics.
- Ensure database schema is optimized for:
  - Fast read/write operations.
  - Scalability to handle large volumes of user data.

### Indexer Service
- Implement an indexer service to process on-chain program logs and populate the database.
- Key responsibilities:
  - **Log Parsing**: Extract relevant data from Solana program logs.
  - **Data Transformation**: Convert raw log data into structured database entries.
  - **Database Insertion**: Insert transformed data into the Postgres database.
- Ensure the indexer service is:
  - Fault-tolerant to handle intermittent failures.
  - Efficient to process logs in near real-time.