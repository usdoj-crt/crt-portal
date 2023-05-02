from django.db import migrations

def add_letters(apps, schema_editor):
    ResponseTemplate = apps.get_model('cts_forms', 'ResponseTemplate')
    subject = '回應：您的民權司報告 - {{ zh_hant.section_name }}科的 {{ record_locator }}'
    ResponseTemplate.objects.create(
        title='CRM - R1 Form Letter (Chinese Traditional)',
        subject=subject,
        body="""
{{ zh_hant.addressee }},

您於{{ zh_hant.date_of_intake }}與司法部聯繫。您的舉報號碼為{{ record_locator }}。民權司仰賴社區成員提供的資訊來識別潛在的民權侵犯行為。聯邦調查局(FBI)和其他執法機構皆為本司進行調查。因此，您不妨聯繫當地的FBI辦公室或訪問www.FBI.gov網站。

刑事科是美國司法部民權司的數個科室之一。我們負責執行聯邦刑事民權法。刑事科起訴涉及以下方面的刑事案件：

- 聯邦、州或其他警務人員或懲戒人員以表面合法的公權力行事卻侵犯民權的行為；
- 仇恨犯罪；
- 出於宗教性質而意圖干擾宗教活動的武力或威脅；
- 旨在干擾提供或獲得生殖健康服務的武力或威脅；以及
- 以強迫勞動或強迫卖淫的形式販運人口。

我們無法幫助您索取賠償或尋求其他個人救濟。我們也無法對正在進行的刑事案件為您提供幫助，包括錯誤的有罪判決、上訴或判刑。有關刑事科或我們執行的工作更多詳細資訊，請訪問我們的網頁： www.justice.gov/crt/about/crm/.

我們將審閱您的來信，以決定是否有必要與您聯繫以獲取更多資訊。我們沒有資源對每封來信進行後續追蹤或答覆。如果您關切之事不在本科的工作範圍之內，則不妨參考民權司的網頁，以決定本部門的其他科室是否能夠解決您所關切之事：www.justice.gov/crt。同樣地，如果您打算舉報犯罪，請聯繫您當地的聯邦和/或州執法機構，例如聯邦調查局(FBI)或您當地的警察局或警長辦公室。

耑此，
/s/
刑事科
""")

    ResponseTemplate.objects.create(
        title='CRM - R2 Form Letter (Chinese Traditional)',
        subject=subject,
        body="""
{{ zh_hant.addressee }},

您於{{ zh_hant.date_of_intake }}聯繫了民權司。您的舉報號碼為{{ record_locator }}。

民權司的刑事科負責執行聯邦刑事民權法。我們的大部分執法活動係針對以表面合法的公權力剝奪民權的事件進行調查和起訴。這些事件通常涉及對執法人員過度使用武力或性虐待的指控。

您提供的資訊不足，因此我們無法確定是否存在可能違反聯邦刑事民權法的行為。因此，我們目前無法授權對您的申述進行調查。但是，如果您能提供申述中所涉及情況的具體資訊，我們將進一步考量該指稱。您應包括受傷者的姓名；導致該事件並包括事件的指控描述；任何可能的證人的名字；事件發生的日期以及您認為與此事件有關的任何其他資訊。請將此類資訊重新提交到我們的線上投訴入口網站https://civilrights.justice.gov/，並提供在此電子郵件的主旨行中所列出的您的申訴編號以供參考。

您可以放心，如果證據顯示存在可起訴的違反聯邦刑事民權法的行為，我们將會採取適當的行動。

謝謝您，
/s/
刑事科
""")

    ResponseTemplate.objects.create(
        title='CRM - Referral to FBI (Chinese Traditional)',
        subject=subject,
        body="""
{{ zh_hant.addressee }},

您於{{ zh_hant.date_of_intake }}與司法部聯繫。

我們做了什麼：

您的舉報號碼為{{ record_locator }}。

民權司的團隊成員審閱了您提交的資訊。根據您的舉報，我們的團隊確認您告發一樁侵犯民權的刑事事件。

我們將仔細審閱您的舉報，如果需要其他資訊，我們將會與您聯繫。但是，您應明瞭，民權司每年都會收到來自公眾的數千份舉報，並且通常只有在聯邦調查局(FBI)或其他執法機構開始調查之後，民權司才會介入。

因此，我們想提醒您，在涉及違反聯邦民權法的刑事犯罪行為的情況下，FBI是第一個也是最理想的舉報單位。

您可以做些什麼：

FBI可能可以為您的狀況提供幫助。您可以透過以下列出任何一種方式與FBI聯繫。

線上：

www.fbi.gov/tips

透過致電或親臨：

聯繫您當地的FBI辦公室（建議）

www.fbi.gov/contact-us/field-offices

您如何提供幫助：

您的舉報將幫助我們推動民權。諸如您的舉報等的資訊可幫助我們了解民權的新趨勢和新問題。這有助於了解我們如何保護這個國家所有人民權利的狀況。

感謝您抽出寶貴時間就您關切之事與司法部聯繫。

耑此，

美國司法部
民權司
""")

    ResponseTemplate.objects.create(
        title='CRT - Comments & Opinions (Chinese Traditional)',
        subject=subject,
        body="""
{{ zh_hant.addressee }},

您於{{ zh_hant.date_of_intake }}與司法部聯繫。您的舉報號碼為{{ record_locator}}。

感謝您的關注和您寫信給我們表達您觀點的寶貴時間。請注意，您提供的資訊將得到適當的考量。

耑此，

美國司法部
民權司
""")

    ResponseTemplate.objects.create(
        title='CRT - EEOC Referral Letter (Chinese Traditional)',
        subject=subject,
        body="""
{{ zh_hant.addressee }},

您於{{ zh_hant.date_of_intake }}與司法部聯繫。在仔細審閱了您提交的內容之後，我們確認其他的聯邦機構可以更適當地處理您的舉報。

我們做了什麼：

您的記錄號碼是{{ record_locator }}。

民權司的團隊成員審閱了您提交的資訊。根據您的舉報，我們的團隊確認了您提出的就業歧視或其他就業相關問題的指稱。

聯邦法律限制了司法部在某些情況下採取直接行動的能力。根據我們團隊對您舉報的審閱，這包括了您的事件。

您可以做些什麼：

我們並非判定您的舉報缺乏根據。相反地，另一個聯邦機構也許可以為您的情況提供幫助。

我們列出了一份可能可以提供幫助的聯邦機構清單。如果您想進一步對此採取行動，則您應與適當的機構聯繫。

請注意：提出與就業歧視有關的申訴有嚴格的時間限制。如果您覺得自己在就業方面受到歧視，則您應儘快聯繫合適的機構。

我遭遇了...

基於：種族、膚色、國籍、宗教、性別（包括懷孕、性取向和性別認同）、年齡、殘疾或報復的就業歧視。

可能可以提供幫助的機構

公平就業機會委員會 (EEOC)

    線上提出申訴：eeoc.gov/filing-charge-discrimination
    透過電話聯繫： 1-800-669-4000
    親自到您最近的EEOC辦公室提出申訴： www.eeoc.gov/field-office

我遭遇了...

基於兵役的就業歧視，包括報復和無法重新聘用。

可能可以提供幫助的機構

美國勞工部
退伍軍人就業和培訓服務局(VETS)

    線上提出申訴或親臨VETS： www.dol.gov/agencies/vets/
    透過電話聯繫： 1-866-487-2365

我遭遇了...

聯邦政府的就業歧視

可能可以提供幫助的機構

您所處聯邦機構的平等就業機會官員(EEO)

    查詢您的聯邦EEO官員： www.eeoc.gov/federal-sector/federal-agency-eeo-directors

我遭遇了...

工傷賠償問題

可能可以提供幫助的機構

美國勞工部
勞工補償計劃辦公室(OWCP)

    致電或親臨：
    https://www.dol.gov/owcp/owcpkeyp.htm

我遭遇了...

工資和/或工作時數問題

可能可以提供幫助的機構

美國勞工部
就業標準管理局薪資與工時科

    如何提出申訴： www.dol.gov/agencies/whd/contact/complaints
    透過電話聯繫： 1-866-487-2365

我遭遇了...

勞工安全問題

可能可以提供幫助的機構

美國勞工部
職業安全與健康管理局(OSHA)

    線上提出申訴：www.osha.gov/workers/
    透過電話聯繫： 1-800-321-6742

我遭遇了...

公平就業機會委員會(EEOC)的問題

可能可以提供幫助的機構

公平就業機會委員會
現場管理計劃辦公室主任

    131 M Street, NE
    Washington, DC 20507

此外，即使司法部無法為您的問題提供幫助，您所屬的州律師協會或當地法律援助辦公室可能可以為您的問題提供幫助。

查詢...

私人律師

可能可以提供幫助的組織

美國律師協會

    www.findlegalhelp.org
    透過電話聯繫： 1-800-285-2221

查詢...

為低收入者服務的私人律師

可能可以提供幫助的組織

法律服務公司（或法律援助辦公室）

    www.lsc.gov/find-legal-aid

您如何提供了幫助：

儘管我們無法在此特定情況下採取行動，但您的舉報將幫助我們推動民權。諸如您的舉報等資訊可幫助我們了解新出現的和緊迫的問題。這有助於我們了解如何保護這個國家所有人的民權。

感謝您抽出寶貴時間就您關切之事與司法部聯繫。

耑此，

美國司法部
民權司
""")

    ResponseTemplate.objects.create(
        title='CRT - No Capacity (Chinese Traditional)',
        subject=subject,
        body="""
{{ zh_hant.addressee }}，

您於{{ zh_hant.date_of_intake }}與司法部聯繫。在仔細審閱了您所提交的內容之後，我們決定不對您的申訴採取任何進一步的行動。

我們做了什麼：

民權司的團隊成員審閱了您提交的資訊。根據我們的審閱，我們決定不對您的申訴採取任何進一步的行動。每年我們都會收到數千份侵犯民權的舉報。遺憾的是，我們沒有對每份舉報都採取直接行動的資源。

您的舉報號碼為{{ record_locator }}。

您可以做些什麼：

我們並非判定您的舉報缺乏根據。您的問題可能仍然可以由其他機構採取行動 - 您所屬的州律師協會或當地法律援助辦公室可能可以提供幫助。

    查詢當地辦公室：

    美國律師協會
    www.findlegalhelp.org
    (800) 285-2221

    法律服務公司（或法律援助辦公室）
    www.lsc.gov/find-legal-aid

您如何提供了幫助：

儘管我們沒有能力處理每份舉報，但是您的舉報可以幫助我們發現影響眾人或社區的問題。它還可以幫助我們了解新的趨勢和主題。

感謝您抽出寶貴時間就您關切之事與司法部聯繫。很抱歉，我們無法在此事件上提供更多幫助。

耑此，

美國司法部
民權司
""")

    ResponseTemplate.objects.create(
        title='CRT - Non-Actionable (Chinese Traditional)',
        subject=subject,
        body="""
{{ zh_hant.addressee }}，

您於{{ zh_hant.date_of_intake }}與司法部聯繫。在仔細審閱了您所提交的內容之後，我們決定不對您的申訴採取任何進一步的行動。

我們做了什麼：

民權司的團隊成員審閱了您所提交的資訊。根據這些資訊，我們的團隊確認我們執行的聯邦民權法未涵蓋您所描述的情況。因此，我們無法採取進一步的行動。

您的舉報號碼為{{ record_locator }}。

您可以做些什麼：

您的問題可能由其他聯邦、州或地方法律所管轄，但我們無權執行。我們並非判定您的舉報缺乏根據。

即使司法部不能幫助您，您所屬的州律師協會或當地法律援助辦公室可能可以為您的問題提供幫助。

    查詢當地辦公室：

    美國律師協會
    www.findlegalhelp.org
    (800) 285-2221

    法律服務公司（或法律援助辦公室）
    www.lsc.gov/find-legal-aid

感謝您抽出寶貴時間就您關切之事與司法部聯繫。很抱歉，我們無法在此事件上提供更多幫助。

耑此，

美國司法部
民權司
""")

    ResponseTemplate.objects.create(
        title='CRT - Request for Agency Review (Chinese Traditional)',
        subject=subject,
        body="""
{{ zh_hant.addressee }}，

您於{{ zh_hant.date_of_intake }}與司法部聯繫。這封信是對您舉報的回覆。

我們做了什麼：

您的舉報號碼為{{ record_locator }}。

民權司的團隊成員審閱了您提交的資訊。您表示您已經向另一聯邦機構提出了歧視申訴或針對另一聯邦機構提出了歧視申訴。

在其他聯邦機構對歧視申訴進行調查之後，司法部不充當其他聯邦機構決定的審查機構。

因此，我們將不會採取進一步的行動。

您可以做些什麼：

本信函並非判定您的舉報缺乏根據。您所屬的州律師協會或當地法律援助辦公室可能可以提供幫助。

查詢...

私人律師

可能可以提供幫助的組織：

美國律師協會

    線上查詢：
    www.findlegalhelp.org

    透過電話聯繫： (800) 285-2221

查詢...

為低收入者服務的私人律師

可能可以提供幫助的組織：

法律服務公司（或法律援助辦公室）

    線上查詢：
    www.lsc.gov/find-legal-aid

您如何提供了幫助：

儘管我們無法在此特定情況下採取行動，但您的舉報將幫助我們推動民權。諸如您的舉報等資訊可幫助我們了解新出現的和緊迫的問題。這有助於我們了解保護這個國家所有人民權的狀況。

感謝您抽出寶貴時間就您關切之事與司法部聯繫。

耑此，

美國司法部
民權司

""")

    ResponseTemplate.objects.create(
        title='HCE - Referral for Housing/Lending/Public Accommodation (Chinese Traditional)',
        subject=subject,
        body="""
{{ zh_hant.addressee }}，

您於{{ zh_hant.date_of_intake }}與司法部聯繫。

我們做了什麼：

您的舉報號碼為{{ record_locator }}。

民權司的團隊成員審閱了您提交的資訊。根據您的舉報，我們的團隊確認您在以下一個或多個方面的歧視的指稱：

1）住房；
2）公共場所，例如旅館和餐廳；或者
3）信用。

請注意，在涉及此類歧視的情況下，民權司通常只有在群體受到影響時才會介入。我們通常不會根據個人聲稱受到的歧視進行調查。

在考慮到這一點的情況下，我們將仔細審閱您的報告，並在需要其他資訊和/或能夠進行調查時與您聯繫。

您可以做些什麼：

如果您的舉報涉及住房歧視，美國住房及城市發展部(“HUD”)可能可以提供幫助。HUD是負責審查僅影響個人的住房申訴的機構。

請注意：對住房歧視提出申訴有嚴格的時間限制。如果您認為自己在住房方面受到歧視，則您應儘快與合適的機構聯繫。

我遭遇了...

住房歧視基於：

- 種族或膚色，
- 國籍，
- 宗教，
- 性別，
- 家庭狀況，
- 殘疾， 或
- 報復

可能可以提供幫助的機構：

美國住房及城市發展部(HUD)
公平住房與平等機會辦公室

    線上提出申訴：www.hud.gov/program_offices/fair_housing_equal_opp/online-complaint

    透過電話聯繫： (800) 669-9777

    親自到您最近的當地辦公室提出申訴：
    www.hud.gov/program_offices/fair_housing_equal_opp/contact_fheo

我遭遇了...

有關以下的問題或有疑問：

- 住房補貼或抵用券：
- 公共住房管理局，
- 公共住房管理局僱員，或
- 收取住房補貼的房東

可能可以提供幫助的機構：

美國住房及城市發展部(HUD)
公共住房和印第安人住房司

    PIH客戶服務中心：
    www.hud.gov/program_offices/public_indian_housing

    透過電話聯繫： (800) 955-2232

我遭遇了...

以下的問題或疑問：

- 無家可歸

可能可以提供幫助的機構：

美國住房及城市發展部
無家可歸者的資源

    線上查詢：
    www.hudexchange.info/housing-and-homeless-assistance/

我遭遇了...

有關下列的欺詐、浪費或濫用：

- HUD，或
- 與HUD相關的計劃

可能可以提供幫助的機構：

美國住房及城市發展部(HUD)
總監察長辦公室(Office of Inspector General)

    線上查詢：
    www.hudoig.gov/hotline

    透過電子郵件聯繫： hotline@hudoig.gov

如果您的舉報涉及貸款歧視，則您可能要向HUD和消費者金融保護局(CFPB)申訴。這些機構負責審查僅影響個人的申訴。

請注意：對貸款歧視提出申訴有嚴格的時間限制。如果您認為自己在貸款方面受到歧視，則您應儘快與合適的機構聯繫。

我遭遇了...

基於以下的住房貸款（即房屋貸款）歧視：

- 種族或膚色，
- 國籍，
- 宗教，
- 性別，
- 家庭狀況，
- 殘疾， 或
- 報復

可能可以提供幫助的機構：

美國住房及城市發展部(HUD)
公平住房與平等機會辦公室

    線上提出申訴：
    www.hud.gov/program_offices/fair_housing_equal_opp/online-complaint

    透過電話聯繫： (800) 669-9777

    親自到您最近的當地辦公室提出申訴：
    www.hud.gov/program_offices/fair_housing_equal_opp/contact_fheo

我遭遇了...

基於以下的住房貸款（即房屋貸款）或任何其他形式的信用歧視：

- 種族或膚色，
- 國籍，
- 宗教，
- 性別，
- 婚姻狀況，
- 年齡 （只要您年齡足以簽訂合約），
- 從任何公共援助計劃中獲得收入，或
- 報復

可能可以提供幫助的機構：
消費者金融保護局(CFPB)

    線上提出申訴：
    www.consumerfinance.gov/complaint/

    透過電話聯繫： (855) 411-2372

如果您的舉報涉及包括旅館、餐廳、劇院和其他娛樂場所在內的公共場所的歧視，則您所在州的州總檢察長可能可以提供幫助。

請注意：提出與公共場所歧視有關的申訴可能有時間限制。如果您認為自己受到歧視，則您應儘快與您所屬的州總檢察長聯繫。

我遭遇了...

基於以下在公共場所（旅館、餐廳、劇院和娛樂場所）的歧視：

- 種族或膚色，
- 宗教， 或
- 原籍國

可能可以提供幫助的機構：

州總檢察長
    線上查詢：www.usa.gov/state-attorney-general
    透過電話聯繫： (844) 872-4681

此外，您所屬的州律師協會或當地法律援助辦公室可能可以為您的問題提供幫助。

查詢...

私人律師

可能可以提供幫助的組織：

美國律師協會
    線上查詢：
    www.findlegalhelp.org

    透過電話聯繫： (800) 285-2221

查詢...

為低收入者服務的私人律師

可能可以提供幫助的組織：

法律服務公司（或法律援助辦公室）

    線上查詢：
    www.lsc.gov/find-legal-aid

您如何提供了幫助：

您的舉報將幫助我們推動民權。諸如您的舉報等資訊可幫助我們了解新出現的和緊迫的民權問題。這有助於我們了解如何保護這個國家所有人民權的狀況。

感謝您抽出寶貴時間就您關切之事與司法部聯繫。

耑此，

美國司法部
民權司

""")

    ResponseTemplate.objects.create(
        title='SPL - Referral for PREA Issues (Chinese Traditional)',
        subject=subject,
        body="""
{{ zh_hant.addressee }}，

您於{{ zh_hant.date_of_intake }}與司法部聯繫。基於對這一點的審閱，我們希望您明瞭，您可能應聯繫所在州的PREA協調員。

我們做了什麼：

您的舉報號碼為{{ record_locator }}。

民權司的團隊成員審閱了您提交的資訊。根據您的舉報，我們的團隊確認了您提出的有關拘留中發生的性虐待或性騷擾的顧慮。這應隸屬《消除監獄強姦法》(PREA)。PREA作為法律禁止以下行為：

- 對囚犯和被拘留者進行性虐待或性騷擾；和
- 對舉報性虐待或性騷擾的囚犯或工作人員進行報復。

我們將繼續審閱您的舉報，並在需要其他資訊時與您聯繫。然而，您應明瞭，在涉及對囚犯和被拘留者進行性虐待或性騷擾的情況下，民權司只能在行為不端現象普遍存在的情況下介入。因此，我們通常無法根據個人申訴展開調查。

因此，我們想提醒您，您所在州的PREA協調員可能可以為您的狀況提供幫助。PREA協調員可以調查諸如您申訴的個人投訴。為了幫助您與所在州的PREA協調員建立聯繫，我們在此回覆中包含了一個目錄。

您可以做些什麼：

您所在州的PREA協調員可能可以為您的狀況提供幫助。您可以參考附件中的目錄與所在州的PREA協調員聯繫。

您也可以在PREA資訊中心的網站上了解有關PREA的更多資訊： www.prearesourcecenter.org/training-technical-assistance/prea-101/prisons-and-jail-standards

您如何提供了幫助：

您的舉報將幫助我們推動民權。諸如您的舉報等的資訊可幫助我們了解民權的新趨勢和新問題。這有助於我們了解如何保護這個國家所有人民權的狀況。

感謝您抽出寶貴時間就您關切之事與司法部聯繫。

耑此，

美國司法部
民權司
""")

    ResponseTemplate.objects.create(
        title='Trending - General COVID inquiries (Chinese Traditional)',
        subject=subject,
        body="""
{{ zh_hant.addressee }}，

感謝您於{{ zh_hant.date_of_intake }}向民權司提交的舉報{{ record_locator }}。

由於COVID-19，許多美國人正在適應“新常態”，试图在預防冠狀病毒傳播的關鍵需求與其他也對健康和福祉有所影響的因素之間取得平衡。與所有緊急情況一樣，COVID-19的爆發已影響到許多不同種族、宗教和族裔的人以及殘疾人士。

美國司法部民權司將與整個聯邦政府的其他機構一起監督觀察與COVID-19相關的民權問題。有關更多資訊，請參見 www.justice.gov/crt/fcs。有關聯邦政府對COVID-19回應的更多資訊，請訪問www.whitehouse.gov/priorities/covid-19/和www.coronavirus.gov。

耑此，
美國司法部
民權司
""")

    ResponseTemplate.objects.create(
        title='CRT - Constant Writer (Chinese Traditional)',
        subject=subject,
        body="""
{{ zh_hant.addressee }}，

您於{{ zh_hant.date_of_intake }}與司法部聯繫。您的舉報號碼為{{ record_locator }}。我們先前曾收到您關於此事件的類似信函，我們已對該詢問信函進行了回覆。

我們沒有其他可以補充前次回覆的內容，對於此事件我們無法為您提供進一步的幫助，我們深表遺憾。

耑此，

美國司法部
民權司
""")

