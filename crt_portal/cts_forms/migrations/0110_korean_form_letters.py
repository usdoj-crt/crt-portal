from django.db import migrations

def add_letters(apps, schema_editor):
    ResponseTemplate = apps.get_model('cts_forms', 'ResponseTemplate')
    subject = '회신: 귀하의 민권국 보고서 - {{ ko.section_name }}과의 {{ record_locator }}'
    ResponseTemplate.objects.create(
        title='CRM - R1 Form Letter (Korean)',
        subject=subject,
        body="""
{{ ko.addressee }},

귀하는 {{ ko.date_of_intake }}에 법무부에 연락하셨습니다. 귀하의 신고서 번호는 {{ record_locator }}입니다. 민권국은 잠재적인 민권 위반 사건을 확인하는 데 지역사회 일원들이 제공하는 정보에 의존합니다. 연방수사국(FBI) 및 기타 사법 기관들이 민권국을 위해 조사를 수행합니다. 그러므로 귀하는 지역 FBI 사무국에 연락하거나 www.FBI.gov를 방문하실 수 있습니다.

형사과는 법무부 민권국에 소속된 여러 부서 과 중 하나입니다. 본 과는 연방 형사 민권법 집행을 담당하고 있습니다. 형사과는 다음과 관련된 형사 사건을 기소합니다.

- 연방, 주, 또는 기타 경찰관 또는 교도관 등과 같은 법적 권한을 갖고 행동하는 사람들에 의한 민권 위반
- 증오 범죄
- 종교적인 속성 때문에 종교적 활동을 방해할 의도로 이루어지는 폭력 또는 위협
- 생식 보건 서비스를 제공하거나 받는 것을 방해할 의도로 이루어지는 폭력 또는 위협 그리고
- 강제 노동 또는 상업적 성행위의 형태인 인신매매.

본 과는 귀하가 손해 배상을 받거나 일체의 기타 개인적 구제를 구하는 것을 도와드릴 수 없습니다. 본 과는 오판, 항소 또는 양형을 포함한 진행 중인 형사 사건에 도움을 드릴 수 없습니다. 형사과 또는 담당 업무에 대한 더 자세한 정보를 민권국 웹페이지에서 조회하실 수 있습니다: www.justice.gov/crt/about/crm/.

본 과는 추가 정보를 얻기 위해 귀하에게 연락할 필요가 있는지 결정하기 위해서 귀하의 서신을 검토할 것입니다. 본 과는 모든 서신에 후속 조치를 취하거나 응답할 자원을 가지고 있지 않습니다. 귀하의 우려사항이 본 과의 업무 영역이 아닐 경우 민권국 웹페이지 www.justice.gov/crt를 참조하셔서 민권국의 다른 과가 귀하의 우려사항을 처리할 수 있는지 알아보실 수 있습니다. 재차 말씀 드리지만, 귀하가 범죄를 신고하기 위해서 서신을 보내셨을 경우 연방수사국 또는 지역 경찰국 또는 보안관 사무소와 같은 귀하 소재 지역의 연방 및/또는 주 법 집행 기관에 연락하시길 바랍니다.

안녕히 계십시오.
/s/
형사과
""")

    ResponseTemplate.objects.create(
        title='CRM - R2 Form Letter (Korean)',
        subject=subject,
        body="""
{{ ko.addressee }},

귀하는 {{ ko.date_of_intake }}에 민권국에 연락하셨습니다. 귀하의 신고서 번호는 {{ record_locator }}입니다.

민권국의 형사과는 연방 형사 민권법 집행을 담당하고 있습니다. 본 과의 집행 활동의 대부분은 법적 권한을 가지고 민권을 박탈하는 사건의 조사 및 기소와 관련이 있습니다. 이러한 문제들은 일반적으로 법 집행관의 과도한 폭력 또는 성적 학대 주장과 관련되어 있습니다.

귀하가 제공한 정보는 연방 형사 민권법 위반 가능성에 대한 실체를 결정하기에 충분치 않습니다. 그러므로 현재로는 귀하의 진정사항을 조사하도록 승인할 수 없습니다. 하지만 귀하가 진정사항과 관련된 상황에 대해서 구체적인 정보를 제공할 경우 귀하가 주장하는 내용을 고려할 것입니다. 귀하는 상해를 당한 사람의 이름, 해당 사건을 포함해서 사건에 이르기까지의 혐의 주장에 관련된 설명, 일체의 가능한 목격자의 이름, 사건 날짜 및 사건과 관련 있다고 생각하는 일체의 기타 정보를 제공해야 합니다. 온라인 진정사항 포털인 https://civilrights.justice.gov/에 이 정보를 다시 제출하고 이 이메일의 제목란에 나와있는 진정사항 번호를 참조로 제공하십시오.

기소 가능한 연방 형사 민권법의 위반을 보여주는 증거가 있을 경우 적절한 조치가 취해질 것입니다.

감사합니다.
/s/
형사과
""")

    ResponseTemplate.objects.create(
        title='CRM - Referral to FBI (Korean)',
        subject=subject,
        body="""
{{ ko.addressee }},

귀하께서는 {{ ko.date_of_intake }}에 법무부에 연락하셨습니다.

조치된 사항:

귀하의 신고서 번호는 {{ record_locator }}입니다.

민권국 담당자들이 귀하가 제출하신 정보를 검토했습니다. 귀하의 신고에 기반하여 담당 팀은 귀하가 민권의 형사 위반을 주장하셨다고 결정했습니다.

민권국은 귀하의 신고서를 주의 깊게 검토하고 추가적 정보가 필요할 경우 연락 드릴 것입니다. 하지만 민권국은 매년 대중으로부터 수천 건의 신고를 받으며 일반적으로 연방수사국(FBI) 또는 기타 법 집행 기관이 조사를 시작한 후에야만 사건에 개입된다는 것을 알려 드립니다.

따라서 연방 민권법의 형사적 위반과 관련된 상황에서는 FBI가 신고를 할 첫 번째 그리고 최선의 기관이라는 것을 아시기 바랍니다.

귀하가 하실 수 있는 일:

FBI가 귀하의 상황에 도움을 드릴 수도 있습니다. 아래에 제시된 방법으로 FBI에 연락할 수 있습니다.

온라인:

www.fbi.gov/tips

전화 또는 직접 방문:

지역 FBI 사무실에 연락(권장함)

www.fbi.gov/contact-us/field-offices

귀하가 도와 주신 내용:

귀하의 신고는 민권 개선에 도움을 줄 수 있습니다. 귀하의 신고와 유사한 신고 정보를 통해 민권국은 민권과 관련된 출현 동향 및 문제들을 이해할 수 있습니다. 이를 통해 민권국은 미국 내 모든 사람들의 민권을 보호하기 위해 어떠한 조치를 취해야 하는지 알 수 있습니다.

시간을 내셔서 귀하의 우려사항을 법무부에 알려 주심에 감사드립니다.

안녕히 계십시오.

미국 법무부
민권국
""")

    ResponseTemplate.objects.create(
        title='CRT - Comments & Opinions (Korean)',
        subject=subject,
        body="""
{{ ko.addressee }},

귀하께서는 {{ ko.date_of_intake }}에 법무부에 연락하셨습니다. 귀하의 신고서 번호는 {{ record_locator }}입니다.

인권 문제와 관련하여 관심을 갖고 시간을 내셔서 귀하의 견해를 표명하시기 위해서 서신을 보내 주신 데 대해 감사 드립니다. 귀하가 제공하신 정보에 관심을 갖고 담당자가 신중히 처리할 것임을 알려 드립니다.

안녕히 계십시오.

미국 법무부
민권국
""")

    ResponseTemplate.objects.create(
        title='CRT - EEOC Referral Letter (Korean)',
        subject=subject,
        body="""
{{ ko.addressee }},

귀하는 {{ ko.date_of_intake }}에 법무부에 연락하셨습니다. 제출하신 내용을 주의 깊게 검토한 결과, 귀하의 신고는 다른 연방 기관이 더 적절하게 처리할 수 있을 것이라고 결정했습니다.

조치된 사항:

귀하의 기록 번호는 {{ record_locator }}입니다.

민권국 담당자들이 귀하가 제출하신 정보를 검토했습니다. 귀하의 신고서에 근거하여, 담당 팀은 귀하가 고용 차별 또는 기타 고용 관련 문제를 주장하셨다고 결정했습니다.

연방 법에 따라, 법무부가 일정한 상황에서 직접적 조치를 취할 수 있는 능력에 한계가 있습니다. 담당 팀이 귀하의 신고서를 검토한 결과, 귀하의 문제는 여기에 포함됩니다.

귀하가 하실 수 있는 일:

귀하의 신고가 가치가 없다고 판단하는 것은 아닙니다. 오히려, 다른 연방 기관이 귀하의 상황에 도움을 드릴 수도 있습니다.

도움이 될 수 있는 연방 기관들의 목록을 본 서신에 포함하였습니다. 이 문제를 더욱 추구하길 원하시면, 적절한 기관에 연락하십시오.

참고: 고용 차별에 관련된 진정사항을 제출하는 데에는 엄격한 시간 제한이 있습니다. 고용 관련 차별을 당했다고 생각할 경우 가능한 한 빨리 적절한 기관에 연락해야 합니다.

나는......을 경험 했다

인종, 피부색, 출신국, 종교, 성별(임신, 성적 지향 및 성별 정체성 포함), 연령, 장애 또는 보복에 근거한 고용 차별.

도움을 줄 수 있는 기관

평등 고용기회 위원회(Equal Employment Opportunity Commission, EEOC)

    온라인으로 제출: eeoc.gov/filing-charge-discrimination
    전화로 연락: 1-800-669-4000
    인근 EEOC 사무실에 직접 방문 제출: www.eeoc.gov/field-office

나는......을 경험 했다

보복 및 재고용 불가를 포함해서 군복무에 기반한 고용 차별.

도움을 줄 수 있는 기관

미국 노동부
재향군인 고용훈련서비스(Veterans Employment Training Service, VETS)

    온라인으로 제출 또는 VETS에 직접 연락: www.dol.gov/agencies/vets/
    전화로 연락: 1-866-487-2365

나는......을 경험 했다

연방 정부에 의한 고용 차별

도움을 줄 수 있는 기관

연방 기관에 주재하는 평등 고용기회(Equal Employment Opportunity, EEO) 담당자

    지역 연방 EEO 담당자를 찾으십시오: www.eeoc.gov/federal-sector/federal-agency-eeo-directors

나는......을 경험 했다

산재보상 문제

도움을 줄 수 있는 기관

미국 노동부
산재보상국(Office of Workers’ Compensation Programs, OWCP)

    전화 연락 및 직접 방문 옵션:
    https://www.dol.gov/owcp/owcpkeyp.htm

나는......을 경험 했다

임금 및/또는 근로시간 문제

도움을 줄 수 있는 기관

미국 노동부
고용기준 사무국, 임금 및 근로시간 과(Employment Standards Administration, Wage and Hour Division)

    진정사항을 제출하는 방법: www.dol.gov/agencies/whd/contact/complaints
    전화로 연락: 1-866-487-2365

나는......을 경험 했다

근로자 안전 관련 문제

도움을 줄 수 있는 기관

미국 노동부
산업안전보건청(Occupational Health and Safety Administration, OSHA)

    온라인으로 제출: www.osha.gov/workers/
    전화로 연락: 1-800-321-6742

나는......을 경험 했다

평등 고용기회 위원회(Equal Employment Opportunity Commission)와의 문제

도움을 줄 수 있는 기관

평등 고용기회 위원회(EEOC)
실장, 현장 관리 프로그램 실(Office of Field Management Programs)

    131 M Street, NE
    Washington, DC 20507

또한 법무부는 도와드릴 수 없지만 귀하가 소재하는 주의 주 변호사 협회 또는 지역 법률구조사무소가 귀하의 문제 해결에 도움을 줄 수도 있습니다.

......을 찾으시려면

개인 변호사

도움을 줄 수 있는 조직

미국 변호사 협회(American Bar Association)

    www.findlegalhelp.org
    전화로 연락: 1-800-285-2221

......을 찾으시려면

저소득층을 위한 개인 변호사

도움을 줄 수 있는 조직

법률서비스 법인(Legal Services Corporation) (또는 법률구조공사(Legal Aid Offices))

    www.lsc.gov/find-legal-aid

귀하가 도와 주신 내용:

이 특정 사안에 대해 민권국이 직접 처리할 수 없으나 귀하의 신고는 민권 개선에 도움을 줄 것입니다. 귀하의 신고와 유사한 신고 정보를 통해 민권국은 민권과 관련된 긴급한 출현 문제들을 파악할 수 있습니다. 이를 통해 민권국은 미국 내 모든 사람들의 민권을 보호하기 위해 어떠한 조치를 취해야 하는지 알 수 있습니다.

시간을 내셔서 귀하의 우려사항을 법무부에 알려 주심에 감사드립니다.

안녕히 계십시오.

미국 법무부
민권국
""")

    ResponseTemplate.objects.create(
        title='CRT - No Capacity (Korean)',
        subject=subject,
        body="""
{{ ko.addressee }}，

귀하는 {{ ko.date_of_intake }}에 법무부에 연락하셨습니다. 귀하가 제출하신 내용을 주의 깊게 검토한 후 귀하의 진정사항에 대해 추가 조치를 취하지 않기로 결정했습니다.

조치된 사항:

민권국 담당자들이 귀하가 제출하신 정보를 검토했습니다. 검토에 기반하여 귀하의 진정사항에 대해 추가 조치를 취하지 않기로 결정했습니다. 민권국은 매년 수천 여 건의 민권 위반 신고를 받습니다. 유감스럽게도 민권국은 모든 신고에 대해서 직접적 조치를 취할 자원을 가지고 있지 않습니다.

귀하의 신고서 번호는 {{ record_locator }}였습니다.

귀하가 하실 수 있는 일:

귀하의 신고가 실체적 사실이 없다고 판단하는 것은 아닙니다. 귀하의 문제에 대해 다른 조직들이 조치를 취할 수 있습니다. 귀하가 소재하는 주의 주 변호사 협회 또는 지역 법률구조공사에서 도움을 줄 수도 있습니다.

    지역 사무소를 찾으시려면:

    미국 변호사 협회(American Bar Association)
    www.findlegalhelp.org
    (800) 285-2221

    법률서비스 법인(Legal Services Corporation) (또는 법률구조공사(Legal Aid Offices))
    www.lsc.gov/find-legal-aid

귀하가 도와 주신 내용:

민권국이 각 개인의 신고를 모두 처리할 수 있는 역량은 없으나, 귀하의 신고를 통해 많은 사람 또는 지역사회에 영향을 미치는 문제들을 알 수 있습니다. 또한 출현하는 문제들의 동향 및 주제들을 파악하는 데도 도움이 됩니다.

시간을 내셔서 귀하의 우려사항을 법무부에 알려 주심에 감사드립니다. 이 문제에 대해서 더 이상의 도움을 드리지 못하는 점을 유감으로 생각합니다.

안녕히 계십시오.

미국 법무부
민권국
""")

    ResponseTemplate.objects.create(
        title='CRT - Non-Actionable (Korean)',
        subject=subject,
        body="""
{{ ko.addressee }}，

귀하는 {{ ko.date_of_intake }}에 법무부에 연락하셨습니다. 귀하가 제출하신 내용을 주의 깊게 검토한 후 귀하의 진정사항에 대해 추가 조치를 취하지 않기로 결정했습니다.

조치된 사항:

민권국 담당자들이 귀하가 제출하신 정보를 검토했습니다. 이 정보에 기반하여 담당 팀은 귀하가 설명하신 상황이 민권국이 집행할 수 잇는 연방 민권법 사안에 해당되지 않는다고 결정했습니다. 그러므로 더 이상의 조치를 취할 수 없습니다.

귀하의 신고서 번호는 {{ record_locator }}입니다.

귀하가 하실 수 있는 일:

귀하의 문제는 민권국이 집행할 권한이 없는 다른 연방, 주, 또는 지역 법률의 관할 사항이 될 수 있습니다. 귀하의 신고가 실체적 사실이 없다고 판단하는 것은 아닙니다.

법무부가 도울 수 없더라도 귀하가 소재하는 주의 주 변호사 협회 또는 지역 법률구조공사에서 귀하의 문제에 도움을 줄 수도 있습니다.

    지역 사무소 찾기:

    미국 변호사 협회(American Bar Association)
    www.findlegalhelp.org
    (800) 285-2221

    법률서비스 법인(Legal Services Corporation) (또는 법률구조공사(Legal Aid Offices))
    www.lsc.gov/find-legal-aid

시간을 내셔서 귀하의 우려사항을 법무부에 알려 주심에 감사드립니다. 이 문제에 대해서 더 이상의 도움을 드리지 못하는 점을 유감으로 생각합니다.

안녕히 계십시오.

미국 법무부
민권국
""")

    ResponseTemplate.objects.create(
        title='CRT - Request for Agency Review (Korean)',
        subject=subject,
        body="""
{{ ko.addressee }}，

귀하는 {{ ko.date_of_intake }}에 법무부에 연락하셨습니다. 이 서신은 귀하의 신고에 대한 답변서입니다.

조치된 사항:

귀하의 신고서 번호는 {{ record_locator }}입니다.

민권국 담당자들이 귀하가 제출하신 정보를 검토했습니다. 귀하는 다른 연방 기관에 또는 다른 연방 기관에 대해서 차별 진정사항을 제출했다고 언급하셨습니다.

법무부는 다른 연방 기관이 차별에 대한 진정사항의 조사 후 내린 결정에 대해 검토할 수 있는 권한이 없습니다.

그러므로 더 이상의 조치를 취하지 않겠습니다.

귀하가 하실 수 있는 일:

이 서신은 귀하의 신고가 가치가 없다고 결정하는 것이 아닙니다. 귀하가 소재하는 주의 주 변호사 협회 또는 지역 법률구조공사에서 도움을 줄 수도 있습니다.

......을 찾으시려면

개인 변호사

도움을 줄 수 있는 조직

미국 변호사 협회(American Bar Association)

    온라인으로 찾기:
    www.findlegalhelp.org

    전화로 연락: (800) 285-2221

......을 찾으시려면

저소득층을 위한 개인 변호사

도움을 줄 수 있는 조직

법률서비스 법인(Legal Services Corporation) (또는 법률구조공사(Legal Aid Offices))

    온라인으로 찾기:
    www.lsc.gov/find-legal-aid

귀하가 도와 주신 내용:

이 특정 사안에 대해 민권국이 직접 처리할 수 없으나 귀하의 신고는 민권 개선에 도움을 줄 수 있습니다. 귀하의 신고와 유사한 신고 정보를 통해 민권국은 민권과 관련된 긴급한 출현 문제들을 파악할 수 있습니다. 이를 통해 민권국은 미국 내 모든 사람들의 민권을 보호하기 위해 어떠한 조치를 취해야 하는지 알 수 있습니다.

시간을 내셔서 귀하의 우려사항을 법무부에 알려 주심에 감사드립니다.

안녕히 계십시오.

미국 법무부
민권국
""")

    ResponseTemplate.objects.create(
        title='HCE - Referral for Housing/Lending/Public Accommodation (Korean)',
        subject=subject,
        body="""
{{ ko.addressee }}，

귀하는 {{ ko.date_of_intake }}에 법무부에 연락하셨습니다.

조치된 사항:

귀하의 신고서 번호는 {{ record_locator }}입니다.

민권국 담당자들이 귀하가 제출하신 정보를 검토했습니다. 귀하의 신고서에 기반하여 민권국 담당 팀은 귀하가 다음 중 한 분야에서 차별을 주장하셨다고 결정했습니다.

1) 주택
2) 호텔 및 식당과 같은 공공 시설 또는
3) 신용.

이러한 유형의 차별과 관련된 상황에서는 민권국은 일반적으로 다수의 사람들이 영향을 받을 경우에만 개입할 수 있다는 점을 이해해 주십시오. 민권국은 일반적으로 차별에 대한 개인의 주장에 기반해서 조사에 착수하지 않습니다.

이 점을 염두하시되, 저희 팀은 귀하의 신고서를 주의 깊게 검토해서 추가 정보가 필요하고/필요하거나 조사에 착수할 수 있게 되면 연락드리겠습니다.

귀하가 하실 수 있는 일:

귀하의 신고가 주거 관련 차별일 경우, 미국 주택도시개발부(Department of Housing & Urban Development, “HUD”)가 도와드릴 수도 있습니다. HUD는 한 개인에게 영향을 미치는 주거 관련 진정사항을 검토하는 일을 담당하는 기관입니다.

참고: 주거 차별 진정사항을 제출하는 데에는 엄격한 시간 제한이 있습니다. 주택 관련 차별을 당했다고 생각할 경우 가능한 한 빨리 적절한 기관에 연락해야 합니다.

나는......을 경험 했다

다음에 근거한 주거 차별:

- 인종 또는 피부색
- 출신국
- 종교
- 성별
- 가족의 상태
- 장애 또는
- 보복

도움을 줄 수 있는 기관:

미국 주택도시개발부(Department of Housing & Urban Development, HUD)
공정주거 및 동등기회 사무국(Office of Fair Housing and Equal Opportunity)

    온라인으로 제출: www.hud.gov/program_offices/fair_housing_equal_opp/online-complaint

    전화로 연락: (800) 669-9777

    인근 지역 사무실에 직접 방문 제출:
    www.hud.gov/program_offices/fair_housing_equal_opp/contact_fheo

나는......을 경험 했다

다음과 관련된 문제 또는 질문:

- 주택 보조금 또는 바우처
- 공공주택 당국
- 공공주택 당국 직원 또는
- 주택 보조금을 받고 있는 집주인

도움을 줄 수 있는 기관:

미국 주택도시개발부(Department of Housing & Urban Development, HUD)
공공 및 인디언 주거 담당 사무소(Public and Indian Housing, PIH)

    PIH 고객 서비스 센터:
    www.hud.gov/program_offices/public_indian_housing

    전화로 연락: (800) 955-2232

나는......을 경험 했다

다음과 관련된 문제 또는 질문:

- 노숙자

도움을 줄 수 있는 기관:

미국 주택도시개발부(Department of Housing & Urban Development)
노숙자에 대한 리소스

    온라인으로 찾기:
    www.hudexchange.info/housing-and-homeless-assistance/

나는......을 경험 했다

다음과 관련된 사기, 낭비 또는 남용:

- HUD 또는
- HUD 관련 프로그램

도움을 줄 수 있는 기관:

미국 주택도시개발부(Department of Housing & Urban Development, HUD)
감찰관실(Office of Inspector General)

    온라인으로 찾기:
    www.hudoig.gov/hotline

    이메일로 연락: hotline@hudoig.gov

귀하의 신고가 대출 차별과 관련된 경우 HUD 및 소비자금융보호국(Consumer Financial Protection Bureau, CFPB)에 진정사항을 제출할 수 있습니다. 이 기관들은 한 개인에게 영향을 미치는 진정사항을 검토하는 일을 담당합니다.

참고: 대출 차별 진정사항을 제출하는 데에는 엄격한 시간 제한이 있습니다. 대출 관련 차별을 당했다고 생각할 경우 가능한 한 빨리 적절한 기관에 연락해야 합니다.

나는......을 경험 했다

다음에 근거한 주택 융자(즉, 모기지) 차별:

- 인종 또는 피부색
- 출신국
- 종교
- 성별
- 가족의 상태
- 장애 또는
- 보복

도움을 줄 수 있는 기관:

미국 주택도시개발부(Department of Housing & Urban Development, HUD)
공정주거 및 동등기회 사무국(Office of Fair Housing and Equal Opportunity)

    온라인으로 제출:
    www.hud.gov/program_offices/fair_housing_equal_opp/online-complaint

    전화로 연락: (800) 669-9777

    인근 지역 사무실에 직접 방문 제출:
    www.hud.gov/program_offices/fair_housing_equal_opp/contact_fheo

나는......을 경험 했다

다음에 근거한 주택 융자(즉, 모기지) 또는 일체 기타 형태의 신용 차별:

- 인종 또는 피부색
- 출신국
- 종교
- 성별
- 결혼 여부
- 연령(계약 체결 가능한 연령자에 한해)
- 일체의 공공 지원 프로그램으로부터 소득 수령 또는
- 보복

도움을 줄 수 있는 기관:
소비자금융보호국(Consumer Financial Protection Bureau, CFPB)

    온라인으로 제출:
    www.consumerfinance.gov/complaint/

    전화로 연락: (855) 411-2372

귀하의 신고가 호텔, 식당, 극장 및 기타 여흥 장소를 포함한 공공 시설에서의 차별과 관련될 경우 귀하가 소재하는 주의 주 법무장관실에서 도와드릴 수 있습니다.

참고: 공공 시설에서의 차별과 관련된 진정사항 제출에는 시간 제한이 있을 수 있습니다. 차별을 당했다고 생각할 경우 가능한 한 빨리 주 법무장관실에 연락해야 합니다.

나는......을 경험 했다

다음에 근거한 공공 시설에서의 차별(호텔, 식당, 극장 및 여흥 장소):

- 인종 또는 피부색
- 종교 또는
- 출신국

도움을 줄 수 있는 기관:

주 법무장관
    온라인으로 찾기: www.usa.gov/state-attorney-general
    전화로 연락: (844) 872-4681

또한 귀하가 소재하는 주의 주 변호사 협회 또는 지역 법률구조공사에서 귀하의 문제에 대해 도움을 줄 수도 있습니다.

......을 찾으시려면

개인 변호사

도움을 줄 수 있는 조직

미국 변호사 협회(American Bar Association)
    온라인으로 찾기:
    www.findlegalhelp.org

    전화로 연락: (800) 285-2221

......을 찾으시려면

저소득층을 위한 개인 변호사

도움을 줄 수 있는 조직

법률서비스 법인(Legal Services Corporation) (또는 법률구조공사(Legal Aid Offices))

    온라인으로 찾기:
    www.lsc.gov/find-legal-aid

귀하가 도와 주신 내용:

귀하의 신고는 민권 개선에 도움을 줄 수 있습니다. 귀하의 신고와 유사한 신고 정보를 통해 민권국은 민권과 관련된 긴급한 출현 문제들을 파악할 수 있습니다. 이를 통해 민권국은 미국 내 모든 사람들의 민권을 보호하기 위해 어떠한 조치를 취해야 하는지 알 수 있습니다.

시간을 내셔서 귀하의 우려사항을 법무부에 알려 주심에 감사드립니다.

안녕히 계십시오.

미국 법무부
민권국
""")

    ResponseTemplate.objects.create(
        title='SPL - Referral for PREA Issues (Korean)',
        subject=subject,
        body="""
{{ ko.addressee }}，

귀하는 {{ ko.date_of_intake }}에 법무부에 연락하셨습니다. 이 시점까지의 검토에 기반하여, 귀하가 소재하는 주의 PREA 코디네이터에게 연락하실 수 있다는 것을 알려 드리고자 합니다.

조치된 사항:

귀하의 신고서 번호는 {{ record_locator }}입니다.

민권국 담당자들이 귀하가 제출하신 정보를 검토했습니다. 귀하의 신고에 기반하여, 담당 팀은 구금 장소에서의 성적학대 또는 성희롱과 관련된 우려사항을 제기하신 것으로 결정했습니다. 이 사안은 감옥강간제거법(Prison Rape Elimination Act, PREA)에 해당될 수 있습니다. PREA는 다음을 불법으로 정하는 법입니다.

- 재소자 및 구류자를 성적으로 학대 또는 성희롱하는 행위 및
- 성적학대 또는 성희롱을 신고하는 재소자 또는 교도소 직원에 대해 보복하는 행위.

귀하의 보고서를 주의 깊게 계속해서 검토하고 추가적 정보가 필요할 경우 연락드리겠습니다. 하지만 재소자 및 구류자의 성적학대 또는 성희롱과 관련된 상황에서 민권국은 비행의 광범위한 패턴이 있을 때에만 개입할 수 있다는 점을 아셔야 합니다. 그러므로 일반적으로 개인의 주장에 기반해서는 조사에 착수할 수 없습니다.

따라서 귀하의 상황에서 해당 주의 PREA 코디네이터가 도움을 드릴 수 있음을 알려드리고자 합니다. PREA 코디네이터는 귀하의 주장과 같은 개개인들의 주장을 조사할 수 있습니다. 귀하가 소재하는 주의 PREA 코디네이터와 연결하는 것을 도와드리기 위해서 이 답변서에 인명부를 포함했습니다.

귀하가 하실 수 있는 일:

귀하가 소재하는 주의 PREA 코디네이터가 귀하의 상황에 도움을 드릴 수 있습니다. 첨부된 인명부를 참조하여 해당 주 PREA 코디네이터에게 연락할 수 있습니다.

PREA에 대한 자세한 내용은 다음 PREA 정보 센터 웹사이트에서 알아보실 수도 있습니다: www.prearesourcecenter.org/training-technical-assistance/prea-101/prisons-and-jail-standards

귀하가 도와 주신 내용:

귀하의 신고는 민권 개선에 도움을 줄 수 있습니다. 귀하의 신고와 유사한 신고 정보를 통해 민권국은 민권과 관련된 출현 동향 및 문제들을 이해할 수 있습니다. 이를 통해 민권국은 미국 내 모든 사람들의 민권을 보호하기 위해 어떠한 조치를 취해야 하는지 알 수 있습니다.

시간을 내셔서 귀하의 우려사항을 법무부에 알려 주심에 감사드립니다.

안녕히 계십시오.

미국 법무부
민권국
""")

    ResponseTemplate.objects.create(
        title='Trending - General COVID inquiries (Korean)',
        subject=subject,
        body="""
{{ ko.addressee }}，

{{ ko.date_of_intake }}에 민권국에 제출하신 신고서 {{ record_locator }}에 감사드립니다.

많은 미국인들이 코로나 바이러스(COVID-19) 팬데믹으로 인해 “뉴노멀”에 적응하며, 코로나바이러스의 전파를 방지해야 하는 극히 중요한 필요성과 건강 및 안녕에 영향을 미치는 다른 요인들 간에 균형을 이루고자 노력하고 있습니다. 모든 비상사태에서처럼 코로나 바이러스(COVID-19) 발병은 여러 다양한 인종, 종교 및 민족성 및 장애를 가진 사람들에게 영향을 미쳤습니다.

연방 정부 내 다른 기관들과 더불어 미국 법무부의 민권국은코로나 바이러스(COVID-19)과 관련된 민권 문제들을 모니터링합니다. 자세한 정보는 www.justice.gov/crt/fcs에서 참조바랍니다. COVID-19에 대한 연방 정부의 대응에 대한 자세한 정보는 www.whitehouse.gov/priorities/covid-19/ 및 www.coronavirus.gov에서 참조할 수 있습니다.

안녕히 계십시오.
미국 법무부
민권국
""")

    ResponseTemplate.objects.create(
        title='CRT - Constant Writer (Korean)',
        subject=subject,
        body="""
{{ ko.addressee }}，

귀하는 {{ ko.date_of_intake }}에 법무부에 연락하셨습니다. 귀하의 신고서 번호는 {{ record_locator }}입니다. 민권국은 이 문제에 대한 유사한 서신을 이전에도 받았으며 그 문의에 답변을 제공하였습니다.

이전에 보내드린 답변에 추가할 수 있는 내용이 없으며 이 문제에 대해서 추가적으로 도움을 드릴 수 없어 진심으로 유감으로 생각합니다.

안녕히 계십시오.

미국 법무부
민권국
""")

