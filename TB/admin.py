from django.contrib import admin
from .models import ThongBao

@admin.register(ThongBao)
class ThongBaoAdmin(admin.ModelAdmin):
    fields = ('loai', 'tieu_de', 'noi_dung', 'nguoi_nhan', 'hinh_anh', 'doi_tuong_id', 'link')

    # ❌ Không cho phép tạo thông báo mới
    def has_add_permission(self, request):
        return False

    # ❌ Không cho sửa
    def has_change_permission(self, request, obj=None):
        return True if obj is None else False
        # obj=None → cho xem danh sách
        # obj!=None → cấm sửa chi tiết

    # ✔ Cho phép xem danh sách
    def has_view_permission(self, request, obj=None):
        return True

    # ❌ Không cho phép xóa
    def has_delete_permission(self, request, obj=None):
        return False

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Ẩn field nguoi_gui trong admin
        if 'nguoi_gui' in form.base_fields:
            form.base_fields.pop('nguoi_gui')
        return form

    def save_model(self, request, obj, form, change):
        # Nếu chỉnh sửa, giữ nguyên người gửi cũ
        if not obj.pk:
            obj.nguoi_gui = request.user
        super().save_model(request, obj, form, change)
