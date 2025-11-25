# LichHen/admin.py
from django.contrib import admin
from .models import LichHen,DV_LichHen
# --- Inline để hiển thị và chỉnh sửa dịch vụ ---
class DV_LichHenInline(admin.TabularInline):
    model = DV_LichHen
    extra = 1   # số dòng trống để thêm mới
    verbose_name = "Dịch vụ trong lịch hẹn"
    verbose_name_plural = "Danh sách dịch vụ"
class LichHenAdmin(admin.ModelAdmin):
    list_display = ('khach_hang', 'so_dien_thoai','thu_cung','nhan_vien', 'thoi_gian', 'trang_thai','hien_thi_dich_vu','ghi_chu', 'ly_do_huy' )
    list_filter = ('trang_thai','nhan_vien','thoi_gian')
    search_fields = ('khach_hang__ho_ten','so_dien_thoai','thu_cung__ten_thucung','nhan_vien__ho_ten')
    ordering = ('-thoi_gian',)
    inlines = [DV_LichHenInline]  # thêm phần inline vào trang lịch hẹn
    class Media:
        css = {
            'all': ('admin_custom.css',)
        }

    # --- Hiển thị danh sách dịch vụ của từng lịch hẹn ---
    def hien_thi_dich_vu(self, obj):
        dich_vus = obj.dv_lichhen_set.select_related('dich_vu').all()
        return ", ".join([dv.dich_vu.ten_dich_vu for dv in dich_vus]) if dich_vus else "(chưa chọn)"

    hien_thi_dich_vu.short_description = "Dịch vụ"
@admin.register(DV_LichHen)
class DV_LichHenAdmin(admin.ModelAdmin):
    list_display = ('lich_hen', 'dich_vu')
    search_fields = ('lich_hen__khach_hang__ho_ten', 'dich_vu__ten_dich_vu')

admin.site.register(LichHen, LichHenAdmin)


# Register your models here.
