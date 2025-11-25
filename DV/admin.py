from django.contrib import admin
from .models import DichVu

@admin.register(DichVu)
class DichVuAdmin(admin.ModelAdmin):
    list_display = ('ten_dich_vu', 'gia')

    # 🟣 Ẩn quyền xoá cho người không phải superuser
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    # 🩷 Ẩn luôn hành động "Xóa các dịch vụ đã chọn" khỏi menu hành động
    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.is_superuser:
            if 'delete_selected' in actions:
                del actions['delete_selected']
        return actions
