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

class MedicareLocalityMap(models.Model):
    """
    Maps ZIP codes to Medicare locality codes.
    """
    zip_code = models.CharField(max_length=5, primary_key=True)
    locality_code = models.CharField(max_length=3)
    state = models.CharField(max_length=2)
    carrier = models.CharField(max_length=2)
    effective_date = models.DateField()
    expiration_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'medicare_locality_map'
        verbose_name = "Medicare Locality Map"
        verbose_name_plural = "Medicare Locality Maps"

    def __str__(self):
        return f"{self.zip_code} -> {self.locality_code}"

class MedicareLocalityMeta(models.Model):
    """
    Metadata about Medicare localities.
    """
    locality_code = models.CharField(max_length=3, primary_key=True)
    locality_name = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    carrier = models.CharField(max_length=2)
    effective_date = models.DateField()
    expiration_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'medicare_locality_meta'
        verbose_name = "Medicare Locality Metadata"
        verbose_name_plural = "Medicare Locality Metadata"

    def __str__(self):
        return f"{self.locality_code} - {self.locality_name}"

class CmsGpci(models.Model):
    """
    Geographic Practice Cost Indices by locality and year.
    """
    id = models.AutoField(primary_key=True)
    locality_code = models.CharField(max_length=3)
    year = models.IntegerField()
    work_gpci = models.DecimalField(max_digits=5, decimal_places=4)
    pe_gpci = models.DecimalField(max_digits=5, decimal_places=4)
    mp_gpci = models.DecimalField(max_digits=5, decimal_places=4)
    effective_date = models.DateField()
    expiration_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'cms_gpci'
        unique_together = ('locality_code', 'year')
        verbose_name = "CMS GPCI"
        verbose_name_plural = "CMS GPCIs"

    def __str__(self):
        return f"{self.locality_code} ({self.year})"

class CmsRvu(models.Model):
    """
    Relative Value Units by procedure code and year.
    """
    id = models.AutoField(primary_key=True)
    procedure_code = models.CharField(max_length=5)
    year = models.IntegerField()
    work_rvu = models.DecimalField(max_digits=6, decimal_places=2)
    pe_rvu = models.DecimalField(max_digits=6, decimal_places=2)
    mp_rvu = models.DecimalField(max_digits=6, decimal_places=2)
    effective_date = models.DateField()
    expiration_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'cms_rvu'
        unique_together = ('procedure_code', 'year')
        verbose_name = "CMS RVU"
        verbose_name_plural = "CMS RVUs"

    def __str__(self):
        return f"{self.procedure_code} ({self.year})"

class CmsConversionFactor(models.Model):
    """
    Yearly Medicare conversion factors.
    """
    id = models.AutoField(primary_key=True)
    year = models.IntegerField(unique=True)
    conversion_factor = models.DecimalField(max_digits=10, decimal_places=2)
    effective_date = models.DateField()
    expiration_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'cms_conversion_factor'
        verbose_name = "CMS Conversion Factor"
        verbose_name_plural = "CMS Conversion Factors"

    def __str__(self):
        return f"CF {self.year}: {self.conversion_factor}" 