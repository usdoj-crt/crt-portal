"""Setting the variables that can be reused in models and forms for readability and reuse"""

from django.utils.translation import gettext_lazy as _

# Translators: This is used as a an empty selection default for drop down menus
EMPTY_CHOICE = _('- Select -')

SERVICEMEMBER_CHOICES = (
    ('yes', _('Yes')),
    ('no', _('No')),
)

SERVICEMEMBER_ERROR = _('Please select a status as an active duty service member.')

PRIMARY_COMPLAINT_CHOICES = (

    ('workplace', _('Workplace discrimination or other employment-related problem')),
    ('housing', _('Housing discrimination or harassment')),
    ('education', _('Discrimination at a school, educational program or service, or related to receiving education')),
    ('police', _('Mistreated by police, correctional staff, or inmates')),
    ('voting', _('Voting rights or ability to vote affected')),
    ('commercial_or_public', _('Discriminated against in a commercial location or public place')),
    ('something_else', _('Something else happened')),
)
PRIMARY_COMPLAINT_DICT = dict(PRIMARY_COMPLAINT_CHOICES)

PRIMARY_COMPLAINT_CHOICES_VOTING = (
    ('voting', _('Voting rights or ability to vote affected')),
    ('workplace', _('Workplace discrimination or other employment-related problem')),
    ('housing', _('Housing discrimination or harassment')),
    ('education', _('Discrimination at a school, educational program or service, or related to receiving education')),
    ('police', _('Mistreated by police, correctional staff, or inmates')),
    ('commercial_or_public', _('Discriminated against in a commercial location or public place')),
    ('something_else', _('Something else happened')),
)
PRIMARY_COMPLAINT_DICT_VOTING = dict(PRIMARY_COMPLAINT_CHOICES)

PRIMARY_COMPLAINT_PROFORM_CHOICES = (
    ('workplace', 'Workplace Discrimination'),
    ('housing', 'Housing Discrimination'),
    ('education', 'Education Discrimination'),
    ('voting', 'Voting Discrimination'),
    ('police', 'Police / Correctional Misconduct'),
    ('commercial_or_public', 'Commercial / Public Discrimination'),
    ('something_else', 'Something else'),
)

PRIMARY_COMPLAINT_PROFORM_CHOICES_VOTING = (
    ('voting', 'Voting Discrimination'),
    ('workplace', 'Workplace Discrimination'),
    ('housing', 'Housing Discrimination'),
    ('education', 'Education Discrimination'),
    ('police', 'Police / Correctional Misconduct'),
    ('commercial_or_public', 'Commercial / Public Discrimination'),
    ('something_else', 'Something else'),
)

LANDING_COMPLAINT_CHOICES = (
    ('hate_crime', _('Victim of a hate crime')),
    ('human_trafficking', _('Victim of human trafficking')),
)
LANDING_COMPLAINT_DICT = dict(LANDING_COMPLAINT_CHOICES)

PRIMARY_COMPLAINT_CHOICES_TO_HELPTEXT = {
    'commercial_or_public': _('This could include a store, restaurant, bar, hotel, place of worship, library, medical facility, bank, courthouse, government building, public park or street, as well as online.'),
    'something_else': _('The examples above reflect some but not all of the civil rights violations that we address. Select this option if you don’t see an example that applies to your situation. You will be able to tell us more later.'),
    'police': _('(Including while in prison)')
}
LANDING_COMPLAINT_CHOICES_TO_HELPTEXT = {
    'hate_crime': _('To potentially be a hate crime, the situation must include physical harm, or attempts to cause harm with a dangerous weapon, because of race, color, national origin, religion, gender, sexual orientation, gender identity, or disability.  Threats of force or physical harm because of race, color, religion or national origin are also potential hate crimes.'),
    'human_trafficking': _('Human trafficking is when someone is forced into labor or sex work for profit. This can happen in many types of work that include, for example: agriculture, domestic work, restaurants, cleaning services, and sex work.')
}

