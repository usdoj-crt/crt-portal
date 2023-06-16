from django.db import migrations

def add_letters(apps, schema_editor):
    ResponseTemplate = apps.get_model('cts_forms', 'ResponseTemplate')
    subject = 'Tugon: Ang Iyong Ulat sa Dibisyon sa Mga Karapatang Sibil – {{ record_locator }} mula sa Seksyon na {{ tl.section_name }}'
    ResponseTemplate.objects.create(
        title='CRM - R1 Form Letter (Tagalog)',
        subject=subject,
        body="""
{{ tl.addressee }},

Nakipag-ugnay ka sa Kagawaran ng Katarungan noong {{ tl.date_of_intake }}. Ang numero ng iyong ulat ay {{ record_locator }}. Ang Dibisyon sa mga Karapatang Sibil ay umaasa sa impormasyon na mula sa mga kasapi ng pamayanan upang makilala ang mga potensyal na mga paglabag sa mga karapatang sibil.  Ang Pampederal na Kawani sa Pagsisiyasat at iba pang mga ahensya na nagpapatupad ng batas ay nagsasagawa ng mga pagsisiyasat para sa Dibisyon. Samakatuwid, baka gusto mong makipag-ugnay sa iyong lokal ng tanggapan ng FBI o bisitahin ang www.FBI.gov.

Ang Seksyong Pangkriminal ay isa sa maraming mga Seksyon sa loob ng Dibisyon sa mga Karapatang Sibil ng Kagawaran sa Katarungan ng Estados Unidos. Responsibilidad naming maipatupad ang mga batas na pangkriminal ng pederal sa mga karapatang sibil. Inuusig ng Seksyong Pangkriminal ang mga kasong kriminal kasangkot ang:

- Mga paglabag sa mga karapatang sibil ng mga tao na sumasailalim sa kulay ng batas, katulad  ng pederal, estado, o iba pang mga pulis o mga kawani sa pagwawasto;
- Mga krimen sa pagkapoot;
- Pagpuwersa o pagbabanta na may pakay na makagambala ng mga aktibidad na pangrelihiyon dahil sa kanilang kalikasan sa relihiyon;
- Pagpuwersa o pagbabanta na may pakay na makagambala sa pagbibigay o pagkuha ng mga serbisyo para sa kalusugan sa pag-aanak at
- Panlilinlang ng mga tao sa kaanyuan ng pagpilit na magtrabaho o pakikipagtalik na pang komersyo.

Hindi ka namin matutulungang mabawi ang mga pinsala o humanap ng anumang iba pang pangpersonal na kaluwagan.  Hindi ka rin namin matutulungan sa mga kasong pangkriminal na nagpapatuloy, kabilang ang maling mga paniniwala, mga apela o paghahatol. Para sa karagdagang detalyadong impormasyon tungkol sa Seksyong Pangkriminal o ang trabahong ginagawa namin, manyaring bisitahin ang webpage namin: www.justice.gov/crt/about/crm/.

Susuriin namin ang iyong sulat upang magpasya kung kinakailangan naming makipag-ugnay sa iyo para sa karagdagang impormasyon. Wala kaming sapat na mga mapagkukunan para mag-follow-up sa o sagutin ang bawat sulat. Kung ang iyong pagkabahala ay hindi sakop sa lugar ng trabaho ng Seksyong ito, baka gusto mong kumunsulta sa webpage ng Dibisyon sa mga Karapatang Sibil upang matukoy kung mayroong ibang Seksyon ng Dibisyon na maaaring tumingin sa iyong mga pagkabahala: www.justice.gov/crt.  Ulit, kung sumusulat ka upang mag-ulat ng isang krimen, mangyaring makipag-ugnay sa mga ahensya na nagpapatupad ng batas na pampederal at/o pang-estado sa iyong lokal na lugar, katulad ng Pampederal na Kawani sa Pagsisiyasat o sa iyong lokal na departamento ng pulisya o tanggapan ng serip.

Taos-puso,
/s/
Ang Seksyong Pangkriminal
""")

    ResponseTemplate.objects.create(
        title='CRM - R2 Form Letter (Tagalog)',
        subject=subject,
        body="""
{{ tl.addressee }},

Nakipag-ugnay ka sa Dibisyon sa mga Karapatang Sibil noong {{ tl.date_of_intake }}. Ang numero ng iyong ulat ay {{ record_locator }}.

Ang Seksyong Pangkriminal ng Dibisyon sa mga Karapatang Sibil ay responsable sa pagpapatupad ng mga batas na pangkriminal ng pederal sa mga karapatang sibil. Karamihan sa mga aktibidad namin sa pagpapatupad ay may kinalaman sa pagsisiyasat at pag-uusig sa pagkakait sa mga karapatang sibil sa ilalim ng kulay ng batas. Ang mga bagay na ito ay kadalasang kasama ang mga paratang ng sobrang pisikal na puwersa o abusong pang-sekswal ng mga opisyal na nagpapatupad ng batas.

Ang mga impormasyon na iyong ibinigay ay hindi sapat upang mapahintulutan kami na tukuyin ang pagkakaroon ng posibleng paglabag sa batas na pangkriminal ng pederal sa mga karapatang sibil. Samakatuwid, hindi namin maaaring pahintulutan ang isang pagsisiyasat sa iyong reklamo sa mga oras na ito. Subalit, maaari naming isaalang-alang pa ang paratan kung magbibigay ka ng tiyak na impormasyon tungkol sa mga pangyayari na kasangkot sa iyong reklamo. Kailangan mong isama ang pangalan ng taong nasaktan; isang salaysay kasama ang mga paratang na nagdulot sa at kasama ang pangyayari; ang pangalan ng sinumang posibleng saksi; ang petsa ng pangyayari at anupamang impormasyon na sa tingin mo ay may kaugnayan sa pangyayari. Mangyaring isumite ulit ang impormasyon na ito sa aming online portal ng reklamo sa https://civilrightsjustice.gov/ at sumangguni sa iyong numero ng reklamo, na nakalista sa linya ng paksa ng email na ito.

Makatitiyak ka na kung nagpapakita ang ebidensya na mayroong mauusig na paglabag sa isang batas na pangkriminal ng pederal sa mga karapatang sibil, gagawin ang akmang pagkilos .

Salamat,
/s/
Ang Seksyong Pangkriminal
""")

    ResponseTemplate.objects.create(
        title='CRM - Referral to FBI (Tagalog)',
        subject=subject,
        body="""
{{ tl.addressee }},

Nakipag-ugnay ka sa Kagawaran ng Katarungan noong {{ tl.date_of_intake }}.

Ano ang aming ginawa:

Ang numero ng iyong ulat ay {{ record_locator }}.

Sinuri ng mga kasapi ng koponan mula sa Dibisyon sa mga Karapatang Sibil ang impormasyon na iyong isinumite.  Batay sa iyong ulat, natukoy ng aming koponan na pinanindigan mo ang isang kriminal na paglabag sa mga karapatang sibil.

Maingat naming susuriin ang iyong ulat at makikipag-ugnay kami sa iyo kung mangangailangan pa kami ng karagdagang impormasyon. Subalit, dapat kang magkaroon ng kamalayan na ang Dibisyon sa mga Karapatang Sibil ay tumatanggap ng libu-libong mga ulat mula sa publiko bawat taon at sa pangkalahatan ay nagiging kasangkot lamang pagkatapos maumpisahan ang isang pagsisiyasat ng Pampederal na Kawani ng Pagsisiyasat (FBI) o ng ibang ahensya na nagpapatupad ng batas.

Alinsunod, nais naming magkaroon ka ng kamalayan na sa mga sitwasyon na kinasasangkutan ng mga paglabag na kriminal ng mga batas na pampederal sa mga karapatang sibil, ang FBI ay nagsisilbing una at pinakamahusay na lugar sa pag-uulat.

Ano ang iyong magagawa:

Baka maaari kang tulungan ng FBI sa iyong sitwasyon.  Maaari kang makipag-ugnay sa FBI sa pamamagitan ng anumang mga kaparaanan na nakabalangkas sa ibaba.

Online:

www.fbi.gov/tips

Sa pamamagitan ng telepono o personal:

Makipag-ugnay sa iyong lokal na tanggapan ng FBI (inirerekomenda)

www.fbi.gov/contact-us/field-offices

Paano kang nakatulong:

Ang iyong ulat ay makakatulong sa amin na isulong ang mga karapatang sibil. Ang impormasyon mula sa mga ulat katulad ng sa iyo ay makakatulong sa amin na maunawaan ang umuusbong na mga kalakaran at mga suliranin sa mga karapatang sibil.  Makakatulong ito na ipaalam kung paano naming pinoprotektahan ang mga karapatang sibil ng lahat ng mga tao sa bansang ito.

Salamat sa paglaan mo ng oras na makipag-ugnay sa Kagawaran ng Katarungan tungkol sa iyong mga pagkabahala.

Taos-puso,

Kagawaran ng Katarungan ng Estados Unidos
Dibisyon sa mga Karapatang Sibil
""")

    ResponseTemplate.objects.create(
        title='CRT - Comments & Opinions (Tagalog)',
        subject=subject,
        body="""
{{ tl.addressee }},

Nakipag-ugnay ka sa Kagawaran ng Katarungan noong {{ tl.date_of_intake }}. Ang numero ng iyong ulat ay {{ record_locator }}.

Pinahahalagahan namin ang iyong interes at oras sa pagsulat sa amin upang ipahiwatig ang iyong mga pananaw. Mangyaring alamin mo na ang impormasyon na iyong ibinigay ay makakatanggap ng naaangkop na pagsasaalng-alang.

Taos-puso,

Kagawaran ng Katarungan ng Estados Unidos
Dibisyon sa mga Karapatang Sibil
""")

    ResponseTemplate.objects.create(
        title='CRT - EEOC Referral Letter (Tagalog)',
        subject=subject,
        body="""
{{ tl.addressee }},

Nakipag-ugnay ka sa Kagawaran ng Katarungan noong {{ tl.date_of_intake }}. Pagkatapos ng maingat na pagsusuri ng iyong isinumite, natukoy namin na ang iyong ulat ay mas naaangkop na hawakan ng isa pang ahensyang pampederal.

Ano ang aming ginawa:

Ang numero ng iyong talaan ay {{ record_locator }}.

Sinuri ng mga kasapi ng koponan mula sa Dibisyon sa mga Karapatang Sibil ang impormasyon na iyong isinumite.  Batay sa iyong ulat, natukoy ng aming koponan na pinanindigan mo na mayroong diskriminasyon sa trabaho o iba pang mga suliranin na may kaugnayan sa trabaho.

Nililimitahan ng batas na pampederal ang kakayahan ng Kagawaran ng Katarungan upang magsagawa ng direktang pagkilos sa ilalim ng tiyak na mga sitwasyon. Batay sa pagsusuri ng aming koponan sa iyong ulat, kabilang dito ang iyong bagay.

Ano ang iyong magagawa:

Hindi namin tinutukoy na ang iyong ulat ay kulang sa merito.  Sa halip, isa pang ahensya na pampederal ang maaaring makatulong sa iyong sitwasyon.

Isinama namin ang isang balangkas ng mga ahensyang pampederal na maaaring makatulong sa iyo.  Kailangan mong makipag-abot sa naaangkop na ahensya kung gusto mong ipagpatuloy pa ito.

TANDAAN:  Mayroong mahigpit na mga limitasyon ng oras sa pagsasampa ng mga reklamo na nauugnay sa diskriminasyon sa trabaho. Kung sa pakiramdam mo na nakaranas ka ng diskriminasyon sa trabaho, kailangan mong makipag-ugnay sa naaangkop na ahensya sa lalong madaling panahon.





NARANASAN KO…

Ang diskriminasyon sa trabaho na batay sa: lahi, kulay, pambansang pinagmulan, relihiyon, kasarian (kabilang ang pagbubuntis, ang orientasyong sekswal, at ang pagkakakilanlan ng kasarian), edad, kapansanan, o pagganti.


AHENSYA NA MAAARING MAKATULONG

Komisyon para sa Pantay na Oportunidad sa Trabaho (EEOC)

    Magsampa sa online: eeoc.gov/filing-charge-discrimination
    Makipag-ugnay sa pamamagitan ng telepono: 1-800-669-4000
    Magsampa ng personal sa iyong pinakamalapit na Tanggapan ng EEOC: www.eeoc.gov/field-office


NARANASAN KO…

Diskriminasyon sa trabaho batay sa serbisyong militar, kabilang ang pagganti, at kabiguan na muling kumuha na trabaho.


AHENSYA NA MAAARING MAKATULONG

Departamento ng Paggawa ng Estados Unidos
Serbisyo sa Pagsasanay sa Trabaho ng mga Beterano (VETS)


    Magsampa sa online o makipag-ugnay sa VETS ng personal:  www.dol.gov/agencies/vets/
    Makipag-ugnay sa pamamagitan ng telepono: 1-866-487-2365


NARANASAN KO…

Diskriminasyon sa trabaho ng gobyernong pampederal




AHENSYA NA MAAARING MAKATULONG

Ang opisyal para sa pantay na oportunidad sa trabaho sa iyong ahensyang pampederal

    Hanapin ang iyong pampederal na opisyal ng EEO: www.eeoc.gov/federal-sector/federal-agency-eeo-directors


NARANASAN KO…

Isang suliranin sa kabayaran ng mga manggagawa


AHENSYA NA MAAARING MAKATULONG

Departamento ng Paggawa ng Estados Unidos
Tanggapan ng mga Palatuntunan para sa Kabayaran ng mga Manggagawa (OWCP)

    Telepono at personal na mga pagpipilian:
    https://www.dol.gov/owcp/owcpkeyp.htm


NARANASAN KO…

Isang suliranin sa mga sahod at/o mga oras ng pagtratrabaho


AHENSYA NA MAAARING MAKATULONG

Departamento ng Paggawa ng Estados Unidos
Administrasyon para sa Pamantayan sa Trabaho, Dibisyon para sa Sahod at Oras

    Paano magsampa ng isang reklamo: www.dol.gov/agencies/whd/contact/complaints
    Makipag-ugnay sa pamamagitan ng telepono: 1-866-487-2365


NARANASAN KO…

Isang suliranin sa kaligtasan ng manggagawa

AHENSYA NA MAAARING MAKATULONG

Departamento ng Paggawa ng Estados Unidos
Administrasyon para sa Ligtas at Kalusugan sa Trahabo (OSHA)

    Magsampa sa online: www.osha.gov/workers/
    Makipag-ugnay sa pamamagitan ng telepono: 1-800-321-6742


NARANASAN KO…

Isang suliranin sa Komisyon para sa Pantay na Oportunidad sa Trabaho


AHENSYA NA MAAARING MAKATULONG

Komisyon para sa Pantay na Oportunidad sa Trabaho
Direktor, Tanggapan ng mga Palatuntunan sa Pamamahala sa Larangan

    131 M Street, NE
    Washington, DC 20507

Sa karagdagan, ang samahan ng bar ng estado o lokal na tanggapan sa ligal na tulong ay maaaring makatulong sa iyong suliranin kahit hindi ka matutulungan ng Kagawaran sa Katarungan.


UPANG MAKAHANAP NG…

Isang personal na abogado


SAMAHANG MAAARING MAKATULONG

Samahan ng Bar ng Amerikano

    www.findlegalhelp.org
    Makipag-ugnay sa pamamagitan ng telepono: 1-800-285-2221



UPANG MAKAHANAP NG…

Isang personal na abogado para sa mga indibidwal na mababa ang sahod


SAMAHANG MAAARING MAKATULONG

Korporasyon para sa mga Pang-ligal na Serbisyo  (o mga Tanggapan sa Ligal na Tulong)

    www.lsc.gov/find-legal-aid


Paano ka nakatulong:

Kahit hindi kami makakilos sa tukoy na halimbawang ito, ang iyong ulat ay makakatulong sa amin na isulong ang mga karapatang sibil. Ang impormasyon mula sa mga ulat katulad ng sa iyo ay tutulong sa amin na maunawaan ang umuusbong at kagyat na mga suliranin.  Makakatulong ito na ipaalam kung paano namin pinoprotektahan ang mga karapatang sibil ng lahat ng mga tao sa bansang ito.

Salamat sa paglaan mo ng oras na makipag-ugnay sa Kagawaran ng Katarungan tungkol sa iyong mga pagkabahala.

Taos-puso,

Kagawaran ng Katarungan ng Estados Unidos
Dibisyon sa mga Karapatang Sibil
""")

    ResponseTemplate.objects.create(
        title='CRT - No Capacity (Tagalog)',
        subject=subject,
        body="""
{{ tl.addressee }}，

Nakipag-ugnay ka sa Kagawaran ng Katarungan noong {{ tl.date_of_intake }}. Pagkatapos ng maingat na pagsusuri ng iyong isinumite, napagpasyahan naming hindi na gumawa ng anumang karagdagang pagkilos sa iyong reklamo.

Ano ang aming ginawa:

Sinuri ng mga kasapi ng koponan mula sa Dibisyon sa mga Karapatang Sibil ang impormasyon na iyong isinumite.  Batay sa aming pagsusuri, napagpasyahan naming hindi na gumawa ng anumang karagdagang pagkilos sa iyong reklamo.  Nakakatanggap kami ng libu-libong mga ulat ng mga paglabag sa mga karapatang sibil bawat taon.  Sa kasamaang palad, wala kaming mapagkukunan na magsagawa ng direktang pagkilos sa bawat ulat.

Ang numero ng iyong ulat ay {{ record_locator }}.

Ano ang iyong magagawa:

Hindi namin tinutukoy na ang iyong ulat ay kulang sa merito. Ang iyong suliranin ay maaari pa ring maaksyunan ng iba – ang iyong samahan ng bar ng estado o lokal na tanggapan sa ligal na tulong ay maaaring makatulong

    Upang makahanap ng lokal na tanggapan:

    Samahan ng Bar ng Amerikano
    www.findlegalhelp.org
    (800) 285-2221

    Korporasyon para sa Ligal na Serbisyo (o mga Tanggapan sa Ligal na Tulong)
    www.lsc.gov/find-legal-aid

Paano ka nakatulong:

Habang wala kaming kakayahan na kunin ang bawat indibidwal na ulat, matutulungan kami ng iyong ulat na hanapin ang mga suliranin na nakakaapekto sa iba’t-ibang mga tao o mga pamayanan. Matutulungan din kami nito na maunawaan ang umuusbong na mga kalakaran at mga paksa.

Salamat sa paglaan mo ng oras na makipag-ugnay sa Kagawaran ng Katarungan tungkol sa iyong mga pagkabahala. Nagsisisi kami na hindi kami makapagbigay ng karagdagang tulong sa bagay na ito.

Taos-puso,

Kagawaran ng Katarungan ng Estados Unidos
Dibisyon sa mga Karapatang Sibil
""")

    ResponseTemplate.objects.create(
        title='CRT - Non-Actionable (Tagalog)',
        subject=subject,
        body="""
{{ tl.addressee }}，

Nakipag-ugnay ka sa Kagawaran ng Katarungan noong {{ tl.date_of_intake }}.  Pagkatapos ng maingat na pagsusuri ng iyong isinumite, napagpasyahan naming hindi na gumawa ng anumang karagdagang pagkilos sa iyong reklamo.

Ano ang aming ginawa:

Sinuri ng mga kasapi ng koponan mula sa Dibisyon sa mga Karapatang Sibil ang impormasyon na iyong isinumite.  Batay sa impormasyong ito, natukoy ng aming koponan na ang mga batas na pampederal sa mga karapatang sibil na aming ipinapatupad ay hindi sinasakop ang iyong inilarawang sitwasyon.  Samakatuwid, hindi na kami makakagawa ng karagdagang pagkilos.

Ang numero ng iyong ulat ay {{ record_locator }}.

Ano ang iyong magagawa:

Ang iyong suliranin ay maaaring masakop ng ibang mga batas na pampederal, pang-estado, o panglokal na wala kaming awtoridad na ipatupad. Hindi namin tinutukoy na ang iyong ulat ay kulang sa merito.

Ang iyong samahan ng bar ng estado o lokal na tanggapan sa ligal na tulong ay maaaring makatulong sa iyong suliranin kahit hindi ka matutulungan ng Kagawaran ng Katarungan.

    Upang makahanap ng lokal na tanggapan:

    Samahan ng Bar ng Amerikano
    www.findlegalhelp.org
    (800) 285-2221

    Korporasyon ng Serbisyong Ligal (o mga Tanggapan sa Ligal na Tulong)
    www.lsc.gov/find-legal-aid

Salamat sa paglaan mo ng oras na makipag-ugnay sa Kagawaran ng Katarungan tungkol sa iyong mga pagkabahala. Nagsisisi kami na hindi kami makapagbigay ng karagdagang tulong sa bagay na ito.

Taos-puso,

Kagawaran ng Katarungan ng Estados Unidos
Dibisyon sa mga Karapatang Sibil
""")

    ResponseTemplate.objects.create(
        title='CRT - Request for Agency Review (Tagalog)',
        subject=subject,
        body="""
{{ tl.addressee }}，

Nakipag-ugnay ka sa Kagawaran ng Katarungan noong {{ tl.date_of_intake }}. Ang sulat na ito ay bilang tugon sa iyong ulat.

Ano ang aming ginawa:

Ang numero ng iyong ulat ay {{ record_locator }}.

Sinuri ng mga kasapi ng koponan mula sa Dibisyon sa mga Karapatang Sibil ang impormasyon na iyong isinumite.  Ipinahiwatig mo na nagsumite ka ng isang reklamo sa diskriminasyon kasama o laban sa isa pang ahensyang Pampederal.

Ang Kagawaran ng Katarungan ay hindi nagsisilbing may awtoridad sa pagsusuri ng mga desisyon ng ibang ahensyang pampederal pagkatapos ng kanilang mga pagsusuri ng mga reklamo tungkol sa diskriminasyon.

Samakatuwid, hindi na kami makakagawa ng karagdagang mga pagkilos.

Ano ang iyong magagawa:

Ang sulat na ito ay hindi isang pagpapasya na ang iyong ulat ay kulang sa merito. Ang iyong samahan ng bar ng estado o lokal na tanggapan sa ligal na tulong ay maaaring makatulong.

UPANG MAKAHANAP NG…

Isang personal na abogado

SAMAHAN NA MAAARING MAKATULONG:

Samahan ng Bar ng Amerikano

    Hanapin online:
    www.findlegalhelp.org

    Makipag-ugnay sa pamamagitan ng telepono: (800) 285-2221

UPANG MAKAHANAP NG…

Isang personal na abogado para sa mga indibidwal na mababa ang sahod

SAMAHANG MAAARING MAKATULONG:

Korporasyon ng mga Serbisyong Pangligal (o mga Tanggapan sa Ligal na Tulong)

    Hanapin online:
    www.lsc.gov/find-legal-aid

Paano ka nakatulong:

Kahit hindi kami makakilos sa tukoy na halimbawang ito, ang iyong ulat ay makakatulong sa amin na isulong ang mga karapatang sibil. Ang impormasyon mula sa mga ulat katulad ng sa iyo ay tutulong sa amin na maunawaan ang umuusbong at kagyat na mga suliranin.  Makakatulong ito na ipaalam kung paano namin pinoprotektahan ang mga karapatang sibil ng lahat ng mga tao sa bansang ito.

Salamat sa paglaan mo ng oras na makipag-ugnay sa Kagawaran ng Katarungan tungkol sa iyong mga pagkabahala.


Taos-puso,

Kagawaran ng Katarungan ng Estados Unidos
Dibisyon sa mga  Karapatang Sibil
""")

    ResponseTemplate.objects.create(
        title='HCE - Referral for Housing/Lending/Public Accommodation (Tagalog)',
        subject=subject,
        body="""
{{ tl.addressee }}，

Nakipag-ugnay ka sa Kagawaran ng Katarungan noong {{ tl.date_of_intake }}.

Ano ang aming ginawa:

Ang numero ng iyong ulat ay {{ record_locator }}.

Sinuri ng mga kasapi ng koponan mula sa Dibisyon sa mga Karapatang Sibil ang impormasyon na iyong isinumite.  Batay sa iyong ulat, natukoy ng aming koponan na iyong pinanindigan na ikaw ay nakaranas ng diskriminasyon sa isa o higit pa sa mga sumunod ng mga lugar:

1) pabahay;
2) pampublikong tirahan, katulad ng mga otel at mga restawran; o
3) kredito.

Mangyaring magkaroon ng kamalayan na sa mga sitwasyon na kasangkot ang ganitong mga uri ng diskriminasyon, ang Dibisyon sa mga Karapatang Sibil ay nagiging kasangkot lamang kung naapektuhan ang mga pangkat ng tao. Sa kabuuan hindi kami nagbubukas ng mga pagsisiyasat batay sa indibidwal na mga pag-angkin ng diskriminasyon.

Ng nasa isip ito, maingat naming susuriin ang iyong ulat at makikipag-ugnay sa iyo kung mangangailangan pa kami ng karagdagang impormasyon at/o maaari kaming magbukas ng isang pagsisiyasat.

Ano ang iyong magagawa:

Kung ang iyong ulat ay nauugnay sa pabahay, ang Departamento sa Pabahay at Kaunlaran sa Lungsod ng Estados Unidos (“HUD”) ay maaaring makatulong. Ang HUD ay ang ahensya na responsable sa pagsusuri ng mga reklamo sa pabahay na nakakaapekto sa isang tao lamang.

TANDAAN:  Mayroong mahigpit na mga limitasyon ng oras sa pagsasampa ng reklamo sa isang diskriminasyon sa pabahay. Kung naniniwala ka na ikaw ay nakaranas ng diskriminasyon sa pabahay, kinakailangan mong makipag-ugnay sa nararapat na ahensya sa lalong madaling panahon.


NARANASAN KO…

Diskriminasyon sa pabahay batay sa:

-Lahi o kulay,
-Pambansang pinagmulan,
-Relihiyon,
-Kasarian,
-Katayuan ng pamilya,
-Kapansanan, o
-Paghihiganti


AHENSYA NA MAAARING MAKATULONG:

Departamento sa Pabahay at Kaunlaran sa Lungsod ng Estados Unidos (HUD)
Tanggapan ng Patas na Pabahay at Pantay na Oportunidad

    Magsampa sa online: www.hud.gov/program_offices/fair_housing_equal_opp/online-complaint

    Makipag-ugnay sa pamamagitan ng  telepono:  (800) 669-9777

    Magsampa ng personal sa iyong pinakamalapit na lokal na tanggapan:
    www.hud.gov/program_offices/fair_housing_equal_opp/contact_fheo


NARANASAN KO…

Isang suliranin kasama ang o mayroong katanungan tungkol sa isang:

-Tulong na salapi sa pabahay o voucher:
-Awtoridad para sa pampublikong pabahay,
-Empleyado ng awtoridad sa pampublikong pabahay, o
-Nagpapaupa na tumatanggap ng tulong na salapi sa isang pabahay


AHENSYA NA MAAARING MAKATULONG:

Departamento sa Pabahay at Kaunlaran sa Lungsod ng Estados Unidos (HUD)
Pabahay na Pampubliko at at Pang-Indiyan

    PIH Sentro ng Serbisyo sa Mamimili:
    www.hud.gov/program_offices/public_indian_housing

    Makipag-ugnay sa pamamagitan ng  telepono: (800) 955-2232


NARANASAN KO…

Isang suliranin kasama ang o mayroong katanungan tungkol sa:

  Kawalan ng tirahan

AHENSYA NA MAAARING MAKATULONG:

Departamento sa Pabahay at Kaunlaran sa Lungsod ng Estados Unidos
Mga Mapagkukunan para sa Kawalan ng Tirahan

    Hanapin online:
    www.hudexchange.info/housing-and-homeless-assistance/


NARANASAN KO…

Panloloko, pagsayang, o pang-aabuso na nauugnay sa:

-HUD, o
-Isang palatuntunan na may kaugnay sa HUD


AHENSYA NA MAAARING MAKATULONG:

Departamento sa Pabahay at Kaunlaran sa Lungsod ng Estados Unidos (HUD)
Tanggapan ng Inspektor Henerall

    Hanapin online:
    www.hudoig.gov/hotline

    Makipag-ugnay sa pamamagitan ng email:  hotline@hudoig.gov

Kung ang iyong ulat ay nauugnay sa diskriminasyon sa pagpapautang, baka gusto mong magsampa ng mga reklamo sa HUD at sa Kawanihan ng Proteksyon sa Pananalapi ng mga Mamimili (CFPB).  Ang mga ahensyang ito ay responsable para sa pagsusuri ng mga reklamo na nakakaapekto sa isang tao lamang.

TANDAAN: Mayroong mahigpit na mga limitasyon ng oras sa pagsasampa ng mga reklamo sa diskriminasyon sa pagpapautan. Kung naniniwala ka na ikaw ay nakaranas ng diskriminasyon sa pagpapautang, kinakailangan mong makipag-ugnay sa nararapat na ahensya sa lalong madaling panahon.


NARANASAN KO…

Diskriminasyon sa pananalaping pambahay (hal. Pagsasangla) batay sa:

-Lahi o kulay,
-Pambansang pinagmulan,
-Relihiyon,
-Kasarian,
-Katayuan ng pamilya,
-Kapansanan, o
-Paghihiganti


AHENSYA NA MAAARING MAKATULONG:

Departamento sa Pabahay at Kaunlaran sa Lungsod ng Estados Unidos (HUD)
Tanggapan ng Patas na Pabahay at Pantay na Oportunidad

    Magsampa sa online:
    www.hud.gov/program_offices/fair_housing_equal_opp/online-complaint

    Makipag-ugnay sa pamamagitan ng  telepono: (800) 669-9777

    Magsampa ng personal sa iyong pinakamalapit na lokal na tanggapan:
    www.hud.gov/program_offices/fair_housing_equal_opp/contact_fheo




NARANASAN KO…

Diskriminasyon sa pananalaping pambahay (hal. Pagsasangla) O ibang kaanyuan ng kredito batay sa:

-Lahi o kulay,
-Pambansang pinagmulan,
-Relihiyon,
-Kasarian,
-Katayuan sa Pag-aasawa,
-Edad (basta nasa sapat kang edad upang pumasok sa isang kontrata),
-Tumatanggap ng kita mula sa anumang palatuntunan sa pampublikong tulong, o
-Paghihiganti


AHENSYA NA MAAARING MAKATULONG:

Kawanihan ng Proteksyon sa Pananalapi ng mga Mamimili (CFPB)

    Magsampa sa online:
    www.consumerfinance.gov/complaint/

    Makipag-ugnay sa pamamagitan ng  telepono: (855) 411-2372

Kung ang iyong ulat ay nauugnay sa diskriminasyon sa mga tirahang pampubliko, kabilang ang mga otel, mga restawran, mga sinehan, at iba pang mga lugar ng libangan, ang iyong abogado heneral ng estado ay maaaring makatulong.

TANDAAN:  Maaaring mayroong mahigpit na mga limitasyon ng oras sa pagsasampa ng mga reklamo sa diskriminasyon sa pampublikong tirahan. Kung naniniwala ka na ikaw ay nakaranas ng diskriminasyon, kinakailangan mong makipag-ugnay sa iyong abogado heneral ng estado sa lalong madaling panahon.


NARANASAN KO…

Diskriminasyon sa pampublikong tirahan (mga otel, mga restawran, mga sinehan, at iba pang mga lugar ng libangan) batay sa:

-Lahi o kulay,
-Relihiyon, o
-Pambansang pinagmulan


AHENSYANG MAAARING MAKATULONG:

Abogadong Heneral ng Estado
    Hanapin online: www.usa.gov/state-attorney-general
    Makipag-ugnay sa pamamagitan ng  telepono: (844) 872-4681

Sa karagdagan, ang iyong samahan ng bar ng estado o lokal na tanggapan sa ligal na tulong ay maaaring makatulong sa iyong suliranin.


UPANG MAKAHANAP NG…

Isang personal na abogado


SAMAHANG MAAARING MAKATULONG:

Samahan ng Bar ng Amerikano
    Hanapin online:
    www.findlegalhelp.org

    Makipag-ugnay sa pamamagitan ng  telepono: (800) 285-2221


UPANG MAKAHANAP NG…

Isang personal na abogado para sa mga indibidwal na mababa ang sahod


SAMAHANG MAAARING MAKATULONG:

Korporasyon sa mga Serbisyong Pangligal (o mga Tanggapan sa Ligal na Tulong)

    Hanapin online:
    www.lsc.gov/find-legal-aid

Paano ka nakatulong:

Ang iyong ulat ay makakatulong sa amin na isulong ang mga karapatang sibil.  Ang impormasyon mula sa mga ulat katulad ng sa iyo ay nakakatulong sa amin na maunawaan ang umuusbong at kagyat na mga suliranin tungkol sa mga karapatang sibil.   Makakatulong ito na ipaalam kung paano namin pinoprotektahan ang mga karapatang sibil ng lahat ng mga tao sa bansang ito.

Salamat sa paglaan mo ng oras na makipag-ugnay sa Kagawaran ng Katarungan tungkol sa iyong mga pagkabahala.

Taos-puso,

Kagawaran ng Katarungan ng Estados Unidos
Dibisyon sa mga Karapatang Sibil
""")

    ResponseTemplate.objects.create(
        title='SPL - Referral for PREA Issues (Tagalog)',
        subject=subject,
        body="""
{{ tl.addressee }}，

Nakipag-ugnay ka sa Kagawaran ng Katarungan noong {{ tl.date_of_intake }}.  Batay sa aming pagsusuri sa puntong ito, gusto naming magkaroon ka ng kaalaman na baka gusto mong makipag-ugnay sa iyong Tagapag-ugnay ng PREA ng estado.

Ano ang aming ginawa:

Ang numero ng iyong ulat ay {{ record_locator }}.

Sinuri ng mga kasapi ng koponan mula sa Dibisyon sa mga Karapatang Sibil ang impormasyon na iyong isinumite.  Batay sa iyong ulat, natukoy ng aming koponan na nagpaabot ka ng mga pagkabahala na kinasasangkutan ang sekswal na pang-aabuso, o sekswal na panliligalig sa kulungan.  Maaari itong sumailalim sa Batas ng Pagtanggal sa Paggahasa sa Bilangguan (PREA).  Ang PREA ay isang batas na ginagawang iligal na:

- sekswal na abusuhin o sekswal na ligaligin ang mga bilanggo at mga detenido; at
- maghiganti laban sa isang billanggo o kasapi ng kawani na nag-uulat ng sekswal na pang-aabuso o sekswal na panliligalig.

Ipagpapatuloy naming suriin ang iyong ulat at makikipag-ugnay sa iyo kung mangangailangan pa kami ng karagdagang impormasyon.  Subalit, kailangang magkaroon ka ng kaalaman na sa mga sitwasyong kasangkot ang sekswal na pang-aabuso o sekswal na panliligalig sa mga bilanggo o mga detinado, ang Dibisyon sa mga Karapatang Sibil ay maaari lamang makisangkot kung saan mayroong laganap na huwaran ng maling pag-uugaling ito.  Samakatuwid, sa pangkalahatan, hindi kami makakapagbukas ng mga pagsisiyasat batay sa indibidwal na mga pag-angkin.

Sa naaayon, gusto naming magkaroon ka ng kalaman na ang iyong Tagapag-ugnay ng PREA ng estado ay maaaring makatulong sa iyong sitwasyon.  Maaaring suriin ng Tagapag-ugnay ng PREA ang indibidwal na mga pag-angkin katulad ng sa iyo. Upang matulungan kang maka-konekta sa iyong Tagapag-ugnay ng PREA ng estado, naglakip kami ng isang direktoryo sa tugon na ito.




Ano ang iyong magagawa:

Ang iyong Tagapag-ugnay ng PREA ng estado ay maaaring makatulong sa iyong sitwasyon. Maaari kang makipag-ugnay sa iyong Tagapag-ugnay ng PREA ng estado sa pagsasangguni sa nakalakip na direktoryo.

Maaari mong ring matutunan ang iba pa tungkol sa PREA sa website ng Sentro ng Impormasyon ng PREA: www.prearesourcecenter.org/training-technical-assistance/prea-101/prisons-and-jail-standards

Paano ka nakatulong:

Ang iyong ulat ay makakatulong sa amin na isulong ang mga karapatang sibil.  Ang impormasyon mula sa mga ulat katulad ng sa iyo ay nakakatulong sa amin na maunawaan ang umuusbong na mga uso at mga suliranin sa mga karapatang sibil.  Makakatulong ito na ipaalam kung paano namin pinoprotektahan ang mga karapatang sibil ng lahat ng mga tao sa bansang ito.

Salamat sa paglaan mo ng oras na makipag-ugnay sa Kagawaran ng Katarungan tungkol sa iyong mga pagkabahala.


Taos-puso,

Kagawaran ng Katarungan ng Estados Unidos
Dibisyon sa mga Karapatang Sibil
""")

    ResponseTemplate.objects.create(
        title='Trending - General COVID inquiries (Tagalog)',
        subject=subject,
        body="""
{{ tl.addressee }}，

Salamat sa iyong ulat {{ record_locator }} na isinampa sa Dibisiyon sa mga Karapatang Sibil noong {{ tl.date_of_intake }}.

Maraming mga Amerikano ang nag-aayos sa “panibagong normal” bilang isang resulta ng COVID-19 - isa na binabalanse ang kritikal na pangangailangan upang maiwasan ang pagkalat ng coronavirus kasama ang ibang mga kadahilanan na nakakaapekto din sa kalusugan at kabutihan. Katulad ng lahat ng mga emerhensya, ang pagsiklab ng COVID-19 ay nakaapekto sa mga tao ng maraming iba't ibang mga lahi, mga relihiyon, at mga etniko, pati na rin ang may mga kapansanan.

Ang Dibisyon sa mga Karapatang Sibil ng Kagawaran ng Katarungan ng Estados Unidos, kasama ang iba pang mga ahensya sa buong pamahalaang pampederal, ay sumusubaybay sa mga suliranin sa mga karapatang sibil na nauugnay sa COVID-19. Para sa karagdagang impormasyon, mangyaring tingnan ang www.justice.gov/crt/fcs. Karagdagang impormasyon sa tugon ng pamahalaan sa COVID-19 ay magagamit sa www.whitehouse.gov/priorities/covid-19/
at www.coronavirus.gov.

Taos-puso,


Kagawaran ng Katarungan ng Estados Unidos
Dibisyon sa mga  Karapatang Sibil
""")

    ResponseTemplate.objects.create(
        title='CRT - Constant Writer (Tagalog)',
        subject=subject,
        body="""
{{ tl.addressee }}，

Nakipag-ugnay ka sa Kagawaran ng Katarungan noong {{ tl.date_of_intake }}. Ang numero ng iyong ulat ay {{ record_locator }}.  Nakatanggap kami dati ng kaparehong pagsusulatan mula sa iyo tungkol sa bagay na ito at tumugon kami sa pagtatanong na iyon.

Wala na kaming maidadagdag sa aming paunang tugon at taos-puso kaming nagsisisi na hindi ka namin maalok ng karagadagang tulong tungkol sa bagay na ito.



Taos-puso,


Kagawaran ng Katarungan ng Estados Unidos
Dibisyon sa mga  Karapatang Sibil
""")

