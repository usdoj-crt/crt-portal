from django.db import migrations

def add_letters(apps, schema_editor):
    ResponseTemplate = apps.get_model('cts_forms', 'ResponseTemplate')
    subject = '回应：您的民权司报告 - {{ zh_hans.section_name }}科的 {{ record_locator }}'
    ResponseTemplate.objects.create(
        title='CRM - R1 Form Letter (Chinese Simplified)',
        subject=subject,
        body="""
{{ zh_hans.addressee }},

您于{{ zh_hans.date_of_intake }}联系了司法部。您的报告编号为 {{ record_locator }}。民权司依靠社区成员提供的信息确定可能的侵犯民权行为。联邦调查局（FBI）和其他执法机构均为该部门进行调查。因此，您可能需要联系您当地的 FBI 办事处或访问 www.FBI.gov。

刑事科是美国司法部民权司的几个部门之一。我们负责执行联邦刑事民权法。刑事科起诉涉及以下方面的刑事案件：

- 联邦、州或其他警务人员或惩戒人员等以表面合法的公权力行事却侵犯民权的行为；
- 仇恨犯罪；
- 出于宗教性质而企图干涉宗教活动的武力或威胁；
- 企图干扰提供或获得生殖健康服务的武力或威胁；以及
- 以强迫劳动或卖淫的形式贩卖人口。

我们无法帮助您赔偿损失或寻求其他个人救济。我们也不能协助您处理正在进行的刑事案件，包括错误定罪、上诉或判刑。更多有关刑事科或我们所从事工作的详细信息，请访问我们的网页：www.justice.gov/crt/about/crm/.

我们将审查您的来信，以便决定是否有必要与您联系以获取更多信息。我们没有资源跟进或回复每封来信。如果您关注的事项不在本部门的工作范围内，不妨参考民权司的网页，以确定该司的另一部门是否能够解决您所关注的事项：www.justice.gov/crt。再次强调，如果您来信是要报告犯罪行为，请联系您当地的联邦和/或州执法机构，例如联邦调查局、您当地的警察局或警长办公室。

此致，
/s/
刑事科
""")

    ResponseTemplate.objects.create(
        title='CRM - R2 Form Letter (Chinese Simplified)',
        subject=subject,
        body="""
{{ zh_hans.addressee }},

您于{{ zh_hans.date_of_intake }}联系了民权司。您的报告编号为 {{ record_locator }}。

民权司刑事科负责执行联邦刑事民权法规。我们的大部分执法活动是针对以表面合法的公权力剥夺公民权利的行为进行调查和起诉。这些事件通常涉及指控执法人员过度使用武力或性侵犯。

您提供的信息不足以让我们确定是否存在可能违反联邦刑事民权法规的行为。因此，我们目前无法授权对您的投诉进行调查。但是，如果您提供有关投诉所涉及情况的具体信息，我们将进一步考虑该指控。您的报告应包括受伤者的姓名；对涉及导致事件发生并包括事件的陈述；任何可能的证人姓名；事件发生的日期以及您认为与此事件有关的任何其他信息。请将此信息重新提交到我们的在线投诉门户网站https://civilrights.justice.gov/，并提供在此電子郵件的主旨行中所列出的您的投诉编号以供參考。

您可以放心，如果证据表明存在可起诉的违反联邦刑事民权法的行为，我们会采取适当的行动。

谢谢！
/s/
刑事科
""")

    ResponseTemplate.objects.create(
        title='CRM - Referral to FBI (Chinese Simplified)',
        subject=subject,
        body="""
{{ zh_hans.addressee }},

您于{{ zh_hans.date_of_intake }}联系了司法部。

我们已经完成以下事项：

您的报告编号为 {{ record_locator }}。

民权司的团队成员审查了您提交的信息。根据您的举报，我们的团队确定您指控的是一起侵犯公民权利的犯罪行为。

我们将仔细审查您的举报，如果需要其他信息，我们会与您联系。然而，您也应该了解，民权司每年都会收到数千份公众举报，并且通常只有在联邦调查局（FBI）或其他执法机构开始调查之后，民权司才会介入。

因此，我们想提醒您，在涉及违反联邦民权法犯罪行为的情况下，FBI 是首个也是最理想的举报机构。

您可以做的事情：

FBI 可能可以帮助您。您可以通过以下任何一种方式与 FBI 联系。

在线：

www.fbi.gov/contact-us

电话或面谈：

联系您当地的 FBI 办公室（较佳的方式）

www.fbi.gov/contact-us/field-offices

您如何提供了帮助：

您的举报将帮助我们推进民事权利。您和他人的举报所提供的信息可以帮助我们了解有关民事权利的新趋势和问题。这有助于我们了解如何保护我国所有人的民事权利。

感谢您抽出宝贵时间就您所关注的事与司法部联系。

此致，

美国司法部
民权司
""")

    ResponseTemplate.objects.create(
        title='CRT - Comments & Opinions (Chinese Simplified)',
        subject=subject,
        body="""
{{ zh_hans.addressee }},

您于{{ zh_hans.date_of_intake }}联系了司法部。您的报告编号为 {{ record_locator }}。

感谢您愿意抽出时间写信给我们表达您的观点。请注意，您所提供的信息将会得到适当的考虑。

此致，

美国司法部
民权司
""")

    ResponseTemplate.objects.create(
        title='CRT - EEOC Referral Letter (Chinese Simplified)',
        subject=subject,
        body="""
{{ zh_hans.addressee }},

您于{{ zh_hans.date_of_intake }}联系了司法部。在仔细审查了您提交的内容之后，我们确定您的举报将由其他联邦机构处理更为妥善。

我们已经完成以下事项：

您的记录编号是 {{ record_locator }}。

民权司的团队成员审查了您提交的信息。根据您的举报，我们的团队确定您所说的就业歧视行为或其他与就业有关的问题。

联邦法律限制了司法部在某些情况下采取直接行动的能力。根据我们团队对您举报的审查，这包括您的问题。

您可以做的事情：

我们并非判定您的举报缺乏根据。而是根据您的情况，另外一个联邦机构可能能够提供帮助。

我们列出了可能可以提供帮助的联邦机构。如果您想继续跟进此事，则应与适当的机构联系。

注意：提出与就业歧视相关的投诉有严格的时间限制。如果您觉得自己在就业方面受到歧视，则应尽快联系相应机构。

我经历了……

基于种族、肤色、原籍国、宗教、性别（包括怀孕、性取向和性别认同）、年龄、残疾或报复的就业歧视。

可能可以提供帮助的机构

平等就业机会委员会（EEOC）

    在线提交：eeoc.gov/filing-charge-discrimination
    通过电话联系：1-800-669-4000
    在离您最近的 EEOC 办公室当面提交： www.eeoc.gov/field-office

我经历了……

基于兵役的就业歧视，包括报复和无法重新聘用。

可能可以提供帮助的机构

美国劳工部
退伍军人就业培训服务处（VETS）

    在线提交或当面联系VETS：www.dol.gov/agencies/vets/
    通过电话联系：1-866-487-2365

我经历了……

联邦政府的就业歧视

可能可以提供帮助的机构

联邦机构的平等就业机会官员

    查找您的联邦 EEO 官员：www.eeoc.gov/federal-sector/federal-agency-eeo-directors

我经历了……

工伤赔偿问题

可能可以提供帮助的机构

美国劳工部
劳工赔偿计划办公室（OWCP）

    电话和亲自前往选项：
    https://www.dol.gov/owcp/owcpkeyp.htm

我经历了……

工资和/或工作时间问题

可能可以提供帮助的机构

美国劳工部
就业标准管理局，工资和工时司

    如何提出投诉：www.dol.gov/agencies/whd/contact/complaints
    通过电话联系：1-866-487-2365

我经历了……

工人安全问题

可能可以提供帮助的机构

美国劳工部
职业健康与安全管理局（OSHA）

    在线提交：www.osha.gov/workers/
    通过电话联系：1-800-321-6742

我经历了……

平等就业机会委员会的问题

可能可以提供帮助的机构

平等就业机会委员会
现场管理计划办公室主任

    131 M Street, NE
    Washington, DC 20507

此外，即使司法部不能帮助您，您的州律师协会或本地法律援助办公室也可能可以为您提供帮助。

如需查找……

私人律师

可能有帮助的组织

美国律师协会

    www.findlegalhelp.org
    通过电话联系：1-800-285-2221

如需查找……

为低收入人士服务的私人律师

可能有帮助的组织

法律服务公司（或法律援助办公室）

    www.lsc.gov/find-legal-aid

您如何提供了帮助：

尽管在此特定情况下我们无法采取行动，但是您的举报将帮助我们推进民事权利。您和他人的举报所提供的信息有助于我们了解新发和紧急的问题。这有助于我们了解如何保护我国所有人的民事权利。

感谢您抽出宝贵时间就您所关注的事项与司法部联系。

此致，

美国司法部
民权司
""")

    ResponseTemplate.objects.create(
        title='CRT - No Capacity (Chinese Simplified)',
        subject=subject,
        body="""
{{ zh_hans.addressee }}，

您于{{ zh_hans.date_of_intake }}联系了司法部。在仔细审查了您提交的内容后，我们决定不对您的投诉采取任何进一步行动。

我们已经完成以下事项：

民权司的团队成员审查了您提交的信息。根据我们的审查，我们决定不对您的投诉采取任何进一步行动。每年我们都会收到数千份侵犯民事权利的举报。遗憾的是，我们没有资源对每份举报采取直接行动。

您的报告编号为 {{ record_locator }}。

您可以做的事情：

我们并非判定您的举报缺乏根据。您的问题可能仍然可以由其他人负责处理，您的州律师协会或本地法律援助办公室可能会为您提供帮助。

    如需查找本地办公室：

    美国律师协会
    www.findlegalhelp.org
    (800) 285-2221

    法律服务公司（或法律援助办公室）
    www.lsc.gov/find-legal-aid

您如何提供了帮助：

虽然我们没有能力处理每份举报，但是您的举报可以帮助我们发现影响多人或社区的问题。它还可以帮助我们了解新的趋势和主题。

感谢您抽出宝贵时间就您所关注的事项与司法部联系。很抱歉，我们无法在此问题上提供更多帮助。

此致，

美国司法部
民权司
""")

    ResponseTemplate.objects.create(
        title='CRT - Non-Actionable (Chinese Simplified)',
        subject=subject,
        body="""
{{ zh_hans.addressee }}，

您于{{ zh_hans.date_of_intake }}联系了司法部。在仔细审查了您提交的内容后，我们决定不对您的投诉采取任何进一步行动。

我们已经完成以下事项：

民权司的团队成员审查了您提交的信息。根据这些信息，我们的团队确定我们执行的联邦民权法不涵盖您所描述的情况。因此，我们无法采取进一步的行动。

您的报告编号为 {{ record_locator }}。

您可以做的事情：

您的问题可能被我们无权执行的其他联邦、州或地方法律所涵盖。我们并非判定您的举报缺乏根据。

即使司法部不能帮助您，您的州律师协会或本地法律援助办公室也可能可以为您提供帮助。

    如需查找本地办公室：

    美国律师协会
    www.findlegalhelp.org
    (800) 285-2221

    法律服务公司（或法律援助办公室）
    www.lsc.gov/find-legal-aid

感谢您抽出宝贵时间就您所关注的事项与司法部联系。很抱歉，我们无法在此问题上提供更多帮助。

此致，

美国司法部
民权司
""")

    ResponseTemplate.objects.create(
        title='CRT - Request for Agency Review (Chinese Simplified)',
        subject=subject,
        body="""
{{ zh_hans.addressee }}，

您于{{ zh_hans.date_of_intake }}联系了司法部。这封信是对您的举报的答复。

我们已经完成以下事项：

您的报告编号为 {{ record_locator }}。

民权司的团队成员审查了您提交的信息。您表示您已向或针对另一联邦机构提出了歧视投诉。

司法部不是审查其他联邦机构在调查有关歧视的投诉后所作决定的权力机构。

因此，我们将不采取进一步的行动。

您可以做的事情：

这封信并不表示您的举报缺乏根据。您的州律师协会或本地法律援助办公室可能会提供帮助。

如需查找……

私人律师

可能有帮助的组织：

美国律师协会

    在线查找：
    www.findlegalhelp.org

    通过电话联系：(800) 285-2221

如需查找……

低收入人士的私人律师

可能有帮助的组织：

法律服务公司（或法律援助办公室）

    在线查找：
    www.lsc.gov/find-legal-aid


您如何提供了帮助：

尽管在此特定情况下我们无法采取行动，但是您的举报将帮助我们推进民事权利。您和他人的举报所提供的信息有助于我们了解新发和紧急的问题。这有助于我们了解如何保护我国所有人的民事权利。

感谢您抽出宝贵时间就您所关注的事项与司法部联系。

此致，

美国司法部
民权司
""")

    ResponseTemplate.objects.create(
        title='HCE - Referral for Housing/Lending/Public Accommodation (Chinese Simplified)',
        subject=subject,
        body="""
{{ zh_hans.addressee }}，

您于{{ zh_hans.date_of_intake }}联系了司法部。

我们已经完成以下事项：

您的报告编号为 {{ record_locator }}。

民权司的团队成员审查了您提交的信息。根据您的举报，我们的团队确定您指控了以下一个或多个领域的歧视：

1）住房；
2）公共住宿，例如酒店和餐馆；或者
3）信贷。

请注意，在涉及以上类型歧视的情况下，民权司通常只有在群体人员受到影响时才会介入。我们通常不会根据某个人的歧视投诉展开调查。

考虑到这一点，我们将仔细审查您的举报，并在需要其他信息和/或能够展开调查时与您联系。

您可以做的事情：

如果您的举报涉及住房歧视，美国住房和城市发展部（“HUD”）可能会提供帮助。HUD 是负责审查仅影响某个人住房投诉的机构。

注意：提出与住房歧视相关的投诉有严格的时间限制。如果您认为自己在住房方面受到歧视，则应尽快联系相应的机构。

我经历了……

基于以下方面的住房歧视：

- 种族或肤色
- 原籍国
- 宗教
- 性别
- 家庭状况
- 残疾，或
- 报复

可能会提供帮助的机构：

美国住房和城市发展部（HUD）
公平住房和平等机会办公室

    在线提交：www.hud.gov/program_offices/fair_housing_equal_opp/online-complaint

    通过电话联系： (800) 669-9777

    在离您最近的本地办公室当面提交：
    www.hud.gov/program_offices/fair_housing_equal_opp/contact_fheo

我经历了……

有关以下方面的问题或疑问：

- 住房补贴或代金券：
- 公共住房管理局
- 公共住房管理局雇员，或
- 房东收受住房补贴

可能可以提供帮助的机构：

美国住房和城市发展部（HUD）
公共和印第安人住房司

    PIH 客户服务中心：
    www.hud.gov/program_offices/public_indian_housing

    通过电话联系：(800) 955-2232

我经历了……

有关以下方面的问题或疑问：

- 无家可归

可能可以提供帮助的机构：

美国住房和城市发展部
无家可归者的资源

    在线查找：
    www.hudexchange.info/housing-and-homeless-assistance/

我经历了……

与以下方面有关的欺诈、浪费或滥用：

- HUD，或
- 与 HUD 相关的计划

可能可以提供帮助的机构：

美国住房和城市发展部（HUD）
监察长办公室

    在线查找：
    www.hudoig.gov/hotline

    通过电子邮件联系：hotline@hudoig.gov

如果您的举报涉及贷款歧视，您可能要向 HUD 和消费者金融保护局（CFPB）进行投诉。这些机构负责审查仅影响个人的投诉。

注意：提出与贷款歧视相关的投诉有严格的时间限制。如果您认为自己在贷款方面受到歧视，则应尽快联系相应的机构。

我经历了……

基于以下方面的住房贷款（即抵押贷款）歧视：

- 种族或肤色
- 原籍国
- 宗教
- 性别
- 家庭状况
- 残疾，或
- 报复

可能会提供帮助的机构：

美国住房和城市发展部（HUD）
公平住房和平等机会办公室

    在线提交：
    www.hud.gov/program_offices/fair_housing_equal_opp/online-complaint

    通过电话联系：(800) 669-9777

    在离您最近的本地办公室当面提交：
    www.hud.gov/program_offices/fair_housing_equal_opp/contact_fheo

我经历了……

基于以下方面的住房贷款（即抵押贷款）或任何其他形式的信贷歧视：

- 种族或肤色
- 原籍国
- 宗教
- 性别
- 婚姻状况
- 年龄（只要您达到了可以签订合同的年龄）
- 从任何公共援助计划中获得收入，或
- 报复

可能可以提供帮助的机构：
消费者金融保护局（CFPB）

    在线提交：
    www.consumerfinance.gov/complaint/

    通过电话联系：(855) 411-2372

如果您的举报涉及包括酒店、餐馆、剧院和其他娱乐场所在内的公共场所的歧视，您所在州的总检察长可能可以提供帮助。

注意：提出与公共场所歧视有关的投诉可能会有时间限制。如果您认为自己受到歧视，则应尽快与州检察长联系。

我经历了……

基于以下方面在公共场所（酒店、餐馆、剧院和娱乐场所）的歧视：

- 种族或肤色
- 宗教，或
- 原籍国

可能可以提供帮助的机构：

州总检察长
    在线查找：www.usa.gov/state-attorney-general
    通过电话联系：(844) 872-4681

此外，您的州律师协会或本地法律援助办公室也可能可以为您解决问题。

如需查找……

私人律师

可能有帮助的组织：

美国律师协会
    在线查找：
    www.findlegalhelp.org

    通过电话联系：(800) 285-2221

如需查找……

为低收入人士服务的私人律师

可能有帮助的组织：

法律服务公司（或法律援助办公室）

    在线查找：
    www.lsc.gov/find-legal-aid


您如何提供了帮助：

您的举报将帮助我们推进民事权利。您和他人的举报所提供的信息可以帮助我们了解有关民事权利的新发和紧急问题。这有助于我们了解如何保护本国所有人的民事权利。

感谢您抽出宝贵时间就您所关注的事项与司法部联系。

此致，

美国司法部
民权司
""")

    ResponseTemplate.objects.create(
        title='SPL - Referral for PREA Issues (Chinese Simplified)',
        subject=subject,
        body="""
{{ zh_hans.addressee }}，

您于{{ zh_hans.date_of_intake }}联系了司法部。根据对这一点的审查，我们希望让您了解，您可能需要联系所在州的 PREA 协调员。

我们已经完成以下事项：

您的报告编号为 {{ record_locator }}。

民权司的团队成员审查了您提交的信息。根据您的举报，我们的团队确定您对拘留期间的性虐待或性骚扰提出了关注。这可能属于《监狱强奸消除法案》（PREA）的范围。PREA 作为法律禁止以下行为：

- 对囚犯和被拘留者进行性虐待或性骚扰；以及
- 对举报性虐待或性骚扰的囚犯或工作人员进行报复。

我们将继续审查您的报告，如果需要其他信息，我们会与您联系。但是，您应该了解，在涉及对囚犯和被拘留者进行性虐待或性骚扰的情况下，民权司只能在行为不端现象普遍存在的情况下介入。因此，我们通常无法根据个人投诉展开调查。

所以，我们想提醒您，您所在州的 PREA 协调员可能可以为您提供帮助。PREA 协调员可以调查像您的问题这样的个人申诉。为了帮助您与所在州的 PREA 协调员建立联系，我们在此回复中包含了目录。

您可以做的事情：

您所在州的 PREA 协调员可能可以为您提供帮助。您可以通过参考附件中的目录与所在州的 PREA 协调员联系。

您也可以在 PREA 信息中心的网站上了解更多有关 PREA 的信息：www.prearesourcecenter.org/training-technical-assistance/prea-101/prisons-and-jail-standards

您如何提供了帮助：

您的举报将帮助我们推进民事权利。您和他人的举报所提供的信息可以帮助我们了解有关民事权利的新趋势和新问题。这有助于我们了解如何保护本国所有人的民事权利。

感谢您抽出宝贵时间就您所关注的事项与司法部联系。

此致，

美国司法部
民权司
""")

    ResponseTemplate.objects.create(
        title='Trending - General COVID inquiries (Chinese Simplified)',
        subject=subject,
        body="""
{{ zh_hans.addressee }}，

感谢您于{{ zh_hans.date_of_intake }}向民权司提交的报告 {{ record_locator }}。

由于新冠疫情，很多美国人正在适应一种“新常态”：一种可以平衡预防冠状病毒传播的迫切需要与影响健康和福祉其他因素的新常态。与所有紧急情况一样，COVID-19疫情已影响到许多不同种族，宗教和族裔的人以及残疾人。

美国司法部民权司将与整个联邦政府的其他机构一道，监督与新冠疫情相关的民权问题。如需了解更多相关信息，请参见 www.justice.gov/crt/fcs。如需了解更多有关联邦政府对新冠疫情回应的信息，请访问 www.whitehouse.gov/priorities/covid-19/ 和 www.coronavirus.gov。

此致，
美国司法部
民权司
""")

    ResponseTemplate.objects.create(
        title='CRT - Constant Writer (Chinese Simplified)',
        subject=subject,
        body="""
{{ zh_hans.addressee }}，

您于{{ zh_hans.date_of_intake }}联系了司法部。您的报告编号为 {{ record_locator }}。我们之前曾收到您关于此事件的类似信件并已进行了回复。

关于之前的回复，我们没有其他可以补充的内容，因此无法就此事为您提供进一步的帮助，我们对此深感遗憾。

此致，

美国司法部
民权司
""")