PRIMARY_COMPLAINT_CHOICES_TO_EXAMPLES = {
    'workplace': [
        _('Fired, not hired, or demoted for reasons unrelated to job performance or qualifications'),
        _('Retaliated against for reporting discrimination'),
        _('Inappropriately asked to provide immigration documentation'),
        _('Denied reemployment or fired based on military service'),
        _('Denied an accommodation for a disability, including not being allowed to have a service animal <strong>in the workplace</strong>'),
    ],
    'housing': [
        _('Denied housing, a permit, or a loan based on personal characteristics like race, sex, and/or having children under 18 years old'),
        _('Harassment by a landlord or another tenant, including sexual harassment'),
        _('Challenges with terminating a lease due to military status change'),
        _('Denied an accommodation for a disability, including not being allowed to have a service or assistance animal <strong>in public housing</strong>'),
    ],
    'education': [
        _('Harassment based on race, sex, national origin, disability, or religion'),
        _('Denied admission or segregated in an education program or activity'),
        _('Denied educational accommodations for a disability or language barrier'),
    ],
    'voting': [
        _('Obstacles to registering to vote, obtaining or submitting a ballot, having your ballot counted, or entering a polling place to vote'),
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
        _('Denied service or entry because of a perceived personal characteristic like race, sex, or religion'),
        _('Denied an accommodation for a disability, including not being allowed to have a service animal <strong>in a commercial or public location</strong>'),
    ],
    'something_else': []
}
PRIMARY_COMPLAINT_CHOICES_TO_EXAMPLES_VOTING = {
    'voting': [
        _('Obstacles to registering to vote, obtaining or submitting a ballot, having your ballot counted, or entering a polling place to vote'),
        _('Denied adequate voting assistance or accommodations for a disability at a polling place'),
        _('Restricted or prevented from participating in an election, including voting, becoming a candidate, or being elected for office'),
    ],
    'workplace': [
        _('Fired, not hired, or demoted for reasons unrelated to job performance or qualifications'),
        _('Retaliated against for reporting discrimination'),
        _('Inappropriately asked to provide immigration documentation'),
        _('Denied reemployment or fired based on military service'),
        _('Denied an accommodation for a disability, including not being allowed to have a service animal <strong>in the workplace</strong>'),
    ],
    'housing': [
        _('Denied housing, a permit, or a loan based on personal characteristics like race, sex, and/or having children under 18 years old'),
        _('Harassment by a landlord or another tenant, including sexual harassment'),
        _('Challenges with terminating a lease due to military status change'),
        _('Denied an accommodation for a disability, including not being allowed to have a service or assistance animal <strong>in public housing</strong>'),
    ],
    'education': [
        _('Harassment based on race, sex, national origin, disability, or religion'),
        _('Denied admission or segregated in an education program or activity'),
        _('Denied educational accommodations for a disability or language barrier'),
    ],
    'police': [
        _('Police brutality or use of excessive force, including patterns of police misconduct'),
        _('Searched and arrested under false pretenses, including racial or other discriminatory profiling'),
        _('Denied rights while arrested or incarcerated'),
        _('Denied access to safe living conditions or accommodations for a disability, language barrier, or religious practice while incarcerated'),
    ],
    'commercial_or_public': [
        _('A physical or online location that does not provide disability accommodations'),
        _('Denied service or entry because of a perceived personal characteristic like race, sex, or religion'),
        _('Denied an accommodation for a disability, including not being allowed to have a service animal <strong>in a commercial or public location</strong>'),
    ],
    'something_else': []
}
LANDING_COMPLAINT_CHOICES_TO_EXAMPLES = {
    'hate_crime': [
        _('Physical attack causing injury, or an attempt to cause injury with a dangerous weapon, because of the above characteristics'),
        _('Attacks, threats of violence, or destruction of property at place of worship (ie: shooting, arson, bombing, smashing windows, writing slurs)'),
    ],
    'human_trafficking': [
        _('Coerced into working through threats of harm or deportation, psychological manipulation, debt manipulation, document confiscation, or confinement'),
        _('Forced into sex work for profit through physical abuse or assault, sexual abuse or assault, other threats of harm, or confinement'),
    ]
}

