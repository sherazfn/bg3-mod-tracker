# Test Suite

Comprehensive test suite for mod changelog functionality.

## Running Tests

### Install dependencies
```bash
pip install -r requirements-test.txt
```

### Run all tests
```bash
pytest
```

### Run specific test file
```bash
pytest tests/test_mod_scenarios.py
```

### Run with coverage
```bash
pytest --cov=scripts --cov-report=html
```

## Test Scenarios Covered

### Mod Update Scenarios (`test_mod_scenarios.py`)

#### Core Scenarios
1. **New Mod** - Mod appears for first time (creates 'added' event)
2. **Console Version Bump** - PS5 version increases (creates 'updated' event)
3. **Description Only Change** - Only description changes, no version bump (no 'updated' event)
4. **PC-Only Version Bump** - Windows version bumps, PS5 unchanged (creates 'updated' event — any platform counts)
5. **Multiple Console Updates** - Multiple PS5 version bumps (multiple 'updated' events)
6. **Name Change Only** - Only name changes (no 'updated' event)
7. **Mixed Platform Updates** - Both PS5 and Windows change (any platform bump triggers update)
8. **Windows-Only Mod Version Bump** - Windows-only mod version bumps (creates 'updated' event)

#### Edge Cases
9. **Version Decrease** - PS5 version decreases (no 'updated' event)
10. **PS5 Version Same, Other Changes** - PS5 version unchanged, other fields change (no 'updated' event)
11. **Multiple Mods** - Multiple mods with different update patterns

#### Removal Scenarios
12. **Mod Removed** - Mod appears then is removed from data.json (still exists in DB with last version)
13. **Mod Reappears** - Mod removed then reappears (continues tracking or creates new entry)
14. **Mod Removed with Other Mods** - One mod removed while others continue (other mods unaffected)
15. **Mod Removed No PS5 Platform** - Mod without PS5 platform is removed (still tracked)
16. **Mod Platforms Populated** - Mod.platforms reflects the latest platforms list across versions

### Workflow Logic Tests (`test_workflow_logic.py`)

1. **No Changes Detected** - Git correctly detects no changes
2. **Changes Detected** - Git correctly detects changes
3. **Combined Files Staging** - Both data.json and index.html stage correctly

## Test Structure

- `conftest.py` - Pytest fixtures and configuration
- `test_mod_scenarios.py` - Mod update scenario tests (16 tests)
- `test_workflow_logic.py` - Workflow change detection tests (3 tests)
- `test_integration_pipeline.py` - Full pipeline integration tests (6 tests)

## Integration Tests

Full pipeline tests (`test_integration_pipeline.py`) simulate the complete GitHub Actions workflow:

1. **test_full_pipeline_new_mod** - Complete pipeline with new mod
2. **test_full_pipeline_version_bump** - Pipeline with mod version bump
3. **test_full_pipeline_multiple_mods** - Pipeline with multiple mods
4. **test_full_pipeline_no_changes** - Pipeline when data.json unchanged
5. **test_full_pipeline_cleanup** - Verify cleanup works correctly
6. **test_full_pipeline_with_live_data** - Pipeline using actual data.json (if available)

These tests:
- Create git repositories with commits
- Run git-history to generate databases
- Run generate_html to create HTML
- Verify outputs
- Clean up all temporary files

### Running Integration Tests

```bash
# Run all integration tests
pytest tests/test_integration_pipeline.py -v

# Run with output
pytest tests/test_integration_pipeline.py -v -s

# Skip slow tests (like live data test)
pytest tests/test_integration_pipeline.py -v -m "not slow"
```
