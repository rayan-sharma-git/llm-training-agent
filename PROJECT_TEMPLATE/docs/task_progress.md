# Task Progress — Analyze Project Fix & Full Feature Implementation

## Phase 1: Root Cause Fix (Analyze Project)
- [ ] Fix coroutine `.model_dump()` bug in `backend/api/routes.py` (await before model_dump)
- [ ] Fix stale results dict fallback in `backend/api/routes.py` prediction/recommendation/report sections
- [ ] Fix the same bug in `extension/backend/api/routes.py` (packaged copy)
- [ ] Fix missing imports (`get_active_provider`, `get_active_model`) in extension/backend/api/routes.py
- [ ] Fix scanner robustness: ignore .git/node_modules/venv/__pycache__, fix glob patterns

## Phase 2: Other Code Bug Fixes
- [ ] Fix `ai/providers.py` dead file conflict with `ai/providers/` package
- [ ] Fix `core/di.py` `_instances` not initialized in `__init__`
- [ ] Fix `conftest.py` `get_session_factory(engine)` argument bug
- [ ] Fix `test_integration.py` trailing HTML artifact
- [ ] Fix `test_dataset_analyzer.py` dict-vs-model access

## Phase 3: BackendManager & Error Handling
- [ ] Improve BackendManager dependency check (add httpx, sqlalchemy, etc.)
- [ ] Fix settings webview `getApiKey()` call (method doesn't exist on ApiClient)
- [ ] Fix settings webview `ollamaBaseUrl` element reference

## Phase 4: Extension Configuration
- [ ] Fix package.json provider enum (add all providers)
- [ ] Add API key configuration via SecretStorage

## Phase 5: Tests
- [ ] Add comprehensive scanner tests
- [ ] Add backend API integration tests

## Phase 6: Build, Package, Verify
- [ ] Compile TypeScript
- [ ] Run Python tests
- [ ] Re-run backend startup + Analyze Project test
- [ ] Re-copy backend into extension
- [ ] Package .vsix
- [ ] Verify full flow end-to-end

## Phase 7: Documentation
- [ ] Write 3_scanner_fix.md report
- [ ] Update README
