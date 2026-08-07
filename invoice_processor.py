import re
from datetime import datetime


RAW_RECORDS = [
    {"invoice_id": "INV-1001", "amount": "$1,200.00", "date": "2024-01-05", "vendor": "Acme Corp"},
    {"invoice_id": "INV-1002", "amount": "95O.5", "date": "01/06/2024", "vendor": "Beta LLC"},
    {"invoice_id": "INV-1003", "amount": "N/A", "date": "2024-01-07", "vendor": "Acme Corp"},
    {"invoice_id": "INV-1004", "amount": "2,340", "date": "Jan 8, 2024", "vendor": ""},
    {"invoice_id": "INV-1001", "amount": "$1,200.00", "date": "2024-01-05", "vendor": "Acme Corp"},
    {"invoice_id": "INV-1005", "amount": "-450.00", "date": "2024-13-40", "vendor": "Gamma Inc"},
    {"invoice_id": "INV-1006", "amount": " ", "date": "2024/01/09", "vendor": "Delta Co"},
    {"invoice_id": "INV-1007", "amount": "3200.00", "date": "2019-01-10", "vendor": "Acme Corp"},
]

def commas_are_valid(amount_text):
    """
    Check that commas separate groups of three digits.

    Valid examples:
    1,200
    12,500
    1,200,000
    1,200.50

    Invalid examples:
    1,20
    12,,500
    12222,,,
    """

    if "," not in amount_text:
        return True

    text_to_check = amount_text

    if text_to_check.startswith("-"):
        text_to_check = text_to_check[1:]

    whole_number = text_to_check.split(".")[0]

    groups = whole_number.split(",")

    first_group = groups[0]

    if len(first_group) < 1:
        return False

    if len(first_group) > 3:
        return False

    if first_group.isdigit() is False:
        return False

    for group in groups[1:]:

        if len(group) != 3:
            return False

        if group.isdigit() is False:
            return False

    return True


def normalize_amount(amount):
    """
    Convert an amount into a float.

    Return None when the amount is missing or invalid.
    """

    if amount is None:
        return None

    amount_text = str(amount)

    amount_text = amount_text.strip()

    if amount_text == "":
        return None

    if amount_text.upper() == "N/A":
        return None

    currency_symbols = "$€£₪¥"

    starts_with_currency = False
    ends_with_currency = False

    if amount_text[0] in currency_symbols:
        starts_with_currency = True
        amount_text = amount_text[1:]

    if amount_text != "":

        if amount_text[-1] in currency_symbols:
            ends_with_currency = True
            amount_text = amount_text[:-1]

    if starts_with_currency is True:

        if ends_with_currency is True:
            return None

    amount_text = amount_text.strip()

    if amount_text == "":
        return None

    # Correct the OCR mistake from the assignment.
    # Example: 95O.5 becomes 950.5.
    amount_text = amount_text.replace("O", "0")

    # Only digits, commas, decimal points,
    # and an optional minus sign are allowed.
    valid_characters_pattern = r"^-?[0-9,.]+$"

    pattern_matches = re.fullmatch(
        valid_characters_pattern,
        amount_text,
    )

    if pattern_matches is None:
        return None

    decimal_point_count = amount_text.count(".")

    if decimal_point_count > 1:
        return None

    commas_valid = commas_are_valid(amount_text)

    if commas_valid is False:
        return None

    amount_text = amount_text.replace(",", "")

    try:
        normalized_amount = float(amount_text)

        return normalized_amount

    except ValueError:
        return None


def normalize_date(date_value):
    """
    Convert a date into YYYY-MM-DD format.

    Return None when the date is missing or invalid.
    """

    if date_value is None:
        return None

    date_text = str(date_value)

    date_text = date_text.strip()

    if date_text == "":
        return None

    date_formats = [
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%b %d, %Y",
        "%Y/%m/%d",
    ]

    for date_format in date_formats:

        try:
            parsed_date = datetime.strptime(
                date_text,
                date_format,
            )

            normalized_date = parsed_date.strftime(
                "%Y-%m-%d"
            )

            return normalized_date

        except ValueError:
            continue

    return None


def process_records(
    raw_records: list[dict],
) -> tuple[list[dict], list[dict]]:
    """
    Takes the raw records and returns:

    1. clean_records
    2. flagged_records
    """

    clean_records = []

    flagged_records = []

    seen_invoice_ids = set()

    for raw_record in raw_records:

        invoice_id = raw_record.get("invoice_id")

        amount = raw_record.get("amount")

        date_value = raw_record.get("date")

        vendor = raw_record.get("vendor")

        reasons = []

        if invoice_id is None:
            invoice_id = ""

        invoice_id = str(invoice_id)

        invoice_id = invoice_id.strip()

        if vendor is None:
            vendor = ""

        vendor = str(vendor)

        vendor = vendor.strip()

        if invoice_id == "":
            reasons.append("Missing invoice ID")

        elif invoice_id in seen_invoice_ids:
            reasons.append("Duplicate invoice ID")

        else:
            seen_invoice_ids.add(invoice_id)

        normalized_amount = normalize_amount(amount)

        if normalized_amount is None:
            reasons.append("Invalid or missing amount")

        else:

            if normalized_amount < 0:
                reasons.append("Negative amount")

        normalized_date = normalize_date(date_value)

        if normalized_date is None:
            reasons.append("Invalid date")

        if vendor == "":
            reasons.append("Missing vendor")

        if normalized_date is not None:

            parsed_date = datetime.strptime(
                normalized_date,
                "%Y-%m-%d",
            )

            invoice_year = parsed_date.year

            if invoice_year < 2020:
                reasons.append(
                    "Invoice date is unusually old"
                )

        if len(reasons) > 0:

            flagged_record = raw_record.copy()

            reason_text = "; ".join(reasons)

            flagged_record["reason"] = reason_text

            flagged_records.append(flagged_record)

        else:

            clean_record = {}

            clean_record["invoice_id"] = invoice_id

            clean_record["amount"] = normalized_amount

            clean_record["date"] = normalized_date

            clean_record["vendor"] = vendor

            clean_records.append(clean_record)

    return clean_records, flagged_records


def print_results(clean_records, flagged_records):
    """
    Print the results in a readable format.
    """

    print("CLEAN RECORDS")
    print("-------------")

    for record in clean_records:
        print(record)

    print()

    print("FLAGGED RECORDS")
    print("----------------")

    for record in flagged_records:
        print(record)


if __name__ == "__main__":

    clean_records, flagged_records = process_records(
        RAW_RECORDS
    )

    print_results(
        clean_records,
        flagged_records,
    )