def remove_letters(apps, schema_editor):
    ResponseTemplate = apps.get_model('cts_forms', 'ResponseTemplate')
    ResponseTemplate.objects.filter(title='CRM - R1 Form Letter (Tagalog)').delete()
    ResponseTemplate.objects.filter(title='CRM - R2 Form Letter (Tagalog)').delete()
    ResponseTemplate.objects.filter(title='CRM - Referral to FBI (Tagalog)').delete()
    ResponseTemplate.objects.filter(title='CRT - Comments & Opinions (Tagalog)').delete()
    ResponseTemplate.objects.filter(title='CRT - EEOC Referral Letter (Tagalog)').delete()
    ResponseTemplate.objects.filter(title='CRT - No Capacity (Tagalog)').delete()
    ResponseTemplate.objects.filter(title='CRT - Non-Actionable (Tagalog)').delete()
    ResponseTemplate.objects.filter(title='CRT - Request for Agency Review (Tagalog)').delete()
    ResponseTemplate.objects.filter(title='HCE - Referral for Housing/Lending/Public Accommodation (Tagalog)').delete()
    ResponseTemplate.objects.filter(title='SPL - Referral for PREA Issues (Tagalog)').delete()
    ResponseTemplate.objects.filter(title='Trending - General COVID inquiries (Tagalog)').delete()
    ResponseTemplate.objects.filter(title='CRT - Constant Writer (Tagalog)').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('cts_forms', '0108_vietnamese_form_letters'),
    ]

    operations = [
        migrations.RunPython(add_letters, remove_letters)
    ]
