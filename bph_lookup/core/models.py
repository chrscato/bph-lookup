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
        db_table = 'state'
        verbose_name = "State"
        verbose_name_plural = "States"

    def __str__(self):
        return f"{self.state_name} ({self.state_code})"

class Region(models.Model):
    """
    Maps a region to a state, such as a locality or carrier area.
    """
    region_id = models.AutoField(primary_key=True)
    state_code = models.CharField(max_length=2)  # Changed from ForeignKey to CharField
    region_type = models.CharField(max_length=50)
    region_code = models.CharField(max_length=50)
    region_name = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'region'
        unique_together = ('state_code', 'region_type', 'region_code')
        verbose_name = "Region"
        verbose_name_plural = "Regions"

    def __str__(self):
        return f"{self.state_code}-{self.region_code} ({self.region_name})"

class ProcedureCode(models.Model):
    """
    CPT, HCPCS, or DRG code and its metadata.
    """
    procedure_code = models.CharField(max_length=20, primary_key=True)
    description = models.TextField()
    code_type = models.CharField(max_length=10)
    category = models.CharField(max_length=50, null=True, blank=True)
    subcategory = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'procedure_code'

    def __str__(self):
        return self.procedure_code

class FeeSchedule(models.Model):
    id = models.AutoField(primary_key=True)
    state_code = models.CharField(max_length=2)  # Changed from ForeignKey to CharField
    schedule_type = models.CharField(max_length=50)
    effective_date = models.DateField()
    expiration_date = models.DateField(null=True, blank=True)
    conversion_factor = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'fee_schedule'

    def __str__(self):
        return f"{self.state_code} {self.schedule_type} ({self.effective_date})"

class FeeScheduleRate(models.Model):
    id = models.AutoField(primary_key=True)
    fee_schedule_id = models.IntegerField()  # Changed from ForeignKey to IntegerField
    procedure_code = models.CharField(max_length=20)  # Changed from ForeignKey to CharField
    modifier = models.CharField(max_length=5, null=True, blank=True, default=None)
    region_id = models.IntegerField(null=True, blank=True)  # Changed from ForeignKey to IntegerField
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
        db_table = 'fee_schedule_rate'
        unique_together = ('fee_schedule_id', 'procedure_code', 'modifier', 'region_id')

    def __str__(self):
        return f"{self.procedure_code} {self.modifier or ''} {self.region_id or ''}: {self.rate}"

class MedicareLocalityMap(models.Model):
    """
    Maps ZIP codes to Medicare locality codes.
    """
    zip_code = models.CharField(max_length=5, primary_key=True)
    state_code = models.CharField(max_length=2)  # Changed from 'state' to match your DB
    carrier_code = models.CharField(max_length=2)  # Changed from 'carrier' to match your DB
    locality_code = models.CharField(max_length=3)
    year_qtr = models.CharField(max_length=10)  # Added to match your DB

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
    mac_code = models.CharField(max_length=10)  # Changed from locality_code primary key
    locality_code = models.CharField(max_length=3)
    state_name = models.CharField(max_length=100)  # Changed from locality_name
    fee_schedule_area = models.CharField(max_length=100)  # Added to match your DB
    counties = models.TextField(null=True, blank=True)  # Added to match your DB

    class Meta:
        db_table = 'medicare_locality_meta'
        verbose_name = "Medicare Locality Metadata"
        verbose_name_plural = "Medicare Locality Metadata"

    def __str__(self):
        return f"{self.locality_code} - {self.state_name}"

class CmsGpci(models.Model):
    """
    Geographic Practice Cost Indices by locality and year.
    """
    locality_code = models.CharField(max_length=3)
    year = models.IntegerField()
    work_gpci = models.DecimalField(max_digits=5, decimal_places=4)
    pe_gpci = models.DecimalField(max_digits=5, decimal_places=4)
    mp_gpci = models.DecimalField(max_digits=5, decimal_places=4)
    locality_name = models.CharField(max_length=100, null=True, blank=True)  # Added to match your DB

    class Meta:
        db_table = 'cms_gpci'
        verbose_name = "CMS GPCI"
        verbose_name_plural = "CMS GPCIs"

    def __str__(self):
        return f"{self.locality_code} ({self.year})"

class CmsRvu(models.Model):
    """
    Relative Value Units by procedure code and year.
    """
    procedure_code = models.CharField(max_length=5)
    modifier = models.CharField(max_length=5, null=True, blank=True)  # Added to match your DB
    work_rvu = models.DecimalField(max_digits=6, decimal_places=2)
    practice_expense_rvu = models.DecimalField(max_digits=6, decimal_places=2)  # Changed name to match DB
    malpractice_rvu = models.DecimalField(max_digits=6, decimal_places=2)
    total_rvu = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)  # Added to match your DB
    year = models.IntegerField()

    class Meta:
        db_table = 'cms_rvu'
        verbose_name = "CMS RVU"
        verbose_name_plural = "CMS RVUs"

    def __str__(self):
        return f"{self.procedure_code} ({self.year})"

class CmsConversionFactor(models.Model):
    """
    Yearly Medicare conversion factors.
    """
    year = models.IntegerField(primary_key=True)
    conversion_factor = models.DecimalField(max_digits=10, decimal_places=2)
    effective_date = models.DateField()
    last_updated = models.DateTimeField(auto_now=True)  # Added to match your DB

    class Meta:
        db_table = 'cms_conversion_factor'
        verbose_name = "CMS Conversion Factor"
        verbose_name_plural = "CMS Conversion Factors"

    def __str__(self):
        return f"CF {self.year}: {self.conversion_factor}"

# Additional models that exist in your database but not in Django models
class ZipCodeEnriched(models.Model):
    """
    ZIP code with geographic information.
    """
    zip_code = models.CharField(max_length=5, primary_key=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    county = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=2, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'zip_code_enriched'
        managed = False  # Tell Django not to manage this table

class CommercialRate(models.Model):
    """
    Commercial insurance rates.
    """
    id = models.AutoField(primary_key=True)
    procedure_code = models.CharField(max_length=20)
    modifier = models.CharField(max_length=5, null=True, blank=True)
    zip_code = models.CharField(max_length=10)
    provider = models.CharField(max_length=200)
    payer = models.CharField(max_length=200)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    effective_date = models.DateField()
    data_source = models.CharField(max_length=100)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'commercial_rate'
        managed = False  # Tell Django not to manage this table

class MedicareRate(models.Model):
    """
    Medicare rates by locality.
    """
    id = models.AutoField(primary_key=True)
    procedure_code = models.CharField(max_length=20)
    modifier = models.CharField(max_length=5, null=True, blank=True)
    locality_code = models.CharField(max_length=10)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    effective_date = models.DateField()
    expiration_date = models.DateField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'medicare_rate'
        managed = False  # Tell Django not to manage this table