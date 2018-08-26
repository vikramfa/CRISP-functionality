from django.contrib.postgres.fields import JSONField
from django.db import models
from django.conf import settings
from rest_services.validators import validate_files

# Create your models here.
BATCH_STATUS_CHOICES = (
    ('DONE','DONE'),
    ('INIT','INIT'),
    ('CANCELLED','CANCELLED'),
    ('FAILED','FAILED'),
)

FORMAT_CHOICES = (
    ('C','CSV'),
    ('T','TSV'),
    ('X','XLSX'),
)

# Create your models here.

class Batch(models.Model):
    batch_id = models.AutoField("The id of the batch", primary_key=True)
    batch_name = models.CharField("The name of the batch", max_length=100)
    batch_status = models.CharField("The status of the batch", max_length=9, choices=BATCH_STATUS_CHOICES, default="INIT")
    source_file_name = models.FileField("The input source file", validators=[validate_files], upload_to='batch_files')
    total_ips = models.IntegerField("The total number of IP records", null=True)
    file_format = models.CharField("The format of the input source file", max_length=5, choices=FORMAT_CHOICES)
    user_created_by = models.CharField("The id of user who created the batch", max_length=100)
    created_at = models.DateTimeField("The timestamp when created", auto_now_add=True)
    cancelled_at = models.DateTimeField("The timestamp when cancelled", null=True)
    shodan_input_records = models.IntegerField("The total number of shodan Input records", null=True)
    shodan_processed_records = models.IntegerField("The total number of shodan Output records", null=True)
    shodan_failed_records = models.IntegerField("The total number of shodan Error records", null=True)
    shodan_records_update = models.CharField("shodan records updated or not", max_length=1, default='N')
    domainiq_input_records = models.IntegerField("The total number of domainiq Input records", null=True)
    domainiq_processed_records = models.IntegerField("The total number of domainiq Output records", null=True)
    domainiq_failed_records = models.IntegerField("The total number of domainiq Error records", null=True)
    domainiq_records_update = models.CharField("domainIQ records updated or not", max_length=1, default='N')
    censys_input_records = models.IntegerField("The total number of censys Input records", null=True)
    censys_processed_records = models.IntegerField("The total number of censys Output records", null=True)
    censys_failed_records = models.IntegerField("The total number of censys Error records", null=True)
    censys_records_update = models.CharField("censys records updated or not", max_length=1, default='N')

    class Meta:
        db_table = 'batch'

    def __str__(self):
        return "{0},{1}=> {2} at {3}".format(self.batch_id, self.user_created_by, self.source_file_name, self.batch_status)

class EmployeeAddress(models.Model):

    #stu_id = models.ForeignKey(Student, related_name='address', on_delete= models.CASCADE)
    #address_id = models.AutoField('address id', primary_key=True)
    city = models.CharField('student city',max_length=50, null=True)

    class Meta:
        db_table = 'empaddress'

class Employee(models.Model):

    #stu_id = models.AutoField('student id',primary_key=True)
    name = models.CharField('student name',max_length=50, null=True)
    marks = models.IntegerField('student marks',null=True)
    stu_add = models.OneToOneField(EmployeeAddress)

    class Meta:
        db_table = 'employee'