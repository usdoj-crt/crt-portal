"""Setting the variables that can be reused in models and forms for readability and reuse"""

from django.utils.translation import gettext_lazy as _

SERVICEMEMBER_CHOICES = (
    ('yes', _('Yes')),
    ('no', _('No')),
)

SERVICEMEMBER_ERROR = _('Please select a status as an active duty service member.')

PRIMARY_COMPLAINT_CHOICES = (
    ('workplace', _('Workplace discrimination or other employment-related problem')),
    ('housing', _('Housing discrimination or harassment')),
    ('education', _('Discrimination at a school, educational program, or related to receiving education')),
    ('voting', _('Right to vote impacted')),
    ('police', _('Mistreated by police, law enforcement, or correctional staff (including while in prison)')),
    ('commercial_or_public', _('Discriminated against in any other commercial location or public place')),
    ('something_else', _('Something else happened')),
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
        _('Denied service or entry because of a perceived personal characteristic like race, sex, or religion'),
        _('Blocked from receiving reproductive health services'),
    ],
    'something_else': []
}

ELECTION_CHOICES = (
    ('federal', _('Federal')),
    ('state_local', _('State or local')),
    ('both', _('Both')),
    ('unknown', _('I\'m not sure')),
)

HATE_CRIMES_TRAFFICKING_MODEL_CHOICES = (
    ('physical_harm', _('Physical harm or threats of violence based on race, color, national origin, religion, gender, sexual orientation, gender identity, or disability')),
    ('trafficking', _('Coerced or forced to do work or perform a commercial sex act')),
)

HATE_CRIMES_TRAFFICKING_CHOICES = (
    _('Physical harm or threats of violence based on race, color, national origin, religion, gender, sexual orientation, gender identity, or disability'),
    _('Coerced or forced to do work or perform a commercial sex act'),
)

# PROTECTED_CLASS_CHOICES means "PROTECTED_CLASS_FORM_CHOICES" and refers to the choices that will be displayed on the form front-end.
# See protected maintenance docs: https://github.com/usdoj-crt/crt-portal/blob/develop/docs/maintenance_or_infrequent_tasks.md#change-protected-class-options
# This tuple will create the initial order, the form_order data can be directly adjusted after the initial load.
PROTECTED_CLASS_CHOICES = (
    _('Race/color'),
    _('National origin (including ancestry and ethnicity)'),
    _('Immigration/citizenship status (choosing this will not share your status)'),
    _('Religion'),
    _('Sex or gender identity (including gender stereotypes) or pregnancy'),
    _('Sexual orientation'),
    _('Disability (including temporary or recovery)'),
    _('Language'),
    _('Family, marriage, or parental status'),
    _('Military status'),
    _('Age'),
    _('Genetic information'),
    _('None of these apply to me'),
    _('Other reason'),
)

# used in internal CRT view display
PROTECTED_CLASS_CODES = {
    'Disability (including temporary or recovery)': 'Disability',
    'Race/color': 'Race/color',
    'National origin (including ancestry and ethnicity)': 'National origin',
    'Immigration/citizenship status (choosing this will not share your status)': 'Immigration',
    'Religion': 'Religion',
    'Sex or gender identity (including gender stereotypes) or pregnancy': 'Sex',
    'Sexual orientation': 'Orientation',
    'Family, marriage, or parental status': 'Family status',
    'Military status': 'Military',
    'Age': 'Age',
    'Genetic information': 'Genetic',
    'Other reason': 'Other',
    'None of these apply to me': 'None',
    'Language': 'Language'
}

PROTECTED_MODEL_CHOICES = (
    ('disability', _('Disability (including temporary or recovery)')),
    ('race', _('Race/color')),
    ('origin', _('National origin (including ancestry and ethnicity)')),
    ('immigration', _('Immigration/citizenship status (choosing this will not share your status)')),
    ('religion', _('Religion')),
    ('gender', _('Sex or gender identity (including gender stereotypes) or pregnancy')),
    ('orientation', _('Sexual orientation')),
    ('family', _('Family, marriage, or parental status')),
    ('military', _('Military status')),
    ('age', _('Age')),
    ('genetic', _('Genetic information')),
    ('language', _('Language')),
    ('other', _('Other reason')),
    ('none', _('None of these apply to me')),
)

PROTECTED_CLASS_ERROR = _('Please make a selection to continue. If none of these apply to your situation, please select "Other reason" and explain.')

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

CORRECTIONAL_FACILITY_LOCATION_TYPE_CHOICES = (
    ('state_local', _('State/local')),
    ('federal', _('Federal')),
    ('private', _('Private')),
    ('not_sure', _('I\'m not sure'))
)

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

EMPLOYER_SIZE_CHOICES = (
    ('14_or_less', _('Fewer than 15 employees')),
    ('15_or_more', _('15 or more employees')),
    ('not_sure', _('I\'m not sure')),
)

PUBLIC_OR_PRIVATE_SCHOOL_CHOICES = (
    ('public', _('Public school or educational program')),
    ('private', _('Private school or educational program')),
    ('not_sure', _('I\'m not sure')),
)

PUBLIC_OR_PRIVATE_FACILITY_CHOICES = (
    ('state_local_facility', _('State or local facility')),
    ('federal_facility', _('Federal facility')),
    ('private_facility', _('Private facility')),
    ('not_sure', _('Not sure')),
)

PUBLIC_OR_PRIVATE_HEALTHCARE_CHOICES = (
    ('state_local_facility', _('State or local facility')),
    ('federal_facility', _('Federal facility')),
    ('private_facility', _('Private facility')),
    ('not_sure', _('Not sure')),
)

RESPONDENT_TYPE_CHOICES = (
    ('employer', _('Employer or potential employer')),
    ('landlord', _('Landlord, leasing office, or home/rental provider')),
    ('police_corrections_staff', _('Police, prison guard, or other corrections staff')),
    ('other_public_official', _('Other public official (judge, voting official, or other government official)')),
    ('school', _('Individual(s) from school or educational program (teacher, administrator, staff, or students)')),
    ('healthcare', _('Healthcare provider or staff')),
    ('lender', _('Bank or loaning service')),
)

WHO_FOR_CHOICES = (
    ('myself', _('I\'m reporting for myself')),
    ('another', _('I\'m reporting on behalf of another person')),
    ('undisclosed', _('I prefer not to disclose')),
)

RELATIONSHIP_CHOICES = (
    ('parent_guardian', _('I''m a parent or guardian of the person affected')),
    ('professional', _('I''m providing professional assistance')),
    ('witness to the situation', _('I''m a witness to the situation')),
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
