from django.db import models

class State(models.Model):
    """
    Represents a U.S. state or territory for fee schedule purposes.
    """
    state_code = models.CharField(max_length=2, primary_key=True, help_text="2-character state code (e.g., 'CA')")
    state_name = models.CharField(max_length=50)
    effective_date = models.DateField()
    expiration_date = models.DateField(null=True, blank=True)
    has_regions = models.BooleanField(default=False)
    data_source = models.CharField(max_length=255, null=True, blank=True)
    data_url = models.CharField(max_length=255, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "State"
        verbose_name_plural = "States"

    def __str__(self):
        return f"{self.state_name} ({self.state_code})"

class Region(models.Model):
    """
    Maps a region to a state, such as a locality or carrier area.
    """
    region_id = models.AutoField(primary_key=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name="regions")
    region_type = models.CharField(max_length=50)
    region_code = models.CharField(max_length=50)
    region_name = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        unique_together = ('state', 'region_type', 'region_code')
        verbose_name = "Region"
        verbose_name_plural = "Regions"

    def __str__(self):
        return f"{self.state.state_code}-{self.region_code} ({self.region_name})"

class ProcedureCode(models.Model):
    """
    CPT, HCPCS, or DRG code and its metadata.
    """
    procedure_code = models.CharField(max_length=20, primary_key=True)
    description = models.TextField()
    code_type = models.CharField(max_length=10)
    category = models.CharField(max_length=50, null=True, blank=True)
    subcategory = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.procedure_code

class FeeSchedule(models.Model):
    id = models.AutoField(primary_key=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    schedule_type = models.CharField(max_length=50)
    effective_date = models.DateField()
    expiration_date = models.DateField(null=True, blank=True)
    conversion_factor = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.state.state_code} {self.schedule_type} ({self.effective_date})"

class FeeScheduleRate(models.Model):
    id = models.AutoField(primary_key=True)
    fee_schedule = models.ForeignKey(FeeSchedule, on_delete=models.CASCADE)
    procedure_code = models.ForeignKey(ProcedureCode, on_delete=models.CASCADE)
    modifier = models.CharField(max_length=5, null=True, blank=True, default=None)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, null=True, blank=True)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    rate_unit = models.CharField(max_length=20, default="1")
    is_by_report = models.BooleanField(default=False)
    effective_date = models.DateField()
    last_updated = models.DateTimeField(auto_now=True)
    access_count = models.IntegerField(default=0)
    last_accessed = models.DateTimeField(auto_now=True)
    service_type = models.TextField(null=True, blank=True)
    category_id = models.TextField(null=True, blank=True)
    percent_of_charge = models.TextField(null=True, blank=True)
    place_of_service = models.TextField(null=True, blank=True)
    code_type = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ('fee_schedule', 'procedure_code', 'modifier', 'region')

    def __str__(self):
        return f"{self.procedure_code} {self.modifier or ''} {self.region or ''}: {self.rate}" 