ELECTION_CHOICES = (
    ('federal', _('Federal')),
    ('state_local', _('State or local')),
    # Translators: Both state, federal and local elections
    ('both', _('Both')),
    ('unknown', _('I\'m not sure')),
)
ELECTION_DICT = dict(ELECTION_CHOICES)

# preserving archival data
HATE_CRIMES_TRAFFICKING_MODEL_CHOICES = (
    ('physical_harm', _('Physical harm or threats of violence based on race, color, national origin, religion, gender, sexual orientation, gender identity, or disability')),
    ('trafficking', _('Threatened, forced, and held against your will for the purposes of performing work or commercial sex acts. This could include threats of physical harm, withholding promised wages, or being held under a false work contract')),
)
HATE_CRIMES_TRAFFICKING_CHOICES = [choice[1] for choice in HATE_CRIMES_TRAFFICKING_MODEL_CHOICES]

# This it the one in use
HATE_CRIME_CHOICES = (
    ('yes', _('Yes')),
    ('no', _('No')),
)

# See protected maintenance docs: https://github.com/usdoj-crt/crt-portal/blob/develop/docs/maintenance_or_infrequent_tasks.md#change-protected-class-options
# This tuple will create the form_order, then lists a short code that we use for the model value and CRT display views, then the name as it will display on the form.
PROTECTED_CLASS_FIELDS = [
    # (form order, code, display name)
    (0, 'Age', _('Age')),
    (1, 'Disability', _('Disability (including temporary or recovered and including HIV and drug addiction)')),
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

# CRT views only
NEW_STATUS = 'new'
OPEN_STATUS = 'open'
CLOSED_STATUS = 'closed'
STATUS_CHOICES = (
    (NEW_STATUS, 'New'),
    (OPEN_STATUS, 'Open'),
    (CLOSED_STATUS, 'Closed'),
)

# CRT views only
SECTION_CHOICES = (
    ('ADM', 'Administrative'),
    ('APP', 'Appellate'),
    ('CRM', 'Criminal'),
    ('DRS', 'Disability Rights'),
    ('ELS', 'Employment Litigation'),
    ('EOS', 'Educational Opportunities'),
    ('FCS', 'Federal Coordination and Compliance'),
    ('HCE', 'Housing and Civil Enforcement'),
    ('IER', 'Immigrant and Employee Rights'),
    ('POL', 'Policy'),    # Added to support SVI related report
    ('SPL', 'Special Litigation'),
    ('VOT', 'Voting'),
)
# for form letter translations only. Note that these choices
# technically differ from section choices since they have "de" (of).
#  Spanish
SECTION_CHOICES_ES = (
    ('ADM', 'Administrativa'),
    ('APP', 'de Apelación'),
    ('CRM', 'Penal'),
    ('DRS', 'de Derechos en Razón a Discapacidad'),
    ('ELS', 'de Litigios Laborales'),
    ('EOS', 'de Oportunidades Educativas'),
    ('FCS', 'de Coordinación y Cumplimiento Federal'),
    ('HCE', 'de Coordinación y Cumplimiento Federal'),
    ('IER', 'de Derechos de Inmigrantes y Empleados'),
    ('POL', 'de Políticas'),    # Added to support SVI related report form letter
    ('SPL', 'de Litigios Especiales'),
    ('VOT', 'de Votación'),
)

#  Korean
SECTION_CHOICES_KO = (
    ('ADM', '행정'),
    ('CRM', '형사'),
    ('DRS', '장애인 권리'),
    ('ELS', '고용 소송'),
    ('EOS', '교육 기회'),
    ('FCS', '연방 조정 및 규정준수'),
    ('HCE', '주택 및 민법 시행'),
    ('IER', '이민 및 직원 권리'),
    ('POL', '정책 섹션'),    # Added to support SVI related report form letters
    ('SPL', '특별 소송'),
    ('VOT', '투표'),
)

#  Tagalog
SECTION_CHOICES_TL = (
    ('ADM', 'Pang-Administratibo'),
    ('CRM', 'Kriminal'),
    ('DRS', 'Mga Karapatan ng May Kapansanan'),
    ('ELS', 'Paglilitis sa Trabaho'),
    ('EOS', 'Mga Oportunidad sa Edukasyon'),
    ('FCS', 'Pederal na Koordinasyon at Pagsunod'),
    ('HCE', 'Pabahay at Pagpapatupad ng Sibil'),
    ('IER', 'Imigrasyon at Mga Karapatan ng Empleyado'),
    ('POL', 'Patakaran'),    # Added to support SVI related report
    ('SPL', 'Espesyal na Paglilitis'),
    ('VOT', 'Pagboto'),
)

SECTION_CHOICES_VI = (
    ('ADM', 'Ban Hành Chánh'),
    ('CRM', 'Ban Hình Sự'),
    ('DRS', 'Ban Quyền của Người Khuyết Tật'),
    ('ELS', 'Ban Tranh Tụng về Bất những vấn đề/bất công trong Việc Làm'),
    ('EOS', 'Ban Cơ Hội Được Giáo Dục tốt'),
    ('FCS', 'Ban Tuân Thủ và Điều Phối Liên Bang'),
    ('HCE', 'Ban Gia Cư và Thực Thi Dân Sự'),
    ('IER', 'Ban  Di Trú và Quyền của Người Lao Động'),
    ('POL', 'Ban Phần Chính Sách'),    # Added to support SVI related report
    ('SPL', 'Ban Tố Tụng Đặc Biệt'),
    ('VOT', 'Ban Bầu Cử'),
)

#  Chinese Traditional
SECTION_CHOICES_ZH_HANT = (
    ('ADM', '行政管理'),
    ('CRM', '刑事'),
    ('DRS', '残疾權利'),
    ('ELS', '就業訴訟'),
    ('EOS', '教育机會'),
    ('FCS', '聮邦恊调與遵守'),
    ('HCE', '住房和民事执法'),
    ('IER', '移民與雇員權利'),
    ('POL', '政策部分'),    # Added to support SVI related report form letter
    ('SPL', '特别訴訟'),
    ('VOT', '投票'),
)

#  Chinese Simplified
SECTION_CHOICES_ZH_HANS = (
    ('ADM', '行政管理'),
    ('CRM', '刑事'),
    ('DRS', '残疾权利'),
    ('ELS', '就业诉讼'),
    ('EOS', '教育机会'),
    ('FCS', '联邦协调与遵守'),
    ('HCE', '住房和民事执法'),
    ('IER', '移民与雇员权利'),
    ('POL', '政策部分'),    # Added to support SVI related report form letter
    ('SPL', '特别诉讼'),
    ('VOT', '投票'),
)

# CRT view global section filter
SECTION_CHOICES_WITHOUT_LABELS = tuple([(key[0], key[0]) for key in SECTION_CHOICES])

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
    'store': _('Store, restaurant, bar, hotel, theater'),
    'healthcare': _('Hospital or clinic (including inpatient and outpatient programs), reproductive care clinic, state developmental institution, nursing home'),
    'financial': _('Bank, credit union, loan services'),
    'public_space': _('Park, sidewalk, street, other public buildings (courthouse, DMV, city library)'),
    'other': ''
}

