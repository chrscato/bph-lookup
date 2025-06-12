from django.shortcuts import render
from django.db import connection
from django.contrib import messages
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .forms import MedicareRateLookupForm, WorkersCompRateLookupForm

from .models import State, ProcedureCode, FeeScheduleRate, Region
from .serializers import FeeScheduleRateSerializer

def rate_lookup(request, template_name="core/medicare_rate_lookup.html"):
    """
    Medicare rate lookup: User enters ZIP code and CPT code.
    Returns calculated Medicare allowed amount based on GPCI, RVU, and conversion factor.
    """
    form = MedicareRateLookupForm()
    context = {'form': form}

    if request.method == "POST":
        form = MedicareRateLookupForm(request.POST)
        if form.is_valid():
            zip_code = form.cleaned_data['zip_code']
            procedure_code = form.cleaned_data['procedure_code']

            try:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT
                            mloc.zip_code, mloc.state_code, meta.state_name, meta.fee_schedule_area,
                            gpci.locality_name, gpci.work_gpci, gpci.pe_gpci, gpci.mp_gpci,
                            rvu.procedure_code, rvu.work_rvu, rvu.practice_expense_rvu, rvu.malpractice_rvu,
                            cf.conversion_factor,
                            ((COALESCE(rvu.work_rvu, 0) * COALESCE(gpci.work_gpci, 0) +
                              COALESCE(rvu.practice_expense_rvu, 0) * COALESCE(gpci.pe_gpci, 0) +
                              COALESCE(rvu.malpractice_rvu, 0) * COALESCE(gpci.mp_gpci, 0))
                             * COALESCE(cf.conversion_factor, 0)) AS allowed_amount
                        FROM medicare_locality_map mloc
                        JOIN medicare_locality_meta meta ON mloc.carrier_code = meta.mac_code AND mloc.locality_code = meta.locality_code
                        JOIN cms_gpci gpci ON TRIM(meta.fee_schedule_area) = TRIM(gpci.locality_name) AND mloc.locality_code = gpci.locality_code
                        JOIN cms_rvu rvu ON 1=1
                        JOIN cms_conversion_factor cf ON gpci.year = cf.year
                        WHERE mloc.zip_code = %s AND gpci.year = 2025 AND rvu.year = 2025 
                        AND rvu.procedure_code = %s AND (rvu.modifier IS NULL OR rvu.modifier = '')
                    """, [zip_code, procedure_code])
                    
                    columns = [col[0] for col in cursor.description]
                    result = cursor.fetchone()
                    
                    if result:
                        context['result'] = dict(zip(columns, result))
                        messages.success(request, 'Rate calculation completed successfully.')
                    else:
                        messages.warning(request, 'No results found for the given ZIP code and procedure code.')
            except Exception as e:
                messages.error(request, f'Error calculating rate: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')

    return render(request, template_name, context)


def home(request):
    """Landing page with introductory text and quick Medicare lookup."""
    return rate_lookup(request, template_name="core/home.html")


def workers_comp_lookup(request, template_name="core/workers_comp_rate_lookup.html"):
    """Workers' compensation fee schedule lookup by state and CPT code."""
    form = WorkersCompRateLookupForm()
    context = {"form": form}

    if request.method == "POST":
        form = WorkersCompRateLookupForm(request.POST)
        if form.is_valid():
            state = form.cleaned_data["state"]
            procedure_code = form.cleaned_data["procedure_code"]

            try:
                rate = (
                    FeeScheduleRate.objects
                    .select_related("fee_schedule", "procedure_code", "region")
                    .filter(
                        fee_schedule__state=state,
                        procedure_code__procedure_code=procedure_code,
                    )
                    .order_by("-fee_schedule__effective_date")
                    .first()
                )
                if rate:
                    context["rate"] = rate
                    messages.success(request, "Rate lookup completed successfully.")
                else:
                    messages.warning(request, "No results found for the given state and procedure code.")
            except Exception as e:
                messages.error(request, f"Error retrieving rate: {str(e)}")
        else:
            messages.error(request, "Please correct the errors below.")

    return render(request, template_name, context)


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
