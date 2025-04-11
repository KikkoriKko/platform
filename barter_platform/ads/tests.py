from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import Ad, ExchangeProposal, Category


class AdTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')

        self.category = Category.objects.create(name='Electronics')

        self.ad = Ad.objects.create(
            user=self.user,
            title="Test Item",
            description="A test item for barter",
            category=self.category,
            condition="new",
        )

    def test_ad_search(self):
        response = self.client.get('/api/ads/', {'search': 'Test Item'})
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)
        self.assertEqual(response.data[0]['title'], 'Test Item')

    def test_ad_filter(self):
        response = self.client.get('/api/ads/', {'category': 'Electronics'})
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)
        self.assertEqual(response.data[0]['category'], 'Electronics')

    def test_create_exchange_proposal(self):
        ad_receiver = Ad.objects.create(
            user=self.user,
            title="Receiver Item",
            description="Item to receive",
            category=self.category,
            condition="used",
        )

        response = self.client.post('/api/exchange-proposals/', {
            'ad_sender': self.ad.id,
            'ad_receiver': ad_receiver.id,
            'comment': 'Interested in exchange!',
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], 'waiting')
        self.assertEqual(response.data['ad_sender'], self.ad.id)
        self.assertEqual(response.data['ad_receiver'], ad_receiver.id)

    def test_update_exchange_proposal_status(self):
        proposal = ExchangeProposal.objects.create(
            ad_sender=self.ad,
            ad_receiver=self.ad,
            comment="Test proposal",
            status="waiting"
        )

        response = self.client.patch(f'/api/exchange-proposals/{proposal.id}/', {'status': 'accepted'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'accepted')
        proposal.refresh_from_db()
        self.assertEqual(proposal.status, 'accepted')
