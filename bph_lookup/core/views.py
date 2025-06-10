from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import State, ProcedureCode, FeeScheduleRate, Region
from .serializers import FeeScheduleRateSerializer

def rate_lookup(request):
    """
    Simple lookup: User selects state, zip, code.
    Returns all matching fee schedule rates.
    """
    context = {
        'states': State.objects.all(),
        'codes': ProcedureCode.objects.all(),
    }

    if request.method == "POST":
        state_code = request.POST.get('state')
        procedure_code = request.POST.get('procedure_code')
        zip_code = request.POST.get('zip_code')

        region = Region.objects.filter(state__state_code=state_code).first()
        rates = FeeScheduleRate.objects.filter(
            procedure_code__procedure_code=procedure_code,
            region=region,
            fee_schedule__state__state_code=state_code
        ).select_related('fee_schedule', 'region', 'procedure_code')
        context['rates'] = rates

    return render(request, "core/rate_lookup.html", context)


@api_view(["GET"])
def rate_lookup_api(request):
    """Return fee schedule rates matching query parameters."""
    state_code = request.query_params.get("state")
    procedure_code = request.query_params.get("procedure_code")
    zip_code = request.query_params.get("zip_code")

    region = None
    if state_code:
        region = Region.objects.filter(state__state_code=state_code).first()

    rates = FeeScheduleRate.objects.all()
    if state_code:
        rates = rates.filter(fee_schedule__state__state_code=state_code)
    if procedure_code:
        rates = rates.filter(procedure_code__procedure_code=procedure_code)
    if region:
        rates = rates.filter(region=region)

    serializer = FeeScheduleRateSerializer(
        rates.select_related("procedure_code", "fee_schedule", "region"), many=True
    )
    return Response(serializer.data)
