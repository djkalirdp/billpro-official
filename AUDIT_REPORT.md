# BillPro – Initial Commercial Readiness Audit

**Audit date:** 15 November 2026  
**Scope:** Uploaded `BillPro_all_files.zip` (87 archive entries), source review, Python syntax compilation, route/access review, requirements review, and SQLite sample database integrity check.

## Executive summary

BillPro is a substantial Flask + SQLite billing/inventory application, not a starter project. The archive contains the main Flask application, database layer, two invoice PDF generators, GST/stock/outstanding report generation, desktop templates, dedicated mobile templates, installer scripts, a developer guide, and a populated sample database.

The project is **not yet ready to be called production/commercial-ready**. The main blockers are application security, incomplete dependency declarations, inconsistent authorization relative to the documented cashier role, lack of automated tests, and inability to run an end-to-end smoke test in this environment because Flask/Werkzeug are not installed and package installation was blocked by unavailable network access.

## Verified findings

- Archive contained 87 entries and was extracted successfully.
- `python -m compileall -q .` completed successfully for the Python source files.
- `app.py` declares 88 Flask routes.
- The sample SQLite database passed `PRAGMA integrity_check` (`ok`).
- The sample database contained 14 application tables and populated records (including 8 invoices, 15 products, 8 buyers, 5 vendors, and 6 purchases).
- `PRAGMA foreign_key_check` reported no violations in the supplied sample database.
- No dedicated automated test suite was found in the archive.

## Findings requiring attention

### Critical – security before commercial deployment

1. **Known fallback Flask secret key.** `app.py` falls back to the literal `billing-app-secret-2025-change-this`. A deployed instance that does not set `SECRET_KEY` is exposed to session-signing risks. Require a unique strong secret from the environment for production.
2. **Debug mode enabled in launcher.** The `__main__` block calls `app.run(debug=True, host='0.0.0.0', ...)`. Debug mode must not be used for a commercial deployment. Bind locally by default for a local desktop-style install, and use a production WSGI server for network deployments.
3. **No CSRF protection found.** The app has many state-changing POST forms but no CSRF token implementation or token references found in templates. Add CSRF protection to every state-changing form and API mutation before internet/LAN exposure.
4. **Exception details are returned to clients.** The global exception handler currently includes the exception text in the HTTP response. Return a generic error page and retain full details only in server logs.
5. **Default admin credentials are documented and created automatically.** A fresh database receives `admin / admin123`; the README also publishes these credentials. Force a password change or require administrator setup during first run.

### High – authorization and data safety

6. **Cashier permissions appear broader than documented.** The README says Cashier has Billing + Buyers + Invoice view only. However, multiple buyer/payment actions, vendor ledger/payment actions, reports, batch pages, credit/debit notes, and proforma routes are protected only by `login_required`, not `admin_required`. Confirm the intended permission matrix and enforce it consistently.
7. **Logout uses GET.** `/logout` mutates session state using GET. Convert it to POST and protect it with CSRF.
8. **SQLite path depends on current working directory.** `database_manager.py` uses relative `data/billing_app.db` and `backups`. Starting the program from another working directory can create/use a different database and backup folder. Resolve paths relative to the application directory.
9. **Sample database naming/location is inconsistent.** The supplied archive contains `sample_billing.db` at its root, while `create_sample_db.py` writes `data/sample_billing.db`; the application opens `data/billing_app.db`. The intended sample-data import/restore workflow is not explicit.
10. **Migration errors are silently swallowed.** The schema migration loop catches broad exceptions and ignores them as “already exists”. This can hide genuine migration failures and leave an incomplete schema. Ignore only the expected duplicate-column/table cases and log all other failures.
11. **Financial workflows need transactional tests.** Invoice save/cancel, purchase edit, credit/debit notes, stock movement, batch tracking, and ledger updates span multiple records. These need rollback/consistency tests, especially for repeated edits/cancellations and partial payments.

### Medium – build, installation, and product quality

12. **`requirements.txt` is incomplete.** `reports_generator.py` imports `openpyxl`, but it was not declared. The requirements file was updated in this audit to include `openpyxl` and `Pillow` alongside Flask, Werkzeug, ReportLab, and num2words.
13. **Runtime smoke test could not be completed.** Flask and Werkzeug are absent in the audit environment. Installing them was attempted, but package index access failed due unavailable network/DNS. The application has therefore not been confirmed to start or render routes in this environment.
14. **No repeatable test suite.** Add unit tests for GST calculations, totals/rounding, ledger balances, stock movement, and migration behavior, plus Flask test-client tests for login/roles and critical routes.
15. **Installer behavior needs a reproducible clean-machine test.** Linux installer downloads source from GitHub and has separate dependency logic; Windows installer also uses its own install sequence. Test both from clean Windows/Linux environments and verify the actual archive/release version installed.

## Role review – likely mismatches to validate

Routes below are currently protected by `login_required` even though the README documents a restricted Cashier role. This list is a review queue, not an assertion that every route must be admin-only:

- Buyer profile/payment operations: `/buyers/add`, `/buyers/<id>/edit`, `/buyers/<id>/payment`, `/buyers/<id>/add-sale`, `/payments/<id>/edit-sale`, and buyer ledger pages.
- Vendor ledger/payment: `/vendors/<id>/ledger`, `/vendors/<id>/ledger/pdf`, `/vendors/<id>/payment`.
- Reports and batch information: `/reports`, `/reports/stock`, GST reports, customer/vendor outstanding reports, `/batches`, `/batches/history`.
- Credit/debit notes and proforma/quotation creation, viewing, and PDF routes.

