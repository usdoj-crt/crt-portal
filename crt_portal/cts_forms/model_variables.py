"""Setting the variables that can be reused in models and forms for readability and reuse"""

from django.utils.translation import gettext_lazy as _

EMPTY_CHOICE = ('', _('- Select -'))

SERVICEMEMBER_CHOICES = (
    ('yes', _('Yes')),
    ('no', _('No')),
)

SERVICEMEMBER_ERROR = _('Please select a status as an active duty service member.')

PRIMARY_COMPLAINT_CHOICES = (
    ('workplace', _('Workplace discrimination or other employment-related problem')),
    ('housing', _('Housing discrimination or harassment')),
    ('education', _('Discrimination at a school, educational program or service, or related to receiving education')),
    ('voting', _('Voting rights or ability to vote blocked or affected')),
    ('police', _('Mistreated by police, law enforcement, or correctional staff (including while in prison)')),
    ('commercial_or_public', _('Discriminated against in a commercial location or public place')),
    ('something_else', _('Something else happened')),
)
PRIMARY_COMPLAINT_DICT = dict(PRIMARY_COMPLAINT_CHOICES)

PRIMARY_COMPLAINT_CHOICES_TO_HELPTEXT = {
    'commercial_or_public': _('This could include a store, restaurant, bar, hotel, place of worship, library, medical facility, bank, courthouse, government building, public park or street, as well as online.'),
    'something_else': _('The examples above reflect some but not all of the civil rights violations that we address. Select this option if you don’t see an example that applies to your situation. You will be able to tell us more later.')
}

PRIMARY_COMPLAINT_CHOICES_TO_EXAMPLES = {
    'workplace': [
        _('Fired, not hired, or demoted for reasons unrelated to job performance or qualifications'),
        _('Retaliated against for reporting discrimination'),
        _('Inappropriately asked to provide immigration documentation'),
    ],
    'housing': [
        _('Denied housing, a permit, or a loan based on personal characteristics like race, sex, and/or having children under 18 years old'),
        _('Denied an accommodation for a disability, including not being allowed to have a service animal'),
        _('Harassment by a landlord or another tenant, including sexual harassment'),
    ],
    'education': [
        _('Harassment based on race, sex, national origin, disability, or religion'),
        _('Denied admission or segregated in an education program or activity'),
        _('Denied educational accommodations for a disability or language barrier'),
    ],
    'voting': [
        _('Blocked or prevented from registering to vote, obtaining or submitting a ballot, having your ballot counted, or entering a polling place to vote'),
        _('Denied adequate voting assistance or accommodations for a disability at a polling place'),
        _('Restricted or prevented from participating in an election, including voting, becoming a candidate, or being elected for office'),
    ],
    'police': [
        _('Police brutality or use of excessive force, including patterns of police misconduct'),
        _('Searched and arrested under false pretenses, including racial or other discriminatory profiling'),
        _('Denied rights while arrested or incarcerated'),
        _('Denied access to safe living conditions or accommodations for a disability, language barrier, or religious practice while incarcerated'),
    ],
    'commercial_or_public': [
        _('A physical or online location that does not provide disability accommodations'),
        _('Denied service or entry because of a perceived personal characteristic  like race, sex, or religion'),
        _('Threatened or harassed while seeking or receiving reproductive health services'),
    ],
    'something_else': []
}

ELECTION_CHOICES = (
    ('federal', _('Federal')),
    ('state_local', _('State or local')),
    ('both', _('Both')),
    ('unknown', _('I\'m not sure')),
)
ELECTION_DICT = dict(ELECTION_CHOICES)

HATE_CRIMES_TRAFFICKING_MODEL_CHOICES = (
    ('physical_harm', _('Physical harm or threats of violence based on race, color, national origin, religion, gender, sexual orientation, gender identity, or disability')),
    ('trafficking', _('Coerced or forced to do work or perform a sex act in exchange for something of value')),
)

HATE_CRIMES_TRAFFICKING_CHOICES = (
    _('Physical harm or threats of violence based on race, color, national origin, religion, gender, sexual orientation, gender identity, or disability'),
    _('Coerced or forced to do work or perform a sex act in exchange for something of value'),
)


