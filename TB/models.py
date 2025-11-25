from django.db import models
from django.contrib.auth.models import User
from TK.models import KhachHang, NhanVien

# Create your models here.


# Bảng Thông báo thực tế
class ThongBao(models.Model):
    TIEU_DE_CHOICES = [
        ('lich_hen', 'Lịch hẹn'),
        ('khieu_nai', 'Khiếu nại'),
        ('he_thong', 'Hệ thống'),
    ]
    tieu_de = models.CharField(max_length=100)
    noi_dung = models.TextField()
    loai = models.CharField(max_length=20, choices=TIEU_DE_CHOICES, default='lich_hen')
    ngay_tao = models.DateTimeField(auto_now_add=True)
    da_doc = models.BooleanField(default=False)
    ghi_chu = models.TextField(blank=True, null=True)
    dich_vu = models.CharField(max_length=255, blank=True, null=True)
    nguoi_gui = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='thongbao_gui'
    )
    nguoi_nhan = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='thongbao_nhan'
    )

    # 🌸 Thêm trường link điều hướng
    link = models.CharField(
        max_length=300,
        blank=True,
        null=True,
        help_text="Đường dẫn khi người dùng bấm vào thông báo"
    )
    doi_tuong_id = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.tieu_de} - {self.nguoi_nhan.username}"

    class Meta:
        ordering = ['-ngay_tao']