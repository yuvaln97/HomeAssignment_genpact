import unittest

from invoice_processor import (
    RAW_RECORDS,
    normalize_amount,
    normalize_date,
    process_records,
)


class TestInvoiceProcessor(unittest.TestCase):

    def test_amount_with_currency_and_commas(self):
        result = normalize_amount("$1,200.00")

        self.assertEqual(result, 1200.0)

    def test_amount_with_ocr_error(self):
        result = normalize_amount("95O.5")

        self.assertEqual(result, 950.5)

    def test_invalid_amount(self):
        result = normalize_amount("FOOO")

        self.assertIsNone(result)

    def test_negative_amount_normalization(self):
        result = normalize_amount("-450.00")

        self.assertEqual(result, -450.0)

    def test_date_with_dashes(self):
        result = normalize_date("2024-01-05")

        self.assertEqual(result, "2024-01-05")

    def test_date_with_month_day_year(self):
        result = normalize_date("01/06/2024")

        self.assertEqual(result, "2024-01-06")

    def test_invalid_date(self):
        result = normalize_date("2024-13-40")

        self.assertIsNone(result)

    def test_process_records_returns_lists(self):
        clean_records, flagged_records = process_records(RAW_RECORDS)

        self.assertIsInstance(clean_records, list)
        self.assertIsInstance(flagged_records, list)

    def test_number_of_clean_records(self):
        clean_records, flagged_records = process_records(RAW_RECORDS)

        self.assertEqual(len(clean_records), 2)

    def test_number_of_flagged_records(self):
        clean_records, flagged_records = process_records(RAW_RECORDS)

        self.assertEqual(len(flagged_records), 6)

    def test_first_clean_record(self):
        clean_records, flagged_records = process_records(RAW_RECORDS)

        first_record = clean_records[0]

        self.assertEqual(first_record["invoice_id"], "INV-1001")
        self.assertEqual(first_record["amount"], 1200.0)
        self.assertEqual(first_record["date"], "2024-01-05")
        self.assertEqual(first_record["vendor"], "Acme Corp")

    def test_ocr_record_is_cleaned(self):
        clean_records, flagged_records = process_records(RAW_RECORDS)

        second_record = clean_records[1]

        self.assertEqual(second_record["invoice_id"], "INV-1002")
        self.assertEqual(second_record["amount"], 950.5)
        self.assertEqual(second_record["date"], "2024-01-06")
        self.assertEqual(second_record["vendor"], "Beta LLC")

    def test_duplicate_record_is_flagged(self):
        clean_records, flagged_records = process_records(RAW_RECORDS)

        duplicate_found = False

        for record in flagged_records:
            if "Duplicate invoice ID" in record["reason"]:
                duplicate_found = True

        self.assertTrue(duplicate_found)

    def test_missing_vendor_is_flagged(self):
        clean_records, flagged_records = process_records(RAW_RECORDS)

        missing_vendor_found = False

        for record in flagged_records:
            if "Missing vendor" in record["reason"]:
                missing_vendor_found = True

        self.assertTrue(missing_vendor_found)

    def test_negative_amount_is_flagged(self):
        clean_records, flagged_records = process_records(RAW_RECORDS)

        negative_amount_found = False

        for record in flagged_records:
            if "Negative amount" in record["reason"]:
                negative_amount_found = True

        self.assertTrue(negative_amount_found)

    def test_invalid_date_is_flagged(self):
        clean_records, flagged_records = process_records(RAW_RECORDS)

        invalid_date_found = False

        for record in flagged_records:
            if "Invalid date" in record["reason"]:
                invalid_date_found = True

        self.assertTrue(invalid_date_found)

    def test_old_date_is_flagged(self):
        clean_records, flagged_records = process_records(RAW_RECORDS)

        old_date_found = False

        for record in flagged_records:
            if "Invoice date is unusually old" in record["reason"]:
                old_date_found = True

        self.assertTrue(old_date_found)


if __name__ == "__main__":
    unittest.main()