from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import ThongBao

@admin.register(ThongBao)
class ThongBaoAdmin(admin.ModelAdmin):
    list_display = ('id', 'tieu_de', 'nguoi_gui', 'nguoi_nhan', 'loai', 'ngay_tao', 'da_doc')
    list_filter = ('loai', 'ngay_tao', 'da_doc')
    search_fields = ('tieu_de', 'noi_dung', 'nguoi_gui__username', 'nguoi_nhan__username')
    ordering = ('-ngay_tao',)