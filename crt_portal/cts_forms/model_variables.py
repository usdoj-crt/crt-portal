"""Setting the variables that can be reused in models and forms for readability and reuse"""

PRIMARY_COMPLAINT_CHOICES = (
    ('denied_access', 'Denied access or removed from a location (including segregation)'),
    ('prevented_from_service', 'Prevented from using a service or service terminated'),
    ('denied_housing', 'Denied housing or subjected to harmful living conditions'),
    ('fired', 'Fired, not hired, demoted, or asked to show more documentation than required'),
    ('retaliated', 'Retaliated against or otherwise mistreated for reporting an issue'),
    ('harassed', 'Harassed, threatened, assaulted, or otherwise made to feel unsafe (including sexual harassment or assault)'),
    ('vote', 'Ability to vote was impacted'),
    ('discriminated_against', 'Otherwise discriminated against'),
)

PROTECTED_CLASS_CHOICES = (
    'Disability (including temporary or in recovery)',
    'Race/color',
    'National origin (including ancestry, ethnicity, and language)',
    'Immigration/citizenship status (choosing this does not share your status)',
    'Religion',
    'Sex or gender identity (including gender stereotypes) or pregnancy',
    'Sexual orientation',
    'Family, marriage, or parental status',
    'Military status',
    'Age',
    'Genetic information',
    'Other',
)

# used in internal CRT view display
PROTECTED_CLASS_CODES = {
    'Disability (including temporary or in recovery)': 'Disability',
    'Race/color': 'Race/color',
    'National origin (including ancestry, ethnicity, and language)': 'National Origin',
    'Immigration/citizenship status (choosing this does not share your status)': 'Immigration',
    'Religion': 'Religion',
    'Sex or gender identity (including gender stereotypes) or pregnancy': 'Sex',
    'Sexual orientation': 'Orientation',
    'Family, marriage, or parental status': 'Family status',
    'Military status': 'Military',
    'Age': 'Age',
    'Genetic information': 'Genetic',
    'Other': None,
}

PROTECTED_MODEL_CHOICES = (
    ('disability', 'Disability (including temporary or in recovery)'),
    ('race', 'Race/color'),
    ('origin', 'National origin (including ancestry, ethnicity, and language)'),
    ('immigration', 'Immigration/citizenship status (choosing this does not share your status)'),
    ('religion', 'Religion'),
    ('gender', 'Sex or gender identity (including gender stereotypes) or pregnancy'),
    ('orientation', 'Sexual orientation'),
    ('family', 'Family, marriage, or parental status'),
    ('military', 'Military status'),
    ('age', 'Age'),
    ('genetic', 'Genetic information'),
    ('other', 'Other'),
)

PLACE_CHOICES = (
    ('home', 'Home, potential home, or services to help with purchasing a home (banks, lenders, or other financial services)'),
    ('workplace', 'Workplace or potential workplace'),
    ('school', 'Educational institution (school, university), education program or educational activity (after school program or workshop)'),
    ('place_of_worship', 'Place of worship'),
    ('store', 'Retail/commercial building (store, restaurant, hotel, nightclub, theater, gym, or other commercial space)'),
    ('public_space', 'Outdoor public space (including car, street, sidewalk, park)'),
    ('voting', 'Voting location or ballot (including mail-in ballots)'),
    ('healthcare', 'Healthcare facility (including mental health or long-term care)'),
    ('incarcerated', 'Prison, jail, or juvenile corrections facility, or while otherwise incarcerated'),
    ('government_building', 'Another government building (courthouse, DMV, post office)'),
)

PUBLIC_OR_PRIVATE_EMPLOYER_CHOICES = (
    ('public_employer', 'Public employer -- Funded by the government like a post office, fire department, courthouse, DMV, or public school. This could be at the local, state, or federal level.'),
    ('private_employer', 'Private employer -- Businesses or non-profits not funded by the government such as retail stores, banks, or restaurants.'),
    ('not_sure', 'I\'m not sure'),
)

EMPLOYER_SIZE_CHOICES = (
    ('14_or_less', 'Fewer than 15 employees'),
    ('15_or_more', '15 or more employees'),
)

PUBLIC_OR_PRIVATE_SCHOOL_CHOICES = (
    ('public', 'Public -- Schools or programs funded by local, state, or the federal government'),
    ('private', 'Private -- Schools or programs funded privately such as charter schools, magnet schools, or faith-based colleges'),
    ('not_sure', 'I\'m not sure'),
)

