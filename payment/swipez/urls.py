from django.urls import path

from .views import views_example

app_name = 'swipez'

urlpatterns = [
    path('', views_example.HomePageView.as_view(), name='example'),
    path('test/', views_example.test, name='example_test'),
    path('payment/', views_example.payment, name='example_payment'),
    path('webhook/', views_example.response, name='example_webhook'),
]
