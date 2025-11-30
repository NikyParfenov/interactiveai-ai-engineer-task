VALID_MODEL = "gpt-4o"
VALID_TEMPERATURE = 0

VALID_CONSISTENT = "True if text matches JSON data, False if there are discrepancies"
VALID_FEATURES = "Features mentioned in text but marked as false/absent in JSON. Example: 'mentions balcony but JSON has balcony=false'"
VALID_MISSING_FEATURES = "Important features present in JSON (true/available) but not mentioned in text"
VALID_INCORRECT_NUMBERS = "Numbers in text that don't match JSON. Example: 'text says 2 bedrooms but JSON has 3'"
VALID_WRONG_LISTING_TYPE = "True if text mentions sale when JSON says rent, or vice versa"
VALID_WRONG_LANGUAGE = "True if text language doesn't match JSON language field"
VALID_OTHER_INCONSISTENCIES = "Any other discrepancies between text and JSON"
VALID_SUMMARY = "Brief summary of all issues found, or 'All consistent' if no issues"