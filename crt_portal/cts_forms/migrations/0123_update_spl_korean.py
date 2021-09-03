from django.db import migrations


def tweak_spl_tagalog(apps, schema_editor):
    ResponseTemplate = apps.get_model('cts_forms', 'ResponseTemplate')
    korean_spl_form = ResponseTemplate.objects.get(title='SPL - Standard Form Letter (Korean)')
    # adjust addressee and indentation
    korean_spl_form.body = """
{{ ko.addressee }},

귀하의 {{ ko.date_of_intake }} 서신에 감사드립니다. 귀하의 신고 번호는 {{ record_locator }} 입니다. 특별소송과 는 민권 침해를 식별하기 위해 지역 사회 구성원들의 정보에 의존합니다. 매 주 저희는 수 백 건의 잠재적 침해에 대한 신고를
접수합니다. 저희는 이 정보를 수집하고 분석하여 사건을 선별하기 위해 사용하거나 기존 사건의 증거로 사용할 수 있습니다. 귀하의 서신을 검토하여 추가 정보를 위해 귀하에게 연락 할 지를 결정할 것입니다. 저희에게는 모든 서신에 답할 자원이 없습니다.

 특별소송과는 민권국에 속한 여러 부서 중의 하나입니다. 저희는 네 가지 분야의 민권을 보호하는 일을 합니다: 1) 교도소, 감옥, 소년원 및 장애인을 위한 의료 시설을(의료 시설에 있는 사람이 대신 지역 사회에서 서비스를 받아야 하는지를 포함한) 포함 한 주립 및 지방 기관에 있는 사람들의 권리; 2) 주립 및 지방 경찰 및 보안관 부서와 교류하는 사람들의 권리; 3) 사람들이 생식 건강 관리 클리닉 또는 종교 기관에 안전하게 접근 할 수 있는 권리; 그리고 4) 사람들이 주립 및 지방 기관에서 자신의 종교생활을 할 수 있는 권리. 저희는 연방 기관 또는 연방 공무원과 관련된 문제를 해결할 권한이 없습니다.

 귀하의 우려가 본 부서의 업무 영역에 속하지 않는 경우 민권국 웹 페이지를
참조하여 적합한 부서를 찾으실 수 있습니다: https://civilrights.justice.gov/.

 특별 소송과는 여러 무리의 사람들에게 영향을 미치는
광범위한 문제로 인해 발생하는 사례 만 처리합니다. 저희는 개인적인 문제에 대해서는
지원하지 않습니다. 저희는 귀하가 손해 또는 개인적 구제를 복구하도록 도울 수
없습니다. 저희는 부당한 유죄 판결, 항소 또는 선고를 포함한 형사 사건을 지원할 수
없습니다.

 귀하에게 개인적인 문제가 있거나 보상 또는 다른 형태의 개인적인 구제를 구하는
경우, 개인 변호사, 비영리 또는 법률 구조 단체에 도움을 요청 할 수도 있습니다. 저희가 개인 또는 단일 사건을 해결할 수 있는 분야는 두가지 뿐 입니다: 1) 주립 또는 지방 정부가 운영하거나 이를 위해 운영되는 교도소, 감옥, 정신 병원 또는 기타 시설에서 귀하의 종교생활을 금지 시키는 경우 저희는 귀하를 도울 수 있습니다; 2) 귀하가 생식 건강 관리 시설 또는 종교 기관에 출입 할 때 무력 또는 무력의 위협을 경험 한 경우 저희는 귀하를 도울 수 있습니다.

 특별소송과 또는 저희가 하는 일에 대한 자세한
정보는 저희 웹 페이지를 참고하십시오: www.justice.gov/crt/about/spl/.

감사드립니다.

미국 법무부  
민권국
"""
    korean_spl_form.save()


class Migration(migrations.Migration):

    dependencies = [
        ('cts_forms', '0122_update_spl_tagalog'),
    ]

    operations = [
        migrations.RunPython(tweak_spl_tagalog)
    ]
