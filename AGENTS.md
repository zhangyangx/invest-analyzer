# Repository Guidelines

## Project Structure & Module Organization
Core scripts live in `scripts/`. Each script does one job and returns JSON, for example `stock_quote.py`, `stock_kline.py`, and `news_fetcher.py`. Shared helpers belong in `scripts/_utils.py`, and static settings live in `scripts/config.json`.

Tests live in `test/`. Follow the existing pattern `test_<script_name>.py` and add new suites to `test/run_all_tests.py`. Reference material and planning notes live at the repo root (`README.md`, `SKILL.md`, `SKILL_API.md`) and in `docs/plans/`.

## Build, Test, and Development Commands
This repository uses Python 3 and the standard library only; there is no build step.

```bash
python3 test/run_all_tests.py
python3 test/test_stock_quote.py
python3 -m unittest test.test_stock_quote.TestStockQuote.test_sh_stock_code_6digit
python3 test/third_party_api_checks.py
cd scripts && python3 stock_quote.py 600519
```

Use `test/run_all_tests.py` before opening a PR. Run `third_party_api_checks.py` only when you need to confirm external API availability.

## Coding Style & Naming Conventions
Follow the existing Python style: 4-space indentation, `snake_case` for functions and variables, and clear module names such as `stock_search.py`. Keep scripts small, procedural, and standard-library-only. Preserve JSON output contracts, `ensure_ascii=False`, and the current exit-code pattern for errors. Add brief comments only where parsing or fallback logic is not obvious.

## Testing Guidelines
Use `unittest` and keep tests deterministic except for the explicit API connectivity checks. Cover argument parsing, invalid input, output structure, and edge cases. Name test classes after the target script and name methods by behavior, for example `test_invalid_stock_code`.

## Commit & Pull Request Guidelines
Recent history mixes short imperative subjects with optional prefixes, for example `chore: update news fetcher and tests` and `Enhance technical analysis with full indicator history`. Keep commit subjects concise, imperative, and focused on one change.

PRs should explain the user-visible behavior change, list affected scripts or APIs, and include the exact test command(s) run. If output shape changes, include a short JSON example in the PR description.

## Configuration & API Notes
This project depends on external market-data and news endpoints. Avoid adding non-standard dependencies or hard-coded secrets. When changing request logic, verify both script behavior and `test/third_party_api_checks.py`.
