from django.urls import path
from . import views
from .views import get_unread_count
urlpatterns = [
    path('', views.chatbox_view, name='chatbox'),
    path("gui/", views.gui_tin_nhan, name="gui_tin_nhan"),
    # ADMIN / NHÂN VIÊN
    path("khach/<int:khach_id>/", views.chat_admin, name="admin_chat_khach"),
    path("khach/", views.danh_sach_khach, name="danh_sach_khach"),
    path("get-unread-count/", views.get_unread_count, name="get_unread_count"),
    path("get-unread-customers/", views.admin_unread_customers, name="admin_unread_customers")

]
