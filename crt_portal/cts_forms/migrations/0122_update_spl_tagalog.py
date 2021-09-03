from django.db import migrations


def tweak_spl_tagalog(apps, schema_editor):
    ResponseTemplate = apps.get_model('cts_forms', 'ResponseTemplate')
    tagalog_spl_form = ResponseTemplate.objects.get(title='SPL - Standard Form Letter (Tagalog)')
    # adjust addressee and indentation
    tagalog_spl_form.body = """
{{ tl.addressee }},

Salamat sa iyong liham noong {{ tl.date_of_intake }}.  Ang iyong report number ay {{ record_locator }}.  Ang Seksyon para sa Espesyal na Paglilitis ay umaasa sa impormasyon mula sa mga miyembro ng komunidad upang matukoy ang mga paglabag sa mga karapatang sibil.  Bawat linggo, nakakatanggap kami ng daan-daang ulat ng mga potensyal na paglabag.  Kinokolekta at sinusuri namin ang impormasyong ito upang matulungan kaming pumili ng mga kaso, at maaari naming gamitin ang impormasyong ito bilang katibayan sa isang umiiral na kaso.  Pag-aaralan namin ang iyong liham upang mapagpasyahan kung kailangang makipag-ugnayan sa iyo para sa karagdagang impormasyon.  Wala kaming mga mapagkukunan para subaybayan ang bawat liham. 
 
Ang Seksyon para sa Espesyal na Paglilitis ay isa sa ilang Seksyon sa Dibisyon para sa mga Karapatang Sibil.  Nagtatrabaho kami upang maprotektahan ang mga karapatang sibil sa apat na aspeto:  1) mga karapatan ng mga tao sa mga institusyong pang-estado o lokal, kabilang ang: mga kulungan, mga bilangguan, mga pasilidad na piitan para sa kabataan, at mga pasilidad  para sa pangangalagang pangkalusugan para sa mga taong may mga kapansanan (kabilang na rin kahit mga taong nasa mga pasilidad para sa pangangalagang pangkalusugan na dapat ay sa komunidad tumanggap ng mga serbisyo); 2) mga karapatan ng mga taong nakikipag-ugnayan sa kagawaran ng pulisya o serip na pang-estado o lokal; 3) mga karapatan ng mga tao sa ligtas na pagpunta sa mga klinikang para sa pangangalaga ng kalusugang reproduktibo o institusyong panrelihiyon; at 4) mga karapatan ng mga tao na isagawa ang kanilang pananampalataya sa mga institusyong pang-estado o lokal.  Hindi kami awtorisadong tugunan ang mga isyu sa mga pederal na pasilidad o pederal na opisyal.   
 
Kung ang iyong pag-aalala ay hindi saklaw sa gawain ng Seksyong ito, maaaring naisin mo na sumangguni sa web page ng Dibisyon para sa mga Karapatang Sibil (Civil Rights Division) upang mahanap ang tamang seksyon:  https://civilrights.justice.gov/.   
   
Kagawaran ng Katarungan ng Estados Unidos
 
Dibisyon para sa mga Karapatang Sibil
"""
    tagalog_spl_form.save()


class Migration(migrations.Migration):

    dependencies = [
        ('cts_forms', '0121_create_spl_tagalog'),
    ]

    operations = [
        migrations.RunPython(tweak_spl_tagalog)
    ]
