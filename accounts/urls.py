from django.urls import include, path

from .views import forgot_password, login, logout, reset_password, signup, verify_code

urlpatterns = [
    path("login/", login, name="login"),
    path("signup/", signup, name="signup"),
    path("logout/", logout, name="logout"),
    path("oauth/", include("allauth.urls")),
    path("forgot-password/", forgot_password, name="forgot_password"),
    path("reset-password/<uidb64>/<token>/", reset_password, name="reset_password"),
    path("verify-code/", verify_code, name="verify_code"),
]
