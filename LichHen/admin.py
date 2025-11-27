# LichHen/admin.py
from django.contrib import admin
from .models import LichHen, DV_LichHen
from TK.models import NhanVien

# --- Inline để hiển thị và chỉnh sửa dịch vụ ---
class DV_LichHenInline(admin.TabularInline):
    model = DV_LichHen
    extra = 1
    verbose_name = "Dịch vụ trong lịch hẹn"
    verbose_name_plural = "Danh sách dịch vụ"


@admin.register(LichHen)
class LichHenAdmin(admin.ModelAdmin):

    list_display = ('khach_hang', 'so_dien_thoai','thu_cung','nhan_vien', 'thoi_gian', 'trang_thai','hien_thi_dich_vu','ghi_chu', 'ly_do_huy')
    list_filter = ('trang_thai','nhan_vien','thoi_gian')
    search_fields = ('khach_hang__ho_ten','so_dien_thoai','thu_cung__ten_thucung','nhan_vien__ho_ten')
    ordering = ('-thoi_gian',)
    inlines = [DV_LichHenInline]

    # Khóa trường nhan_vien đối với STAFF
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        # STAFF không được chọn nhan_vien
        if request.user.is_staff and not request.user.is_superuser:
            if 'nhan_vien' in form.base_fields:
                form.base_fields['nhan_vien'].disabled = True

        return form

    # Hiển thị DV
    def hien_thi_dich_vu(self, obj):
        dich_vus = obj.dv_lichhen_set.select_related('dich_vu').all()
        return ", ".join([dv.dich_vu.ten_dich_vu for dv in dich_vus]) if dich_vus else "(chưa chọn)"
    hien_thi_dich_vu.short_description = "Dịch vụ"

    # Quyền sửa readonly fields
    def get_readonly_fields(self, request, obj=None):

        # Tạo mới
        if obj is None:
            if request.user.is_superuser:
                return ['ly_do_huy', 'nguoi_tao', 'tong_tien']
            if request.user.is_staff:
                return ['tong_tien', 'ly_do_huy', 'nguoi_tao']
            return [f.name for f in self.model._meta.fields]

        # Lịch khách tạo
        if obj.nguoi_tao is None:
            if request.user.is_superuser:
                return ['khach_hang', 'thu_cung', 'so_dien_thoai', 'thoi_gian', 'ghi_chu', 'tong_tien', 'ly_do_huy','nguoi_tao']
            if request.user.is_staff:
                return ['khach_hang', 'thu_cung', 'nhan_vien', 'so_dien_thoai', 'thoi_gian', 'ghi_chu','tong_tien', 'ly_do_huy','nguoi_tao']

        # Lịch do chính user tạo
        if obj.nguoi_tao == request.user:
            return ['ly_do_huy','nguoi_tao','tong_tien']

        # Staff khác → chỉ sửa trạng thái
        if request.user.is_staff:
            return ['khach_hang', 'thu_cung', 'nhan_vien','so_dien_thoai', 'thoi_gian', 'ghi_chu','tong_tien', 'ly_do_huy']

        return []

    def save_model(self, request, obj, form, change):
        if not change:
            obj.nguoi_tao = request.user
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        obj = form.instance
        obj.tinh_tong_tien()

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        # Admin xem tất cả
        if request.user.is_superuser:
            return qs

        # Nhân viên xem lịch do mình phụ trách
        if request.user.is_staff:
            try:
                nv = NhanVien.objects.get(user=request.user)
            except NhanVien.DoesNotExist:
                return qs.none()  # nhân viên chưa có profile NhanVien → không thấy lịch nào

            return qs.filter(nhan_vien=nv)

        # Khách thì không có quyền vào admin
        return qs.none()


@admin.register(DV_LichHen)
class DV_LichHenAdmin(admin.ModelAdmin):
    list_display = ('lich_hen', 'dich_vu')
    search_fields = ('lich_hen__khach_hang__ho_ten', 'dich_vu__ten_dich_vu')
