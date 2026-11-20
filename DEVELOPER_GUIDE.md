# BillPro — Developer Guide

## Project Overview
GST-compliant billing + inventory desktop/mobile app.
**Stack:** Python Flask + SQLite · ReportLab PDFs · openpyxl Excel · Bootstrap 5

---

## File Structure

```
billing-app/
├── app.py                  # All Flask routes (~3500+ lines)
├── database_manager.py     # All SQLite functions + schema migrations
├── pdf_generator.py        # Invoice PDF Preview 1 (3 copies)
├── pdf_generator_v2.py     # Invoice PDF Preview 2 (11 fixed rows)
├── reports_generator.py    # GSTR/Stock/Outstanding/CN/DN PDF+Excel
├── settings.json           # Company info, bank, UPI, invoice settings
├── billing.db              # SQLite DB (auto-created on first run)
├── install.sh              # Linux/Mac/Termux installer
├── install.bat             # Windows installer
├── start.sh / start.bat    # App launchers
├── logs/
│   ├── activity.log        # All user actions (RotatingFileHandler 5MB×5)
│   └── error.log           # Errors only
├── invoices/               # Auto-saved A4 invoice PDFs
├── static/uploads/         # Logo uploads
└── templates/
    ├── *.html              # Desktop templates (Bootstrap 5)
    └── mobile/             # Mobile templates (custom CSS)
```

---

## Database Schema

### Key Tables

| Table | Key Columns |
|---|---|
| `buyers` | id, name, gstin, state, opening_balance, credit_limit, **auto_billing** |
| `vendors` | id, name, gstin, state, phone, email |
| `products` | id, name, hsn, gst_rate, rate, selling_price, stock_qty, **reorder_level** |
| `product_variations` | id, product_id, variation_name, selling_price, stock_qty, rate |
| `invoices` | id, invoice_no, buyer_id, invoice_date, payment_mode, taxable_value, total_gst, total_cgst, total_sgst, total_igst, grand_total, paid_amount, round_off |
| `invoice_items` | id, invoice_id, product_id, description, hsn, gst_rate, quantity, rate, discount_percent, amount, variation_id, batch_no |
| `customer_payments` | id, buyer_id, payment_date, amount, payment_mode, notes |
| `purchases` | id, vendor_id, bill_no, purchase_date, total_amount, reverse_charge |
| `purchase_items` | id, purchase_id, product_id, hsn, gst_rate, quantity, rate, total_amount, cgst_amount, sgst_amount, igst_amount |
| `vendor_payments` | id, vendor_id, payment_date, amount, payment_mode, notes |
| `credit_notes` | id, cn_no, cn_date, buyer_id, invoice_id, reason, stock_return, grand_total |
| `credit_note_items` | id, cn_id, product_id, hsn, gst_rate, quantity, rate, amount |
| `debit_notes` | id, dn_no, dn_date, vendor_id, purchase_id, reason, stock_return, grand_total |
| `debit_note_items` | id, dn_id, product_id, hsn, gst_rate, quantity, rate, amount |
| `batch_tracking` | id, product_id, batch_no, invoice_id, invoice_item_id, buyer_id, qty_in, qty_out |

### Important Notes
- `customer_payments` with `payment_mode='Manual Sale'` and **negative amount** = kaccha sale debit entry
- `buyers.auto_billing = 1` = buyer is eligible for auto billing generator
- `invoice_items` does NOT have `taxable_value`, `cgst_amount`, `sgst_amount`, `igst_amount` columns
- `invoices` has `subtotal` + `total_discount` + `taxable_value` (all separate)

---

## Key Routes

### Billing
| Route | Method | Description |
|---|---|---|
| `/billing` | GET/POST | Create new invoice |
| `/invoices` | GET | Invoice list |
| `/invoices/<id>` | GET | Invoice detail |
| `/invoices/<id>/cancel` | POST | Cancel + restore stock |
| `/invoices/<id>/pdf` | GET | Download PDF (`?size=A4/A4L/A5/A5L`) |

### Buyers
| Route | Method | Description |
|---|---|---|
| `/buyers` | GET | Buyer list |
| `/buyers/add` | GET/POST | Add buyer (`auto_billing` field saved) |
| `/buyers/<id>/edit` | GET/POST | Edit buyer |
| `/buyers/<id>/ledger` | GET | Buyer ledger |
| `/buyers/<id>/add-payment` | POST | Record payment |
| `/buyers/<id>/add-sale` | POST | Add manual/kaccha sale |
| `/payments/<id>/edit` | POST | Edit payment |
| `/payments/<id>/edit-sale` | POST | Edit manual sale entry |
| `/payments/<id>/delete` | POST | Delete payment/entry |

### Reports
| Route | Method | Description |
|---|---|---|
| `/reports/gstr1` | GET | `?start&end&format&sales_hsn` |
| `/reports/gstr3b` | GET | `?start&end&format&sales_hsn&purchase_hsn` |
| `/reports/gstr2b` | GET | Purchase register |
| `/reports/stock` | GET | Stock report |
| `/reports/customer-outstanding` | GET | `?start&end&only_due&format&size` |
| `/reports/vendor-outstanding` | GET | `?start&end&only_due&format&size` |

