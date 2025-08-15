from django.urls import path, include
from .views import *


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path("logout/", LogoutView.as_view()),
    path('user/', UserView.as_view()),
    path("csrf/", CSRFView.as_view()),

    path("crash_point/", get_crash_point),
    path("wallet/balance/", get_balance),
    path("wallet/deposit/", deposit),
    path("wallet/withdraw/", withdraw),
    path("wallet/history/", wallet_history),
    path('wallet/bet/', place_bet),
    path('wallet/win/', handle_win),
    path('wallet/cancel/', cancel_bet),
    path('send-otp/', send_otp),
    path('verify-otp/', verify_otp),
    path('reset-password/', reset_password),
]