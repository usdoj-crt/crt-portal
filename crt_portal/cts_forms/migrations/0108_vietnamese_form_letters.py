from django.db import migrations

def add_letters(apps, schema_editor):
    ResponseTemplate = apps.get_model('cts_forms', 'ResponseTemplate')
    subject = 'Hồi đáp: Báo Cáo của Ban Dân Quyền của Quý Vị - {{ record_locator }} từ Phòng {{ vi.section_name }}'
    ResponseTemplate.objects.create(
        title='CRM - R1 Form Letter (Vietnamese)',
        subject=subject,
        body="""
{{ vi.addressee }},

Quý vị đã liên hệ với Bộ Tư pháp vào ngày {{ vi.date_of_intake }}. Mã số báo cáo của quý vị là {{ record_locator }}. Ban Dân quyền dựa vào thông tin từ các thành viên cộng đồng để xác định các hành vi vi phạm dân quyền tiềm ẩn. Cục Điều tra Liên bang và các cơ quan hành pháp khác tiến hành các cuộc điều tra cho Ban. Do đó, quý vị có thể muốn liên hệ với văn phòng FBI địa phương hoặc truy cập www.FBI.gov.

Bộ phận Hình sự là một trong một số các Bộ phận trong Ban Dân quyền của Bộ Tư pháp Hoa Kỳ. Chúng tôi chịu trách nhiệm thực thi các quy chế về quyền dân sự hình sự của liên bang. Bộ phận Hình sự truy tố các vụ án hình sự liên quan đến:

- Hành vi vi phạm dân quyền của những người hành động nhân danh luật pháp, chẳng hạn như quan chức liên bang, tiểu bang, hoặc các sĩ quan cảnh sát hoặc cán bộ cải huấn khác;
- Tội phạm thù ghét;
- Ép buộc hoặc đe dọa nhằm cản trở các hoạt động tôn giáo vì tính chất tôn giáo của chúng;
- Ép buộc hoặc đe dọa nhằm cản trở việc cung cấp hoặc nhận các dịch vụ sức khỏe sinh sản và
- Buôn bán người dưới hình thức cưỡng bức lao động hoặc mại dâm.

Chúng tôi không thể giúp quý vị khắc phục tổn hại hoặc tìm kiếm bất kỳ biện pháp cứu trợ cá nhân nào khác. Chúng tôi cũng không thể hỗ trợ quý vị trong các vụ án hình sự đang diễn ra, bao gồm cả việc cáo buộc, kháng cáo, hoặc kết án oan sai. Để biết thêm thông tin chi tiết về Bộ phận Hình sự hoặc công việc mà chúng tôi làm, vui lòng truy cập trang web của chúng tôi: www.justice.gov/crt/about/crm/.

Chúng tôi sẽ xem xét thư của quý vị để quyết định xem có cần thiết phải liên hệ với quý vị để biết thêm thông tin hay không. Chúng tôi không có đủ nguồn lực để theo dõi hoặc trả lời mọi bức thư. Nếu mối quan ngại của quý vị không nằm trong lĩnh vực công việc của Bộ phận này, quý vị có thể tham khảo trang web của Ban Dân quyền để xác định xem một Bộ phận khác của Ban có thể giải quyết mối quan ngại của quý vị hay không: www.justice.gov/crt. Một lần nữa, nếu quý vị viết lá thư này để tố giác một tội ác, vui lòng liên hệ với các cơ quan hành pháp liên bang và/hoặc tiểu bang trong khu vực địa phương của quý vị, chẳng hạn như Cục Điều tra Liên bang hoặc sở cảnh sát địa phương hoặc văn phòng cảnh sát trưởng.

Trân trọng,
/s/
Bộ phân Hình sự
""")

    ResponseTemplate.objects.create(
        title='CRM - R2 Form Letter (Vietnamese)',
        subject=subject,
        body="""
{{ vi.addressee }},

Quý vị đã liên hệ với Ban Dân quyền vào ngày {{ vi.date_of_intake }}. Mã số báo cáo của quý vị là {{ record_locator }}.

Bộ phận Hình sự của Ban Dân quyền chịu trách nhiệm thực thi các đạo luật về quyền dân sự hình sự của liên bang. Phần lớn hoạt động thực thi của chúng tôi liên quan đến việc điều tra và truy tố các hành vi tước quyền công dân theo luật. Những vấn đề này thường liên quan đến các cáo buộc về vũ lực quá mức hoặc lạm dụng tình dục của các viên chức hành pháp.

Thông tin mà quý vị cung cấp không đủ để cho phép chúng tôi xác định là có sự tồn tại của hành vi vi phạm các quy chế về quyền dân sự hình sự của liên bang. Do đó, chúng tôi không thể cho phép điều tra khiếu nại của quý vị vào lúc này. Tuy nhiên, chúng tôi sẽ xem xét thêm về cáo buộc nếu quý vị cung cấp thông tin cụ thể về các trường hợp liên quan đến khiếu nại của quý vị. Quý vị phải nêu tên của người bị thương; một bản tường thuật liên quan đến các cáo buộc dẫn đến và bao gồm cả vụ việc; tên của bất kỳ nhân chứng khả dĩ nào; ngày xảy ra vụ việc và bất kỳ thông tin nào khác mà quý vị cho là có liên quan đến vụ việc này. Vui lòng gửi lại thông tin này đến cổng thông tin khiếu nại trực tuyến của chúng tôi https://civilrights.justice.gov/ và ghi rõ số hồ sơ khiếu nại của quý vị, được liệt kê trong dòng chủ đề của email này.

Quý vị có thể yên tâm rằng nếu bằng chứng cho thấy có hành vi vi phạm có thể truy tố đối với quy chế về quyền dân sự hình sự của liên bang, thì các hành động phù hợp sẽ được thực hiện.

Xin cảm ơn quý vị,
Bộ phân Hình sự
""")

    ResponseTemplate.objects.create(
        title='CRM - Referral to FBI (Vietnamese)',
        subject=subject,
        body="""
{{ vi.addressee }},

Quý vị đã liên hệ với Bộ Tư pháp vào ngày {{ vi.date_of_intake }}.

Những gì chúng tôi đã làm:

Mã số báo cáo của quý vị là {{ record_locator }}.

Các thành viên trong nhóm của Ban Dân quyền đã duyệt xét các thông tin mà quý vị gửi.  Dựa trên báo cáo của quý vị, nhóm của chúng tôi xác định rằng quý vị đã cáo buộc một hành vi vi phạm hình sự các quyền công dân.

Chúng tôi sẽ xem xét cẩn thận báo cáo của quý vị và sẽ liên hệ với quý vị nếu chúng tôi cần thêm thông tin. Tuy nhiên, quý vị cần biết rằng Ban Dân quyền nhận được hàng nghìn báo cáo từ công chúng mỗi năm và thường chỉ tham gia sau khi Cục Điều tra Liên bang (FBI) hoặc cơ quan hành pháp khác bắt đầu điều tra.

Do đó, chúng tôi muốn quý vị biết rằng trong các tình huống liên quan đến hành vi vi phạm hình sự luật dân quyền của liên bang, FBI là cơ quan đầu tiên và tốt nhất để quý vị báo cáo.

Những gì quý vị có thể làm:

FBI có thể giúp đỡ quý vị trong tình huống này. Quý vị có thể liên hệ với FBI bằng bất kỳ phương thức nào được nêu dưới đây.

Trực tuyến:
www.fbi.gov/tips

Qua điện thoại hoặc gặp trực tiếp:

Liên hệ với văn phòng FBI địa phương của quý vị (được khuyến nghị)

www.fbi.gov/contact-us/field-offices

Quý vị đã giúp đỡ như thế nào:

Báo cáo của quý vị sẽ giúp chúng tôi nâng cao dân quyền. Thông tin từ các báo cáo như của quý vị giúp chúng tôi hiểu được các xu hướng và vấn đề về dân quyền mới xuất hiện.  Điều này giúp cung cấp thông tin về cách chúng tôi bảo vệ dân quyền của tất cả mọi người trên đất nước này.

Cảm ơn quý vị đã dành thời gian liên hệ với Bộ Tư pháp về những mối quan ngại của mình.

Trân trọng,

Bộ Tư pháp Hoa Kỳ
Ban Dân Quyền
""")

    ResponseTemplate.objects.create(
        title='CRT - Comments & Opinions (Vietnamese)',
        subject=subject,
        body="""
{{ vi.addressee }},
Quý vị đã liên hệ với Bộ Tư pháp vào ngày {{ vi.date_of_intake }}. Mã số báo cáo của quý vị là {{ record_locator }}.

Chúng tôi đánh giá cao sự quan tâm của quý vị và thời gian quý vị viết thư cho chúng tôi để bày tỏ quan điểm của quý vị. Xin hãy biết rằng thông tin quý vị đã cung cấp sẽ được cân nhắc phù hợp.

Trân trọng,

Bộ Tư pháp Hoa Kỳ
Ban Dân Quyền
""")

    ResponseTemplate.objects.create(
        title='CRT - EEOC Referral Letter (Vietnamese)',
        subject=subject,
        body="""
{{ vi.addressee }},

Quý vị đã liên hệ với Bộ Tư pháp vào ngày {{ vi.date_of_intake }}. Sau khi xem xét cẩn thận những gì quý vị đã gửi, chúng tôi đã xác định rằng báo cáo của quý vị sẽ được một cơ quan liên bang khác xử lý một cách thích hợp hơn.

Những gì chúng tôi đã làm:

Mã số hồ sơ của quý vị là {{ record_locator }}.

Các thành viên trong nhóm của Ban Dân quyền đã đánh giá các thông tin quý vị gửi.  Dựa trên báo cáo của quý vị, nhóm của chúng tôi xác định rằng quý vị đã cáo buộc hành vi phân biệt đối xử trong việc làm hoặc các vấn đề khác liên quan đến việc làm.

Luật liên bang giới hạn khả năng của Bộ Tư pháp trong việc thực hiện hành động trực tiếp trong một số tình huống nhất định. Dựa trên đánh giá của nhóm chúng tôi về báo cáo của quý vị, điều này bao gồm cả vấn đề của quý vị.

Những gì quý vị có thể làm:

Chúng tôi không xác định rằng báo cáo của quý vị là thiếu thỏa đáng. Thay vào đó, một cơ quan liên bang khác có thể giúp đỡ quý vị trong tình huống này.

Chúng tôi đã liệt kê danh sách các cơ quan liên bang có thể trợ giúp. Quý vị nên liên hệ với cơ quan thích hợp nếu quý vị muốn theo đuổi vụ việc này xa hơn.

GHI CHÚ: Có những giới hạn nghiêm ngặt về thời gian nộp đơn khiếu nại liên quan đến hành vi phân biệt đối xử trong việc làm. Nếu quý vị cảm thấy quý vị đã bị phân biệt đối xử về việc làm, quý vị cần liên hệ với cơ quan thích hợp sớm nhất có thể.

TÔI ĐÃ GẶP PHẢI...

Sự phân biệt đối xử trong việc làm dựa trên: chủng tộc, màu da, quốc gia xuất xứ, tôn giáo, giới tính (bao gồm tình trạng mang thai, khuynh hướng tình dục và nhận dạng giới tính), tuổi tác, tình trạng khuyết tật, hoặc việc trả thù.

CƠ QUAN CÓ THỂ GIÚP ĐỠ

Ủy ban Cơ hội Việc làm Bình đẳng (EEOC)

    Nộp trực tuyến:  eeoc.gov/filing-charge-discrimination
   Liên hệ qua điện thoại: 1-800-669-4000
    Nộp trực tiếp tại Văn phòng EEOC gần nhất: www.eeoc.gov/field-office

TÔI ĐÃ GẶP PHẢI...

Sự phân biệt đối xử về việc làm dựa trên tình trạng phục vụ quân ngũ, bao gồm việc trả thù và không tái tuyển dụng.

CƠ QUAN CÓ THỂ GIÚP ĐỠ

Bộ Lao động Hoa Kỳ
Dịch vụ Tuyển dụng và Đào tạo Cựu Chiến binh (VETS)

    Nộp trực tuyến hoặc liên hệ trực tiếp với VETS:  www.dol.gov/agencies/vets/
   Liên hệ qua điện thoại: 1-866-487-2365

TÔI ĐÃ GẶP PHẢI...

Sự phân biệt đối xử trong việc làm của chính phủ liên bang

CƠ QUAN CÓ THỂ GIÚP ĐỠ

Nhân viên phụ trách cơ hội việc làm bình đẳng tại cơ quan liên bang của quý vị

    Tìm nhân viên phụ trách EEO liên bang của quý vị:

TÔI ĐÃ GẶP PHẢI...

Vấn đề bồi thường cho người lao động

CƠ QUAN CÓ THỂ GIÚP ĐỠ

Bộ Lao động Hoa Kỳ
Văn phòng các Chương trình Bồi thường cho Người lao động (OWCP)

    Tùy chọn gọi điện thoại và gặp trực tiếp:
https://www.dol.gov/owcp/owcpkeyp.htm
TÔI ĐÃ GẶP PHẢI...

Vấn đề về tiền lương và/hoặc giờ làm việc

CƠ QUAN CÓ THỂ GIÚP ĐỠ

Bộ Lao động Hoa Kỳ
Cơ quan Quản lý các Tiêu chuẩn Việc làm, Ban Tiền lương và Giờ Làm việc

    Cách để nộp đơn khiếu nại: www.dol.gov/agencies/whd/contact/complaints
    Liên hệ qua điện thoại: 1-866-487-2365

TÔI ĐÃ GẶP PHẢI...

Vấn đề về an toàn của người lao động

CƠ QUAN CÓ THỂ GIÚP ĐỠ

Bộ Lao động Hoa Kỳ
Cơ quan Quản lý An toàn và Sức khỏe Nghề nghiệp (OSHA)

    Nộp trực tuyến: www.osha.gov/workers/
    Liên hệ qua điện thoại: 1-800-321-6742

TÔI ĐÃ GẶP PHẢI...

Một vấn đề với Ủy ban Cơ hội Việc làm Bình đẳng

CƠ QUAN CÓ THỂ GIÚP ĐỠ

Ủy ban Cơ hội Việc làm Bình đẳng
Giám đốc, Văn phòng các Chương trình Quản lý Hiện trường

    131 M Street, NE
    Washington, DC 20507

Ngoài ra, hiệp hội luật sư tiểu bang hoặc văn phòng hỗ trợ pháp lý địa phương của quý vị có thể giúp giải quyết vấn đề của quý vị mặc dù Bộ Tư pháp không thể làm điều đó.

ĐỂ TÌM...

Một luật sư cá nhân

TỔ CHỨC CÓ THỂ GIÚP ĐỠ

Hiệp hội Luật sư Hoa Kỳ
www.findlegalhelp.org
    Liên hệ qua điện thoại: 1-800-285-2221

ĐỂ TÌM...

Luật sư cá nhân dành cho những người có thu nhập thấp

TỔ CHỨC CÓ THỂ GIÚP ĐỠ

Legal Services Corporation (hoặc Legal Aid Offices)
www.lsc.gov/find-legal-aid

Quý vị đã giúp đỡ như thế nào:

Mặc dù chúng tôi không thể hành động trong trường hợp cụ thể này, nhưng báo cáo của quý vị sẽ giúp chúng tôi nâng cao dân quyền. Thông tin từ các báo cáo như của quý vị giúp chúng tôi hiểu được các vấn đề cấp bách và mới xuất hiện.  Điều này giúp cung cấp thông tin về cách chúng tôi bảo vệ dân quyền của tất cả mọi người trên đất nước này.

Cảm ơn quý vị đã dành thời gian liên hệ với Bộ Tư pháp về những mối quan ngại của mình.

Trân trọng,

Bộ Tư pháp Hoa Kỳ
Ban Dân Quyền
""")

    ResponseTemplate.objects.create(
        title='CRT - No Capacity (Vietnamese)',
        subject=subject,
        body="""
{{ vi.addressee }}，

Quý vị đã liên hệ với Bộ Tư pháp vào ngày {{ vi.date_of_intake }}. Sau khi xem xét cẩn thận những thông tin quý vị đã gửi, chúng tôi đã quyết định không thực hiện thêm bất kỳ hành động nào đối với khiếu nại của quý vị.

Những gì chúng tôi đã làm:

Các thành viên trong nhóm của Ban Dân quyền đã duyệt xét các thông tin mà quý vị gửi.  Dựa trên đánh giá của chúng tôi, chúng tôi đã quyết định không thực hiện thêm bất kỳ hành động nào đối với khiếu nại của quý vị.  Chúng tôi nhận được hàng nghìn báo cáo về hành vi vi phạm dân quyền mỗi năm.  Tiếc rằng chúng tôi không có đủ nguồn lực để thực hiện hành động trực tiếp cho tất cả mọi báo cáo.

Mã số báo cáo của quý vị là {{ record_locator }}.

Những gì quý vị có thể làm:

Chúng tôi không xác định rằng báo cáo của quý vị là thiếu thỏa đáng. Vấn đề của quý vị vẫn có thể được những cơ quan khác giải quyết - hiệp hội luật sư tiểu bang hoặc văn phòng hỗ trợ pháp lý địa phương có thể giúp đỡ quý vị.

    Để tìm một văn phòng địa phương:

    Hiệp hội Luật sư Hoa Kỳ
www.findlegalhelp.org
    (800) 285-2221


    Legal Service Corporation (hoặc Legal Aid Offices)
www.lsc.gov/find-legal-aid

Quý vị đã giúp đỡ như thế nào:

Mặc dù chúng tôi không có khả năng giải quyết từng báo cáo riêng lẻ, nhưng báo cáo của quý vị có thể giúp chúng tôi tìm ra các vấn đề ảnh hưởng đến nhiều người hoặc cộng đồng. Báo cáo đó cũng giúp chúng tôi hiểu các xu hướng và chủ đề mới xuất hiện.

Cảm ơn quý vị đã dành thời gian liên hệ với Bộ Tư pháp về những mối quan ngại của mình.  Chúng tôi rất tiếc vì chúng tôi không thể trợ giúp thêm về vấn đề này.

Trân trọng,

Bộ Tư pháp Hoa Kỳ
Ban Dân Quyền
""")

    ResponseTemplate.objects.create(
        title='CRT - Non-Actionable (Vietnamese)',
        subject=subject,
        body="""
{{ vi.addressee }}，

Quý vị đã liên hệ với Bộ Tư pháp vào ngày {{ vi.date_of_intake }}. Sau khi xem xét cẩn thận những thông tin quý vị đã gửi, chúng tôi đã quyết định không thực hiện thêm bất kỳ hành động nào đối với khiếu nại của quý vị.

Những gì chúng tôi đã làm:

Các thành viên trong nhóm của Ban Dân quyền đã đánh giá các thông tin mà quý vị gửi.  Dựa trên thông tin này, nhóm của chúng tôi xác định rằng luật dân quyền của liên bang mà chúng tôi đảm bảo thực thi không bao gồm tình huống quý vị đã mô tả.  Do đó, chúng tôi không thể thực hiện thêm hành động nào nữa.

Mã số báo cáo của quý vị là {{ record_locator }}.

Những gì quý vị có thể làm:

Vấn đề của quý vị có thể được bao hàm trong các luật liên bang, tiểu bang, hoặc địa phương khác mà chúng tôi không có thẩm quyền thực thi. Chúng tôi không xác định rằng báo cáo của quý vị là thiếu thỏa đáng.

Hiệp hội luật sư tiểu bang hoặc văn phòng hỗ trợ pháp lý địa phương của quý vị có thể giúp giải quyết vấn đề của quý vị dù Bộ Tư pháp không thể làm điều đó.

    Để tìm một văn phòng địa phương:

    Hiệp hội Luật sư Hoa Kỳ
www.findlegalhelp.org
    (800) 285-2221
    Legal Service Corporation (hoặc Legal Aid Offices)
www.lsc.gov/find-legal-aid

Cảm ơn quý vị đã dành thời gian liên hệ với Bộ Tư pháp về những mối quan ngại của mình. Chúng tôi rất tiếc vì chúng tôi không thể trợ giúp thêm về vấn đề này.

Trân trọng,

Bộ Tư pháp Hoa Kỳ
Ban Dân Quyền
""")

    ResponseTemplate.objects.create(
        title='CRT - Request for Agency Review (Vietnamese)',
        subject=subject,
        body="""
{{ vi.addressee }}，

Quý vị đã liên hệ với Bộ Tư pháp vào ngày {{ vi.date_of_intake }}. Đây là thư trả lời khiếu nại của quý vị.

Những gì chúng tôi đã làm:

Mã số báo cáo của quý vị là {{ record_locator }}.

Các thành viên trong nhóm của Ban Dân quyền đã đánh giá các thông tin mà quý vị gửi.  Quý vị cho biết rằng quý vị đã nộp đơn khiếu nại về hành vi phân biệt đối xử lên hoặc kiện lại một cơ quan Liên bang khác.

Bộ Tư pháp không phải là cơ quan có thẩm quyền đánh giá các quyết định của các cơ quan Liên bang khác sau khi họ điều tra các khiếu nại về hành vi phân biệt đối xử.

Do đó, chúng tôi sẽ không thực hiện thêm hành động nào nữa.

Những gì quý vị có thể làm:

Thư này không phải là quyết định rằng báo cáo của quý vị thiếu thỏa đáng. Hiệp hội luật sư tiểu bang hoặc văn phòng hỗ trợ pháp lý địa phương có thể giúp đỡ quý vị.

ĐỂ TÌM...

Một luật sư cá nhân

TỔ CHỨC CÓ THỂ GIÚP ĐỠ:

Hiệp hội Luật sư Hoa Kỳ

    Tìm trực tuyến:
www.findlegalhelp.org
    Liên hệ qua điện thoại: (800) 285-2221

ĐỂ TÌM...

Luật sư cá nhân dành cho những người có thu nhập thấp

TỔ CHỨC CÓ THỂ GIÚP ĐỠ:

Legal Services Corporation (hoặc Legal Aid Offices)

    Tìm trực tuyến:
www.lsc.gov/find-legal-aid

Quý vị đã giúp đỡ như thế nào:

Mặc dù chúng tôi không thể hành động trong trường hợp cụ thể này, nhưng báo cáo của quý vị sẽ giúp chúng tôi nâng cao dân quyền. Thông tin từ các báo cáo như của quý vị giúp chúng tôi hiểu được các vấn đề cấp bách và mới xuất hiện. Điều này giúp cung cấp thông tin về cách chúng tôi bảo vệ dân quyền của tất cả mọi người trên đất nước này.

Cảm ơn quý vị đã dành thời gian liên hệ với Bộ Tư pháp về những mối quan ngại của mình.

Trân trọng,

Bộ Tư pháp Hoa Kỳ
Ban Dân Quyền
""")

    ResponseTemplate.objects.create(
        title='HCE - Referral for Housing/Lending/Public Accommodation (Vietnamese)',
        subject=subject,
        body="""
{{ vi.addressee }}，

Quý vị đã liên hệ với Bộ Tư pháp vào ngày {{ vi.date_of_intake }}.

Những gì chúng tôi đã làm:

Mã số báo cáo của quý vị là {{ record_locator }}.

Các thành viên trong nhóm của Ban Dân quyền đã đánh giá các thông tin mà quý vị gửi. Dựa trên báo cáo của quý vị, nhóm của chúng tôi xác định rằng quý vị đã cáo buộc hành vi phân biệt đối xử ở một trong các lĩnh vực sau:

1) nhà ở;
2) các cở sở công cộng, chẳng hạn như khách sạn và nhà hàng; hoặc
3) tín dụng.

Xin lưu ý rằng trong các tình huống liên quan đến các loại hành vi phân biệt đối xử này, Ban Dân quyền thường chỉ tham gia khi các nhóm đông người bị ảnh hưởng. Chúng tôi thường không mở các cuộc điều tra dựa trên các khiếu nại về hành vi phân biệt đối xử của từng cá nhân.

Với quan điểm này, chúng tôi sẽ xem xét cẩn thận báo cáo của quý vị và sẽ liên hệ với quý vị nếu chúng tôi cần thêm thông tin và/hoặc có thể mở một cuộc điều tra.

Những gì quý vị có thể làm:

Nếu báo cáo của quý vị liên quan đến phân biệt đối xử về nhà ở, Bộ Gia Cư và Phát triển Đô thị Hoa Kỳ (“HUD”) có thể giúp đỡ quý vị. HUD là cơ quan chịu trách nhiệm xem xét các khiếu nại về nhà ở chỉ ảnh hưởng đến một người.

GHI CHÚ: Có những giới hạn thời gian nghiêm ngặt trong việc nộp đơn khiếu nại về hành vi phân biệt đối xử về nhà ở. Nếu quý vị tin rằng quý vị đã bị phân biệt đối xử về nhà ở, quý vị cần liên hệ với cơ quan thích hợp sớm nhất có thể.

TÔI ĐÃ GẶP PHẢI...

Sự phân biệt đối xử về nhà ở dựa trên:

- Chủng tộc hoặc màu da,
- Quốc gia xuất xứ,
- Tôn giáo,
- Giới tính,
- Tình trạng gia đình,
- Tình trạng khuyết tật, hoặc
- Việc trả thù

CƠ QUAN CÓ THỂ GIÚP ĐỠ:

Bộ Gia Cư và Phát triển Đô thị Hoa Kỳ (HUD)
Văn phòng Gia cư Công bằng và Cơ hội Bình đẳng

    Nộp trực tuyến: www.hud.gov/program_offices/fair_housing_equal_opp/online-complaint

    Liên hệ qua điện thoại: (800) 669-9777

    Nộp trực tiếp tại văn phòng địa phương gần quý vị nhất:
www.hud.gov/program_offices/fair_housing_equal_opp/contact_fheo

TÔI ĐÃ GẶP PHẢI...

Vấn đề về hoặc có thắc mắc về:

- Trợ cấp nhà ở hoặc phiếu chọn nhà:
- Cơ quan quản lý nhà ở xã hội,
- Nhân viên cơ quan quản lý nhà ở xã hội, hoặc
- Chủ nhà nhận trợ cấp nhà ở

CƠ QUAN CÓ THỂ GIÚP ĐỠ:

Bộ Gia Cư và Phát triển Đô thị Hoa Kỳ (HUD)
Cơ quan Nhà ở Xã hội và Nhà cho người Mỹ Bản địa

    Trung tâm Dịch vụ Khách hàng PIH:
www.hud.gov/program_offices/public_indian_housing

    Liên hệ qua điện thoại: (800) 955-2232
TÔI ĐÃ GẶP PHẢI...

Vấn đề về hoặc có thắc mắc về:

- Tình trạng vô gia cư

CƠ QUAN CÓ THỂ GIÚP ĐỠ:

Bộ Gia Cư và Phát triển Đô thị Hoa Kỳ
Các nguồn trợ giúp về tình trạng vô gia cư

    Tìm trực tuyến:
www.hudexchange.info/housing-and-homeless-assistance/
TÔI ĐÃ GẶP PHẢI...

Sự lừa đảo, lãng phí, hoặc lạm dụng liên quan đến:

- HUD, hoặc
- một chương trình liên kết với HUD

CƠ QUAN CÓ THỂ GIÚP ĐỠ:

Bộ Gia Cư và Phát triển Đô thị Hoa Kỳ (HUD)
Văn phòng Tổng Thanh tra

    Tìm trực tuyến:
www.hudoig.gov/hotline
    Liên hệ qua email: hotline@hudoig.gov
Nếu báo cáo của quý vị liên quan đến hành vi phân biệt đối xử trong việc cho vay, quý vị có thể muốn gửi khiếu nại lên HUD và Cục Bảo vệ Tài chính Người Tiêu dùng (CFPB).  Đây là các cơ quan chịu trách nhiệm đánh giá các khiếu nại chỉ ảnh hưởng đến một người.

GHI CHÚ: Có những giới hạn thời gian nghiêm ngặt trong việc nộp đơn khiếu nại về hành vi phân biệt đối xử về việc cho vay. Nếu quý vị tin rằng quý vị đã bị phân biệt đối xử về việc cho vay, quý vị cần liên hệ với cơ quan thích hợp sớm nhất có thể.

TÔI ĐÃ GẶP PHẢI...

Sự phân biệt đối xử trong việc cho vay mua nhà (có nghĩa là mua nhà trả góp) dựa trên:

- Chủng tộc hoặc màu da,
- Quốc gia xuất xứ,
- Tôn giáo,
- Giới tính,
- Tình trạng gia đình,
- Tình trạng khuyết tật, hoặc
- Việc trả thù

CƠ QUAN CÓ THỂ GIÚP ĐỠ:

Bộ Gia Cư và Phát triển Đô thị Hoa Kỳ (HUD)
Văn phòng Gia cư Công bằng và Cơ hội Bình đẳng

    Nộp trực tuyến:
www.hud.gov/program_offices/fair_housing_equal_opp/online-complaint
    Liên hệ qua điện thoại: (800) 669-9777
    Nộp trực tiếp tại văn phòng địa phương gần nhất:
www.hud.gov/program_offices/fair_housing_equal_opp/contact_fheo

TÔI ĐÃ GẶP PHẢI...

Sự phân biệt đối xử trong việc cho vay mua nhà (có nghĩa là mua nhà trả góp) HOẶC bất kỳ hình thức tín dụng nào khác dựa trên:

- Chủng tộc hoặc màu da,
- Quốc gia xuất xứ,
- Tôn giáo,
- Giới tính,
- Tình trạng hôn nhân,
- Tuổi (miễn là quý vị đủ tuổi để tham gia hợp đồng),
- Nhận thu nhập từ bất kỳ chương trình trợ cấp công cộng nào, hoặc
- Việc trả thù

CƠ QUAN CÓ THỂ GIÚP ĐỠ:
Cục Bảo vệ Tài chính Người Tiêu dùng (CFPB)

    Nộp trực tuyến:
www.consumerfinance.gov/complaint/
    Liên hệ qua điện thoại: (855) 411-2372
Nếu báo cáo của quý vị liên quan đến hành vi phân biệt đối xử tại các cơ sở công cộng, bao gồm khách sạn, nhà hàng, rạp chiếu phim và các địa điểm giải trí khác, thì tổng chưởng lý của tiểu bang có thể giúp đỡ quý vị.

GHI CHÚ: Có thể có giới hạn thời gian trong việc nộp đơn khiếu nại liên quan đến hành vi phân biệt đối xử trong các cơ sở công cộng. Nếu quý vị tin rằng quý vị đã bị phân biệt đối xử, quý vị cần liên hệ với tổng chưởng lý của tiểu bang quý vị sớm nhất có thể.

TÔI ĐÃ GẶP PHẢI...

Phân biệt đối xử tại cơ sở công cộng (khách sạn, nhà hàng, rạp chiếu phim và địa điểm giải trí) dựa trên:

- Chủng tộc hoặc màu da,
- Tôn giáo, hoặc
- Quốc gia xuất xứ

CƠ QUAN CÓ THỂ GIÚP ĐỠ:

Tổng Chưởng lý Tiểu bang
    Tìm trực tuyến: www.usa.gov/state-attorney-general
Liên hệ qua điện thoại: (844) 872-4681
Ngoài ra, hiệp hội luật sư tiểu bang hoặc văn phòng hỗ trợ pháp lý địa phương có thể giúp giải quyết vấn đề của quý vị.

ĐỂ TÌM...

Một luật sư cá nhân

TỔ CHỨC CÓ THỂ GIÚP ĐỠ:

Hiệp hội Luật sư Hoa Kỳ
    Tìm trực tuyến:
www.findlegalhelp.org
    Liên hệ qua điện thoại: (800) 285-2221

ĐỂ TÌM...

Luật sư cá nhân dành cho những người có thu nhập thấp

TỔ CHỨC CÓ THỂ GIÚP ĐỠ:

Legal Services Corporation (hoặc Legal Aid Offices)

    Tìm trực tuyến:
www.lsc.gov/find-legal-aid

Quý vị đã giúp đỡ như thế nào:

Báo cáo của quý vị sẽ giúp chúng tôi nâng cao dân quyền. Thông tin từ các báo cáo như báo cáo của quý vị giúp chúng tôi hiểu được các vấn đề cấp bách và mới xuất hiện về dân quyền. Điều này giúp cung cấp thông tin về cách chúng tôi bảo vệ dân quyền của tất cả mọi người trên đất nước này.

Cảm ơn quý vị đã dành thời gian liên hệ với Bộ Tư pháp về những mối quan ngại của mình.

Trân trọng,

Bộ Tư pháp Hoa Kỳ
Ban Dân Quyền
""")

    ResponseTemplate.objects.create(
        title='SPL - Referral for PREA Issues (Vietnamese)',
        subject=subject,
        body="""
{{ vi.addressee }}，

Quý vị đã liên hệ với Bộ Tư pháp vào ngày {{ vi.date_of_intake }}.  Dựa trên đánh giá của chúng tôi cho đến thời điểm này, chúng tôi muốn quý vị biết rằng quý vị có thể liên hệ với Điều phối viên PREA của tiểu bang của quý vị.

Những gì chúng tôi đã làm:

Mã số báo cáo của quý vị là {{ record_locator }}.

Các thành viên trong nhóm của Ban Dân quyền đã đánh giá các thông tin mà quý vị gửi.  Dựa trên báo cáo của quý vị, nhóm của chúng tôi xác định rằng quý vị đã nêu lên những quan ngại liên quan đến hành vi lạm dụng tình dục hoặc quấy rối tình dục khi bị giam giữ.  Điều này có thể thuộc Đạo luật Xóa bỏ Hiếp dâm trong Tù (PREA). PREA là luật quy định những việc sau đây là trái luật:

- lạm dụng tình dục hoặc quấy rối tình dục tù nhân và người bị giam giữ; và
- trả đũa một tù nhân hoặc nhân viên báo cáo hành vi lạm dụng tình dục hoặc quấy rối tình dục.

Chúng tôi sẽ tiếp tục xem xét báo cáo của quý vị và sẽ liên hệ với quý vị nếu chúng tôi cần thêm thông tin.  Tuy nhiên, quý vị nên biết rằng trong các tình huống liên quan đến lạm dụng tình dục hoặc quấy rối tình dục tù nhân và người bị giam giữ, Ban Dân quyền chỉ có thể tham gia khi có một kiểu hành vi sai trái diễn ra trên diện rộng.  Do đó, chúng tôi thường không thể mở các cuộc điều tra dựa trên các khiếu nại riêng lẻ.

Vì vậy, chúng tôi muốn quý vị biết rằng Điều phối viên PREA của tiểu bang có thể trợ giúp quý vị trong tình huống của quý vị.  Điều phối viên PREA có thể điều tra các khiếu nại cá nhân như khiếu nại của quý vị. Để giúp quý vị kết nối với Điều phối viên PREA của tiểu bang của quý vị, chúng tôi đã gửi một danh mục kèm theo thư trả lời này.

Những gì quý vị có thể làm:

Điều phối viên PREA của tiểu bang có thể trợ giúp quý vị trong tình huống của quý vị. Quý vị có thể liên hệ với Điều phối viên PREA của tiểu bang bằng cách tham khảo danh mục đính kèm.

Quý vị cũng có thể tìm hiểu thêm về PREA tại trang web của Trung tâm Thông tin PREA:
www.prearesourcecenter.org/training-technical-assistance/prea-101/prisons-and-jail-standards

Quý vị đã giúp đỡ như thế nào:

Báo cáo của quý vị sẽ giúp chúng tôi nâng cao dân quyền. Thông tin từ các báo cáo như của quý vị giúp chúng tôi hiểu được các xu hướng và vấn đề mới xuất hiện về dân quyền. Điều này giúp cung cấp thông tin về cách chúng tôi bảo vệ dân quyền của tất cả mọi người trên đất nước này.

Cảm ơn quý vị đã dành thời gian liên hệ với Bộ Tư pháp về những mối quan ngại của mình.

Trân trọng,

Bộ Tư pháp Hoa Kỳ
Ban Dân Quyền
""")

    ResponseTemplate.objects.create(
        title='Trending - General COVID inquiries (Vietnamese)',
        subject=subject,
        body="""
{{ vi.addressee }}，

Cảm ơn quý vị đã gửi báo cáo {{ record_locator }} cho Ban Dân quyền vào ngày {{ vi.date_of_intake }}.

Nhiều người dân Mỹ đang thích nghi với “trạng thái bình thường mới” do COVID-19 – một trạng thái cân bằng nhu cầu thiết yếu để ngăn chặn sự lây lan của coronavirus cùng với các yếu tố khác cũng ảnh hưởng đến sức khỏe và sự an lành. Như trong tất cả các trường hợp khẩn cấp, sự bùng phát dịch bệnh COVID-19 đã ảnh hưởng đến những người thuộc nhiều chủng tộc, tôn giáo, và sắc tộc khác nhau, cũng như những người khuyết tật.

Ban Dân Quyền của Bộ Tư Pháp Hoa Kỳ, cùng với các cơ quan khác trong toàn bộ chính quyền liên bang, theo dõi các vấn đề về dân quyền liên quan đến COVID-19. Để biết thêm thông tin, vui lòng truy cập www.justice.gov/crt/fcs. Thông tin thêm về sự ứng phó của chính phủ liên bang đối với COVID-19 có sẵn tại www.whitehouse.gov/priorities/covid-19/ và www.coronavirus.gov.

Trân trọng,
Bộ Tư pháp Hoa Kỳ
Ban Dân Quyền
""")

    ResponseTemplate.objects.create(
        title='CRT - Constant Writer (Vietnamese)',
        subject=subject,
        body="""
{{ vi.addressee }}，

Quý vị đã liên hệ với Bộ Tư pháp vào ngày {{ vi.date_of_intake }}. Mã số báo cáo của quý vị là {{ record_locator }}.  Trước đây, chúng tôi đã nhận được thư tín tương tự từ quý vị liên quan đến vấn đề này và chúng tôi đã trả lời câu hỏi của quý vị.

Chúng tôi không thể bổ sung thêm thông tin nào vào câu trả lời trước đó của mình và chúng tôi thật lấy làm tiếc rằng chúng tôi không thể giúp đỡ thêm cho quý vị về vấn đề này.

Trân trọng,

Bộ Tư pháp Hoa Kỳ
Ban Dân Quyền
""")