### Auto Billing
| Route | Method | Description |
|---|---|---|
| `/auto-billing` | GET | Form (shows last invoice date as min) |
| `/auto-billing` | POST `dry_run=1` | Preview — stores in session |
| `/auto-billing` | POST `confirm_save=1` | Confirm — saves session data to DB |
| `/buyers/<id>/toggle-auto-billing` | POST | Toggle auto_billing flag |

### API
| Route | Returns |
|---|---|
| `/api/buyer-invoices?buyer_id=` | Buyer's non-cancelled invoices |
| `/api/invoice-items/<id>` | Invoice line items |
| `/api/vendor-purchases?vendor_id=` | Vendor's purchases |
| `/api/purchase-items/<id>` | Purchase line items |
| `/api/hsn-list?start&end` | `{sales:[{hsn,product,gst_rate}], purchases:[...]}` |

---

## Auto Billing Logic

### How it works
1. User enables `auto_billing = 1` on buyer(s) via Buyer Edit form
2. Opens `/auto-billing` — selects products, date range, constraints
3. **Date restriction:** Start date must be ≥ last invoice date (enforced via `min` attr + JS validation)
4. System generates random invoices:
   - Per day: random `min_per_day` to `max_per_day` bills
   - Per bill: random `min_items` to `max_items` products
   - Random buyer from auto_billing-enabled buyers
   - Random qty 1–5 per item
   - Trimmed if > `max_per_bill`
   - Stopped when total ≥ `total_cap`
5. Invoices sorted by date before number assignment → **sequential numbers = chronological order**
6. Dry run → sorted list stored in `session['auto_billing_preview']`
7. Confirm → numbers assigned, `bulk_create_invoices()` called

### bulk_create_invoices columns used
```python
# invoices table:
invoice_no, buyer_id, invoice_date, payment_mode,
subtotal, total_discount, taxable_value,
total_gst, total_cgst, total_sgst, total_igst,
freight, round_off, grand_total, paid_amount,
order_ref, dispatch_info

# invoice_items table (NO taxable_value/cgst/sgst columns):
invoice_id, product_id, description, hsn,
gst_rate, quantity, rate, discount_percent, amount,
variation_id, batch_no
```

---

## PDF System

| File | Sizes | Notes |
|---|---|---|
| `pdf_generator.py` | A4/A4L/A5/A5L | Preview 1 — 3 copies, dynamic rows |
| `pdf_generator_v2.py` | A4/A4L/A5/A5L | Preview 2 — 11 fixed rows, centered header |
| `reports_generator.py` | A4/A4L/A5/A5L | GSTR, Stock, Outstanding, CN/DN PDFs |

Column widths auto-scale: `scale = usable_width / sum(raw_widths)`

A5 portrait: `ROWS_PER_PAGE = 8`, full invoice in `KeepTogether`
A5 landscape: `ROWS_PER_PAGE = 9`, full invoice in `KeepTogether`

---

## PDF Layout Rule (pdf_generator.py + pdf_generator_v2.py)

Every table on an invoice page must have the **same total width**, otherwise edges stick out (asymmetry).

| Constant | Meaning |
|---|---|
| `CW_CM` | `19.0 * W_SCALE` cm — total width of EVERY table (head, items, footer, HSN, terms) |
| `HALF_CM` | `CW_CM / 2` — shared vertical divider for head / footer / terms boxes |
| `_inset` | space between page frame and tables; used by loose text (copy label, "Total Tax in words") |

- Items-table columns are **auto-fitted to content** (`stringWidth`); Description takes the leftover. Sum is always `CW_PT`.
- Money cells use a non-breaking space (`Rs.\u00a02210.00`) so the symbol never wraps away from the number.
- Huge numbers: item font shrinks (down to 65%) instead of wrapping.
- Nested tables inside a cell: give the outer cell `LEFTPADDING/RIGHTPADDING = 0`, else the inner table overflows the border by 12pt.
- Use `CURRENCY_SYM`, never a hard-coded rupee sign (shows as a black box when DejaVu font is missing, e.g. Termux).
- Known limit: A5 Landscape (Preview 1) and A4L/A5L (Preview 2) still run each copy onto 2 pages.

## Logging
```python
log_activity('ACTION_NAME', 'detail string')  # → activity.log
log_error('ACTION_NAME', str(exception))       # → error.log
```
Both use `session.get('username', 'system')` for user tracking.

---

## Common Patterns

### mrender() — auto mobile/desktop routing
```python
return mrender('template.html', **context)
# Detects User-Agent → renders mobile/ or desktop version
```

### DB helper functions
```python
db.get_all('buyers')                    # All rows
db.get_by_id('buyers', id)             # Single row
db.add_record('buyers', data_dict)     # Insert
db.update_record('buyers', id, data)   # Update
db.delete_record('buyers', id)         # Delete
db.execute_query(sql, params, fetchall=True)  # Raw query
```

---

## GST Calculation Rules
- Same state (buyer.state == company.state) → CGST + SGST (half each)
- Different state → IGST (full rate)
- `tax = taxable_value * gst_rate / 100`
- CGST = SGST = tax / 2

## GSTR HSN Filter
- `sales_hsn` param → comma-separated HSN codes → filter `invoice_items.hsn`
- `purchase_hsn` param → filter `purchase_items.hsn` for ITC calculation
- Empty = include all (no filter)

---

## V1.3 Roadmap
- Stock Adjustment module
- Invoice Duplicate (clone)
- WhatsApp Share PDF
- Expense Tracker
