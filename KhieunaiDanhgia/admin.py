from django.contrib import admin
from .models import KhieuNai, DanhGia

@admin.register(KhieuNai)
class KhieuNaiAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'nguoi_gui', 'get_thu_cung', 'get_dich_vu', 'nhan_vien_phu_trach', 'trang_thai', 'ngay_gui'
    )
    list_display_links = ('id', 'nguoi_gui')

    list_filter = ('trang_thai', 'ngay_gui')

    search_fields = (
        'nguoi_gui__username', 'nhan_vien_phu_trach__username', 'lich_hen__thu_cung__ten_thucung', 'noi_dung'
    )

    fields = (
        'lich_hen', 'nguoi_gui', 'noi_dung', 'minh_chung', 'yeu_cau', 'phan_hoi', 'trang_thai', 'nhan_vien_phu_trach', 'ngay_gui',
    )

    readonly_fields = ('nguoi_gui', 'lich_hen', 'ngay_gui')

    # Định nghĩa các hàm lấy thông tin liên quan
    def get_thu_cung(self, obj):
        return obj.lich_hen.thu_cung.ten_thucung
    get_thu_cung.short_description = "Thú cưng"

    def get_dich_vu(self, obj):
        return ", ".join([dv_lh.dich_vu.ten_dich_vu for dv_lh in obj.lich_hen.dv_lichhen_set.all()]) or "Không có"
    get_dich_vu.short_description = "Dịch vụ"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_staff and not request.user.is_superuser:
            return qs.filter(nhan_vien_phu_trach=request.user)
        return qs

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            # Superuser chỉ được phép sửa trường 'nhân viên phụ trách'
            return ['nguoi_gui', 'lich_hen', 'ngay_gui', 'noi_dung', 'minh_chung', 'yeu_cau', 'phan_hoi', 'trang_thai']
        if request.user.is_staff and not request.user.is_superuser:
            return [
                'nguoi_gui', 'lich_hen', 'ngay_gui', 'nhan_vien_phu_trach', 'noi_dung', 'minh_chung', 'yeu_cau',
            ]
        return self.readonly_fields
    def has_add_permission(self, request):
        # Cấm Superuser tạo mới khiếu nại
        if request.user.is_superuser:
            return False  # Trả về False để không cho phép tạo mới khiếu nại
        return super().has_add_permission(request)  # Cho phép những người khác tạo mới
    def has_delete_permission(self, request, obj=None):
        # Cấm admin xóa khiếu nại
        return False
    def save_model(self, request, obj, form, change):
        if obj.phan_hoi and obj.trang_thai != 'Đã phản hồi':
            obj.trang_thai = 'Đã phản hồi'
        super().save_model(request, obj, form, change)

# Cấu hình hiển thị cho model Đánh giá
@admin.register(DanhGia)
class DanhGiaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nguoi_dung', 'lich_hen', 'diem', 'nhan_xet', 'ngay_danh_gia')
    list_filter = ('diem',)
    search_fields = ('nguoi_dung__username', 'lich_hen__thu_cung__ten_thucung')

    # Đảm bảo rằng các trường trong form sẽ là read-only (không thể sửa)
    def get_readonly_fields(self, request, obj=None):
        # Kiểm tra nếu là admin
        if request.user.is_staff:
            return [
                'nguoi_dung',
                'lich_hen',
                'diem',
                'nhan_xet',
                'ngay_danh_gia',
            ]  # Không cho phép sửa những trường này
        return self.readonly_fields

    # Tùy chỉnh hành động lưu khi có thay đổi trong form
    def save_model(self, request, obj, form, change):
        # Admin chỉ xem, không sửa nên không cần thay đổi gì khi lưu
        if request.user.is_staff:
            return  # Admin không được phép thay đổi
        super().save_model(request, obj, form, change)  # Nếu không phải admin, cho phép lưu lại

        # Cấm Admin xóa đánh giá
    def has_delete_permission(self, request, obj=None):
        return False  # Trả về False để không cho phép xóa
        # Cấm Superuser tạo mới đánh giá

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return False  # Cấm Superuser tạo mới
        return super().has_add_permission(request)  # Cho phép những người khác