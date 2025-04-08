from django.urls import path
from .views import login, signup, logout, forgot_password, verify_code, reset_password


urlpatterns = [
    path('login/', login, name="login"),
    path('signup/', signup, name="signup"),
    path('logout/', logout, name="logout"),
    path('forgot-password/', forgot_password, name="forgot_password"),
    path('reset-password/<uidb64>/<token>/', reset_password, name="reset_password"),
    path('verify-code/', verify_code, name="verify_code")
]
