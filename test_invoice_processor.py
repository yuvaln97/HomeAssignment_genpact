import unittest

from invoice_processor import (
    RAW_RECORDS,
    commas_are_valid,
    normalize_amount,
    normalize_date,
    process_records,
)


class TestInvoiceProcessor(unittest.TestCase):

    def test_amount_with_currency_and_commas(self):
        result = normalize_amount("$1,200.00")

        self.assertEqual(result, 1200.0)

    def test_amount_with_currency_at_end(self):
        result = normalize_amount("950.50€")

        self.assertEqual(result, 950.5)

    def test_amount_with_ocr_error(self):
        result = normalize_amount("95O.5")

        self.assertEqual(result, 950.5)

    def test_amount_without_currency(self):
        result = normalize_amount("3200.00")

        self.assertEqual(result, 3200.0)

    def test_amount_with_valid_commas(self):
        result = normalize_amount("1,234,567.89")

        self.assertEqual(result, 1234567.89)

    def test_invalid_word_amount(self):
        result = normalize_amount("FOOO")

        self.assertIsNone(result)

    def test_invalid_letters_at_start(self):
        result = normalize_amount("ABC1200")

        self.assertIsNone(result)

    def test_invalid_letters_at_end(self):
        result = normalize_amount("1200ABC")

        self.assertIsNone(result)

    def test_invalid_letters_in_middle(self):
        result = normalize_amount("12ABC00")

        self.assertIsNone(result)

    def test_invalid_multiple_decimal_points(self):
        result = normalize_amount("12.5.6")

        self.assertIsNone(result)

    def test_invalid_multiple_commas(self):
        result = normalize_amount("12,,,000")

        self.assertIsNone(result)

    def test_invalid_comma_group(self):
        result = normalize_amount("1,20")

        self.assertIsNone(result)

    def test_invalid_currency_on_both_sides(self):
        result = normalize_amount("$1200€")

        self.assertIsNone(result)

    def test_empty_amount(self):
        result = normalize_amount(" ")

        self.assertIsNone(result)

    def test_none_amount(self):
        result = normalize_amount(None)

        self.assertIsNone(result)

    def test_na_amount(self):
        result = normalize_amount("N/A")

        self.assertIsNone(result)

    def test_negative_amount_normalization(self):
        result = normalize_amount("-450.00")

        self.assertEqual(result, -450.0)

    def test_valid_commas_function(self):
        result = commas_are_valid("1,200,000.50")

        self.assertTrue(result)

    def test_invalid_commas_function(self):
        result = commas_are_valid("1,20,000")

        self.assertFalse(result)

    def test_date_with_dashes(self):
        result = normalize_date("2024-01-05")

        self.assertEqual(result, "2024-01-05")

    def test_date_with_month_day_year(self):
        result = normalize_date("01/06/2024")

        self.assertEqual(result, "2024-01-06")

    def test_date_with_written_month(self):
        result = normalize_date("Jan 8, 2024")

        self.assertEqual(result, "2024-01-08")

    def test_date_with_slashes(self):
        result = normalize_date("2024/01/09")

        self.assertEqual(result, "2024-01-09")

    def test_invalid_date(self):
        result = normalize_date("2024-13-40")

        self.assertIsNone(result)

    def test_process_records_returns_lists(self):
        clean_records, flagged_records = process_records(
            RAW_RECORDS
        )

        self.assertIsInstance(clean_records, list)

        self.assertIsInstance(flagged_records, list)

    def test_number_of_clean_records(self):
        clean_records, flagged_records = process_records(
            RAW_RECORDS
        )

        self.assertEqual(len(clean_records), 2)

    def test_number_of_flagged_records(self):
        clean_records, flagged_records = process_records(
            RAW_RECORDS
        )

        self.assertEqual(len(flagged_records), 6)

    def test_first_clean_record(self):
        clean_records, flagged_records = process_records(
            RAW_RECORDS
        )

        first_record = clean_records[0]

        self.assertEqual(
            first_record["invoice_id"],
            "INV-1001",
        )

        self.assertEqual(
            first_record["amount"],
            1200.0,
        )

        self.assertEqual(
            first_record["date"],
            "2024-01-05",
        )

        self.assertEqual(
            first_record["vendor"],
            "Acme Corp",
        )

    def test_ocr_record_is_cleaned(self):
        clean_records, flagged_records = process_records(
            RAW_RECORDS
        )

        second_record = clean_records[1]

        self.assertEqual(
            second_record["invoice_id"],
            "INV-1002",
        )

        self.assertEqual(
            second_record["amount"],
            950.5,
        )

        self.assertEqual(
            second_record["date"],
            "2024-01-06",
        )

        self.assertEqual(
            second_record["vendor"],
            "Beta LLC",
        )

    def test_duplicate_record_is_flagged(self):
        clean_records, flagged_records = process_records(
            RAW_RECORDS
        )

        duplicate_found = False

        for record in flagged_records:

            reason = record["reason"]

            if "Duplicate invoice ID" in reason:
                duplicate_found = True

        self.assertTrue(duplicate_found)

    def test_missing_vendor_is_flagged(self):
        clean_records, flagged_records = process_records(
            RAW_RECORDS
        )

        missing_vendor_found = False

        for record in flagged_records:

            reason = record["reason"]

            if "Missing vendor" in reason:
                missing_vendor_found = True

        self.assertTrue(missing_vendor_found)

    def test_negative_amount_is_flagged(self):
        clean_records, flagged_records = process_records(
            RAW_RECORDS
        )

        negative_amount_found = False

        for record in flagged_records:

            reason = record["reason"]

            if "Negative amount" in reason:
                negative_amount_found = True

        self.assertTrue(negative_amount_found)

    def test_invalid_date_is_flagged(self):
        clean_records, flagged_records = process_records(
            RAW_RECORDS
        )

        invalid_date_found = False

        for record in flagged_records:

            reason = record["reason"]

            if "Invalid date" in reason:
                invalid_date_found = True

        self.assertTrue(invalid_date_found)

    def test_old_date_is_flagged(self):
        clean_records, flagged_records = process_records(
            RAW_RECORDS
        )

        old_date_found = False

        for record in flagged_records:

            reason = record["reason"]

            if "Invoice date is unusually old" in reason:
                old_date_found = True

        self.assertTrue(old_date_found)


if __name__ == "__main__":
    unittest.main()