PUBLIC_OR_PRIVATE_FACILITY_CHOICES = (
    ('state_local_facility', 'State or local facility'),
    ('federal_facility', 'Federal facility'),
    ('private_facility', 'Private facility'),
    ('not_sure', 'Not sure'),
)

PUBLIC_OR_PRIVATE_HEALTHCARE_CHOICES = (
    ('state_local_facility', 'State or local facility'),
    ('federal_facility', 'Federal facility'),
    ('private_facility', 'Private facility'),
    ('not_sure', 'Not sure'),
)

RESPONDENT_TYPE_CHOICES = (
    ('employer', 'Employer or potential employer'),
    ('landlord', 'Landlord, leasing office, or home/rental provider'),
    ('police_corrections_staff', 'Police, prison guard, or other corrections staff'),
    ('other_public_official', 'Other public official (judge, voting official, or other government official)'),
    ('school', 'Individual(s) from school or educational program (teacher, administrator, staff, or students)'),
    ('healthcare', 'Healthcare provider or staff'),
    ('lender', 'Bank or loaning service'),
)

WHEN_CHOICES = (
    ('last_6_months', 'Within the last 6 months'),
    ('last_3_years', 'Within the last 3 years'),
    ('greater_than_3_years', 'More than 3 years ago'),
)

HOW_MANY_CHOICES = (
    ('no', 'No'),
    ('not_sure', 'I\'m not sure'),
    ('yes', 'Yes'),
)

WHO_FOR_CHOICES = (
    ('myself', 'I\'m reporting for myself'),
    ('another', 'I\'m reporting on behalf of another person'),
    ('undisclosed', 'I prefer not to disclose'),
)

RELATIONSHIP_CHOICES = (
    ('parent_guardian', 'I''m a parent or guardian of the person affected'),
    ('professional', 'I''m providing professional assistance'),
    ('witness to the situation', 'I''m a witness to the situation'),
)

STATES_AND_TERRITORIES = (
    ("AL", "Alabama "),
    ("AK", "Alaska "),
    ("AZ", "Arizona "),
    ("AR", "Arkansas "),
    ("CA", "California "),
    ("CO", "Colorado "),
    ("CT", "Connecticut "),
    ("DE", "Delaware "),
    ("DC", "District of Columbia "),
    ("FL", "Florida "),
    ("GA", "Georgia "),
    ("HI", "Hawaii "),
    ("ID", "Idaho "),
    ("IL", "Illinois "),
    ("IN", "Indiana "),
    ("IA", "Iowa "),
    ("KS", "Kansas "),
    ("KY", "Kentucky "),
    ("LA", "Louisiana "),
    ("ME", "Maine "),
    ("MD", "Maryland "),
    ("MA", "Massachusetts "),
    ("MI", "Michigan "),
    ("MN", "Minnesota "),
    ("MS", "Mississippi "),
    ("MO", "Missouri "),
    ("MT", "Montana "),
    ("NE", "Nebraska "),
    ("NV", "Nevada "),
    ("NH", "New Hampshire "),
    ("NJ", "New Jersey "),
    ("NM", "New Mexico "),
    ("NY", "New York "),
    ("NC", "North Carolina "),
    ("ND", "North Dakota "),
    ("OH", "Ohio "),
    ("OK", "Oklahoma "),
    ("OR", "Oregon "),
    ("PA", "Pennsylvania "),
    ("RI", "Rhode Island "),
    ("SC", "South Carolina "),
    ("SD", "South Dakota "),
    ("TN", "Tennessee "),
    ("TX", "Texas "),
    ("UT", "Utah "),
    ("VT", "Vermont "),
    ("VA", "Virginia "),
    ("WA", "Washington "),
    ("WV", "West Virginia "),
    ("WI", "Wisconsin "),
    ("WY", "Wyoming "),
    ("AS", "American Samoa "),
    ("GU", "Guam "),
    ("MP", "Northern Mariana Islands "),
    ("PR", "Puerto Rico "),
    ("VI", "Virgin Islands "),
    ("AE", "Armed Forces Africa "),
    ("AA", "Armed Forces Americas "),
    ("AE", "Armed Forces Canada "),
    ("AE", "Armed Forces Europe "),
    ("AE", "Armed Forces Middle East "),
    ("AP", "Armed Forces Pacific "),
)
