# Agent guidance

## Testing

- SDK static: `cd sdk && poetry check --lock && poetry run black --check --quiet . && poetry run isort --check-only --quiet chatfaq_sdk examples` (timeout 120s).
- SDK tests: `cd sdk && poetry run python -m unittest discover -s tests -p 'test_*.py' -q` (~1s; timeout 60s).
- SDK package: `cd sdk && poetry build` (~1s; timeout 120s); validate the wheel from an isolated Python 3.14 environment.
- Widget static: `cd widget && pnpm exec nuxt prepare && pnpm exec vue-tsc --noEmit --pretty false` (~9s; timeout 180s).
- Widget package: `cd widget && pnpm run package` (~9s; timeout 300s), then validate package entry points and `npm pack --dry-run --json`.
- Widget app build: `cd widget && pnpm run build` (~9s; timeout 300s).
- Always redirect output to a temporary file; stay quiet on success and show only relevant failure excerpts.
- Last measured: 2026-11-23.
