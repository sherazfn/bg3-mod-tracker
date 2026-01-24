# Integration Tests - Full Pipeline

## Overview

Integration tests that simulate the complete GitHub Actions workflow from start to finish, including:
- Git repository setup with commits
- Database generation using git-history
- HTML generation
- Output verification
- Cleanup

## Test Suite

### ✅ All 6 Integration Tests Passing

### Test Scenarios

#### 1. **test_full_pipeline_new_mod**
- **What it tests**: Complete pipeline with a new mod appearing
- **Steps**:
  1. Create git repo with initial empty data.json
  2. Commit with new mod data
  3. Run git-history to generate database
  4. Run generate_html to create HTML
  5. Verify database structure and content
  6. Verify HTML output
- **Expected**: Database created, HTML generated, mod tracked correctly

#### 2. **test_full_pipeline_version_bump**
- **What it tests**: Pipeline with mod version bump
- **Steps**:
  1. Create git repo with mod at version 1
  2. Commit with mod at version 2 (PS5 version bump)
  3. Run full pipeline
  4. Verify both 'added' and 'updated' events
- **Expected**: Database tracks version bump, HTML shows update

#### 3. **test_full_pipeline_multiple_mods**
- **What it tests**: Multiple mods with different update patterns
- **Steps**:
  1. Create git repo with two mods
  2. Update one mod (version bump), keep other unchanged
  3. Run full pipeline
  4. Verify independent tracking
- **Expected**: Each mod tracked independently, correct events for each

#### 4. **test_full_pipeline_no_changes**
- **What it tests**: Pipeline when data.json hasn't changed
- **Steps**:
  1. Create git repo with mod
  2. Commit same data again (no changes)
  3. Run full pipeline
  4. Verify graceful handling
- **Expected**: Pipeline completes, no errors, mod still tracked

#### 5. **test_full_pipeline_cleanup**
- **What it tests**: Cleanup behavior (like workflow)
- **Steps**:
  1. Run full pipeline
  2. Delete database (simulate cleanup)
  3. Verify HTML persists
- **Expected**: Database can be deleted, HTML remains usable

#### 6. **test_full_pipeline_with_live_data**
- **What it tests**: Pipeline using actual data.json from repository
- **Steps**:
  1. Copy live data.json to test directory
  2. Create git repo with live data
  3. Run full pipeline
  4. Verify database creation (may skip HTML if schema differs)
- **Expected**: Database created successfully, validates git-history works with real data

## Key Features

### Git Repository Simulation
- Creates isolated git repositories for each test
- Makes realistic commits with data.json
- Uses 'main' branch (required by git-history)
- Handles no-change commits gracefully

### Database Generation
- Runs actual `git-history` command
- Verifies database structure (tables/views)
- Checks data integrity
- Validates item_version_detail view exists

### HTML Generation
- Runs actual `generate_html.py` script
- Creates assets directory structure
- Verifies HTML file creation
- Checks HTML content structure

### Cleanup
- All temporary files cleaned up automatically
- Database connections properly closed
- No file locks on Windows
- Tests are isolated and independent

## Running Tests

### Run All Integration Tests
```bash
pytest tests/test_integration_pipeline.py -v
```

### Run with Detailed Output
```bash
pytest tests/test_integration_pipeline.py -v -s
```

### Run Specific Test
```bash
pytest tests/test_integration_pipeline.py::TestFullPipeline::test_full_pipeline_new_mod -v -s
```

### Skip Slow Tests
```bash
pytest tests/test_integration_pipeline.py -v -m "not slow"
```

## Test Output

Each test provides detailed output showing:
- What is being tested
- Expected results
- Actual results at each step
- [PASS] confirmation when successful

Example output:
```
=== Testing: Full Pipeline - New Mod ===
What we're testing: Complete workflow from git commits to HTML generation
Expected: Database created, HTML generated, mod appears in output

=== Setting up Git Repository ===
Creating git repo in: /tmp/...
Created commit 1 with 1 mod(s)

=== Step 1: Running update_history.py ===
[PASS] Database created at: /tmp/.../mods.db
Got: Database file exists (53248 bytes)
Got: Database objects = ['item_version_detail', ...]

=== Step 2: Running generate_html.py ===
Got: Generated HTML with 1 mod(s)
Got: HTML file exists (35001 bytes)

[PASS] Full pipeline test passed: Database and HTML generated correctly
```

## Requirements

- `git-history` must be installed: `pip install git-history`
- Git must be available in PATH
- Python 3.12+

## Notes

- Tests use temporary directories (automatically cleaned up)
- Tests create isolated git repositories (no interference)
- Live data test may skip HTML generation if schema differs (acceptable)
- All database connections are properly closed
- Tests run in < 6 seconds total

## Integration with CI/CD

These tests can be added to GitHub Actions:

```yaml
- name: Run integration tests
  run: |
    pip install -r requirements-test.txt git-history
    pytest tests/test_integration_pipeline.py -v
```
