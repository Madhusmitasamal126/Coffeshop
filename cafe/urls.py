from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("menu/", views.menu_view, name="menu"),
    path("menu/<int:item_id>/", views.menu_details, name="menu_details"),
    path("order/", views.order_page, name="order_page"),
    path("confirm_order/", views.order_confirm, name="order_confirm"),
    path("payment/<int:order_id>/", views.payment_page, name="payment_page"),
    path("payment_success/<int:order_id>/", views.payment_success, name="payment_success"),
    path("about/", views.about_view, name="about"),
    path("contact/", views.contact_view, name="contact"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
]