CORRECTIONAL_FACILITY_LOCATION_CHOICES = (
    ('outside', _('No')),
    ('inside', _('Yes'))
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
PUBLIC_OR_PRIVATE_EMPLOYER_DICT = dict(PUBLIC_OR_PRIVATE_EMPLOYER_CHOICES)
PUBLIC_OR_PRIVATE_EMPLOYER_ERROR = _('Please select what type of employer this is.')

EMPLOYER_SIZE_CHOICES = (
    ('14_or_less', _('Fewer than 15 employees')),
    ('15_or_more', _('15 or more employees')),
    ('not_sure', _('I\'m not sure')),
)
EMPLOYER_SIZE_DICT = dict(EMPLOYER_SIZE_CHOICES)
EMPLOYER_SIZE_ERROR = _('Please select how large the employer is.')

# CRT views only
EMPLOYER_FRIENDLY_TEXT = {
    'public_employer': 'Public',
    'private_employer': 'Private',
    'not_sure': 'Not sure',
    '14_or_less': 'Less than 15',
    '15_or_more': '15 or more',
}

PUBLIC_OR_PRIVATE_SCHOOL_CHOICES = (
    ('public', _('Public school or educational program')),
    ('private', _('Private school or educational program')),
    ('not_sure', _('I\'m not sure')),
)
PUBLIC_OR_PRIVATE_SCHOOL_DICT = dict(PUBLIC_OR_PRIVATE_SCHOOL_CHOICES)

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
INTAKE_FORMAT_ERROR = 'Please select an intake format'  # Proform only, no translation needed

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
    ('web', 'Web'),
    ('letter', 'Letter'),
    ('phone', 'Phone'),
    ('fax', 'Fax'),
    ('email', 'Email'),
)

