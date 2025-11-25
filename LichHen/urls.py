from django.urls import path
from . import views

urlpatterns = [
    # Xem danh sách lịch hẹn sắp tới
    path('sap-toi/', views.lich_hen_sap_toi, name='lich_hen_sap_toi'),

    # Thêm lịch hẹn mới
    path('tao-lich-hen/', views.tao_lich_hen, name='them_lich_hen'),


    # Xóa lịch hẹn
    path('xoa/<int:id>/', views.xoa_lich_hen, name='xoa_lich_hen'),

    # (Tùy chọn) xem lịch sử hoặc lịch đã hủy
    path('lich-su/', views.lich_su_lich_hen, name='lich_su_lich_hen'),
    path('da-huy/', views.lich_da_huy, name='lich_da_huy'),
    path('api/thu-cung/<int:pk>/', views.thong_tin_thu_cung, name='api_thu_cung'),

]
