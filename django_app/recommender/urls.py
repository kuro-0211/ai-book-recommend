from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("my/", views.my_history, name="my_history"),
    path("signup/", views.signup, name="signup"),
]
