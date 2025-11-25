from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

class KhachHang(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    ho_ten = models.CharField(max_length=100, blank=True)
    so_dien_thoai = models.CharField(max_length=15)
    dia_chi = models.CharField(max_length=255)
    gioi_tinh = models.CharField(max_length=1, choices=[('M', 'Nam'), ('F', 'Nữ')])
    ngay_sinh = models.DateField(null=True, blank=True)
    email = models.EmailField(max_length=255, blank=True)
    ngay_tham_gia = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username



class NhanVien(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    ho_ten = models.CharField(max_length=100, blank=True)
    email = models.EmailField(max_length=255, blank=True)
    so_dien_thoai = models.CharField(max_length=15)
    dia_chi = models.CharField(max_length=255)
    ngay_vao_lam = models.DateField()

    def __str__(self):
        return self.ho_ten or (self.user.get_full_name() or self.user.username)


class ThuCung(models.Model):
    khach_hang = models.ForeignKey(KhachHang, on_delete=models.CASCADE)
    ten_thucung = models.CharField(max_length=100)
    loai = models.CharField(max_length=100)
    tuoi = models.IntegerField()
    can_nang = models.FloatField(null=True, blank=True)
    ghi_chu = models.TextField(blank=True)

    def __str__(self):
        return f"{self.ten_thucung} ({self.loai})"

class TichDiem(models.Model):
    khach_hang = models.OneToOneField(KhachHang, on_delete=models.CASCADE, related_name='tich_diem')
    tong_diem = models.IntegerField(default=0)
    cap_bac = models.CharField(max_length=50, default='Thành viên mới')

    def cap_nhat_cap_bac(self):
        if self.tong_diem >= 1000:
            self.cap_bac = "Kim cương 💎"
        elif self.tong_diem >= 500:
            self.cap_bac = "Vàng 🏆"
        elif self.tong_diem >= 200:
            self.cap_bac = "Bạc"
        else:
            self.cap_bac = "Thành viên mới 🐾"
        self.save()

    def __str__(self):
        return f"{self.khach_hang.ho_ten} - {self.tong_diem} điểm"

class LichSuTichDiem(models.Model):
    khach_hang = models.ForeignKey(KhachHang, on_delete=models.CASCADE)
    so_diem = models.IntegerField()
    noi_dung = models.CharField(max_length=255)
    ngay_cap_nhat = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.khach_hang.ho_ten} ({self.so_diem} điểm)"