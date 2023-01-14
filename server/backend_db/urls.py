from django.urls import path, re_path # , include
from django.contrib import admin
#  path('', views.index, name='index'),
# path('backend_db/', include('backend_db.urls')),
# from backend_db.views import register_view, get_elexon, get_elexon_by_date
from backend_db.views import UserView, get_elexon, get_elexon_by_date, register_view, GeolocationsView
from django.conf.urls import include
from rest_framework.routers import DefaultRouter

# router = DefaultRouter()
# router.register(r'userProfile', UserViewSet, basename = 'userProfile')

urlpatterns = [
    # re_path('userProfile/', include(router.urls)),
    # path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # re_path('^', include(router.urls)),
    path('userProfile/', UserView.as_view(), name = 'userProfile'),
    path('Geolocations/', GeolocationsView.as_view(), name = 'geolocations'),
    path('register_users/', register_view, name='register_users'),
    path('get_elexon/', get_elexon, name='get_elexon'),
    path('get_elexon/<str:date>', get_elexon_by_date, name='get_elexon_by_date'),
    # re_path('^',include(router.urls)),
]