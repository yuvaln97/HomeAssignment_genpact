# Thoughts and Assumptions

I started by asking ChatGPT to explain the assignment in simple terms and provide an initial implementation.

One of the main areas I focused on was amount validation. The initial implementation mainly removed currency symbols and attempted to convert the remaining value into a number. I noticed that stronger validation was needed because OCR output could contain words, letters in different positions, invalid comma placement, multiple decimal points, or unexpected special characters.

We created a specific set of rules for amount validation. The program accepts supported currency symbols at either the beginning or the end of the value, but not on both sides. It rejects unexpected letters and characters, checks that there is at least one digit, validates the number of decimal points, and checks that commas divide the number into correct groups of three digits.

We also handled the OCR mistake included in the sample data, where the capital letter `O` appears instead of the number `0`, as in `95O.5`. I questioned the initial correction because blindly replacing every `O` could turn invalid words into numbers. The final implementation allows this correction only when the value also contains a digit and rejects other letters.

I decided that negative invoice amounts should be flagged as suspicious. Although a negative value could represent a refund, the provided data appears to represent regular invoices and their costs. Therefore, a negative value is recognized as a valid numeric value but is placed in the flagged-records list for manual review.

For dates, I accepted several input formats and standardized every valid date to the `YYYY-MM-DD` output format. I assumed that the ambiguous value `01/06/2024` uses the `MM/DD/YYYY` input format and therefore represents January 6, 2024. This assumption matches the sequence of dates in the sample records.

I also asked about the difference between `strptime` and `strftime`. I learned that `strptime` parses a string and converts it into a `datetime` object according to a specified input format. `strftime` performs the opposite operation and converts a `datetime` object into a formatted string. When `strptime` cannot parse a date using the current format, it raises a `ValueError`, and the loop continues to try the next supported format.

 Moreover, I questioned the duplicate-record logic. The first version added the invoice ID to the set only at the end of processing the complete invoice. I suggested checking and storing the ID near the beginning of each iteration instead. The updated code now flags the ID immediately if it was already seen and adds it to the set immediately when it is new.

The function returns two lists: `clean_records` and `flagged_records`. Both are lists of dictionaries. Every flagged invoice remains a complete dictionary containing its original fields, with an additional `reason` field. Using a list is important because duplicate invoice IDs can exist and each occurrence must remain a separate record.

Finally, I added unit tests for individual validation rules and an integration test that runs `process_records` against all eight original sample records. The test compares the complete clean-records list and flagged-records list with the expected results. Additional tests cover words in amount fields, letters at different positions, malformed commas, multiple decimal points, currency symbols, missing values, OCR mistakes, supported date formats, duplicate IDs, negative amounts, missing vendors, and unusually old dates.
