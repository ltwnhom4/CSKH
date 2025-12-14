

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DanhGia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('diem', models.PositiveSmallIntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], verbose_name='Mức độ hài lòng')),
                ('nhan_xet', models.TextField(blank=True, verbose_name='Nhận xét')),
                ('ngay_danh_gia', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='KhieuNai',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('noi_dung', models.TextField(verbose_name='Nội dung khiếu nại')),
                ('minh_chung', models.FileField(blank=True, null=True, upload_to='minhchung/', verbose_name='Minh chứng (ảnh hoặc video)')),
                ('yeu_cau', models.TextField(verbose_name='Yêu cầu/mong muốn')),
                ('phan_hoi', models.TextField(blank=True, null=True, verbose_name='Phản hồi / Ghi chú từ nhân viên')),
                ('trang_thai', models.CharField(choices=[('Chờ xử lý', 'Chờ xử lý'), ('Đang xử lý', 'Đang xử lý'), ('Đã phản hồi', 'Đã phản hồi')], default='Chờ xử lý', max_length=30)),
                ('ngay_gui', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
