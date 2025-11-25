from django.urls import path
from .import views
urlpatterns = [
    path('dangky/', views.dangky, name='dangky'),
    path('dangnhap/', views.dangnhap, name='dangnhap'),
    path('quenmatkhau/', views.quenmatkhau, name='quenmatkhau'),
    path('dangxuat/', views.dangxuat, name='dangxuat'),
    path('thongtintaikhoan/', views.thongtintaikhoan, name='thongtintaikhoan'),
    path('xoa_tai_khoan/', views.xoa_tai_khoan, name='xoa_tai_khoan'),
    path('thong-tin-nhanvien/', views.thong_tin_nhanvien, name='thong_tin_nhanvien'),
    path('tich-diem/', views.quan_ly_tich_diem, name='quan_ly_tich_diem'),
    path('tich-diem-cua-toi/', views.xem_tich_diem, name='xem_tich_diem'),
]
