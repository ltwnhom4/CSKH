from django.urls import path
from . import views
app_name = 'TB'
urlpatterns = [
    path('<int:id>/', views.chi_tiet_thong_bao, name='chi_tiet_thong_bao'),
    path('', views.danh_sach_thong_bao, name='danh_sach_thong_bao'),
    path('thongbao/', views.danh_sach_thong_bao, name='danh_sach_thong_bao'),
    path('tat-ca/', views.trang_thong_bao, name='trang_thong_bao'),
    path('xem/<int:tb_id>/', views.xem_thong_bao, name='xem_thong_bao'),
    path('tao-khuyen-mai/', views.tao_khuyen_mai, name='tao_khuyen_mai'),
    path('khuyen-mai/', views.danh_sach_khuyen_mai, name='danh_sach_khuyen_mai'),

]
