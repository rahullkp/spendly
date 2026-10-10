# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Spendly: a Flask expense-tracker web app built as a step-by-step learning
project. The author is learning web development, so ask before editing files
and explain changes simply.

## Commands

- Run the app: `./venv/bin/python app.py` (dev server, debug on, http://127.0.0.1:5001)
- Install dependencies: `./venv/bin/pip install -r requirements.txt`
- Tests: pytest and pytest-flask are in requirements.txt, but there is no tests/ directory yet.
  Run one test with `./venv/bin/pytest tests/test_x.py::test_name`.
- No linter or build step is configured.

## Architecture

- `app.py` holds all routes. The real pages are `/`, `/register`, `/login`,
  `/terms` and `/privacy`. They only render templates, with no form handling.
- The other routes (`/logout`, `/profile`, `/expenses/add`, `/expenses/<id>/edit`,
  `/expenses/<id>/delete`) are placeholders that return "coming in Step N" strings.
  They are meant to be implemented in order.
- `database/db.py` is a stub with comments only. Step 1 will add `get_db()`
  (SQLite, row_factory, foreign keys on), `init_db()` (CREATE TABLE IF NOT EXISTS)
  and `seed_db()`. Nothing uses a database yet.
- Templates extend `templates/base.html`. It has the navbar and footer and loads
  `static/css/style.css` and `static/js/main.js` through `url_for`. Link between
  pages with `url_for('<function name>')`, not hard-coded paths.
- Fonts (DM Serif Display, DM Sans, Inter) come from Google Fonts in base.html.

## Conventions

- Don't run `git commit` unless asked. The author makes commits themselves.


## Code Style
Python: PEP 8, snake_case for all variables and functions
Templates: Jinja2 with url_for() for every internal link — never hardcode URLs
Route functions: one responsibility only — fetch data, render template, done
DB queries: always use parameterized queries (? placeholders) — never f-strings in SQL
Error handling: use abort() for HTTP errors, not bare return "error string"


## Tech Stack
Flask only — no FastAPI, no Django, no other web frameworks
SQLite only — no PostgreSQL, no SQLAlchemy ORM, no external DB
Vanilla JS only — no React, no jQuery, no npm packages
No new pip packages — work within requirements.txt as-is unless explicitly told otherwise
Python 3.10+ assumed — f-strings and match statements are fine


## Implemented vs stub routes
this part containes the development path

all the routes -> status

## Wrning and things to avoid
Never use raw string returns for stub routes once a step is implemented — always render a template
Never hardcode URLs in templates — always use url_for()
Never put DB logic in route functions — it belongs in database/db.py
Never install new packages mid-feature without flagging it — keep requirements.txt in sync
Never use JS frameworks — the frontend is intentionally vanilla
database/db.py is currently empty — do not assume helpers exist until the step that implements them
FK enforcement is manual — SQLite foreign keys are off by default; get_db() must run PRAGMA foreign_keys = ON on every connection
The app runs on port 5001, not the Flask default 5000 — don't change this