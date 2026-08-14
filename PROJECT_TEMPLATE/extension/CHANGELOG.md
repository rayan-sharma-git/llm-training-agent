# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-08-05

### Added
- Initial release
- Project analysis and scanning
- Chat interface with AI providers
- Report generation
- Sidebar views (Overview, Chat, Reports)
- Activity Bar icon

### Fixed
- Fixed `escapeHtml` to properly escape HTML entities (was replacing with same characters)
- Fixed activation events to use correct view IDs (`onView:llmTrainingAgent.*`)
- Namespaced view IDs to prevent collisions with other extensions
- Implemented functional Chat view using `WebviewViewProvider`
- Fixed `Open Chat` command to open the Chat sidebar view
- Fixed test suite to reference correct view IDs
- Fixed test suite `index.ts` to not auto-run tests on import
- Cleaned up package contents (excluded test files, source, and backup archives)
- Fixed corrupted LICENSE file
- Updated README with accurate feature documentation