"""
====================================================
  SAMPLE DATABASE GENERATOR
  Billing & Inventory Software
  Run: python create_sample_db.py
====================================================
"""

import sqlite3
import os
import hashlib
from datetime import datetime, timedelta
import random

DB_PATH = "data/sample_billing.db"

# ── Helpers ──────────────────────────────────────
def d(days_ago=0):
    return (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")

def pw(plain):
    # Simple hash matching the app's format (werkzeug pbkdf2)
    # We'll store plaintext marker for sample - app will need werkzeug
    try:
        from werkzeug.security import generate_password_hash
        return generate_password_hash(plain)
    except:
        return plain

# ── Connect ──────────────────────────────────────
os.makedirs("data", exist_ok=True)
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON")
conn.execute("PRAGMA journal_mode = WAL")
c = conn.cursor()

print("\n  Creating tables...")

# ════════════════════════════════════════════════
#  TABLES
# ════════════════════════════════════════════════
c.executescript("""
CREATE TABLE IF NOT EXISTS users (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS products (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL UNIQUE,
    hsn             TEXT,
    gst_rate        REAL NOT NULL,
    rate            REAL NOT NULL,
    stock_qty       REAL NOT NULL DEFAULT 0,
    unit            TEXT,
    selling_price   REAL DEFAULT 0,
    wholesale_price REAL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS product_variations (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id      INTEGER NOT NULL,
    variation_name  TEXT NOT NULL,
    selling_price   REAL DEFAULT 0,
    wholesale_price REAL DEFAULT 0,
    stock_qty       REAL DEFAULT 0,
    rate            REAL DEFAULT 0,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS vendors (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    name    TEXT NOT NULL UNIQUE,
    gstin   TEXT,
    address TEXT,
    phone   TEXT,
    email   TEXT
);

CREATE TABLE IF NOT EXISTS buyers (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL UNIQUE,
    gstin           TEXT,
    address TEXT,
    phone   TEXT,
    email   TEXT,
    state   TEXT,
    opening_balance REAL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS invoices (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_no       TEXT UNIQUE NOT NULL,
    invoice_date     TEXT NOT NULL,
    buyer_id         INTEGER,
    payment_mode     TEXT,
    order_ref        TEXT,
    dispatch_info    TEXT,
    subtotal         REAL NOT NULL DEFAULT 0,
    total_discount   REAL NOT NULL DEFAULT 0,
    total_gst        REAL NOT NULL DEFAULT 0,
    taxable_value    REAL NOT NULL DEFAULT 0,
    total_cgst       REAL NOT NULL DEFAULT 0,
    total_sgst       REAL NOT NULL DEFAULT 0,
    total_igst       REAL NOT NULL DEFAULT 0,
    freight          REAL DEFAULT 0,
    round_off        REAL DEFAULT 0,
    grand_total      REAL NOT NULL DEFAULT 0,
    paid_amount      REAL DEFAULT 0,
    previous_balance REAL DEFAULT 0,
    FOREIGN KEY (buyer_id) REFERENCES buyers(id)
);

CREATE TABLE IF NOT EXISTS invoice_items (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id       INTEGER,
    product_id       INTEGER,
    variation_id     INTEGER DEFAULT NULL,
    description      TEXT,
    hsn              TEXT,
    gst_rate         REAL,
    quantity         REAL,
    rate             REAL,
    discount_percent REAL DEFAULT 0,
    amount           REAL,
    batch_no         TEXT DEFAULT '',
    FOREIGN KEY (invoice_id)   REFERENCES invoices(id),
    FOREIGN KEY (product_id)   REFERENCES products(id),
    FOREIGN KEY (variation_id) REFERENCES product_variations(id)
);

CREATE TABLE IF NOT EXISTS customer_payments (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    buyer_id     INTEGER NOT NULL,
    payment_date TEXT,
    amount       REAL,
    payment_mode TEXT,
    notes        TEXT,
    FOREIGN KEY (buyer_id) REFERENCES buyers(id)
);

CREATE TABLE IF NOT EXISTS purchases (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    vendor_id      INTEGER NOT NULL,
    bill_no        TEXT,
    purchase_date  TEXT,
    total_amount   REAL,
    amount_paid    REAL DEFAULT 0,
    payment_status TEXT DEFAULT 'Unpaid',
    notes          TEXT,
    taxable_amount REAL DEFAULT 0,
    sgst_amount    REAL DEFAULT 0,
    cgst_amount    REAL DEFAULT 0,
    igst_amount    REAL DEFAULT 0,
    total_tax      REAL DEFAULT 0,
    reverse_charge INTEGER DEFAULT 0,
    FOREIGN KEY (vendor_id) REFERENCES vendors(id)
);

CREATE TABLE IF NOT EXISTS purchase_items (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    purchase_id    INTEGER,
    product_id     INTEGER,
    description    TEXT,
    hsn            TEXT,
    gst_rate       REAL,
    quantity       REAL,
    rate           REAL,
    batch_no       TEXT,
    expiry_date    TEXT,
    taxable_amount REAL DEFAULT 0,
    cgst_amount    REAL DEFAULT 0,
    sgst_amount    REAL DEFAULT 0,
    igst_amount    REAL DEFAULT 0,
    amount         REAL,
    FOREIGN KEY (purchase_id) REFERENCES purchases(id),
    FOREIGN KEY (product_id)  REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS purchase_payments (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    purchase_id  INTEGER NOT NULL,
    payment_date TEXT,
    amount       REAL,
    payment_mode TEXT,
    reference_no TEXT,
    FOREIGN KEY (purchase_id) REFERENCES purchases(id)
);

CREATE TABLE IF NOT EXISTS batch_tracking (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id  INTEGER,
    batch_no    TEXT NOT NULL,
    expiry_date TEXT,
    purchase_id INTEGER,
    invoice_id  INTEGER,
    qty_in      REAL DEFAULT 0,
    qty_out     REAL DEFAULT 0,
    entry_date  TEXT
);

CREATE TABLE IF NOT EXISTS proforma_invoices (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    quotation_no    TEXT UNIQUE NOT NULL,
    quotation_date  TEXT NOT NULL,
    buyer_id        INTEGER,
    buyer_name      TEXT,
    buyer_address   TEXT,
    buyer_phone     TEXT,
    buyer_gstin     TEXT,
    subtotal        REAL DEFAULT 0,
    total_discount  REAL DEFAULT 0,
    total_gst       REAL DEFAULT 0,
    taxable_value   REAL DEFAULT 0,
    total_cgst      REAL DEFAULT 0,
    total_sgst      REAL DEFAULT 0,
    total_igst      REAL DEFAULT 0,
    freight         REAL DEFAULT 0,
    round_off       REAL DEFAULT 0,
    grand_total     REAL DEFAULT 0,
    notes           TEXT,
    status          TEXT DEFAULT 'Draft',
    validity_days   INTEGER DEFAULT 30,
    FOREIGN KEY (buyer_id) REFERENCES buyers(id)
);

CREATE TABLE IF NOT EXISTS proforma_items (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    proforma_id  INTEGER NOT NULL,
    product_id   INTEGER,
    variation_id INTEGER,
    description  TEXT,
    hsn          TEXT,
    gst_rate     REAL,
    quantity     REAL,
    rate         REAL,
    discount_percent REAL DEFAULT 0,
    amount       REAL,
    FOREIGN KEY (proforma_id) REFERENCES proforma_invoices(id),
    FOREIGN KEY (product_id)  REFERENCES products(id)
);
""")
conn.commit()
print("  ✔  Tables created")

# ════════════════════════════════════════════════
#  USERS
# ════════════════════════════════════════════════
print("\n  Adding users...")
users = [
    ("admin",   pw("admin123"), "Admin"),
    ("cashier1",pw("cash123"),  "Cashier"),
]
for u in users:
    c.execute("INSERT OR IGNORE INTO users (username,password,role) VALUES (?,?,?)", u)
conn.commit()
print("  ✔  2 users added  (admin/admin123, cashier1/cash123)")

# ════════════════════════════════════════════════
#  VENDORS  (Sample Supplier names)
# ════════════════════════════════════════════════
print("\n  Adding sample vendors...")
vendors = [
    ("Sample Traders Pvt Ltd",   "27AABCS1234A1Z5", "12, MIDC Industrial Area, Pune - 411019",          "9876543210", "sample.traders@email.com"),
    ("Demo Wholesale Co",        "29AADCD5678B2Z1", "45, Gandhinagar Market, Bengaluru - 560009",        "9123456780", "demo.wholesale@email.com"),
    ("Test Distributors",        "06AABCT9012C3Z8", "78, Sector 18, Gurugram - 122015",                  "9988776655", "test.dist@email.com"),
    ("Example Suppliers Ltd",    "24AACES3456D4Z2", "90, Ring Road, Surat - 395002",                     "9765432100", "example.sup@email.com"),
    ("Sample Imports & Exports", "33AABCE7890E5Z6", "23, Anna Salai, Chennai - 600002",                  "9654321098", "sample.imp@email.com"),
]
for v in vendors:
    c.execute("INSERT OR IGNORE INTO vendors (name,gstin,address,phone,email) VALUES (?,?,?,?,?)", v)
conn.commit()
print(f"  ✔  {len(vendors)} vendors added")

# ════════════════════════════════════════════════
#  BUYERS  (Sample Customer names)
# ════════════════════════════════════════════════
print("\n  Adding sample buyers...")
buyers = [
    # name, gstin, address, phone, email, state, opening_balance
    ("Sample Retail Store",      "27AABCR1111A1Z5", "15, MG Road, Mumbai - 400001",        "9812345678", "sampleretail@email.com",  "Maharashtra",   5000.00),
    ("Demo Medical Hall",        "07AADCD2222B2Z1", "32, Nehru Place, Delhi - 110019",      "9823456789", "demomedical@email.com",   "Delhi",         2500.00),
    ("Test General Store",       "29AACES3333C3Z8", "67, Brigade Road, Bengaluru - 560001", "9834567890", "testgeneral@email.com",   "Karnataka",     0.00),
    ("Example Pharma",           "24AABCE4444D4Z2", "89, CG Road, Ahmedabad - 380009",      "9845678901", "examplepharma@email.com", "Gujarat",       1200.00),
    ("Sample Super Market",      "06AABCS5555E5Z6", "11, Connaught Place, Delhi - 110001",  "9856789012", "samplesupermarket@gmail.com","Delhi",       0.00),
    ("Demo Kirana Shop",         "",                "45, Gandhi Nagar, Jaipur - 302001",    "9867890123", "",                        "Rajasthan",     800.00),
    ("Test Chemist",             "33AADCE6666F6Z3", "78, Anna Nagar, Chennai - 600040",     "9878901234", "testchemist@email.com",   "Tamil Nadu",    0.00),
    ("Example Wholesale",        "36AACES7777G7Z7", "23, Banjara Hills, Hyderabad - 500034","9889012345", "exwholesale@email.com",   "Telangana",     3000.00),
]
for b in buyers:
    c.execute("INSERT OR IGNORE INTO buyers (name,gstin,address,phone,email,state,opening_balance) VALUES (?,?,?,?,?,?,?)", b)
conn.commit()
print(f"  ✔  {len(buyers)} buyers added")

# ════════════════════════════════════════════════
#  PRODUCTS  (Sample with variations)
# ════════════════════════════════════════════════
print("\n  Adding sample products...")
products = [
    # name, hsn, gst_rate, cost(rate), stock, unit, selling_price, wholesale_price
    ("Sample Shampoo",         "3305", 18.0, 120.0, 500,  "Bottle", 160.0, 145.0),
    ("Demo Face Cream",        "3304", 18.0,  85.0, 300,  "Pcs",    115.0, 100.0),
    ("Test Cooking Oil",       "1511",  5.0, 180.0, 200,  "Litre",  210.0, 195.0),
    ("Sample Biscuits",        "1905",  5.0,  22.0, 1000, "Pkt",     30.0,  27.0),
    ("Demo Soap",              "3401", 18.0,  18.0, 800,  "Pcs",     28.0,  24.0),
    ("Test Toothpaste",        "3306", 12.0,  55.0, 400,  "Tube",    75.0,  68.0),
    ("Sample Rice",            "1006",  5.0,  42.0, 5000, "Kg",      52.0,  47.0),
    ("Demo Hair Oil",          "3305", 18.0,  65.0, 350,  "Bottle",  90.0,  80.0),
    ("Test Detergent",         "3402", 18.0,  75.0, 600,  "Kg",     100.0,  90.0),
    ("Sample Mineral Water",   "2201",  0.0,   8.0, 2000, "Bottle",  15.0,  12.0),
    ("Demo Cold Drink",        "2202", 12.0,  22.0, 500,  "Bottle",  35.0,  30.0),
    ("Test Notebook",          "4820", 12.0,  28.0, 250,  "Pcs",     40.0,  35.0),
    ("Sample Pen",             "9608", 12.0,   5.0, 2000, "Pcs",      8.0,   7.0),
    ("Demo Mosquito Coil",     "3808", 12.0,  30.0, 400,  "Pkt",     42.0,  38.0),
    ("Test Floor Cleaner",     "3402", 18.0,  90.0, 300,  "Bottle", 125.0, 110.0),
]
product_ids = {}
for p in products:
    c.execute("""INSERT OR IGNORE INTO products
        (name,hsn,gst_rate,rate,stock_qty,unit,selling_price,wholesale_price)
        VALUES (?,?,?,?,?,?,?,?)""", p)
    pid = c.lastrowid
    product_ids[p[0]] = pid

conn.commit()
print(f"  ✔  {len(products)} products added")

# ── Product Variations ────────────────────────
print("\n  Adding product variations...")
# Get actual IDs
for name in list(product_ids.keys()):
    row = c.execute("SELECT id FROM products WHERE name=?", (name,)).fetchone()
    if row:
        product_ids[name] = row[0]

variations = [
    # product_name, variation_name, selling, wholesale, stock, cost
    ("Sample Shampoo",   "100ml",  80.0,  72.0, 200, 60.0),
    ("Sample Shampoo",   "200ml", 145.0, 130.0, 180, 110.0),
    ("Sample Shampoo",   "400ml", 270.0, 245.0, 120, 200.0),
    ("Test Cooking Oil", "500ml",  110.0, 100.0, 80,  88.0),
    ("Test Cooking Oil", "1 Litre",210.0, 195.0, 150, 180.0),
    ("Test Cooking Oil", "5 Litre",980.0, 900.0, 50,  840.0),
    ("Demo Soap",        "75gm",   18.0,  15.0, 400,  12.0),
    ("Demo Soap",        "125gm",  28.0,  24.0, 300,  18.0),
    ("Sample Rice",      "1 Kg",   52.0,  47.0, 500,  42.0),
    ("Sample Rice",      "5 Kg",  248.0, 225.0, 200, 200.0),
    ("Sample Rice",      "25 Kg", 1180.0,1080.0, 50,  980.0),
    ("Demo Hair Oil",    "100ml",  50.0,  44.0, 150,  35.0),
    ("Demo Hair Oil",    "200ml",  90.0,  80.0, 120,  65.0),
]
var_ids = {}
for vname, vvar, vs, vw, vstk, vcost in variations:
    pid = product_ids.get(vname)
    if pid:
        c.execute("""INSERT INTO product_variations
            (product_id,variation_name,selling_price,wholesale_price,stock_qty,rate)
            VALUES (?,?,?,?,?,?)""", (pid, vvar, vs, vw, vstk, vcost))
        var_ids[f"{vname}|{vvar}"] = c.lastrowid

conn.commit()
print(f"  ✔  {len(variations)} variations added")

# ════════════════════════════════════════════════
#  PURCHASES  (Sample Purchase Bills)
# ════════════════════════════════════════════════
print("\n  Adding sample purchases...")

def make_purchase(vendor_id, bill_no, date, items, paid, reverse=0):
    """items = [(product_name, qty, rate, gst_rate, batch, expiry)]"""
    taxable = sum(q*r for _,q,r,g,b,e in items)
    cgst    = sum(q*r*(g/200) for _,q,r,g,b,e in items)
    sgst    = cgst
    total_tax = cgst + sgst
    total   = taxable + total_tax
    status  = "Paid" if paid >= total else ("Partial" if paid > 0 else "Unpaid")

    c.execute("""INSERT INTO purchases
        (vendor_id,bill_no,purchase_date,total_amount,amount_paid,payment_status,
         taxable_amount,cgst_amount,sgst_amount,total_tax,reverse_charge)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (vendor_id, bill_no, date, round(total,2), paid, status,
         round(taxable,2), round(cgst,2), round(sgst,2), round(total_tax,2), reverse))
    purch_id = c.lastrowid

    for pname, qty, rate, gst, batch, expiry in items:
        pid  = product_ids.get(pname, 1)
        tax  = qty*rate*(gst/200)
        amt  = qty*rate + tax*2
        c.execute("""INSERT INTO purchase_items
            (purchase_id,product_id,description,hsn,gst_rate,quantity,rate,
             batch_no,expiry_date,taxable_amount,cgst_amount,sgst_amount,amount)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (purch_id, pid, pname, "0000", gst, qty, rate,
             batch, expiry,
             round(qty*rate,2), round(tax,2), round(tax,2), round(amt,2)))

        # Batch tracking
        c.execute("""INSERT INTO batch_tracking
            (product_id,batch_no,expiry_date,purchase_id,qty_in,qty_out,entry_date)
            VALUES (?,?,?,?,?,0,?)""",
            (pid, batch, expiry, purch_id, qty, date))

    if paid > 0:
        c.execute("""INSERT INTO purchase_payments
            (purchase_id,payment_date,amount,payment_mode)
            VALUES (?,?,?,?)""",
            (purch_id, date, paid, "Bank Transfer"))

    return purch_id

# Get vendor IDs
v = c.execute("SELECT id,name FROM vendors").fetchall()
vids = {row[1]: row[0] for row in v}

make_purchase(
    vids["Sample Traders Pvt Ltd"], "ST/2025-26/001", d(60),
    [
        ("Sample Shampoo",   200, 120.0, 18.0, "BTCH-SH-001", "2027-01-01"),
        ("Demo Face Cream",  100,  85.0, 18.0, "BTCH-FC-001", "2027-06-01"),
        ("Demo Hair Oil",    150,  65.0, 18.0, "BTCH-HO-001", "2026-12-01"),
    ], 14000, 0
)

make_purchase(
    vids["Demo Wholesale Co"], "DW/2025-26/045", d(45),
    [
        ("Test Cooking Oil", 100, 180.0, 5.0, "BTCH-OIL-001", "2026-06-01"),
        ("Sample Biscuits",  500,  22.0, 5.0, "BTCH-BSC-001", "2026-09-01"),
        ("Sample Rice",     1000,  42.0, 5.0, "BTCH-RIC-001", "2027-03-01"),
    ], 70000, 0
)

make_purchase(
    vids["Test Distributors"], "TD/26/112", d(30),
    [
        ("Demo Soap",         300,  18.0, 18.0, "BTCH-SP-001", "2027-01-01"),
        ("Test Toothpaste",   200,  55.0, 12.0, "BTCH-TP-001", "2026-11-01"),
        ("Test Detergent",    100,  75.0, 18.0, "BTCH-DT-001", "2027-06-01"),
    ], 25000, 20000
)

make_purchase(
    vids["Example Suppliers Ltd"], "ESL/2526/089", d(20),
    [
        ("Sample Mineral Water", 1000, 8.0,  0.0, "BTCH-MW-001", "2026-08-01"),
        ("Demo Cold Drink",       200, 22.0, 12.0, "BTCH-CD-001", "2026-10-01"),
    ], 12000, 12000
)

make_purchase(
    vids["Sample Imports & Exports"], "SIE/26/033", d(10),
    [
        ("Test Notebook",  100, 28.0, 12.0, "BTCH-NB-001", "2028-01-01"),
        ("Sample Pen",    1000,  5.0, 12.0, "BTCH-PN-001", "2028-01-01"),
        ("Demo Mosquito Coil", 200, 30.0, 12.0, "BTCH-MC-001", "2027-06-01"),
    ], 9000, 0
)

make_purchase(
    vids["Sample Traders Pvt Ltd"], "ST/2025-26/002", d(5),
    [
        ("Sample Shampoo", 100, 120.0, 18.0, "BTCH-SH-002", "2027-03-01"),
        ("Test Floor Cleaner", 50, 90.0, 18.0, "BTCH-FC2-001", "2027-01-01"),
    ], 18000, 18000
)

conn.commit()
print("  ✔  6 purchase bills added with items, payments & batch tracking")

# ════════════════════════════════════════════════
#  SALES INVOICES
# ════════════════════════════════════════════════
print("\n  Adding sample sales invoices...")

# Get buyer IDs
brows = c.execute("SELECT id,name,state FROM buyers").fetchall()
bids  = {row[1]: (row[0], row[2]) for row in brows}

COMPANY_STATE = "Maharashtra"  # Change to match your company state

def make_invoice(inv_no, date, buyer_name, items, paid, freight=0, discount=0, prev_bal=0):
    """items = [(product_name, variation_name_or_None, qty, rate, gst_rate, discount_pct)]"""
    buyer_id, buyer_state = bids[buyer_name]
    is_igst = (buyer_state != COMPANY_STATE)

    subtotal     = sum(qty*rate for _,_,qty,rate,_,_ in items)
    total_disc   = sum(qty*rate*(dpct/100) for _,_,qty,rate,_,dpct in items)
    taxable      = subtotal - total_disc

    if is_igst:
        total_igst = sum((qty*rate*(1-dpct/100))*(gst/100) for _,_,qty,rate,gst,dpct in items)
        total_cgst = 0.0
        total_sgst = 0.0
    else:
        total_cgst = sum((qty*rate*(1-dpct/100))*(gst/200) for _,_,qty,rate,gst,dpct in items)
        total_sgst = total_cgst
        total_igst = 0.0

    total_gst  = round(total_cgst + total_sgst + total_igst, 2)
    grand      = round(taxable + total_gst + freight, 2)
    round_off  = round(round(grand) - grand, 2)
    grand      = round(grand + round_off, 2)

    c.execute("""INSERT INTO invoices
        (invoice_no,invoice_date,buyer_id,payment_mode,
         subtotal,total_discount,taxable_value,total_gst,
         total_cgst,total_sgst,total_igst,
         freight,round_off,grand_total,paid_amount,previous_balance)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (inv_no, date, buyer_id,
         "Cash" if paid>=grand else "Credit",
         round(subtotal,2), round(total_disc,2), round(taxable,2), total_gst,
         round(total_cgst,2), round(total_sgst,2), round(total_igst,2),
         freight, round_off, grand, min(paid, grand), prev_bal))
    inv_id = c.lastrowid

    for pname, vname, qty, rate, gst, dpct in items:
        pid  = product_ids.get(pname, 1)
        vid  = var_ids.get(f"{pname}|{vname}") if vname else None
        disc_amt = qty*rate*(dpct/100)
        taxable_item = qty*rate - disc_amt
        amt  = taxable_item * (1 + gst/100)
        c.execute("""INSERT INTO invoice_items
            (invoice_id,product_id,variation_id,description,hsn,
             gst_rate,quantity,rate,discount_percent,amount)
            VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (inv_id, pid, vid,
             f"{pname} {vname}" if vname else pname,
             "0000", gst, qty, rate, dpct, round(amt,2)))

        # Batch tracking out
        batch = c.execute(
            "SELECT batch_no FROM batch_tracking WHERE product_id=? AND qty_in>0 LIMIT 1",
            (pid,)).fetchone()
        if batch:
            c.execute("""INSERT INTO batch_tracking
                (product_id,batch_no,purchase_id,invoice_id,qty_in,qty_out,entry_date)
                VALUES (?,?,0,?,0,?,?)""",
                (pid, batch[0], inv_id, qty, date))

    return inv_id

# Invoice 1 - Local buyer, Cash
inv1 = make_invoice("SAMPLE/25-26/001", d(55), "Sample Retail Store",
    [
        ("Sample Shampoo",   "200ml", 10, 145.0, 18.0, 0),
        ("Demo Face Cream",  None,    5,  115.0, 18.0, 0),
        ("Demo Soap",        "125gm", 20,  28.0, 18.0, 0),
    ], 3000, freight=50, prev_bal=5000)

# Invoice 2 - Local buyer, Credit with discount
inv2 = make_invoice("SAMPLE/25-26/002", d(40), "Test General Store",
    [
        ("Test Cooking Oil", "1 Litre", 20, 210.0, 5.0, 2),
        ("Sample Biscuits",  None,      50,  30.0, 5.0, 0),
        ("Sample Rice",      "5 Kg",    10, 248.0, 5.0, 0),
    ], 0)

# Invoice 3 - Outstation buyer (IGST)
inv3 = make_invoice("SAMPLE/25-26/003", d(35), "Example Pharma",
    [
        ("Test Toothpaste",   None,    15, 75.0, 12.0, 0),
        ("Demo Mosquito Coil",None,    10, 42.0, 12.0, 0),
        ("Test Floor Cleaner",None,     5,125.0, 18.0, 5),
    ], 2000)

# Invoice 4 - Large order, partial payment
inv4 = make_invoice("SAMPLE/25-26/004", d(25), "Example Wholesale",
    [
        ("Sample Shampoo",   "100ml", 50,  80.0, 18.0, 5),
        ("Sample Shampoo",   "200ml", 30, 145.0, 18.0, 5),
        ("Demo Hair Oil",    "100ml", 40,  50.0, 18.0, 0),
        ("Demo Hair Oil",    "200ml", 20,  90.0, 18.0, 0),
        ("Demo Soap",        "75gm",  60,  18.0, 18.0, 0),
    ], 5000, prev_bal=3000)

# Invoice 5 - Local, fully paid
inv5 = make_invoice("SAMPLE/25-26/005", d(15), "Demo Kirana Shop",
    [
        ("Sample Mineral Water", None, 50, 15.0, 0.0, 0),
        ("Demo Cold Drink",      None, 24, 35.0, 12.0, 0),
        ("Sample Biscuits",      None, 30, 30.0,  5.0, 0),
        ("Sample Rice",         "1 Kg",20, 52.0,  5.0, 0),
    ], 99999)

# Invoice 6 - Recent, credit
inv6 = make_invoice("SAMPLE/25-26/006", d(8), "Demo Medical Hall",
    [
        ("Test Toothpaste",  None,  10, 75.0, 12.0, 0),
        ("Demo Face Cream",  None,  8, 115.0, 18.0, 0),
        ("Sample Pen",       None, 50,   8.0, 12.0, 0),
    ], 0)

# Invoice 7 - Today's invoice
inv7 = make_invoice("SAMPLE/25-26/007", d(0), "Sample Super Market",
    [
        ("Test Detergent",    None,  10, 100.0, 18.0, 0),
        ("Demo Soap",        "125gm",30,  28.0, 18.0, 0),
        ("Test Notebook",    None,   20,  40.0, 12.0, 0),
        ("Sample Pen",       None,  100,   8.0, 12.0, 0),
    ], 3000, freight=100)

# Cancelled invoice (to show cancel feature)
c.execute("""INSERT INTO invoices
    (invoice_no,invoice_date,buyer_id,payment_mode,
     subtotal,total_discount,taxable_value,total_gst,
     total_cgst,total_sgst,total_igst,freight,round_off,grand_total,paid_amount)
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
    ("[CANCELLED] SAMPLE/25-26/003-A", d(32), bids["Test Chemist"][0],
     "Cash", 0,0,0,0,0,0,0,0,0,0,0))

conn.commit()
print("  ✔  7 sales invoices added  (1 cancelled sample bhi hai)")

# ════════════════════════════════════════════════
#  CUSTOMER PAYMENTS
# ════════════════════════════════════════════════
print("\n  Adding customer payments...")
payments = [
    (bids["Sample Retail Store"][0],  d(50), 3000, "Cash",         "Against SAMPLE/001"),
    (bids["Sample Retail Store"][0],  d(45), 2000, "UPI",          "UPI Ref: SAM123456"),
    (bids["Test General Store"][0],   d(38), 2500, "Bank Transfer","NEFT Ref: DM789012"),
    (bids["Example Wholesale"][0],    d(20), 5000, "Cheque",        "Chq No: 123456"),
    (bids["Example Wholesale"][0],    d(10), 3000, "UPI",           "UPI Ref: EW456789"),
    (bids["Demo Medical Hall"][0],    d(30), 1500, "Cash",          "Advance payment"),
    (bids["Demo Kirana Shop"][0],     d(12), 2000, "UPI",           "UPI Ref: DK112233"),
    (bids["Sample Super Market"][0],  d(2),  3000, "Cash",          "Partial advance"),
]
for p in payments:
    c.execute("""INSERT INTO customer_payments
        (buyer_id,payment_date,amount,payment_mode,notes)
        VALUES (?,?,?,?,?)""", p)
conn.commit()
print(f"  ✔  {len(payments)} customer payments added")

# ════════════════════════════════════════════════
#  PROFORMA / QUOTATIONS
# ════════════════════════════════════════════════
print("\n  Adding sample quotations...")

def make_proforma(qno, date, buyer_name, items, notes="", status="Sent"):
    buyer_id, buyer_state = bids[buyer_name]
    buyer_row = c.execute("SELECT name,address,phone,gstin FROM buyers WHERE id=?", (buyer_id,)).fetchone()

    subtotal = sum(qty*rate for _,_,qty,rate,_,_ in items)
    total_disc = sum(qty*rate*(dpct/100) for _,_,qty,rate,_,dpct in items)
    taxable = subtotal - total_disc
    cgst = sum((qty*rate*(1-dpct/100))*(gst/200) for _,_,qty,rate,gst,dpct in items)
    sgst = cgst
    grand = round(taxable + cgst + sgst, 2)

    c.execute("""INSERT INTO proforma_invoices
        (quotation_no,quotation_date,buyer_id,buyer_name,buyer_address,buyer_phone,buyer_gstin,
         subtotal,total_discount,taxable_value,total_gst,total_cgst,total_sgst,total_igst,
         grand_total,notes,status,validity_days)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,0,?,?,?,30)""",
        (qno, date, buyer_id,
         buyer_row[0], buyer_row[1], buyer_row[2], buyer_row[3],
         round(subtotal,2), round(total_disc,2), round(taxable,2),
         round(cgst+sgst,2), round(cgst,2), round(sgst,2),
         grand, notes, status))
    pro_id = c.lastrowid

    for pname, vname, qty, rate, gst, dpct in items:
        pid = product_ids.get(pname, 1)
        vid = var_ids.get(f"{pname}|{vname}") if vname else None
        amt = qty*rate*(1-dpct/100)*(1+gst/100)
        c.execute("""INSERT INTO proforma_items
            (proforma_id,product_id,variation_id,description,hsn,
             gst_rate,quantity,rate,discount_percent,amount)
            VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (pro_id, pid, vid,
             f"{pname} {vname}" if vname else pname,
             "0000", gst, qty, rate, dpct, round(amt,2)))

