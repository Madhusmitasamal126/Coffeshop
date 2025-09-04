from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('menu/', views.menu_view, name='menu'),
    path('order/', views.order_page, name='order_page'),
    path('order_confirm/', views.order_confirm, name='order_confirm'),  
     path("about/", views.about_view, name="about"),
    path("contact/", views.contact_view, name="contact"),
    path("payment/<int:order_id>/", views.payment_page, name="payment_page"),
    path("payment-success/<int:order_id>/", views.payment_success, name="payment_success"),
]
