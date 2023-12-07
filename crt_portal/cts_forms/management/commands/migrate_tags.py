from django.core.management.base import BaseCommand
from cts_forms.models import Tag


class Command(BaseCommand):  # pragma: no cover
    help = "Load and migrate section tags"

    def _fetch_spl_tags(self):
        tags, did_create = zip(*[
            Tag.objects.update_or_create(
                name=name,
                section='SPL',
                defaults={
                    'description': f'{description_1} ({description_2})',
                    'tooltip': f'{description_1} ({description_2})',
                    'show_in_lists': True,
                }
            )
            for name, description_1, description_2 in SPL_TAGS
        ])
        return tags, sum(did_create)

    def _create_or_update_tags(self):
        tags, number_created = zip(*[
            self._fetch_spl_tags(),
        ])

        total_created = sum(number_created)
        self.stdout.write(self.style.SUCCESS(f'Created {total_created} tags'))

        return tags

    def handle(self, *args, **options):
        del args, options  # unused
        self._create_or_update_tags()


SPL_TAGS = [
    ('ABNG', 'Abuse/Neglect', '168 - CRIPA'),
    ('ACCR', 'Access To Courts', '168 - CRIPA'),
    ('ACCS', 'Accessibility (Ada)', '204 - ADA'),
    ('AGDS', 'Discrimination-Age', '168 - CRIPA'),
    ('AGNG', 'Aging', '168 - CRIPA'),
    ('ALSD', 'Access To Legal Services/Due Process', '168 - CRIPA'),
    ('AMDA', 'Americans With Disabilities Act', '204 - ADA INMATES ONLY'),
    ('CMPL', 'Community Placement', '168 - CRIPA'),
    ('CRIP', 'Cripa Request', '168 - CRIPA'),
    ('DETH', 'Death', '168 - CRIPA'),
    ('DIGN', 'Discrimination-Gender', '168 - CRIPA'),
    ('DILG', 'Discrimination-Lgbt', '168 - CRIPA'),
    ('DINO', 'Discrimination-Imm/No/Lep', '168 - CRIPA'),
    ('DINU', 'Diet/Nutrition', '168 - CRIPA'),
    ('DIRE', 'Discrimination-Race/Ethnicity', '168 - CRIPA'),
    ('DIRL', 'Discrimination-Religion', '210 - RLUIPA'),
    ('DNTL', 'Dental', '168 - CRIPA'),
    ('EVSA', 'Environmental Safety/Sanitation', '168 - CRIPA'),
    ('EXER', 'Exercise', '168 - CRIPA'),
    ('EXFC', 'Excessive Force', '168 - CRIPA'),
    ('FAFS', 'First Amendment-Freedom Of Speech', '168 - CRIPA'),
    ('FAOT', 'First Amendment-Other', '168 - CRIPA'),
    ('FARF', 'First Amendment-Religious Freedom', '210 - RLUIPA'),
    ('FEPR', 'Feeding Practices', '168 - CRIPA'),
    ('FOAC', 'Face-Obstructive Activities', '206 - FACE'),
    ('FPRD', 'Face-Property Damage', '206 - FACE'),
    ('FTIN', 'Failure to Investigate', '207 - POLICE'),
    ('FVLT', 'Face-Violence/Threats', '206 - FACE'),
    ('GANG', 'Gang Related Activities', '168 - CRIPA'),
    ('GRVN', 'Grievances', '168 - CRIPA'),
    ('IMPB', 'Improper Pedestrian/Bike Stops', '207 - POLICE'),
    ('IMVS', 'Improper Vehicle Stop Searches', '207 - POLICE'),
    ('ISSE', 'Isolation/Seclusion', '168 - CRIPA'),
    ('JVDM', 'Juvenile Justice Administration', '168 - CRIPA'),
    ('JVFC', 'Juvenile Facility', '168 - CRIPA'),
    ('JVIS', 'Juvenile Isolation', '168 - CRIPA'),
    ('LOHP', 'Lack Of Hygiene Products', '168 - CRIPA'),
    ('MAIL', 'Mail', '168 - CRIPA'),
    ('MDCR', 'Medical Care', '168 - CRIPA'),
    ('MNHC', 'Mental Health Care', '168 - CRIPA'),
    ('MTGS', 'Most Integrated Setting (Ada)', '204 - ADA'),
    ('NOJR', 'No Jurisdiction', '168 - CRIPA'),
    ('OCTH', 'Occupational Therapy', '168 - CRIPA'),
    ('OVCW', 'Overcrowding', '168 - CRIPA'),
    ('PCSC', 'Police-Civilian Complaint System And Discipline', '207 - POLICE'),
    ('PCCS', 'Police-Coercive Sexual Conduct', '207 - POLICE'),
    ('PDHG', 'Police-Discriminatory Highway Stops', '207 - POLICE'),
    ('PDPD', 'Police-Discriminatory Pedestrian Stops', '207 - POLICE'),
    ('PDUT', 'Police-Discriminatory Urban Traffic Stops', '207 - POLICE'),
    ('PEXF', 'Police-Excessive Force', '207 - POLICE'),
    ('PFAR', 'Police-False Arrest', '207 - POLICE'),
    ('PFHO', 'Protection From Harm-Other', '168 - CRIPA'),
    ('PHIV', 'Protection From Harm-Inmate Violence', '168 - CRIPA'),
    ('PHSP', 'Protection From Harm-Suicide Prevention', '168 - CRIPA'),
    ('PHSR', 'Psychiatric Services', '168 - CRIPA'),
    ('PLCA', 'Police-Canine', '207 - POLICE'),
    ('PLCY', 'Policy And Procedures', '207 - POLICE'),
    ('PLSI', 'Police/School Interaction', '207 - POLICE'),
    ('PMEE', 'Police-Improper Searches/Seizures', '207 - POLICE'),
    ('PMHI', 'Police/Mental Health Interaction', '207 - POLICE'),
    ('PODP', 'Discrimination Policing-Other', '207 - POLICE'),
    ('PRAC', 'Police-Racial Profiling', '207 - POLICE'),
    ('PREA', 'Prison Rape Elimination Act', '168 - CRIPA'),
    ('PRTL', 'Police-Retaliation', '207 - POLICE'),
    ('RAPE', 'Rape', '168 - CRIPA'),
    ('RCPR', 'Racial Profiling', '168 - CRIPA'),
    ('RECR', 'Recreation', '168 - CRIPA'),
    ('RETL', 'Retaliation', '168 - CRIPA'),
    ('RHBL', 'Rehabilitation/Habilitation Services', '168 - CRIPA'),
    ('RSCH', 'Restraints-Chemical', '168 - CRIPA'),
    ('RSPH', 'Restraints-Physical', '168 - CRIPA'),
    ('RSTR', 'Restraints', '168 - CRIPA'),
    ('RWTR', 'Repeat Writer', 'ANY CODE'),
    ('SBAT', 'Substance Abuse Treatment', '168 - CRIPA'),
    ('SCPR', 'Suicide Prevention', '168 - CRIPA'),
    ('SEXD', 'Sexual Discrimination', '168 - CRIPA'),
    ('SEXM', 'Sexual Misconduct', '168 - CRIPA'),
    ('SNTN', 'Sanitation', '168 - CRIPA'),
    ('SPED', 'Special Education/Idea', '168 - CRIPA'),
    ('STFF', 'Staffing', '168 - CRIPA'),
    ('TASR', 'Taser', '168 - CRIPA'),
    ('THCO', 'Theft/Corruption', '168 - CRIPA'),
    ('THRT', 'Threats', '168 - CRIPA'),
    ('VENT', 'Ventilation', '168 - CRIPA'),
    ('VIST', 'Visitation', '168 - CRIPA'),
]
