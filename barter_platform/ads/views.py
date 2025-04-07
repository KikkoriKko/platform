from rest_framework import filters, viewsets
from rest_framework.response import Response
from .models import Ad, ExchangeProposal
from .serializers import AdSerializer, ExchangeProposalSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .forms import AdForm, ExchangeProposalForm
from .models import Ad
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate, logout


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
        # При создании предложения автоматически устанавливаем статус в 'ожидает'
        serializer.save(status='waiting')

    def update(self, request, *args, **kwargs):
        # Обработка обновления статуса предложения
        proposal = self.get_object()
        if 'status' in request.data:
            status = request.data['status']
            if status not in ['waiting', 'accepted', 'rejected']:
                return Response({'detail': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
            proposal.status = status
            proposal.save()
            return Response(self.get_serializer(proposal).data, status=status.HTTP_200_OK)
        return super().update(request, *args, **kwargs)


@login_required
def create_ad(request):
    if request.method == 'POST':
        form = AdForm(request.POST)
        if form.is_valid():
            ad = form.save(commit=False)
            ad.user = request.user  # Привязка объявления к текущему пользователю
            ad.save()
            return redirect('ad_list')  # После создания редиректим на страницу с объявлениями
    else:
        form = AdForm()
    return render(request, 'ads/create_ad.html', {'form': form})


@login_required
def create_exchange_proposal(request, ad_id):
    ad_receiver = Ad.objects.get(id=ad_id)
    if not ad_receiver:
        raise Http404("Ad not found")
    if request.method == 'POST':
        form = ExchangeProposalForm(request.POST)
        if form.is_valid():
            proposal = form.save(commit=False)
            proposal.ad_sender = Ad.objects.get(user=request.user)  # Привязка предложения к текущему пользователю
            proposal.ad_receiver = ad_receiver
            proposal.save()
            return redirect('ad_list')
    else:
        form = ExchangeProposalForm(initial={'ad_receiver': ad_receiver.id})
    return render(request, 'ads/create_proposal.html', {'form': form, 'ad_receiver': ad_receiver})


def ad_list(request):
    ads = Ad.objects.all()  # Получаем все объявления
    return render(request, 'ads/ad_list.html', {'ads': ads})


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # После успешной регистрации перенаправляем на страницу входа
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
                return redirect('ad_list')  # Перенаправление после успешного логина
            else:
                form.add_error(None, 'Invalid login credentials')
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


def ad_delete(request, ad_id):
    ad = get_object_or_404(Ad, id=ad_id)

    # Проверка, что пользователь является автором объявления
    if ad.user != request.user:
        return HttpResponseForbidden("Вы не можете удалить это объявление")

    # Удаление объявления
    ad.delete()

    # Перенаправление после удаления
    return redirect('ad_list')