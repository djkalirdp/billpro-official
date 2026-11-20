"""Regression tests for BillPro stock and expense workflows.

Run with: python -m unittest discover -s tests -v
"""
import os
import sqlite3
import tempfile
import unittest

import database_manager as db


class BillProFeatureTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(prefix='billpro_test_')
        self.old_db_file = db.DB_FILE
        self.old_backup_dir = db.BACKUP_DIR
        db.DB_FILE = os.path.join(self.temp_dir.name, 'data', 'billing_app.db')
        db.BACKUP_DIR = os.path.join(self.temp_dir.name, 'backups')
        os.makedirs(os.path.dirname(db.DB_FILE), exist_ok=True)
        db.create_tables()
        self.buyer_id = db.add_record('buyers', {
            'name': 'Regression Buyer', 'state': 'Delhi',
            'phone': '9876543210', 'opening_balance': 0,
        })
        self.product_id = db.add_record('products', {
            'name': 'Regression Product', 'gst_rate': 18, 'rate': 50,
            'stock_qty': 5, 'unit': 'pcs', 'selling_price': 100,
            'wholesale_price': 80,
        })

    def tearDown(self):
        db.DB_FILE = self.old_db_file
        db.BACKUP_DIR = self.old_backup_dir
        self.temp_dir.cleanup()

    def test_stock_adjustments_are_audited_and_cannot_go_negative(self):
        ok, new_stock = db.adjust_stock(self.product_id, 2, 'in', 'Count correction', created_by='tester')
        self.assertTrue(ok)
        self.assertEqual(new_stock, 7)
        ok, new_stock = db.adjust_stock(self.product_id, 0, 'set', 'Physical count', created_by='tester')
        self.assertTrue(ok)
        self.assertEqual(new_stock, 0)
        ok, message = db.adjust_stock(self.product_id, 1, 'out', 'Invalid removal', created_by='tester')
        self.assertFalse(ok)
        self.assertIn('Insufficient stock', message)
        self.assertEqual(len(db.get_stock_adjustments()), 2)

    def test_stock_adjustment_can_target_a_variation(self):
        variation_id = db.add_record('product_variations', {
            'product_id': self.product_id, 'variation_name': 'Large',
            'selling_price': 120, 'wholesale_price': 90,
            'stock_qty': 4, 'rate': 55,
        })
        ok, new_stock = db.adjust_stock(self.product_id, 2, 'out', 'Variation sold',
                                        variation_id=variation_id, created_by='tester')
        self.assertTrue(ok)
        self.assertEqual(new_stock, 2)
        self.assertEqual(db.get_by_id('products', self.product_id)['stock_qty'], 5)
        self.assertEqual(db.get_by_id('product_variations', variation_id)['stock_qty'], 2)

    def test_expense_register_saves_and_filters(self):
        expense_id = db.add_expense({
            'expense_date': '2026-11-15', 'category': 'Rent',
            'description': 'Shop rent', 'amount': 12500.50,
            'payment_mode': 'UPI', 'reference_no': 'UTR-1',
            'notes': '', 'created_by': 'tester',
        })
        self.assertIsNotNone(expense_id)
        self.assertEqual(len(db.get_expenses('2026-11-01', '2026-11-30')), 1)
        self.assertEqual(db.get_expenses('2026-10-01', '2026-10-31'), [])
        with self.assertRaises(ValueError):
            db.add_expense({
                'expense_date': 'not-a-date', 'category': 'Other',
                'description': 'Invalid date', 'amount': 10,
            })

    def test_invoice_numbering_skips_cancelled_suffixes(self):
        db.add_record('invoices', {
            'invoice_no': 'INV-0009 [CANCELLED]', 'invoice_date': '2026-11-15',
            'buyer_id': self.buyer_id, 'subtotal': 0, 'total_discount': 0,
            'taxable_value': 0, 'total_gst': 0, 'grand_total': 0,
        })
        self.assertEqual(db.get_next_invoice_number('INV-'), 'INV-0010')
        self.assertEqual(db.get_next_invoice_number_bulk(2), ['INV-0010', 'INV-0011'])

    def test_invoice_stock_deduction_and_insufficient_stock_rollback(self):
        header = {
            'invoice_no': 'TEST-0001', 'invoice_date': '2026-11-15',
            'buyer_id': self.buyer_id, 'subtotal': 200,
            'total_discount': 0, 'taxable_value': 200,
            'total_gst': 36, 'grand_total': 236, 'paid_amount': 0,
        }
        item = {
            'product_id': self.product_id, 'description': 'Regression Product',
            'hsn': '', 'gst_rate': 18, 'quantity': 2, 'rate': 100,
            'discount_percent': 0, 'amount': 200,
        }
        invoice_id = db.save_invoice(header, [item], 'Delhi')
        self.assertIsNotNone(invoice_id)
        self.assertEqual(db.get_by_id('products', self.product_id)['stock_qty'], 3)

        failed_header = dict(header, invoice_no='TEST-0002')
        failed_item = dict(item, quantity=4, amount=400)
        self.assertIsNone(db.save_invoice(failed_header, [failed_item], 'Delhi'))
        self.assertEqual(db.get_by_id('products', self.product_id)['stock_qty'], 3)
        conn = sqlite3.connect(db.DB_FILE)
        try:
            self.assertEqual(conn.execute('SELECT COUNT(*) FROM invoices').fetchone()[0], 1)
            self.assertEqual(conn.execute('PRAGMA integrity_check').fetchone()[0], 'ok')
        finally:
            conn.close()


if __name__ == '__main__':
    unittest.main()
