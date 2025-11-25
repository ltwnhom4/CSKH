
from django.urls import path
from .import views
from trangchu import views as trangchu_views
urlpatterns = [
    path('', views.home, name='home'),
    path('lien-he/', trangchu_views.lien_he, name='lien_he'),
]
