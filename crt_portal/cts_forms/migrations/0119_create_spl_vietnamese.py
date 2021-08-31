from django.db import migrations

def add_letters(apps, schema_editor):
    ResponseTemplate = apps.get_model('cts_forms', 'ResponseTemplate')
    subject = 'Hồi đáp: Báo Cáo của Ban Dân Quyền của Quý Vị - {{ record_locator }} từ Phòng {{ vi.section_name }}'
    ResponseTemplate.objects.create(
        title='SPL - Standard Form Letter (Vietnamese)',
        subject=subject,
        language='vi',
        body="""
{{ vi.addressee }},

Cảm ơn quý vị đã gửi thư vào ngày {{ vi.date_of_intake }}. Số hồ sơ của quý vị là {{ record_locator }}. Văn phòng Tố tụng Đặc biệt dựa vào thông tin từ các thành viên cộng đồng để xác định các hành vi vi phạm quyền công dân. Mỗi tuần, chúng tôi nhận được hàng trăm báo cáo về những trường hợp có thể là hành vi phạm luật. Chúng tôi thu thập và phân tích thông tin này để giúp chúng tôi sàng lọc các vụ khiếu nại, và chúng tôi có thể sử dụng thông tin này làm bằng chứng trong một vụ khiếu nại hiện thời. Chúng tôi sẽ xem xét thư của quý vị để quyết định xem có cần thiết phải liên lạc với quý vị để biết thêm thông tin hay không. Chúng tôi không có đủ nguồn nhân lực để theo dõi từng lá thư.

Văn phòng Tố tụng Đặc biệt là một trong số các Văn phòng thuộc Bộ phận Dân quyền. Chúng tôi làm việc để bảo vệ quyền công dân trong bốn lĩnh vực: 1) quyền của người dân trong các cơ sở nhà nước hoặc địa phương, bao gồm: trại giam, nhà tù, cơ sở giam giữ trẻ vị thành niên và cơ sở chăm sóc sức khỏe cho người khuyết tật (bao gồm cả những người trong các cơ sở chăm sóc sức khỏe lẽ ra phải nhận các dịch vụ trong cộng đồng); 2) quyền của những người tương tác với cảnh sát tiểu bang hoặc địa
phương hoặc các sở cảnh sát quận hạt; 3) quyền của người dân được tiếp cận an toàn với các phòng khám chăm sóc sức khỏe sinh sản hoặc các cơ sở tôn giáo; và 4) quyền của mọi người được thực hành tôn giáo của họ trong các cơ sở của nhà nước và địa phương. Chúng tôi không được phép giải quyết các vấn đề với các cơ sở liên bang hoặc các quan chức liên bang.

Nếu mối quan ngại của quý vị không nằm trong phạm vi công việc của Văn phòng này, quý vị có thể tham khảo trang mạng của Bộ phận Dân quyền để tìm đúng văn phòng: https://civilrights.justice.gov/.

Văn phòng Tố tụng Đặc biệt chỉ giải quyết những trường hợp phát sinh từ các vấn đề phổ biến ảnh hưởng đến các nhóm người. Chúng tôi không hỗ trợ các vấn đề riêng lẻ. Chúng tôi không thể giúp quý vị khôi phục thiệt hại hoặc bất kỳ khoản cứu trợ cá nhân nào. Chúng tôi không thể hỗ trợ trong các vụ án hình sự, bao gồm việc kết án, kháng cáo hoặc tuyên án oan sai.

Nếu quý vị gặp vấn đề cá nhân hoặc tìm kiếm sự bồi thường hoặc một hình thức cứu trợ cá nhân nào khác, quý vị có thể tham khảo ý kiến của luật sư riêng hoặc tổ chức trợ giúp pháp lý hoặc phi lợi nhuận để được hỗ trợ. Chỉ có hai lĩnh vực mà chúng tôi có thể hỗ trợ một cá nhân hoặc giải quyết một sự cố duy nhất: 1) chúng tôi có thể hỗ trợ quý vị nếu quý vị đang bị ngăn cản thực hành tôn giáo của mình trong nhà tù, trại giam, bệnh viện tâm thần hoặc cơ sở khác do chính quyền tiểu bang hoặc địa phương điều hành; 2) chúng tôi có thể hỗ trợ quý vị nếu quý vị gặp phải vũ lực hoặc sự đe dọa vũ lực khi tiếp cận cơ sở chăm sóc sức khỏe sinh sản hoặc cơ sở tôn giáo.

Để biết thêm thông tin về Văn phòng Tố tụng Đặc biệt hoặc công việc của chúng tôi làm, vui lòng truy cập trang mạng của chúng tôi: www.justice.gov/crt/about/spl/.

Trân trọng,


Bộ Tư Pháp Hoa Kỳ Bộ Phận Dân Quyền
""")

def remove_letters(apps, schema_editor):
    ResponseTemplate = apps.get_model('cts_forms', 'ResponseTemplate')
    ResponseTemplate.objects.filter(title='SPL - Standard Form Letter (Vietnamese)').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('cts_forms', '0118_create_spl_chinese_simplified'),
    ]

    operations = [
        migrations.RunPython(add_letters, remove_letters)
    ]
