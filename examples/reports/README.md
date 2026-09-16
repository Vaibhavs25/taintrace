# Example typosquat reports

These fixtures show `taintrace v0.2.1` scanning realistic misspellings of popular packages. The JSON below was generated with `taintrace check <file> --format json` from the checked-in fixture files.

## Python: `reqeusts` → `requests`

### Attack context

A dependency entry named `reqeusts` can exploit a transposition typo in the popular `requests` package name. An automated installer could fetch the similarly named package before a reviewer notices the spelling change.

Minimal [`requirements.txt`](python/requirements.txt):

```text
reqeusts==2.31.0
```

Run:

```bash
taintrace check examples/reports/python/requirements.txt --format json
```

Expected report:

```json
{
  "tool": "taintrace",
  "version": "0.2.1",
  "summary": {"total": 1, "suspects": 1, "risk_levels": {"CRITICAL": 1, "HIGH": 0, "MEDIUM": 0}},
  "results": [{"package": "reqeusts", "version": "2.31.0", "risk_level": "CRITICAL", "risk_score": 1.0, "similar_to": ["requests", "mkdocs"], "reason": "Near-identical to 'requests' — likely typosquat"}]
}
```

Fix the dependency entry and regenerate the environment lock state:

```bash
python -c "from pathlib import Path; p=Path('requirements.txt'); p.write_text(p.read_text().replace('reqeusts', 'requests'))"
```

## Node.js: `lodahs` → `lodash`

### Attack context

`lodahs` transposes two letters in `lodash`. A package manifest or generated lockfile containing that spelling can direct an automated install toward a lookalike package.

Minimal [`package-lock.json`](node/package-lock.json) contains `node_modules/lodahs` at version `4.17.21`.

Run:

```bash
taintrace check examples/reports/node/package-lock.json --format json
```

Expected report:

```json
{
  "tool": "taintrace",
  "version": "0.2.1",
  "summary": {"total": 1, "suspects": 1, "risk_levels": {"CRITICAL": 1, "HIGH": 0, "MEDIUM": 0}},
  "results": [{"package": "lodahs", "version": "4.17.21", "risk_level": "CRITICAL", "risk_score": 1.0, "similar_to": ["lodash", "lodash-es", "redux"], "reason": "Near-identical to 'lodash' — likely typosquat"}]
}
```

Fix the dependency and regenerate `package-lock.json`:

```bash
npm uninstall lodahs && npm install lodash@4.17.21
```

## Ruby: `raills` → `rails`

### Attack context

`raills` adds one letter to the widely used `rails` gem name. This kind of near-identical dependency can be selected through autocomplete or a typing slip and then persist in `Gemfile.lock`.

Minimal [`Gemfile.lock`](ruby/Gemfile.lock) contains `raills (7.1.3)`.

Run:

```bash
taintrace check examples/reports/ruby/Gemfile.lock --format json
```

Expected report:

```json
{
  "tool": "taintrace",
  "version": "0.2.1",
  "summary": {"total": 1, "suspects": 1, "risk_levels": {"CRITICAL": 1, "HIGH": 0, "MEDIUM": 0}},
  "results": [{"package": "raills", "version": "7.1.3", "risk_level": "CRITICAL", "risk_score": 1.0, "similar_to": ["rails", "rails-html-sanitizer", "redis", "ransack", "rails-dom-testing", "reline"], "reason": "Near-identical to 'rails' — likely typosquat"}]
}
```

Fix the gem entry and regenerate the lockfile:

```bash
bundle remove raills && bundle add rails --version 7.1.3
```
