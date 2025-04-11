from rest_framework import filters, viewsets
from rest_framework.response import Response
from .models import Ad, ExchangeProposal, Category
from .serializers import AdSerializer, ExchangeProposalSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .forms import AdForm, ExchangeProposalForm
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.core.paginator import Paginator
from django.db.models import Q


class AdViewSet(viewsets.ModelViewSet):
    queryset = Ad.objects.all()
    serializer_class = AdSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    filterset_fields = ['category', 'condition']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ExchangeProposalViewSet(viewsets.ModelViewSet):
    queryset = ExchangeProposal.objects.all()
    serializer_class = ExchangeProposalSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['ad_sender', 'ad_receiver', 'status']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(status='waiting')

    def update(self, request, *args, **kwargs):
        proposal = self.get_object()
        if 'status' in request.data:
            status_value = request.data['status']
            if status_value not in ['waiting', 'accepted', 'rejected']:
                return Response({'detail': 'Invalid status'}, status=400)
            proposal.status = status_value
            proposal.save()
            return Response(self.get_serializer(proposal).data, status=200)
        return super().update(request, *args, **kwargs)


@login_required
def create_ad(request):
    if request.method == 'POST':
        form = AdForm(request.POST, request.FILES)
        if form.is_valid():
            ad = form.save(commit=False)
            ad.user = request.user
            ad.save()
            return redirect('ad_list')
    else:
        form = AdForm()
    return render(request, 'ads/create_ad.html', {'form': form})


@login_required
def edit_ad(request, ad_id):
    ad = get_object_or_404(Ad, id=ad_id)

    if ad.user != request.user:
        return HttpResponseForbidden("Вы не можете редактировать это объявление")

    if request.method == 'POST':
        form = AdForm(request.POST, instance=ad)
        if form.is_valid():
            form.save()
            return redirect('ad_list')
    else:
        form = AdForm(instance=ad)

    return render(request, 'ads/edit_ad.html', {'form': form, 'ad': ad})


@login_required
def create_exchange_proposal(request, ad_id):
    ad_receiver = get_object_or_404(Ad, id=ad_id)
    ad_senders = Ad.objects.filter(user=request.user)

    if not ad_senders:
        return redirect('ad_list')

    if request.method == 'POST':
        form = ExchangeProposalForm(request.POST, user=request.user)
        if form.is_valid():
            proposal = form.save(commit=False)
            proposal.ad_sender = form.cleaned_data['ad_sender']
            proposal.ad_receiver = ad_receiver
            proposal.status = 'waiting'  # Статус ожидает обработки
            proposal.save()
            return redirect('exchange_proposals_sent')  # Направление на страницу с отправленными предложениями
        else:
            form.add_error('ad_sender', 'Выберите объявление для обмена.')

    else:
        form = ExchangeProposalForm(initial={'ad_receiver': ad_receiver.id}, user=request.user)

    return render(request, 'ads/create_proposal.html', {
        'form': form,
        'ad_receiver': ad_receiver,
        'ad_senders': ad_senders
    })


def ad_list(request):
    query = request.GET.get('q')
    category_id = request.GET.get('category')
    condition = request.GET.get('condition')

    ads = Ad.objects.all()

    # Фильтрация по запросу (по названию или описанию)
    if query:
        ads = ads.filter(Q(title__icontains=query) | Q(description__icontains=query))

    # Фильтрация по категории
    if category_id:
        ads = ads.filter(category_id=category_id)

    # Фильтрация по состоянию
    if condition:
        ads = ads.filter(condition=condition)

    # Пагинация
    paginator = Paginator(ads, 10)  # 10 объявлений на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Передача контекста
    context = {
        'page_obj': page_obj,
        'categories': Category.objects.all(),  # Модели категорий
    }

    return render(request, 'ads/ad_list.html', context)


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()

    return render(request, 'registration/signup.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('ad_list')
            else:
                form.add_error(None, 'Invalid login credentials')
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def ad_delete(request, ad_id):
    ad = get_object_or_404(Ad, id=ad_id)

    if ad.user != request.user:
        return HttpResponseForbidden("Вы не можете удалить это объявление")

    ad.delete()
    return redirect('ad_list')


@login_required
def ad_detail(request, ad_id):
    ad = get_object_or_404(Ad, id=ad_id)
    return render(request, 'ads/ad_detail.html', {'ad': ad})


@login_required
def exchange_proposals_for_user(request):
    user_ads = Ad.objects.filter(user=request.user)
    proposals = ExchangeProposal.objects.filter(ad_receiver__in=user_ads)
    return render(request, 'ads/exchange_proposals_received.html', {'proposals': proposals})


@login_required
def exchange_proposals_sent_by_user(request):
    user_ads = Ad.objects.filter(user=request.user)
    proposals = ExchangeProposal.objects.filter(ad_sender__in=user_ads)
    return render(request, 'ads/exchange_proposals_sent.html', {'proposals': proposals})


@login_required
def respond_to_proposal(request, proposal_id, response):
    proposal = get_object_or_404(ExchangeProposal, id=proposal_id)

    if proposal.requested_ad.owner != request.user:
        return redirect('received_proposals')

    if request.method == 'POST' and proposal.status == 'pending':
        if response == 'accepted':
            proposal.status = 'accepted'
        elif response == 'rejected':
            proposal.status = 'rejected'
        proposal.save()

    return redirect('received_proposals')