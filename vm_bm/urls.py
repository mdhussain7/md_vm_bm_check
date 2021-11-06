from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
from .views import UserDataBMI
from django.urls import path

urlpatterns = [
	path('user_ip/', csrf_exempt(UserDataBMI.as_view()), name='user_ip')
]