INCIDENT_DATE_HELPTEXT = _('You must enter a month and year. Please use the format MM/DD/YYYY.')

DATE_ERRORS = {
    'month_required': _('Please enter a month.'),
    'month_invalid': _('Please enter a valid month. Month must be between 1 and 12.'),
    'day_required': 'Please enter a day.',  # Proform only, no translation needed
    'day_invalid': _('Please enter a valid day of the month. Day must be between 1 and the last day of the month.'),
    'year_required': _('Please enter a year.'),
    'no_future': _('Date can not be in the future.'),
    'no_past': _('Please enter a year after 1900.'),
    'crt_no_past': 'Please enter a year after 1999.',  # Proform only, no translation needed
    'not_valid': _('Please enter a valid date. Use format MM/DD/YYYY.'),
    'crt_not_valid': 'Please use a valid date.',  # Proform only, no translation needed
}

VOTING_ERROR = _('Please select the type of election or voting activity.')

# for internal use only
DISTRICT_CHOICES = (
    ('1', '1 - Alabama - ND'),
    ('2', '2 - Alabama - MD'),
    ('3', '3 - Alabama - SD'),
    ('6', '6 - Alaska'),
    ('8', '8 - Arizona'),
    ('9', '9 - Arkansas - ED'),
    ('10', '10 - Arkansas - WD'),
    ('11', '11 - California - ND'),
    ('11E', '11E - California - ED'),
    ('12', '12 - California - SD'),
    ('12C', '12C - California - CD'),
    ('13', '13 - Colorado'),
    ('14', '14 - Connecticut'),
    ('15', '15 - Delaware'),
    ('16', '16 - District of Columbia'),
    ('17', '17 - Florida - ND'),
    ('17M', '17M - Florida - MD'),
    ('18', '18 - Florida - SD'),
    ('19', '19 - Georgia - ND'),
    ('19M', '19M - Georgia - MD'),
    ('20', '20 - Georgia - SD'),
    ('21', '21 - Hawaii'),
    ('22', '22 - Idaho'),
    ('23', '23 - Illinois - ND'),
    ('24', '24 - Illinois - CD'),
    ('25', '25 - Illinois - SD'),
    ('26', '26 - Indiana - ND'),
    ('26S', '26S - Indiana - SD'),
    ('27', '27 - Iowa - ND'),
    ('28', '28 - Iowa - SD'),
    ('29', '29 - Kansas'),
    ('30', '30 - Kentucky - ED'),
    ('31', '31 - Kentucky - WD'),
    ('32', '32 - Louisiana - ED'),
    ('32M', '32M - Louisiana - MD'),
    ('33', '33 - Louisiana - WD'),
    ('34', '34 - Maine'),
    ('35', '35 - Maryland'),
    ('36', '36 - Massachusetts'),
    ('37', '37 - Michigan - ED'),
    ('38', '38 - Michigan - WD'),
    ('39', '39 - Minnesota'),
    ('40', '40 - Mississippi - ND'),
    ('41', '41 - Mississippi - SD'),
    ('42', '42 - Missouri - ED'),
    ('43', '43 - Missouri - WD'),
    ('44', '44 - Montana'),
    ('45', '45 - Nebraska'),
    ('46', '46 - Nevada'),
    ('47', '47 - New Hampshire'),
    ('48', '48 - New Jersey'),
    ('49', '49 - New Mexico'),
    ('50', '50 - New York - ND'),
    ('51', '51 - New York - SD'),
    ('52', '52 - New York - ED'),
    ('53', '53 - New York - WD'),
    ('54', '54 - North Carolina - ED'),
    ('54M', '54M - North Carolina - MD'),
    ('55', '55 - North Carolina - WD'),
    ('56', '56 - North Dakota'),
    ('57', '57 - Ohio - ND'),
    ('58', '58 - Ohio - SD'),
    ('59', '59 - Oklahoma - ED'),
    ('59N', '59N - Oklahoma - ND'),
    ('60', '60 - Oklahoma - WD'),
    ('61', '61 - Oregon'),
    ('62', '62 - Pennsylvania - ED'),
    ('63', '63 - Pennsylvania - MD'),
    ('64', '64 - Pennsylvania - WD'),
    ('65', '65 - Puerto Rico'),
    ('66', '66 - Rhode Island'),
    ('67', '67 - South Carolina'),
    ('69', '69 - South Dakota'),
    ('70', '70 - Tennessee - ED'),
    ('71', '71 - Tennessee - MD'),
    ('72', '72 - Tennessee - WD'),
    ('73', '73 - Texas - ND'),
    ('74', '74 - Texas - SD'),
    ('75', '75 - Texas - ED'),
    ('76', '76 - Texas - WD'),
    ('77', '77 - Utah'),
    ('78', '78 - Vermont'),
    ('79', '79 - Virginia - ED'),
    ('80', '80 - Virginia - WD'),
    ('81', '81 - Washington - ED'),
    ('82', '82 - Washington - WD'),
    ('83', '83 - West Virginia - ND'),
    ('84', '84 - West Virginia - SD'),
    ('85', '85 - Wisconsin - ED'),
    ('86', '86 - Wisconsin - WD'),
    ('87', '87 - Wyoming'),
    ('90', '90 - Virgin Islands'),
    ('91', '91 - Guam'),
    ('103', '103 - Northern Mariana Islands')
)

