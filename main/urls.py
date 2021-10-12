from django.urls import path

from main.views import FirstView, SecondView

app_name = 'main'

urlpatterns = [
    path('first_Page/', FirstView.as_view(), name='first_Page'),
    path('second_Page/', SecondView.as_view(), name='second_Page'),

]