

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('KhieunaiDanhgia', '0003_alter_khieunai_lich_hen'),
    ]

    operations = [
        migrations.AlterField(
            model_name='khieunai',
            name='yeu_cau',
            field=models.TextField(verbose_name='Yêu cầu/mong muốn'),
        ),
    ]