def remove_letters(apps, schema_editor):
    ResponseTemplate = apps.get_model('cts_forms', 'ResponseTemplate')
    ResponseTemplate.objects.filter(title='CRM - R1 Form Letter (Chinese Simplified)').delete()
    ResponseTemplate.objects.filter(title='CRM - R2 Form Letter (Chinese Simplified)').delete()
    ResponseTemplate.objects.filter(title='CRM - Referral to FBI (Chinese Simplified)').delete()
    ResponseTemplate.objects.filter(title='CRT - Comments & Opinions (Chinese Simplified)').delete()
    ResponseTemplate.objects.filter(title='CRT - EEOC Referral Letter (Chinese Simplified)').delete()
    ResponseTemplate.objects.filter(title='CRT - No Capacity (Chinese Simplified)').delete()
    ResponseTemplate.objects.filter(title='CRT - Non-Actionable (Chinese Simplified)').delete()
    ResponseTemplate.objects.filter(title='CRT - Request for Agency Review (Chinese Simplified)').delete()
    ResponseTemplate.objects.filter(title='HCE - Referral for Housing/Lending/Public Accommodation (Chinese Simplified)').delete()
    ResponseTemplate.objects.filter(title='SPL - Referral for PREA Issues (Chinese Simplified)').delete()
    ResponseTemplate.objects.filter(title='Trending - General COVID inquiries (Chinese Simplified)').delete()
    ResponseTemplate.objects.filter(title='CRT - Constant Writer (Chinese Simplified)').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('cts_forms', '0106_chinese_traditional_form_letters'),
    ]

    operations = [
        migrations.RunPython(add_letters, remove_letters)
    ]