## Changes made in this audit pass

- Updated `requirements.txt` to declare `openpyxl` and `Pillow`, which are needed by report/export and PDF/logo functionality, respectively.
- No business logic, financial calculation, or database schema code was changed during this initial audit, because the application could not be executed end-to-end here and changing those paths without regression tests would be unsafe.

## Recommended implementation sequence

### Phase 1 – Secure the foundation

- Remove the known secret-key fallback for production and document environment configuration.
- Disable debug mode by default; use a production WSGI server for deployments beyond local-only use.
- Add CSRF protection and convert logout to POST.
- Replace client-visible exception details with generic error pages.
- Add first-run admin setup/password-change enforcement and login rate limiting.
- Define and enforce a role/permission matrix.

### Phase 2 – Establish test coverage

- Build a temporary-database test harness.
- Test GST intra-state/inter-state calculations and invoice rounding.
- Test stock in/out/restore across invoice, cancellation, purchase, returns, variations, and batches.
- Test buyer/vendor balances, partial payments, edits, and deletions.
- Test migration from each supported database version and validate backups/restores.

### Phase 3 – Commercial workflows

- Add stock adjustment with reason, user, timestamp, and immutable movement history.
- Add invoice duplication with new invoice number/date and explicit stock/payment behavior.
- Add expense tracking and reports.
- Add controlled PDF sharing (WhatsApp/share link) without exposing local filesystem paths.
- Add robust backup/restore, export, and data portability tools.

### Phase 4 – Release readiness

- Test desktop/mobile templates at common screen sizes.
- Add structured logging, health checks, database backup retention, and recovery documentation.
- Validate GST report outputs against representative accountant-reviewed fixtures; do not claim legal/tax compliance solely from code inspection.
- Produce signed/versioned releases, installation instructions, upgrade/migration notes, and a support/backup policy.

## Audit limitation

This is a source and sample-database audit, not a full QA certification. The app was not launched because required runtime packages were missing and external package installation was unavailable. Financial correctness, template rendering, PDF output, installer success, and actual browser behavior remain unverified until an executable test environment is available.

## Auto-billing fixes applied (2026-11-15)

The three auto-billing defects reported by the user have been corrected in `app.py` and `database_manager.py`:

1. **Place-of-supply GST split:** auto-billing now compares the buyer state with the configured company state. Inter-state invoices carry IGST only; intra-state invoices carry CGST + SGST. Missing buyer state falls back to the company state.
2. **Cap reconciliation:** per-bill and overall caps trim whole units/items and recalculate each surviving line's taxable amount and GST. `invoice_items.amount` now contains the taxable value (the same convention as regular billing), and header taxable/GST totals are rebuilt from the final lines. Rounded invoice totals are kept within the configured total cap.
3. **Non-negative stock:** bulk auto-billing validates stock and uses a guarded `UPDATE ... WHERE stock_qty >= quantity`. Each invoice is wrapped in a SQLite savepoint; an insufficient-stock or insert error rolls back that entire invoice, including its payment and stock changes, while other invoices can still be processed.

### Targeted verification

- Python compilation of the modified `app.py` and `database_manager.py`: passed.
- Executed the actual auto-billing route function in an isolated harness with fixed random inputs: inter-state IGST test passed; intra-state CGST/SGST test passed; a 5-unit line trimmed to 2 units under a ₹250 gross cap produced taxable ₹200, GST ₹36, and invoice total ₹236 in both cases.
- Executed `bulk_create_invoices()` against a temporary copy of the sample database: an invoice requesting 501 units when stock was 500 was rejected with no invoice row and no stock change; a valid 1-unit invoice saved and reduced stock from 500 to 499.

The full Flask app still has not been launched in this environment because Flask/Werkzeug and `num2words` are not installed here and package-index access was unavailable during the earlier audit. The user's live database was not modified; all database verification used a temporary copy.


## Feature update (November 2026)

Implemented in this project update:
- Stock adjustment workflow for products and variations, with transaction-safe quantity updates and an audit history (including zero-stock physical counts).
- Expense register with categories, payment mode, date filtering and period total.
- Invoice duplication as a new unpaid invoice with a fresh number/date, recomputed totals and a new stock deduction.
- WhatsApp click-to-chat with invoice details prefilled. The operator must attach the downloaded PDF and press Send; no automatic document upload or message sending is claimed.
- ZIP backup containing a SQLite online-backup snapshot and company settings; restore validates the database, preserves a pre-restore safety snapshot, clears stale WAL sidecars and then swaps the database.
- Added regression tests in `tests/test_new_features.py`.

Validation performed in the available environment:
- Python compilation: passed.
- Jinja template parsing: all 72 templates passed.
- Flask route AST check: 96 routes, no duplicate route paths.
- New-feature database tests (5): stock adjustment/add/remove/set-zero and negative guard; variation stock adjustment; expense insert/date filter; invoice stock deduction and rollback on insufficient stock; invoice numbering after cancellation — passed.
- Backup/restore route test with lightweight Flask/Werkzeug stubs: ZIP creation, integrity validation, pre-restore snapshot and restore — passed.
- Invoice duplicate and WhatsApp URL tests with lightweight framework stubs — passed.

Limitations: this environment does not have Flask, Werkzeug or num2words installed and package-index access is unavailable. Therefore the full server was not launched and browser/device testing was not performed. WhatsApp sharing opens a prefilled chat only; PDF attachment and sending remain a manual action. Expense entries are an internal register and are not currently included in statutory GST/ITC reports.
