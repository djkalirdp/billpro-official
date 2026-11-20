# 🧾 Professional Billing & Inventory Software

GST-compliant billing and inventory management system built with **Python Flask + SQLite**. Runs entirely on your local machine — no internet subscription, no cloud.

---

## 📋 Table of Contents

1. [Features Overview](#-features-overview)
2. [Installation](#-installation)
3. [Login & User Roles](#-login--user-roles)
4. [Dashboard](#-dashboard)
5. [Billing / Create Invoice](#-billing--create-invoice)
6. [Invoice Management](#-invoice-management)
7. [Products & Inventory](#-products--inventory)
8. [Product Variations](#-product-variations-sizecolor)
9. [Product Rate List](#-product-rate-list)
10. [Buyers (Customers)](#-buyers-customers)
11. [Buyer Ledger / Khata](#-buyer-ledger--khata)
12. [Vendors (Suppliers)](#-vendors-suppliers)
13. [Vendor Ledger](#-vendor-ledger)
14. [Purchases](#-purchases)
15. [Credit Notes](#-credit-notes)
16. [Debit Notes](#-debit-notes)
17. [Sales Quotations / Proforma](#-sales-quotations--proforma-invoice)
18. [Batch / Expiry Tracking](#-batch--expiry-tracking)
19. [GST Reports](#-gst-reports)
20. [Outstanding Reports](#-outstanding-reports)
21. [PDF Page Sizes](#-pdf-page-sizes)
22. [Settings](#-settings)
23. [Activity & Error Logs](#-activity--error-logs)
24. [Mobile Interface](#-mobile-interface)
25. [Android (Termux)](#-android-termux)
26. [Sample Database](#-sample-database)
27. [Database & File Structure](#-database--file-structure)
28. [Tech Stack](#-tech-stack)
29. [Important Notes](#-important-notes)
30. [Changelog](#-changelog)
31. [Stock Adjustments](#-stock-adjustments)
32. [Expense Management](#-expense-management)
33. [Duplicate & WhatsApp Invoices](#-duplicate--whatsapp-invoices)
34. [Backup & Restore](#-backup--restore)

---

## ✨ Features Overview

| Category | Features |
|---|---|
| 🧾 **Billing** | GST invoices, Retail & Wholesale, UPI/Cash/Credit/Cheque/Bank Transfer |
| 📋 **Quotations** | Sales Quotation (Proforma Invoice), 1-click convert to Tax Invoice |
| 📦 **Inventory** | Auto stock deduction on sale, stock adjustments with audit history, per-product reorder level, variations |
| 🏷️ **Rate List** | Full price list — HSN, GST%, cost, selling, MRP, stock — with live search |
| 👥 **Buyers** | Customer profiles, credit limit, outstanding balance, opening balance |
| 📒 **Buyer Ledger** | Running balance ledger with edit/delete payment entries |
| 🏭 **Vendors** | Supplier profiles, vendor ledger with running balance |
| 🛒 **Purchases** | Full-page purchase form, Resale vs Raw Material, edit bills |
| 🔄 **Credit Notes** | Sale return / price correction — invoice auto-load, stock return option |
| 🔄 **Debit Notes** | Purchase return — purchase auto-load, stock return option |
| 📦 **Batches** | Batch no. + expiry tracking from purchase to sale |
| 📊 **GST Reports** | GSTR-1, GSTR-2B, GSTR-3B with ITC cross-utilization — PDF + Excel |
| 💰 **Outstanding** | Customer receivable + Vendor payable reports — PDF + Excel |
| 💸 **Expenses** | Expense register with categories, payment mode, date filtering and totals |
| 📲 **Invoice Sharing** | Duplicate invoices and open buyer WhatsApp with invoice details pre-filled |
| 🗄️ **Backup** | Consistent database + settings ZIP backup, validation and restore safety copy |
| 📄 **PDF Sizes** | A4 / A4 Landscape / A5 / A5 Landscape for all PDFs |
| 🖨️ **PDF Templates** | Preview 1 (3 copies) · Preview 2 (11 fixed rows, centered header) |
| 🖼️ **Logo** | Company logo on PDF invoices — 2.5cm × 2cm |
| 👤 **Users** | Admin + Cashier roles, change password for all accounts |
| 📱 **Mobile** | Dedicated mobile UI, bottom navigation, touch autocomplete |
| 🤖 **Android** | Runs on Android via Termux — single install command |
| 📝 **Logs** | Activity log + Error log — auto-rotating, per-user tracking |
| 🗃️ **Sample Data** | Ready-made sample database for testing all features |

---

## 🚀 Installation

### Windows (One-Command — Recommended)

1. Download `install.bat` from the repository
2. **Double-click** `install.bat`
3. Script automatically:
   - Checks Python (shows install guide if missing)
   - Downloads entire repo as ZIP from GitHub
   - Creates Python virtual environment
   - Installs all packages (Flask, ReportLab, openpyxl, num2words, qrcode, Pillow)
   - Downloads DejaVu fonts for ₹ symbol in PDFs
   - Creates `start.bat` launcher

**After install — every time:**
```
Double-click  start.bat
```
Then open browser: `http://localhost:5000`

---

### Linux / macOS (One-Command)

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/djkalirdp/billing/main/install.sh)
```

**After install:**
```bash
bash start.sh
```

---

### Android — Termux (One-Command)

```bash
curl -fsSL https://raw.githubusercontent.com/djkalirdp/billing/main/install.sh -o install.sh && bash install.sh
```

**After install:**
```bash
bash start.sh
```

Open Chrome/Firefox → `http://localhost:5000`

> See [Android (Termux)](#-android-termux) section for details.

---

### Manual Install (any OS)

```bash
git clone https://github.com/djkalirdp/billing.git billing-app
cd billing-app
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

---

### Requirements

| Requirement | Version |
|---|---|
| Python | 3.8 or newer |
| Internet | Only needed during install |
| Browser | Any modern browser |
| OS | Windows 10/11, Linux, macOS, Android (Termux) |

---

## 🔐 Login & User Roles

**Default login:**

| Field | Value |
|---|---|
| Username | `admin` |
| Password | `admin123` |

> ⚠️ **Change password immediately** → Settings → Users → Change Password

### Roles

| Role | Access |
|---|---|
| **Admin** | Everything — billing, inventory, reports, settings, users |
| **Cashier** | Billing + Buyers + Invoice view only |

### User Management
- **Add User** — Settings → Users → Add User form
- **Change Password** — blue key button next to every user (including admin)
- **Delete User** — only non-admin accounts

---

## 📊 Dashboard

| Card | Description |
|---|---|
| **Today's Sales** | Total invoices today |
| **Total Receivable** | All outstanding dues from buyers |
| **Estimated Profit** | (Invoice Rate − Variation Cost) × Qty |
| **Low Stock Items** | Products below their reorder level |

Weekly / Monthly / Yearly sales chart (Chart.js).

---

## 🧾 Billing / Create Invoice

### Steps
1. Select Buyer — previous balance auto-loaded; credit limit warning if exceeded
2. Add Items — autocomplete fills HSN, GST%, rate, unit
3. Variations — dropdown shows size/color options per product
4. GST auto-detected: Same state → **CGST + SGST** · Different state → **IGST**
5. Per-item discount percentage
6. Payment mode — Cash / UPI / Credit / Cheque / Bank Transfer
7. Freight charge (optional)
8. Paid Amount — partial payment supported

### After Saving
- Stock deducted automatically per item/variation
- Invoice PDF auto-saved to `invoices/` (A4)
- If buyer credit limit exceeded → warning flash shown (invoice still saves)

---

## 📋 Invoice Management

| Feature | Details |
|---|---|
| Search | By invoice number, buyer name |
| Date Filter | Custom date range |
| PDF Download | A4 / A4L / A5 / A5L — size picker on detail page |
| Template | Preview 1 (3 copies) or Preview 2 (11 rows) — set in Settings |
| Cancel Invoice | Marks `[CANCELLED]`, restores stock (Admin only) |
| Duplicate Invoice | Creates a fresh invoice number and date, resets paid amount to zero, and deducts stock again |
| WhatsApp | Opens the buyer chat with invoice details pre-filled; download the PDF and attach it in WhatsApp |
| 3 Copies | Original / Duplicate / Triplicate on single PDF (Preview 1) |

---

## 📦 Products & Inventory

| Field | Description |
|---|---|
| Name | Unique product name |
| HSN Code | For GST filing |
| GST Rate | 0 / 5 / 12 / 18 / 28 % |
| Purchase Rate | Cost price — used for profit calculation |
| Selling Price | Default retail price |
| Wholesale Price | For wholesale buyers |
| Stock Qty | Current inventory |
| Unit | Pcs / Kg / Litre / Box / etc. |
| **Reorder Level** | **Per-product low stock threshold (default: 5)** |

> **Reorder Level** — each product has its own threshold. Dashboard and Products page show alert when stock ≤ reorder level.

---

## 📦 Stock Adjustments

Open **Inventory → Stock Adjustment** (Admin only). Choose a product and:
- **Add stock** for inward corrections or extra stock.
- **Remove stock** for damage, loss or correction; the app blocks a negative balance.
- **Set exact stock** after a physical count (including setting stock to zero).

Every adjustment stores the previous and new balance, quantity, date/time, reason and user in the stock-adjustment history. This is separate from purchase entries, so use purchases for supplier bills and adjustments for corrections.

## 💸 Expense Management

Open **Inventory → Expenses** (Admin only) to record operating expenses such as rent, electricity, salary, transport and repairs. Each entry stores date, category, description, amount, payment mode, optional reference and notes. Filter the register by date range and review the period total. Expenses are recorded separately from purchase bills and are not automatically included in GST ITC or statutory returns.

## 📲 Duplicate & WhatsApp Invoices

On an invoice detail page:
- **Duplicate Invoice** creates a new invoice number dated today, copies the buyer and line items, recalculates GST totals, resets paid amount to zero and performs a fresh stock deduction. It will fail if current stock is insufficient.
- **Share on WhatsApp** opens WhatsApp for the buyer's saved mobile number with invoice number, date and total pre-filled. Download the PDF first, then attach it in the WhatsApp chat and send it yourself. BillPro does not send messages or upload documents automatically.

## 🗄️ Backup & Restore

Open **Admin → Backup & Restore**:
- **Create & download backup** produces a ZIP with a consistent SQLite database snapshot and `settings.json`.
- The page lists local backup files for download.
- **Restore** accepts a BillPro backup ZIP or SQLite `.db` file. It checks database integrity and expected BillPro tables before replacing the active database, and saves a pre-restore database snapshot first. A restored database may have different user accounts, so sign in with the credentials stored in that backup.

Keep a copy of backups outside the computer or phone running BillPro. Restore replaces current records; always verify the selected backup before proceeding.

## 🎨 Product Variations (Size/Color)

Each product can have unlimited variations.

| Field | Description |
|---|---|
| Variation Name | 100ml / 200ml / Large / Red etc. |
| Cost Rate | **Own purchase cost** — correct profit per size |
| Selling Price | Variation-specific retail |
| Wholesale Price | Variation-specific wholesale |
| Stock | Variation-specific stock |

---

## 🏷️ Product Rate List

`Products → Rate List`

- All products + variations in one table
- Columns: HSN, GST%, Cost, Selling, Wholesale, Stock, Unit
- Live search filter
- Mobile: card-style view with low stock badge

---

## 👥 Buyers (Customers)

| Field | Description |
|---|---|
| Name | Unique customer name |
| GSTIN | GST number (optional) |
| Address, Phone, Email | Contact info |
| State | Controls IGST vs CGST/SGST |
| Opening Balance | Previous outstanding before software start |
| **Credit Limit** | **Max outstanding allowed — warning on billing if exceeded** |

### Credit Limit
- Set per buyer in Buyer Add/Edit form
- `0` = no limit
- Buyers list shows 🔴 **Limit Full** or 🟡 **Near Limit** badges
- Billing shows warning flash when invoice would exceed limit

---

## 📒 Buyer Ledger / Khata

`Buyers → View Ledger`

| Feature | Details |
|---|---|
| Running Balance | Date-wise debit/credit with closing balance |
| Invoice Entries | Auto-posted as debit |
| Payment Entry | Cash / UPI / Cheque / Bank Transfer |
| Edit Payment | Change amount, date, mode, notes |
| Delete Payment | Remove incorrect entries |
| PDF Download | A4 / A4L / A5 / A5L |
| Credit Note | Automatically reduces buyer balance when CN is saved |

---

## 🏭 Vendors (Suppliers)

- Supplier profiles with GSTIN, address, phone, email
- Vendors list shows **outstanding payable balance** per vendor
- **Ledger** button on vendors list → opens Vendor Ledger

---

## 📒 Vendor Ledger

`Vendors → Ledger`

| Feature | Details |
|---|---|
| Running Balance | Purchases (debit) − Payments (credit) |
| Payment Sources | Both `purchase_payments` + standalone `vendor_payments` |
| Make Payment | Record payment to vendor from ledger page |
| Edit/Delete | Modify payment entries |
| PDF Download | A4 / A4L / A5 / A5L |
| Debit Note | Automatically reduces vendor payable when DN is saved |

---

## 🛒 Purchases

- Full purchase form with GST breakdown
- Purchase Type: **Resale** (adds to stock) or **Raw Material** (no stock change)
- Edit existing purchase bills
- Payment tracking — partial payment supported
- All purchase payments appear in Vendor Ledger automatically

---

## 🔄 Credit Notes

`More → Credit Notes`

Used for: sale return, price correction, excess billing.

### Smart Loading
1. Select **Buyer** → only that buyer's invoices load in dropdown
2. Select **Invoice** → all invoice items auto-populate
3. You can only **delete** items — cannot add new ones
4. Only items from the selected invoice appear

### Stock Return Option
| Option | Effect |
|---|---|
| **Yes** | Product stock restored (goods physically returned) |
| **No** | Only financial adjustment — buyer balance reduced, stock unchanged |

### Effect on Ledger
- Buyer's outstanding balance automatically reduced
- Entry appears in Buyer Ledger as "Credit Note"

### PDF
- Download from CN detail page — A4 / A4L / A5 / A5L

---

## 🔄 Debit Notes

`More → Debit Notes`

Used for: purchase return, vendor overcharge, quality rejection.

### Smart Loading
1. Select **Vendor** → only that vendor's purchases load in dropdown
2. Select **Purchase** → all purchase items auto-populate
3. You can only **delete** items — cannot add new ones

### Stock Return Option
| Option | Effect |
|---|---|
| **Yes** | Product stock reduced (goods sent back to vendor) |
| **No** | Only financial adjustment — vendor payable reduced, stock unchanged |

### Effect on Ledger
- Vendor's payable balance automatically reduced
- Entry appears in Vendor Ledger as "Debit Note"

### PDF
- Download from DN detail page — A4 / A4L / A5 / A5L

---

## 📋 Sales Quotations / Proforma Invoice

`More → Quotations`

- Create quotation with full item details
- Statuses: Draft / Sent / Approved / Converted
- **1-click convert** to Tax Invoice
- PDF download (same invoice format)
- Quotations do NOT deduct stock or create GST liability — only conversion does

---

## 📦 Batch / Expiry Tracking

`More → Batch Tracker`

- Enter Batch No. + Expiry on Purchase Bill
- Select batch when billing (optional)
- Track: purchased from whom → sold to whom
- Expiry Alert: orange banner for batches expiring within 30 days

---

## 📊 GST Reports

`More → Reports` — set date range before generating.

| Report | Contents | Format |
|---|---|---|
| **GSTR-1** | Outward supplies, rate-wise | PDF + Excel |
| **GSTR-2B / Purchase Register** | Inward supplies, vendor GSTIN, RCM | PDF + Excel |
| **GSTR-3B Summary** | Output tax + ITC + Net Payable | PDF + Excel |
| **Stock Report** | Inventory — HSN, cost, selling, value | PDF + Excel |

### Month Shortcuts
All reports have quick month buttons (last 6 months) — tap once to set date range.

### GSTR-3B ITC Cross-Utilization (GST Act compliant)

| ITC | Used Against |
|---|---|
| **IGST ITC** | IGST → CGST → SGST |
| **CGST ITC** | CGST → IGST |
| **SGST ITC** | SGST → IGST |

---

## 💰 Outstanding Reports

`More → Reports → Customer Outstanding / Vendor Outstanding`

### Customer Outstanding (Receivable)
Shows how much each buyer owes.

| Column | Description |
|---|---|
| Customer | Buyer name + phone |
| Opening Balance | Balance before software |
| Total Invoiced | Sum of all invoices in period |
| Total Paid | Sum of all payments in period |
| Outstanding | Net amount due |
| Status | 🔴 Due / ✅ Clear |

### Vendor Outstanding (Payable)
Shows how much you owe each vendor.

| Column | Description |
|---|---|
| Vendor | Vendor name + phone |
| Total Purchases | Sum of all purchase bills in period |
| Total Paid | Purchase payments + vendor payments |
| Payable | Net amount to pay |
| Status | 🔴 Payable / ✅ Clear |

### Filters
- **Date range** — period-wise outstanding
- **Only Due** — hide zero-balance entries
- **Sort** — highest outstanding first

### Export
- PDF: A4 / A4L / A5 / A5L (auto-scaled columns, never overflow)
- Excel: Full data with totals row

---

## 📄 PDF Page Sizes

| Size | Dimensions | Best For |
|---|---|---|
| **A4** | 210 × 297 mm | Default |
| **A4 Landscape** | 297 × 210 mm | Wide tables |
| **A5** | 148 × 210 mm | Compact booklets |
| **A5 Landscape** | 210 × 148 mm | Small horizontal |

Columns auto-scale to fit page — no overflow on any size.

---

## 🖨️ Invoice PDF Templates

### Preview 1 — Standard
- 3 copies: Original / Duplicate / Triplicate
- Dynamic rows — only as many rows as items
- Seller box (left) + Invoice details (right) layout

### Preview 2 — Classic (11 Fixed Rows)
- Single copy
- **Always 11 rows per page** — empty rows shown as blank boxes
- If items > 10: overflow to next page with same header
- Centered company name header — MSP Traders style
- GSTIN top-left, copy label top-right

**Select template:** Settings → Invoice PDF Template

---

## ⚙️ Settings

`More → Settings` (Admin only)

| Section | Fields |
|---|---|
| **Company Info** | Name, Address, Phone, Email, GSTIN, State, Logo |
| **Bank Details** | Bank Name, Account No., IFSC, Branch |
| **UPI** | UPI ID → QR code on all invoice PDFs |
| **Invoice Settings** | Prefix, Terms & Conditions |
| **Invoice Template** | Preview 1 (3 copies) or Preview 2 (11 fixed rows) |
| **Firm Type** | Trading (Retail/Wholesale) or Manufacturing |
| **Users** | Add / Change Password / Delete |

### Firm Type
- **Trading** — current mode, normal billing
- **Manufacturing** — foundation for V2.0 BOM/Production module (coming soon)

**Logo:** Upload PNG/JPG → displays at 2.5cm × 2cm on PDF invoices.

---

## 📝 Activity & Error Logs

All user actions and errors are automatically logged.

**Location:** `billing-app/logs/`

| File | Contents |
|---|---|
| `activity.log` | Login, invoice save, product add, settings change, CN/DN save |
| `error.log` | Report errors, HTTP errors, unhandled exceptions |

**Format:**
```
2026-04-04 09:15:32 | INFO  | USER=admin | ACTION=INVOICE_SAVE | InvoiceNo=HFC-001 Total=12390
2026-04-04 09:20:11 | ERROR | USER=admin | ACTION=REPORT | ERROR=...
```

**Auto-rotating:** 5MB per file × 5 backups = max 50MB total.

---

## 📱 Mobile Interface

Auto-loads on phones/tablets (detects User-Agent).

### Bottom Navigation
| Tab | Pages |
|---|---|
| 🏠 Home | Dashboard |
| 📄 Bills | Invoice list |
| ➕ | New Invoice |
| 👥 Buyers | Buyer list + ledger |
| ⋯ More | Everything else |

### More Menu Includes
- Products, Rate List, Vendors, Vendor Ledger
- Purchases, Quotations
- **Credit Notes, Debit Notes** (new)
- Reports (with Outstanding Reports)
- Settings, Users

---

## 🤖 Android (Termux)

Run full billing software on Android phone — no PC needed.

### Install (one command)
```bash
# In Termux app:
curl -fsSL https://raw.githubusercontent.com/djkalirdp/billing/main/install.sh -o install.sh && bash install.sh
```

Installer automatically:
- Installs Python, git via `pkg`
- Installs system libraries for Pillow (`libjpeg-turbo`, `libpng`, `libwebp`)
- Creates virtual environment
- Installs all Python packages
- Sets up start script

### Start
```bash
bash start.sh
```
Open Android browser → `http://localhost:5000`

### Access from PC (same WiFi)
```
http://<phone-ip>:5000
```
IP shown after install completes.

### Tips
- Keep Termux session running while using browser
- Use Termux: Task for background running
- All features including PDF generation work on Android

---

## 🗃️ Sample Database

`sample_billing.db` — pre-filled demo data for testing.

| Data | Count |
|---|---|
| Users | 2 (admin + cashier) |
| Vendors | 5 |
| Buyers | 8 (local + outstation + opening balances) |
| Products | 15 (FMCG items) |
| Variations | 13 (sizes/packs) |
| Purchases | 6 (with items, payments, batches) |
| Invoices | 7 (local + IGST + cancelled) |
| Payments | 8 (Cash/UPI/Cheque/NEFT) |
| Quotations | 3 (Draft/Sent/Approved) |
| Batch Records | 41 |

### How to Use
1. Download `sample_billing.db`
2. Rename your existing `billing.db` as backup
3. Copy `sample_billing.db` → `billing.db`
4. Restart app

---

## 🗄️ Database & File Structure

```
billing-app/
├── app.py                    # Flask routes
├── database_manager.py       # DB functions + schema
├── pdf_generator.py          # Invoice PDF Preview 1
├── pdf_generator_v2.py       # Invoice PDF Preview 2 (11 rows)
├── reports_generator.py      # GST reports + CN/DN PDF + Outstanding PDF
├── settings.json             # Company settings
├── install.sh                # Linux/Mac/Termux installer
├── install.bat               # Windows installer
├── start.sh / start.bat      # App launchers
├── requirements.txt
├── DejaVuSans.ttf            # Font for ₹ symbol
├── DejaVuSans-Bold.ttf
│
├── logs/
│   ├── activity.log          # All user actions
│   └── error.log             # Errors only
├── invoices/                 # Auto-saved A4 PDFs
├── reports/                  # Downloaded reports
├── static/uploads/           # Logo files
│
└── templates/
    ├── base.html
    ├── dashboard.html
    ├── billing.html
    ├── invoices.html
    ├── invoice_detail.html
    ├── products.html
    ├── product_form.html
    ├── product_rate_list.html
    ├── product_variations.html
    ├── buyers.html
    ├── buyer_form.html
    ├── buyer_ledger.html
    ├── vendors.html
    ├── vendor_form.html
    ├── vendor_ledger.html         ← new
    ├── purchases.html
    ├── purchase_form.html
    ├── credit_notes.html          ← new
    ├── credit_note_form.html      ← new
    ├── credit_note_detail.html    ← new
    ├── debit_notes.html           ← new
    ├── debit_note_form.html       ← new
    ├── debit_note_detail.html     ← new
    ├── proforma_list.html
    ├── proforma_form.html
    ├── proforma_detail.html
    ├── batches.html
    ├── batch_history.html
    ├── reports.html
    ├── settings.html
    ├── users.html
    ├── login.html
    └── mobile/
        └── (all mobile equivalents including CN/DN, vendor ledger, rate list)
```

### Database Tables

| Table | Contents |
|---|---|
| `users` | Login credentials, roles |
| `buyers` | Customer profiles, opening balance, state, **credit_limit** |
| `vendors` | Supplier profiles |
| `products` | Products, HSN, GST, cost, selling, stock, **reorder_level** |
| `product_variations` | Size/color variants — own cost, price, stock |
| `invoices` | Invoice headers — all tax fields, paid amount |
| `invoice_items` | Line items (variation_id, batch_no) |
| `customer_payments` | Payments — editable + deletable |
| `purchases` | Purchase bills — GST, RCM flag |
| `purchase_items` | Line items with batch/expiry, GST columns |
| `purchase_payments` | Payments to vendors |
| `vendor_payments` | Standalone vendor payments |
| `batch_tracking` | IN (purchase) and OUT (sale) movements |
| `proforma_invoices` | Quotation headers |
| `proforma_items` | Quotation line items |
| `credit_notes` | CN header — buyer, invoice, stock_return flag |
| `credit_note_items` | CN line items |
| `debit_notes` | DN header — vendor, purchase, stock_return flag |
| `debit_note_items` | DN line items |

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Backend | Python 3.8+ + Flask 2.3+ |
| Database | SQLite (zero config) |
| PDF | ReportLab 4.0+ |
| Excel | openpyxl 3.1+ |
| Amount in Words | num2words (en_IN) |
| QR Code | qrcode + Pillow |
| Frontend | Bootstrap 5 + Jinja2 |
| Charts | Chart.js 4.4.1 (CDN) |
| Icons | Bootstrap Icons (CDN) |
| Auth | Werkzeug pbkdf2 hashing |
| Logging | Python RotatingFileHandler |

---

## ⚠️ Important Notes

1. **Default password** `admin123` — change immediately via Settings → Users
2. **Company State** — set before invoices; controls IGST vs CGST/SGST
3. **Variation cost** — set each variation's own purchase rate for correct profit
4. **ITC cross-utilization** — IGST credit offsets CGST/SGST per GST Act (automatic)
5. **Quotations** — no stock deduction, no GST liability until converted
6. **Purchase Type** — Resale = stock up; Raw Material = no stock change
7. **Cancel invoice** — restores stock; marks `[CANCELLED]` in invoice number
8. **Credit Note** — buyer select → only their invoices shown → items auto-fill → delete only
9. **Debit Note** — vendor select → only their purchases shown → items auto-fill → delete only
10. **Stock Return (CN/DN)** — choose at creation time; cannot change after save
11. **Credit Limit** — `0` means no limit; warning shown but invoice still saves
12. **Reorder Level** — per product; `0` = no alert; default 5
13. **PDF Preview 2** — 11 rows per page; extra items on next page with same header
14. **Outstanding Report** — uses all-time data if no date range given
15. **Logs** — stored in `logs/` folder; auto-created on first run
16. **Pillow (Android)** — installer handles `libjpeg-turbo` dependency automatically
17. **A5 PDFs** — entire invoice on one page (KeepTogether)
18. **Logo** — 2.5cm × 2cm recommended; 295×236px @ 300dpi
19. **DejaVu fonts** — required for ₹ symbol in PDFs; falls back to `Rs.` if missing
20. **Internet** — needed at startup for Chart.js + Bootstrap Icons CDN
21. **WhatsApp** — BillPro pre-fills the message; download and attach the PDF manually before sending
22. **Expenses** — internal expense register only; not included in GST ITC or statutory returns
23. **Restore** — replacing the database logs you out; sign in with the restored database credentials
24. **Regression tests** — run `python -m unittest discover -s tests -v`

---

## 📌 Changelog

### V1.3 — Current

#### New Features
- ✅ **Stock Adjustment** — main products and variations; stock-in, stock-out, set exact count; audit history and negative-stock protection
- ✅ **Expense Management** — category-based expense register, payment mode, date filters and period totals
- ✅ **Duplicate Invoice** — new invoice number/date, unpaid status, recalculated totals and fresh stock deduction
- ✅ **WhatsApp Invoice Sharing** — buyer click-to-chat with invoice details prefilled; attach downloaded PDF manually
- ✅ **Backup & Restore** — SQLite online-backup snapshot + settings ZIP, database validation, pre-restore safety copy
- ✅ **Invoice numbering** — ignores cancellation suffixes when selecting the next sequential invoice number

### V1.2

#### New Features
- ✅ **Vendor Ledger** — running balance, payments (purchase + standalone), PDF download
- ✅ **Vendor Outstanding balance** — shown on vendors list, fast direct query
- ✅ **Credit Limit per buyer** — warning on billing, Limit Full / Near Limit badge
- ✅ **Custom Reorder Level** — per-product threshold, dashboard + product page alerts
- ✅ **Firm Type Setting** — Trading / Manufacturing toggle in Settings
- ✅ **Credit Notes** — smart invoice loading, stock return option, buyer ledger auto-update, PDF
- ✅ **Debit Notes** — smart purchase loading, stock return option, vendor ledger auto-update, PDF
- ✅ **Customer Outstanding Report** — PDF + Excel, date filter, Only Due toggle, A4/A5 sizes
- ✅ **Vendor Outstanding Report** — PDF + Excel, same filters
- ✅ **Invoice PDF Preview 2** — 11 fixed rows, centered MSP-Traders style header, single copy
- ✅ **Invoice Template selector** — Settings → choose Preview 1 or Preview 2
- ✅ **Activity & Error Logs** — `logs/activity.log` + `logs/error.log`, rotating 5MB × 5
- ✅ **Android (Termux) support** — install.sh updated with libjpeg fix, start.sh mobile-aware
- ✅ **Mobile CN/DN templates** — full mobile UI for Credit Note + Debit Note
- ✅ **Mobile Rate List** — card-style with low stock badge
- ✅ **Mobile Outstanding Reports** — month shortcuts, Only Due toggle, size picker
- ✅ **Mobile Settings** — Invoice template + Firm Type added
- ✅ **Mobile Buyer Form** — Credit Limit field
- ✅ **Mobile Product Form** — Reorder Level field
- ✅ **Mobile Proforma** — full create/list/detail on mobile
- ✅ **PDF column auto-scale** — columns fit any paper size, no overflow

#### Bug Fixes
- ✅ **`batch_tracking` migration** — `buyer_id`, `invoice_item_id` columns added for existing DBs
- ✅ **`purchase_items` migration** — `total_amount`, `cgst_amount` etc. for existing DBs
- ✅ **Vendor ledger** — now includes `purchase_payments` not just `vendor_payments`
- ✅ **reports_generator import alias** — `rg` not `reports_generator` in routes
- ✅ **Jinja2 backslash error** — `vendor_ledger.html` confirm dialog fixed
- ✅ **`users.html` duplicate block** — clean file

### V1.1

#### Bug Fixes
- ✅ **PDF crash** — `NoneType.split()` on NULL fields; all safely coerced to string
- ✅ **Profit calculation** — uses variation's own cost, not parent product cost
- ✅ **GSTR-3B ITC** — IGST credit now offsets CGST/SGST per GST Act
- ✅ **Change Password** — added for all users

#### New Features
- ✅ **Windows installer** (`install.bat`)
- ✅ **Sample database**
- ✅ **Default logo**
- ✅ **User password change**

### Previous Releases (V1.0)
- ✅ Sales Quotations / Proforma → Convert to Invoice
- ✅ PDF Page Sizes — A4 / A4L / A5 / A5L
- ✅ Buyer Ledger — edit/delete payment entries
- ✅ Purchase Type — Resale vs Raw Material
- ✅ GSTR-1, GSTR-2B, GSTR-3B — PDF + Excel with ITC
- ✅ Batch Tracking — purchase to billing, expiry alerts
- ✅ UPI QR Code — on all invoice PDFs
- ✅ Product Variations — own price, cost, stock
- ✅ Rate List — with variations
- ✅ Mobile Interface — dedicated UI for all pages

---

## 🗺️ Roadmap

| Version | Status | Focus |
|---|---|---|
| **V1.1** | ✅ Done | Vendor Ledger, Credit Limit, Reorder Level, CN/DN |
| **V1.2** | ✅ Done | Outstanding Reports, PDF Preview 2, Logging, Android |
| **V1.3** | ✅ Done | Stock Adjustment, Expense Tracker, Invoice Duplicate, WhatsApp Share, Backup & Restore |
| **V1.5** | 📋 Planned | Barcode, Multi-location, Interest on overdue, Audit Trail |
| **V2.0** | 📋 Planned | Manufacturing Module (BOM, Production, WIP, Cost Sheet) |
| **V2.5** | 📋 Planned | Google Drive Cloud Sync |
| **V3.0** | 📋 Planned | E-Invoice (IRN), E-Way Bill, Bank Reconciliation |

---

*Built with Flask + SQLite · Runs locally · No subscription · GST workflows should be verified with your accountant before filing*
