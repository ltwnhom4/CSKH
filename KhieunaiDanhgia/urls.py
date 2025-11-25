from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('tao-danh-gia/<int:lich_hen_id>/', views.tao_danh_gia, name='tao_danh_gia'),
    path('tao-khieu-nai/<int:lich_hen_id>/', views.tao_khieu_nai, name='tao_khieu_nai'),
    path('danh-sach/', views.danh_sach_khieu_nai, name='danh_sach_khieu_nai'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