def remove_letters(apps, schema_editor):
    ResponseTemplate = apps.get_model('cts_forms', 'ResponseTemplate')
    ResponseTemplate.objects.filter(title='CRM - R1 Form Letter (Korean)').delete()
    ResponseTemplate.objects.filter(title='CRM - R2 Form Letter (Korean)').delete()
    ResponseTemplate.objects.filter(title='CRM - Referral to FBI (Korean)').delete()
    ResponseTemplate.objects.filter(title='CRT - Comments & Opinions (Korean)').delete()
    ResponseTemplate.objects.filter(title='CRT - EEOC Referral Letter (Korean)').delete()
    ResponseTemplate.objects.filter(title='CRT - No Capacity (Korean)').delete()
    ResponseTemplate.objects.filter(title='CRT - Non-Actionable (Korean)').delete()
    ResponseTemplate.objects.filter(title='CRT - Request for Agency Review (Korean)').delete()
    ResponseTemplate.objects.filter(title='HCE - Referral for Housing/Lending/Public Accommodation (Korean)').delete()
    ResponseTemplate.objects.filter(title='SPL - Referral for PREA Issues (Korean)').delete()
    ResponseTemplate.objects.filter(title='Trending - General COVID inquiries (Korean)').delete()
    ResponseTemplate.objects.filter(title='CRT - Constant Writer (Korean)').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('cts_forms', '0109_tagalog_form_letters'),
    ]

    operations = [
        migrations.RunPython(add_letters, remove_letters)
    ]
