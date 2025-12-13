from django.contrib import admin
from .models import TinNhan

@admin.register(TinNhan)
class TinNhanAdmin(admin.ModelAdmin):
    list_display = ("id_tinnhan", "nguoi_gui", "noi_dung", "thoi_gian_gui",
                    "ten_khachhang", "ten_nhanvien")
    list_filter = ("nguoi_gui", "thoi_gian_gui", "id_khachhang", "id_nhanvien",)
    search_fields = ("noi_dung", "id_khachhang__ho_ten", "id_nhanvien__ho_ten", )
    ordering = ("-thoi_gian_gui",)

    def ten_khachhang(self, obj):
        return obj.id_khachhang.ho_ten if obj.id_khachhang else "-"
    ten_khachhang.short_description = "Khách hàng"

    def ten_nhanvien(self, obj):
        return obj.id_nhanvien.ho_ten if obj.id_nhanvien else "-"
    ten_nhanvien.short_description = "Nhân viên"
