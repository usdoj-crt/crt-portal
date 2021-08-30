from django.db import migrations


def add_spl_standard_form_letters(apps, schema_editor):
    ResponseTemplate = apps.get_model('cts_forms', 'ResponseTemplate')
    subject = '回應：您的民權司報告 - {{ zh_hant.section_name }}科的 {{ record_locator }}'
    ResponseTemplate.objects.create(
        title='SPL - Standard Form Letter (Chinese Traditional)',
        subject=subject,
        language='zh-hant',
        body="""
{{ zh_hant.addressee }},

感謝您在{{ zh_hant.date_of_intake }}的信函。您的報告號碼為{{ record_locator }}。特別訴訟科依靠社區成員提供的信息來查明侵犯公民權利的行為。每週，我們都會收到數百份關於潛在違規行為的報告。我們收集和分析該等資料以助我們選擇案件，並且我們可能會將這些資料用作現有案件中的證據。我們將審閲您的來信，以確定是否有必要聯絡您以獲取更多資料。我們沒有資源來跟進每一封來函。

特別訴訟科是民權司的幾個科室之一。我們致力於在以下四個方面保護公民權利：1)州或地方機構中的人士的權利，這些機構包括：監獄、監牢、少年拘留設施和殘疾人醫療保健設施（包括醫療保健設施中的人士是否更應該在社區中獲取服務）；2)與州或地方警察或治安部門互動的人士的權利；3)民衆安全使用生殖保健診所或宗教機構的權利；以及 4)民衆在州和地方機構中信奉宗教的權利。我們無權處理涉及聯邦機構或聯邦官員的問題。

如果您的問題不在本科的工作範圍內，您不妨查閱民權司的網頁以尋找正確的部門：https://civilrights.justice.gov/ 。  
  
特別訴訟科只處理廣泛影響到群體的問題引發的案件。我們不協助解決個別問題。 我們無法幫助您獲得損害賠償或任何個人救濟。我們無法協助刑事案件，包括錯誤定罪、上訴或判刑。 


如果您有個別問題，或需要尋求賠償或其他形式的個人救濟，您不妨咨詢私人律師、非營利組織或法律援助組織，向他們尋求協助。我們只有在以下這兩個領域裏可以幫助個人或處理單一事件：1)如果您被禁止在監獄、監牢、精神病院等由州或地方政府運營或為州或地方政府運營的設施中信奉您的宗教，我們可能能夠為您提供協助；2)如果您在使用生殖保健機構或宗教機構時遇到過武力或武力威脅，我們可能能夠為您提供協助。
 
有關特別訴訟科或我們所從事的工作的更多資訊，請訪問我們的網頁： www.justice.gov/crt/about/spl/ 。 

此致 


美國司法部 
民權司
""")


def remove_spl_standard_form_letters(apps, schema_editor):
    ResponseTemplate = apps.get_model('cts_forms', 'ResponseTemplate')
    ResponseTemplate.objects.filter(title='SPL - Standard Form Letter (Chinese Traditional)').delete()


class Migration(migrations.Migration):
    dependencies = [
        ('cts_forms', '0116_create_spl_spanish'),
    ]

    operations = [
        migrations.RunPython(add_spl_standard_form_letters, remove_spl_standard_form_letters)
    ]