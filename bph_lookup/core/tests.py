from django.urls import reverse
from rest_framework.test import APITestCase
from .models import State, Region, ProcedureCode, FeeSchedule, FeeScheduleRate

class RateLookupAPITest(APITestCase):
    def setUp(self):
        self.state = State.objects.create(
            state_code="CA", state_name="California",
            effective_date="2020-01-01"
        )
        self.region = Region.objects.create(
            state=self.state,
            region_type="Carrier",
            region_code="001",
            region_name="CA Region"
        )
        self.code = ProcedureCode.objects.create(
            procedure_code="99213",
            description="Office visit",
            code_type="CPT"
        )
        schedule = FeeSchedule.objects.create(
            state=self.state,
            schedule_type="Physician",
            effective_date="2020-01-01"
        )
        self.rate = FeeScheduleRate.objects.create(
            fee_schedule=schedule,
            procedure_code=self.code,
            modifier="",
            region=self.region,
            rate=100.00,
            rate_unit="1",
            effective_date="2020-01-01"
        )

    def test_rate_lookup_api(self):
        url = reverse('rate_lookup_api')
        response = self.client.get(url, {
            'state': 'CA',
            'procedure_code': '99213'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['procedure_code'], '99213')