# See protected maintenance docs: https://github.com/usdoj-crt/crt-portal/blob/develop/docs/maintenance_or_infrequent_tasks.md#change-protected-class-options
# This tuple will create the form_order, then lists a short code that we use for the model value and CRT display views, then the name as it will display on the form.
PROTECTED_CLASS_FIELDS = [
    # (form order, code, display name)
    (0, 'Age', _('Age')),
    (1, 'Disability', _('Disability (including temporary or recovery)')),
    (2, 'Family status', _('Family, marital, or parental status')),
    (3, 'Gender', _('Gender identity (including gender stereotypes)')),
    (4, 'Genetic', _('Genetic information (including family medical history)')),
    (5, 'Immigration', _('Immigration/citizenship status (choosing this will not share your status)')),
    (6, 'Language', _('Language')),
    (7, 'National origin', _('National origin (including ancestry and ethnicity)')),
    (8, 'Pregnancy', _('Pregnancy')),
    (9, 'Race/color', _('Race/color')),
    (10, 'Religion', _('Religion')),
    (11, 'Sex', _('Sex')),
    (12, 'Orientation', _('Sexual orientation')),
    (13, 'None', _('None of these apply to me')),
    (14, 'Other', _('Other reason')),
]
# PROTECTED_CLASS_CHOICES refers to the choices that will be displayed on the form front-end.
PROTECTED_CLASS_CHOICES = [field[2] for field in PROTECTED_CLASS_FIELDS]
# PROTECTED_MODEL_CHOICES are the constraints added to the database for acceptable answers.
PROTECTED_MODEL_CHOICES = tuple(
    (field[1].lower().replace(' ', '_'), field[2]) for field in PROTECTED_CLASS_FIELDS
)

PROTECTED_CLASS_ERROR = _('Please make a selection to continue. If none of these apply to your situation, please select “None of these apply to me” or "Other reason"and explain.')

STATUS_CHOICES = (
    ('new', _('New')),
    ('open', _('Open')),
    ('closed', _('Closed')),
)

SECTION_CHOICES = (
    ('ADM', _('Administrative')),
    ('APP', _('Appellate')),
    ('CRM', _('Criminal')),
    ('DRS', _('Disability')),
    ('ELS', _('Employment Litigation Services')),
    ('EOS', _('Education')),
    ('FCS', _('Federal Coordination and Compliance')),
    ('HCE', _('Housing')),
    ('IER', _('Immigrant and Employee Rights')),
    ('SPL', _('Special Litigation')),
    ('VOT', _('Voting')),
)

COMMERCIAL_OR_PUBLIC_PLACE_CHOICES = (
    ('place_of_worship', _('Place of worship or about a place of worship')),
    ('store', _('Commercial or retail building')),
    ('healthcare', _('Healthcare facility')),
    ('financial', _('Financial institution')),
    ('public_space', _('Public space')),
    ('other', _('Other'))
)
COMMERCIAL_OR_PUBLIC_PLACE_DICT = dict(COMMERCIAL_OR_PUBLIC_PLACE_CHOICES)
COMMERCIAL_OR_PUBLIC_ERROR = _('Please select the type of location. If none of these apply to your situation, please select "Other".')

COMMERCIAL_PUBLIC_FRIENDLY_TEXT = {
    'place_of_worship': _('Place of worship'),
    'store': _('Commercial'),
    'healthcare': _('Healthcare facility'),
    'financial': _('Financial institution'),
    'public_space': _('Public outdoor space'),
}

COMMERCIAL_OR_PUBLIC_PLACE_HELP_TEXT = {
    'place_of_worship': _('Church, synagogue, temple, religious community center'),
    'store': _('Store, restaurant, bar, hotel, theate'),
    'healthcare': _('Hospital or clinic (including inpatient and outpatient programs), reproductive care clinic, state developmental institution, nursing home'),
    'financial': _('Bank, credit union, loan services'),
    'public_space': _('Park, sidewalk, street, other public buildings (courthouse, DMV, city library)'),
    'other': ''
}

CORRECTIONAL_FACILITY_LOCATION_CHOICES = (
    ('outside', _('Outside a prison or correctional facility')),
    ('inside', _('Inside a prison or correctional facility'))
)
CORRECTIONAL_FACILITY_LOCATION_DICT = dict(CORRECTIONAL_FACILITY_LOCATION_CHOICES)

CORRECTIONAL_FACILITY_LOCATION_TYPE_CHOICES = (
    ('state_local', _('State/local')),
    ('federal', _('Federal')),
    ('private', _('Private')),
    ('not_sure', _('I\'m not sure'))
)
CORRECTIONAL_FACILITY_LOCATION_TYPE_DICT = dict(CORRECTIONAL_FACILITY_LOCATION_TYPE_CHOICES)

CORRECTIONAL_FACILITY_FRIENDLY_TEXT = {
    'outside': _('Outside of prison'),
    'state_local': 'Prison (State/local)',
    'federal': _('Prison (Federal)'),
    'private': _('Prison (Private)'),
    'not_sure': _('Prison (I\'m not sure)'),
}

PUBLIC_OR_PRIVATE_EMPLOYER_CHOICES = (
    ('public_employer', _('Public employer')),
    ('private_employer', _('Private employer')),
    ('not_sure', _('I\'m not sure')),
)
PUBLIC_OR_PRIVATE_EMPLOYER_DICT = dict(PUBLIC_OR_PRIVATE_EMPLOYE
    R_CHOICES)
PUBLIC_OR_PRIVATE_EMPLOYER_ERROR = _('Please select what type of employer this is.')

EMPLOYER_SIZE_CHOICES = (
    ('14_or_less', _('Fewer than 15 employees')),
    ('15_or_more', _('15 or more employees')),
    ('not_sure', _('I\'m not sure')),
)
EMPLOYER_SIZE_DICT = dict(EMPLOYER_SIZE_CHOICES)
EMPLOYER_SIZE_ERROR = _('Please select how large the employer is.')

