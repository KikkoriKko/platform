from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AdViewSet,
    ExchangeProposalViewSet,
    ad_list,
    create_ad,
    create_exchange_proposal,
    signup,
    user_login,
    logout_view,
    ad_delete,
    ad_detail,
    exchange_proposals_for_user,
    exchange_proposals_sent_by_user,
    respond_to_proposal,
)
from django.contrib.auth import views as auth_views

router = DefaultRouter()
router.register(r'ads', AdViewSet)
router.register(r'exchange-proposals', ExchangeProposalViewSet)

urlpatterns = [
    path('api/', include(router.urls)),

    path('', ad_list, name='ad_list'),
    path('create/', create_ad, name='create_ad'),
    path('create-proposal/<int:ad_id>/', create_exchange_proposal, name='create_proposal'),
    path('delete/<int:ad_id>/', ad_delete, name='ad_delete'),
    path('ad/<int:ad_id>/', ad_detail, name='ad_detail'),

    path('signup/', signup, name='signup'),
    path('login/', user_login, name='login'),
    path('logout/', logout_view, name='logout'),

    path('my-proposals/', exchange_proposals_sent_by_user, name='proposals_sent'),
    path('received-proposals/', exchange_proposals_for_user, name='proposals_received'),
    path('respond-proposal/<int:proposal_id>/<str:response>/', respond_to_proposal, name='respond_proposal'),
]
