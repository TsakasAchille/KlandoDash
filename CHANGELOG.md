# Changelog

## [1.5.0] - 2026-02-15

### Added
- **Klando AI Assistant**:
  - New administrative interface at `/admin/ai` powered by **Gemini 1.5 Flash**.
  - **Context-Aware Analysis**: AI has access to real-time stats, recent trips, and site requests to assist admins.
  - **Natural Language Interaction**: Chat interface for querying business data and matching drivers with requests.
  - **Server-Side Integration**: Secure API calls using Next.js Server Actions.
- **Sidebar Enhancements**: Added version display and quick-link to Klando AI.

## [1.4.0] - 2026-02-15

### Added
- **Driver Validation Module**:
  - New administrative interface at `/admin/validation` for verifying driver documents.
  - **Document Preview**: Visual display of ID cards and Driver Licenses stored in Supabase.
  - **Role-Based Security**: Access strictly restricted to administrators via middleware protection.
  - **Server Actions**: Implementation of the validation flow (currently in "Preview" mode with toast notifications).
  - **Database Integration**: Extended user queries to fetch document URLs and added a `pending` validation filter.

## [1.3.0] - 2026-02-15

### Added
- **Trips Page Overhaul**:
  - **Server-side Pagination**: Improved performance for large numbers of trips.
  - **Advanced Filtering**: Added filtering by Status, Max Price, and text search (Departure/Arrival/ID).
  - **Compact UI**: Redesigned trip table and details panel for better information density.
  - **Interactive Map**: Integration of route visualization directly in the compact details panel.
  - **Passenger Quick-links**: Visual passenger avatars with deep-links to user profiles.

## [1.2.0] - 2026-02-15

### Added
- **Server-side Pagination**: Implemented for the Users directory to improve performance with large datasets.
- **Advanced Smart Filtering**:
  - Distinct filters for Member Role (`driver`, `passenger`) and Verification Status (`is_driver_doc_validated`).
  - Added filters for Gender, Minimum Rating, and New Members (last 30 days).
  - All filters are processed server-side for efficiency.
- **Enhanced UI/UX**:
  - Compact table design with optimized row heights and font sizes.
  - Expandable advanced filter panel with visual active-filter indicators.
  - Sticky user details panel for better navigation.
  - Internal scrolling for user trips and transactions lists.
  - Custom sleek scrollbars for a premium dashboard feel.

### Fixed
- **Role Mappings**: Corrected the confusion between dashboard access roles and application member roles.
- **Import Typos**: Fixed a broken import for Lucide icons.

## [1.1.0] - 2026-02-10

### Added
- **Website Integration**: Comprehensive documentation (`docs/WEBSITE_INTEGRATION.md`) and SQL views for integrating the public website.
- **Site Requests Module**:
  - New dashboard page for managing site trip requests.
  - Server actions for status updates (PENDING, CONTACTED, CONVERTED, ARCHIVED).
  - Real-time metrics and info popover.
- **Database Views**:
  - `public_pending_trips`: Optimized view for displaying available trips on the website.
  - `public_completed_trips`: View for historical trip data.
- **UI Components**: Added `Badge` and `Tabs` components to `frontend/src/components/ui`.
- **Documentation**: Added architecture diagrams and integration guides.

## [1.0.2] - 2026-02-09

### Added
- **User Stats**: Added gender and birth date fields to user profiles.
- **Buyer Persona**: Implemented user persona section in statistics with age/gender distribution.
- **Database**: Added SQL inspection tools for database auditing.
