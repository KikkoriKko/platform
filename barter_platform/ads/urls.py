from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdViewSet, ExchangeProposalViewSet
from . import views
from django.contrib.auth import views as auth_views


router = DefaultRouter()
router.register(r'ads', AdViewSet)
router.register(r'exchange-proposals', ExchangeProposalViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('', views.ad_list, name='ad_list'),
    path('create/', views.create_ad, name='create_ad'),
    path('create-proposal/<int:ad_id>/', views.create_exchange_proposal, name='create_proposal'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('delete/<int:ad_id>/', views.ad_delete, name='ad_delete'),
]
