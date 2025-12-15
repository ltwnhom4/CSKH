from django.contrib import admin
from .models import ThongBao

@admin.register(ThongBao)
class ThongBaoAdmin(admin.ModelAdmin):
    fields = (
        'loai',
        'tieu_de',
        'noi_dung',
        'nguoi_gui',
        'nguoi_nhan',
        'hinh_anh',
        'doi_tuong_id',
        'link',
    )

    readonly_fields = fields  # 🔒 TẤT CẢ CHỈ ĐỌC

    # ❌ Không cho tạo
    def has_add_permission(self, request):
        return False

    # ❌ Không cho sửa (nhưng vẫn cho xem danh sách)
    def has_change_permission(self, request, obj=None):
        return False
    # ❌ Không cho xóa
    def has_delete_permission(self, request, obj=None):
        return False
