"""Setting the variables that can be reused in models and forms for readability and reuse"""

from django.utils.translation import gettext as _

PRIMARY_COMPLAINT_CHOICES = (
    ('workplace', _('Workplace discrimination or other employment-related problem')),
    ('housing', _('Housing discrimination or harassment')),
    ('education', _('Discrimination at a school, educational program, or related to receiving education')),
    ('voting', _('Right to vote impacted')),
    ('police', _('Mistreated by police, law enforcement, or correctional staff (including while in prison)')),
    ('commercial_or_public', _('Discriminated against in any other commercial location or public place')),
    ('something_else', _('Something else happened'))
)

PRIMARY_COMPLAINT_CHOICES_TO_HELPTEXT = {
    'commercial_or_public': _('Store, restaurant, bar, hotel, place of worship, library, medical facility, bank, courthouse, government buildings, public park or street, or online'),
    'something_else': _('You will be able to tell us more later')
}

PRIMARY_COMPLAINT_CHOICES_TO_EXAMPLES = {
    'workplace': [
        _('Fired, not hired, or demoted for reasons unrelated to job performance or qualifications'),
        _('Retaliated against for reporting discrimination'),
        _('Inappropriately asked to provide immigration documentation'),
    ],
    'housing': [
        _('Denied housing, a permit, or a loan'),
        _('Harmful living conditions or lack accommodations for disability'),
        _('Harassment by a landlord or another tenant'),
    ],
    'education': [
        _('Harassment based on race, sex, national origin, disability, or religion'),
        _('Denied admission or segregated in an education program or activity'),
        _('Denied services or accommodations for a disability or language barrier'),
    ],
    'voting': [
        _('Blocked from registering to vote, entering a polling place to vote, or any other voting activity'),
        _('Lack of polling place accommodations for disability'),
        _('Ballot tampering'),
    ],
    'police': [
        _('Police brutality or use of excessive force, including patterns of police misconduct'),
        _('Searched and arrested under false pretenses, including racial or other discriminatory profiling'),
        _('Denied rights, language access barriers, subjected to harmful living conditions or lack of accessible facilities'),
    ],
    'commercial_or_public': [
        _('A location or website lacking disability accommodations'),
        _('Denied service or entry because of a perceived personal characteristic like race, sex, or religion')
        _('Blocked from receiving reproductive health services'),
    ],
    'something_else': []
}

# This will create the initial order, the form_order data can be directly adjusted after the initial load.
# See protected maintenance docs: https://github.com/usdoj-crt/crt-portal/blob/develop/docs/maintenance_or_infrequent_tasks.md#change-protected-class-options
PROTECTED_CLASS_CHOICES = (
    'Disability (including temporary or recovery)',
    'Race/color',
    'National origin (including ancestry, ethnicity, and language)',
    'Immigration/citizenship status (choosing this will not share your status)',
    'Religion',
    'Sex or gender identity (including gender stereotypes) or pregnancy',
    'Family, marriage, or parental status',
    'Sexual orientation',
    'Military status',
    'Age',
    'Genetic information',
    'Other reason',
)

# used in internal CRT view display
PROTECTED_CLASS_CODES = {
    'Disability (including temporary or recovery)': 'Disability',
    'Race/color': 'Race/color',
    'National origin (including ancestry, ethnicity, and language)': 'National origin',
    'Immigration/citizenship status (choosing this will not share your status)': 'Immigration',
    'Religion': 'Religion',
    'Sex or gender identity (including gender stereotypes) or pregnancy': 'Sex',
    'Sexual orientation': 'Orientation',
    'Family, marriage, or parental status': 'Family status',
    'Military status': 'Military',
    'Age': 'Age',
    'Genetic information': 'Genetic',
    'Other reason': 'Other',
}

PROTECTED_MODEL_CHOICES = (
    ('disability', 'Disability (including temporary or recovery)'),
    ('race', 'Race/color'),
    ('origin', 'National origin (including ancestry, ethnicity, and language)'),
    ('immigration', 'Immigration/citizenship status (choosing this will not share your status)'),
    ('religion', 'Religion'),
    ('gender', 'Sex or gender identity (including gender stereotypes) or pregnancy'),
    ('orientation', 'Sexual orientation'),
    ('family', 'Family, marriage, or parental status'),
    ('military', 'Military status'),
    ('age', 'Age'),
    ('genetic', 'Genetic information'),
    ('other', 'Other reason'),
)

PROTECTED_CLASS_ERROR = 'Please make a selection to continue. If none of these apply to your situation, please select "Other reason" and explain.'

STATUS_CHOICES = (
    ('new', 'New'),
    ('open', 'Open'),
    ('closed', 'Closed'),
)

SECTION_CHOICES = (
    ('ADM', 'Administrative'),
    ('IER', 'Immigrant and Employee Rights'),
    ('VOT', 'Voting'),
    ('DRS', 'Disability'),
    ('CRM', 'Criminal'),
    ('HCE', 'Housing'),
    ('EOS', 'Education'),
    ('SPL', 'Special Litigation'),
    ('ELS', 'Employment Litigation Services'),
    ('FCS', 'Federal Coordination and Compliance'),
    ('APP', 'Appellate'),
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