# for internal use only
STATUTE_CHOICES = (
    ('144', '144'), ('145', '145'), ('166', '166'), ('167', '167'),
    ('168', '168'), ('169', '169'), ('170', '170'), ('170-USE', '170-USE'),
    ('171', '171'), ('175', '175'), ('187', '187'), ('188', '188'),
    ('197', '197'), ('198', '198'), ('202', '202'), ('204', '204'),
    ('205', '205'), ('206', '206'), ('207', '207'), ('208', '208'),
    ('210', '210'), ('216', '216'), ('217', '217'), ('218', '218'),
    ('219', '219'), ('220', '220'), ('230', '230'), ('259', '259'),
    ('300', '300'), ('39', '39'), ('50', '50'), ('502', '502'), ('504', '504'),
    ('508', '508'), ('595', '595'),
)

# for internal use only
PER_PAGE = (
    ('5', '5'), ('15', '15'), ('25', '25'), ('50', '50')
)

PUBLIC_USER = 'public user'

CONTACT_PHONE_INVALID_MESSAGE = _('If you submit a phone number, please make sure to include between 7 and 15 digits. The characters "+", ")", "(", "-", and "." are allowed. Please include country code if entering an international phone number.')

PRINT_CHOICES = (
    ('correspondent', 'Correspondent Information'),
    ('issue', 'Reported Issue'),
    ('description', 'Personal Description'),
    ('activity', 'Activity'),
    ('summary', 'Summary'),
)
