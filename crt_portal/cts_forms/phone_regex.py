# This regex is designed with U.S. and international phone numbers in mind.
# It doesn't guarantee that a matching value is a valid number, but screens
# out many invalid cases.

# The regex tests that a string has between 10 and 15 numerical characters.

# PASSES: 1112223333
# PASSES: +1112223333
# PASSES: +1 111 222 33333
# PASSES: +12 (345) 678 9000

# FAILS: (123) 456 789 -- too few numerical digits
# FAILS: "happy happy" -- no digits
# FAILS: (123) 456 7890 0000 0000 -- too many digits

phone_validation_regex = r'^\D*(\d\D*){10,15}$'
