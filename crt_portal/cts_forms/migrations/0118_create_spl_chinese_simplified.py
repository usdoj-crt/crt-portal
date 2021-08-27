from django.db import migrations


def add_spl_standard_form_letters(apps, schema_editor):
    ResponseTemplate = apps.get_model('cts_forms', 'ResponseTemplate')
    subject = '回应：您的民权司报告 - {{ zh_hans.section_name }}科的 {{ record_locator }}'
    ResponseTemplate.objects.create(
        title='SPL - Standard Form Letter (Chinese Simplified)',
        subject=subject,
        language='zh-hans',
        body="""
{{ zh_hans.addressee }}，

感谢您在{{ zh_hans.date_of_intake }}的来信。您的报告编号是{{ record_locator }}。特别诉讼科依靠社区成员提供的信息来查明侵犯公民权利的行为。每周，我们都会收到数百份关于潜在违规行为的报告。我们收集和分析这些信息以助于我们选择案件，而且我们可能会将这些信息用作现有案件中的证据。我们将审阅您的来信，以决定是否有必要与您联系以获取更多信息。我们没有资源来跟进每一封来函。

特别诉讼科是民权司的几个科室之一。 我们致力于在以下四个方面保护公民权利：1)州或地方机构中人员的权利，这些机构包括：监狱、监牢、少年拘留设施和残疾人医疗保健设施（包括医疗保健设施中的人员是否应改为在社区获取服务）；2)与州或地方警察或治安部门打交道的人士的权利；3)民众安全使用生殖保健诊所或宗教机构的权利； 以及 4)民众在州和地方机构中信奉宗教的权利。我们无权处理涉及联邦设施或联邦官员的问题。   

如果您的问题不在本科的工作范围内，您可以考虑查阅民权司的网页以寻找正确的部门： https://civilrights.justice.gov/ 。

特别诉讼科只处理广泛影响到群体的问题引发的案件。我们不协助解决个别问题。我们无法帮助您获得损害赔偿或任何个人救济。我们无法协助刑事案件，包括错误定罪、上诉或判刑。


如果您有个别问题，或需要寻求赔偿或其他形式的个人救济，您不妨咨询私人律师、非营利组织或法律援助组织，向他们寻求帮助。我们只有在以下这两个领域里可以帮助个人或处理单个事件：1)如果您被禁止在监狱、监牢、精神病院等由州或地方政府运营或为州或地方政府运营的设施中信奉您的宗教，我们可能能够为您提供帮助；2)如果您在使用生殖保健机构或宗教机构时遇到过武力或武力威胁，我们可能能够为您提供帮助。
 
有关特别诉讼科或我们所从事的工作的更多信息，请访问我们的网页： www.justice.gov/crt/about/spl/ 。

此致


美国司法部 
民权司
""")


def remove_spl_standard_form_letters(apps, schema_editor):
    ResponseTemplate = apps.get_model('cts_forms', 'ResponseTemplate')
    ResponseTemplate.objects.filter(title='SPL - Standard Form Letter (Chinese Simplified)').delete()


class Migration(migrations.Migration):
    dependencies = [
        ('cts_forms', '0117_create_spl_chinese_traditional'),
    ]

    operations = [
        migrations.RunPython(add_spl_standard_form_letters, remove_spl_standard_form_letters)
    ]