EMPLOYER_FRIENDLY_TEXT = {
    'public_employer': _('Public'),
    'private_employer': _('Private'),
    'not_sure': _('Not sure'),
    '14_or_less': _('Less than 15'),
    '15_or_more': _('15 or more'),
}

PUBLIC_OR_PRIVATE_SCHOOL_CHOICES = (
    ('public', _('Public school or educational program')),
    ('private', _('Private school or educational program')),
    ('not_sure', _('I\'m not sure')),
)
PUBLIC_OR_PRIVATE_SCHOOL_DICT = dict(PUBLIC_OR_PRIVATE_SCHOOL_CHOICES)

WHO_FOR_CHOICES = (
    ('myself', _('I\'m reporting for myself')),
    ('another', _('I\'m reporting on behalf of another person')),
    ('undisclosed', _('I prefer not to disclose')),
)

STATES_AND_TERRITORIES = (
    ('AL', _('Alabama')),
    ('AK', _('Alaska')),
    ('AZ', _('Arizona')),
    ('AR', _('Arkansas')),
    ('CA', _('California')),
    ('CO', _('Colorado')),
    ('CT', _('Connecticut')),
    ('DE', _('Delaware')),
    ('DC', _('District of Columbia')),
    ('FL', _('Florida')),
    ('GA', _('Georgia')),
    ('HI', _('Hawaii')),
    ('ID', _('Idaho')),
    ('IL', _('Illinois')),
    ('IN', _('Indiana')),
    ('IA', _('Iowa')),
    ('KS', _('Kansas')),
    ('KY', _('Kentucky')),
    ('LA', _('Louisiana')),
    ('ME', _('Maine')),
    ('MD', _('Maryland')),
    ('MA', _('Massachusetts')),
    ('MI', _('Michigan')),
    ('MN', _('Minnesota')),
    ('MS', _('Mississippi')),
    ('MO', _('Missouri')),
    ('MT', _('Montana')),
    ('NE', _('Nebraska')),
    ('NV', _('Nevada')),
    ('NH', _('New Hampshire')),
    ('NJ', _('New Jersey')),
    ('NM', _('New Mexico')),
    ('NY', _('New York')),
    ('NC', _('North Carolina')),
    ('ND', _('North Dakota')),
    ('OH', _('Ohio')),
    ('OK', _('Oklahoma')),
    ('OR', _('Oregon')),
    ('PA', _('Pennsylvania')),
    ('RI', _('Rhode Island')),
    ('SC', _('South Carolina')),
    ('SD', _('South Dakota')),
    ('TN', _('Tennessee')),
    ('TX', _('Texas')),
    ('UT', _('Utah')),
    ('VT', _('Vermont')),
    ('VA', _('Virginia')),
    ('WA', _('Washington')),
    ('WV', _('West Virginia')),
    ('WI', _('Wisconsin')),
    ('WY', _('Wyoming')),
    ('AS', _('American Samoa')),
    ('GU', _('Guam')),
    ('MP', _('Northern Mariana Islands')),
    ('PR', _('Puerto Rico')),
    ('VI', _('Virgin Islands')),
    ('AE', _('Armed Forces Africa')),
    ('AA', _('Armed Forces Americas')),
    ('AE', _('Armed Forces Canada')),
    ('AE', _('Armed Forces Europe')),
    ('AE', _('Armed Forces Middle East')),
    ('AP', _('Armed Forces Pacific')),
)

VIOLATION_SUMMARY_ERROR = _('Please provide description to continue')
PRIMARY_COMPLAINT_ERROR = _('Please select a primary reason to continue.')

WHERE_ERRORS = (
    ('location_name', _('Please enter the name of the location where this took place.')),
    ('location_city_town', _('Please enter the city or town where this took place.')),
    ('location_state', _('Please select the state where this took place.')),
)

POLICE_LOCATION_ERRORS = {
    'facility': _('Please select where this occurred'),
    'facility_type': _('Please select the type of location'),
}

# for internal use only
INTAKE_FORMAT_CHOICES = (
    ('web', 'web'),
    ('letter', 'letter'),
    ('phone', 'phone'),
    ('fax', 'fax'),
    ('email', 'email'),
)

INCIDENT_DATE_HELPTEXT = _('If this happened over a period of time or is still happening, please provide the most recent date. Please use the format MM/DD/YYYY.')

DATE_ERRORS ={
    'month_required': _('Please enter a month.'),
    'month_invalid': _('Please enter a valid day of the month. Day must be between 1 and the last day of the month.'),
    'year_required': _('Please enter a year.'),
    'no_future': _('Date can not be in the future.'),
    'no_past': _('Please enter a year after 1900.'),
    'not_valid': _('Please enter a valid date format. Use format MM/DD/YYYY.'),
}

VOTING_ERROR = _('Please select the type of election or voting activity.')
