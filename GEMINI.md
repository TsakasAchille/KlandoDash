# KlandoDash Project Summary

## Project Overview

KlandoDash is the administration dashboard for Klando, a carpooling service in Senegal. This full-stack project is built with a modern tech stack, providing a comprehensive interface for managing trips, users, and support tickets.

- **Frontend**: The frontend is a Next.js 14 application, utilizing the App Router for page management. The user interface is built with Shadcn/ui and styled with TailwindCSS, creating a responsive and modern design. Key frontend dependencies include `leaflet` for map visualizations, `recharts` for statistical charts, and `@tanstack/react-table` for data tables.

- **Backend & Database**: The project leverages Supabase, a Backend-as-a-Service (BaaS) platform, which provides a PostgreSQL database, authentication, and auto-generated APIs. The database schema includes core tables for `trips`, `users`, `bookings`, and `support_tickets`. The `database/schema.sql` file defines the complete database structure, including tables, relationships, and indexes.

- **Authentication**: User authentication is handled by NextAuth.js (v5), with Google OAuth as the primary authentication provider. Access to the dashboard is restricted to authorized users listed in the `dash_authorized_users` table in the Supabase database.

- **Data Flow**: The frontend communicates with the Supabase backend through the `@supabase/supabase-js` client library. Data fetching is performed on the server-side using React Server Components, with dedicated query functions in `frontend/src/lib/queries/`. These functions are optimized to fetch only the required data, ensuring efficient data retrieval.

## Building and Running the Project

To get the KlandoDash application up and running, follow these steps:

1.  **Install Dependencies**: Navigate to the `frontend` directory and install the necessary npm packages.

    ```bash
    cd frontend
    npm install
    ```

2.  **Configure Environment Variables**: Create a `.env.local` file in the root of the project and add the required environment variables for Supabase and NextAuth. A symbolic link to this file should be created in the `frontend` directory.

    ```bash
    # Create the .env.local file in the root directory
    touch .env.local

    # Add your environment variables to .env.local
    # (see .env.example for required variables)

    # Create a symbolic link in the frontend directory
    ln -sf ../.env.local frontend/.env.local
    ```

3.  **Run the Development Server**: Start the Next.js development server.

    ```bash
    cd frontend
    npm run dev
    ```

    The application will be accessible at `http://localhost:3000`.

## Development Conventions

- **Code Style**: The project follows standard TypeScript and React conventions. Code is formatted according to the rules defined in the ESLint configuration (`.eslintrc.json`).

- **Data Fetching**: Data is fetched using the Supabase client. For server-side rendering, `createServerClient()` from `frontend/src/lib/supabase.ts` is used. Queries are organized in the `frontend/src/lib/queries` directory.

- **Type Safety**: The project uses TypeScript for type safety. Type definitions for database tables and API responses are located in the `frontend/src/types` directory.

- **UI Components**: The UI is built using Shadcn/ui components, which are highly customizable and accessible. Custom components are located in the `frontend/src/components` directory.
