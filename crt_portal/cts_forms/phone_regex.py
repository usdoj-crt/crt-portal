# This regex is designed with U.S. and international phone numbers in mind.
# It doesn't guarantee that a matching value is a valid international number,
# but it screens out many invalid cases.
# The regex tests for a string between 10 and 15 characters that consists
# only of numeric digits.
phone_validation_regex = r'[\d]{10,15}'