from django.db import models

class DichVu(models.Model):
    ten_dich_vu = models.CharField(max_length=100, verbose_name="Tên dịch vụ")
    mo_ta = models.TextField(verbose_name="Mô tả", blank=True)
    gia = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="Giá")
    hinh_anh = models.ImageField(upload_to="dichvu/", blank=True, null=True, verbose_name="Hình ảnh")

    def __str__(self):
        return self.ten_dich_vu


# Create your models here.
