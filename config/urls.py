
from django.urls import path, include

urlpatterns = [
    # path('v2/api-auth/', include('rest_framework.urls',
    #                              namespace='rest_framework_v2')),
    # path('v2/', include('drones.v2.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('', include('drones.urls')),
]
