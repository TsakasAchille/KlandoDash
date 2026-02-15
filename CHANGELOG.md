# Changelog

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