def remove_letters(apps, schema_editor):
    ResponseTemplate = apps.get_model('cts_forms', 'ResponseTemplate')
    ResponseTemplate.objects.filter(title='CRM - R1 Form Letter (Chinese Traditional)').delete()
    ResponseTemplate.objects.filter(title='CRM - R2 Form Letter (Chinese Traditional)').delete()
    ResponseTemplate.objects.filter(title='CRM - Referral to FBI (Chinese Traditional)').delete()
    ResponseTemplate.objects.filter(title='CRT - Comments & Opinions (Chinese Traditional)').delete()
    ResponseTemplate.objects.filter(title='CRT - EEOC Referral Letter (Chinese Traditional)').delete()
    ResponseTemplate.objects.filter(title='CRT - No Capacity (Chinese Traditional)').delete()
    ResponseTemplate.objects.filter(title='CRT - Non-Actionable (Chinese Traditional)').delete()
    ResponseTemplate.objects.filter(title='CRT - Request for Agency Review (Chinese Traditional)').delete()
    ResponseTemplate.objects.filter(title='HCE - Referral for Housing/Lending/Public Accommodation (Chinese Traditional)').delete()
    ResponseTemplate.objects.filter(title='SPL - Referral for PREA Issues (Chinese Traditional)').delete()
    ResponseTemplate.objects.filter(title='Trending - General COVID inquiries (Chinese Traditional)').delete()
    ResponseTemplate.objects.filter(title='CRT - Constant Writer (Chinese Traditional)').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('cts_forms', '0105_add_violation_summary_search_index'),
    ]

    operations = [
        migrations.RunPython(add_letters, remove_letters)
    ]
