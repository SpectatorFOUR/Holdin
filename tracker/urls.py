from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('history/', views.history, name='history'),
    path('setup/', views.setup_balance, name='setup'),
    path('add/<slug:kind>/', views.add_transaction, name='add_transaction'),
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]



