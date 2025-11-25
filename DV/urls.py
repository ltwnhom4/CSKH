from django.urls import path
from . import views

urlpatterns = [
    path('', views.danh_sach_dich_vu, name='danh_sach_dich_vu'),
    path('<int:id>/', views.chi_tiet_dich_vu, name='chi_tiet_dich_vu'),
]