def remove_letters(apps, schema_editor):
    ResponseTemplate = apps.get_model('cts_forms', 'ResponseTemplate')
    ResponseTemplate.objects.filter(title='CRM - R1 Form Letter (Vietnamese)').delete()
    ResponseTemplate.objects.filter(title='CRM - R2 Form Letter (Vietnamese)').delete()
    ResponseTemplate.objects.filter(title='CRM - Referral to FBI (Vietnamese)').delete()
    ResponseTemplate.objects.filter(title='CRT - Comments & Opinions (Vietnamese)').delete()
    ResponseTemplate.objects.filter(title='CRT - EEOC Referral Letter (Vietnamese)').delete()
    ResponseTemplate.objects.filter(title='CRT - No Capacity (Vietnamese)').delete()
    ResponseTemplate.objects.filter(title='CRT - Non-Actionable (Vietnamese)').delete()
    ResponseTemplate.objects.filter(title='CRT - Request for Agency Review (Vietnamese)').delete()
    ResponseTemplate.objects.filter(title='HCE - Referral for Housing/Lending/Public Accommodation (Vietnamese)').delete()
    ResponseTemplate.objects.filter(title='SPL - Referral for PREA Issues (Vietnamese)').delete()
    ResponseTemplate.objects.filter(title='Trending - General COVID inquiries (Vietnamese)').delete()
    ResponseTemplate.objects.filter(title='CRT - Constant Writer (Vietnamese)').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('cts_forms', '0107_chinese_simplified_form_letters'),
    ]

    operations = [
        migrations.RunPython(add_letters, remove_letters)
    ]
