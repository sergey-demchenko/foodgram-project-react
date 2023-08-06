from django.urls import include, path

from users.views import UserViewSet

subscriptions = UserViewSet.as_view({'get': 'subscriptions', })

urlpatterns = [
    path('users/subscriptions/', subscriptions, name='subscriptions'),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls')),
]
