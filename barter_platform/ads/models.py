from django.db import models
from django.contrib.auth.models import User


class Ad(models.Model):
    CONDITIONS = [
        ('new', 'Новый'),
        ('used', 'Б/У'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    image_url = models.URLField(blank=True, null=True)
    category = models.CharField(max_length=100)
    condition = models.CharField(max_length=4, choices=CONDITIONS)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class ExchangeProposal(models.Model):
    STATUSES = [
        ('waiting', 'Ожидает'),
        ('accepted', 'Принята'),
        ('rejected', 'Отклонена'),
    ]

    ad_sender = models.ForeignKey(Ad, related_name='sent_proposals', on_delete=models.CASCADE)
    ad_receiver = models.ForeignKey(Ad, related_name='received_proposals', on_delete=models.CASCADE)
    comment = models.TextField()
    status = models.CharField(max_length=8, choices=STATUSES, default='waiting')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Proposal from {self.ad_sender.title} to {self.ad_receiver.title}"
