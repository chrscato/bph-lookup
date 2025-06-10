from rest_framework import serializers
from .models import FeeScheduleRate

class FeeScheduleRateSerializer(serializers.ModelSerializer):
    procedure_code = serializers.CharField(source='procedure_code.procedure_code')
    description = serializers.CharField(source='procedure_code.description')
    region = serializers.CharField(source='region.region_name', allow_null=True)
    state = serializers.CharField(source='fee_schedule.state.state_code')
    schedule_type = serializers.CharField(source='fee_schedule.schedule_type')

    class Meta:
        model = FeeScheduleRate
        fields = [
            'id', 'state', 'schedule_type', 'procedure_code', 'description',
            'modifier', 'region', 'rate', 'rate_unit'
        ]