make_proforma("QUOT/25-26/001", d(20), "Test General Store",
    [
        ("Sample Shampoo", "400ml", 20, 270.0, 18.0, 5),
        ("Demo Hair Oil",  "200ml", 10,  90.0, 18.0, 0),
    ], "Valid for 30 days. Prices subject to change.", "Sent")

make_proforma("QUOT/25-26/002", d(12), "Example Pharma",
    [
        ("Test Toothpaste",    None,  50, 75.0, 12.0, 10),
        ("Demo Face Cream",    None,  30,115.0, 18.0,  5),
        ("Demo Mosquito Coil", None, 100, 42.0, 12.0,  0),
    ], "Bulk order discount applied.", "Approved")

make_proforma("QUOT/25-26/003", d(3), "Demo Medical Hall",
    [
        ("Sample Mineral Water", None, 200, 15.0, 0.0,  0),
        ("Demo Cold Drink",      None,  48, 35.0,12.0,  0),
    ], "Monthly supply quotation.", "Draft")

conn.commit()
print("  ✔  3 quotations/proformas added  (Draft, Sent, Approved)")

# ════════════════════════════════════════════════
#  DONE
# ════════════════════════════════════════════════
conn.close()

print()
print("  ================================================================")
print("   SAMPLE DATABASE READY!")
print(f"   File: {DB_PATH}")
print()
print("   Kya kya hai is database mein:")
print("    Users      : 2  (admin/admin123, cashier1/cash123)")
print("    Vendors    : 5  (sample suppliers)")
print("    Buyers     : 8  (sample customers, kuch outstanding balance ke saath)")
print("    Products   : 15 (FMCG/General items)")
print("    Variations : 13 (size/pack variations)")
print("    Purchases  : 6  (bills with items, payments, batch tracking)")
print("    Invoices   : 7  (local + outstation + cancelled)")
print("    Payments   : 8  (customer payments received)")
print("    Quotations : 3  (draft, sent, approved)")
print()
print("   Istemal kaise karo:")
print("   billing-app/data/ folder mein yeh file rakho")
print("   Naam badlo: billing_app.db")
print("  ================================================================")
print()
