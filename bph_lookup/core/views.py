from django.shortcuts import render
from .models import State, ProcedureCode, FeeScheduleRate, Region

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