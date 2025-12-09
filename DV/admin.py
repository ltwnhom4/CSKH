from django.contrib import admin
from .models import DichVu

@admin.register(DichVu)
class DichVuAdmin(admin.ModelAdmin):
    list_display = ('ten_dich_vu', 'gia')

    # 🟣 Ẩn quyền xoá cho người không phải superuser
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

