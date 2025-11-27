from django.db import models
from django.utils import timezone
from TK.models import KhachHang, NhanVien
from django.contrib.auth.models import User  # dùng làm admin


class TinNhan(models.Model):
    NGUOI_GUI_OPTIONS = (
        ("KH", "Khách hàng"),
        ("NV", "Nhân viên"),
        ("AD", "Quản trị viên"),
        ("HT", "Hệ thống"),
    )

    id_tinnhan = models.AutoField(primary_key=True)

    # Khóa ngoại đúng theo ERD
    id_khachhang = models.ForeignKey(KhachHang, on_delete=models.CASCADE, null=True, blank=True)
    id_nhanvien = models.ForeignKey(NhanVien, on_delete=models.SET_NULL, null=True, blank=True)
    id_admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    nguoi_gui = models.CharField(max_length=5, choices=NGUOI_GUI_OPTIONS)
    noi_dung = models.TextField()
    thoi_gian_gui = models.DateTimeField(default=timezone.now)
    phien_chat = models.CharField(max_length=50, null=True, blank=True)
    da_doc = models.BooleanField(default=False)
    def __str__(self):
        return f"[{self.nguoi_gui}] {self.noi_dung[:30]}"
