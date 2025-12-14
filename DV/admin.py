from django.contrib import admin
from .models import DichVu

@admin.register(DichVu)
class DichVuAdmin(admin.ModelAdmin):
    list_display = ('ten_dich_vu', 'gia')
    # ⭐ Bộ lọc theo tên dịch vụ
    list_filter = ('ten_dich_vu',)

    # ⭐ Tìm kiếm theo tên dịch vụ
    search_fields = ('ten_dich_vu',)

    # 🟣 Ẩn quyền xoá cho người không phải superuser
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

