from django.contrib import admin
from .models import (KhachHang, NhanVien, ThuCung, LichSuTichDiem)
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone
from TK.models import NhanVien


class NhanVienAdmin(admin.ModelAdmin):
    list_display = ('ho_ten', 'email', 'so_dien_thoai','dia_chi', 'ngay_vao_lam')
    search_fields = ('ho_ten', 'so_dien_thoai')
    ordering = ('ngay_vao_lam',)

    # 🔒 Tắt quyền thêm thủ công trong admin
    def has_add_permission(self, request):
        return False
class KhachHangAdmin(admin.ModelAdmin):
   list_display = ('ho_ten', 'so_dien_thoai', 'dia_chi','email', 'gioi_tinh', 'ngay_sinh', 'ngay_tham_gia')
   search_fields = ( 'ho_ten', 'so_dien_thoai' )
   ordering = ('ngay_tham_gia',)
   def has_add_permission(self, request):
       return False

class ThuCungAdmin(admin.ModelAdmin):
   list_display = ('ten_thucung', 'loai', 'tuoi', 'can_nang', 'ghi_chu','khach_hang')
   list_filter = ('loai', 'khach_hang')
   search_fields = ('ten_thucung', 'khach_hang')


# Kế thừa UserAdmin mặc định để tùy chỉnh hành vi khi lưu
class CustomUserAdmin(UserAdmin):
    def save_model(self, request, obj, form, change):
        # Gọi phương thức gốc để lưu user
        super().save_model(request, obj, form, change)

        # Khi user được lưu hoặc cập nhật:
        if obj.is_staff:
            # Nếu là nhân viên => tạo hoặc cập nhật NhanVien tương ứng
            NhanVien.objects.update_or_create(
                user=obj,
                defaults={
                    'ho_ten': obj.get_full_name() or obj.username,
                    'email': obj.email,
                    'so_dien_thoai': '',
                    'dia_chi': '',
                    'ngay_vao_lam': timezone.now().date(),
                }
            )
            # Xóa khỏi bảng KhachHang (nếu có)
            KhachHang.objects.filter(user=obj).delete()
        else:
            # Nếu bỏ quyền staff => xóa bản ghi NhanVien
            NhanVien.objects.filter(user=obj).delete()

            KhachHang.objects.get_or_create(
                user=obj,
                defaults={
                    'ho_ten': obj.get_full_name() or obj.username,
                    'email': obj.email,
                    'ngay_tham_gia': timezone.now().date(),
                }
            )
@admin.register(LichSuTichDiem)
class LichSuTichDiemAdmin(admin.ModelAdmin):
    list_display = ('khach_hang', 'so_diem', 'noi_dung', 'ngay_cap_nhat')
    list_filter = ('ngay_cap_nhat',)
    search_fields = ('khach_hang__ho_ten',)

# Gỡ bỏ UserAdmin mặc định của Django
admin.site.unregister(User)
# Đăng ký lại với phiên bản tùy chỉnh
admin.site.register(User, CustomUserAdmin)
admin.site.register(KhachHang, KhachHangAdmin)
admin.site.register(NhanVien, NhanVienAdmin)
admin.site.register(ThuCung, ThuCungAdmin)
