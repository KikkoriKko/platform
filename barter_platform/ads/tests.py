from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import Ad, ExchangeProposal


class AdTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.ad = Ad.objects.create(
            user=self.user,
            title="Test Item",
            description="A test item for barter",
            category="Electronics",
            condition="new",
        )

    def test_ad_search(self):
        response = self.client.get('/ads/api/ads/', {'search': 'Test Item'})
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)

    def test_ad_filter(self):
        response = self.client.get('/ads/api/ads/', {'category': 'Electronics'})
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)

    def test_create_exchange_proposal(self):
        ad_receiver = Ad.objects.create(
            user=self.user,
            title="Receiver Item",
            description="Item to receive",
            category="Electronics",
            condition="used",
        )
        response = self.client.post('/ads/api/exchange-proposals/', {
            'ad_sender': self.ad.id,
            'ad_receiver': ad_receiver.id,
            'comment': 'Interested in exchange!',
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], 'waiting')

    def test_update_exchange_proposal_status(self):
        proposal = ExchangeProposal.objects.create(
            ad_sender=self.ad,
            ad_receiver=self.ad,
            comment="Test proposal",
            status="waiting"
        )
        response = self.client.patch(f'/ads/api/exchange-proposals/{proposal.id}/', {'status': 'accepted'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'accepted')
