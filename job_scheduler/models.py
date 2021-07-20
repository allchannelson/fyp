import datetime
import requests
# dependency: pip install requests

from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator


class Worker(models.Model):
    name = models.CharField(max_length=200)

    # phone validation model derived from https://stackoverflow.com/a/19131360/3715973

    phone_regex = RegexValidator(regex=r'^\d{8}$',
                                 message="Phone number must be entered in the format: '12345678'")
    phone = models.CharField(validators=[phone_regex], max_length=8, blank=False)
    objects = models.Manager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "  Workers"


class Location(models.Model):
    name = models.CharField(max_length=250)
    address = models.CharField(null=True, blank=True, max_length=250)
    # although blank is True, it should never be blank in the DB, because the save will auto-populate from address lookup

    lat = models.DecimalField(verbose_name='Latitude', null=True, blank=True, max_digits=11, decimal_places=7)
    long = models.DecimalField(verbose_name='Longitude', null=True, blank=True, max_digits=11, decimal_places=7)
    lookup_json = models.JSONField(verbose_name='Address Lookup Result (edits will not be saved)', null=True, blank=True)
    objects = models.Manager()

    def __str__(self):
        return self.name

    # https://stackoverflow.com/a/57336548/3715973 for on-save code
    # https://simpleisbetterthancomplex.com/tutorial/2018/02/03/how-to-use-restful-apis-with-django.html for django REST API
    def save(self, *args, **kwargs):
        self.full_clean()
        # self.lookup_json = json.dumps(self.address)
        auto_address = 0
        if not self.address:
            self.address = self.name
            auto_address = 1

        url = f'https://www.als.ogcio.gov.hk/lookup?q={self.address}'
        headers = {'Accept-Encoding': 'gzip', 'Accept-Language': 'en', 'Accept': 'application/json'}
        response = requests.get(url, headers=headers)
        response_json = response.json()
        self.lookup_json = response_json
        response_address = response_json['SuggestedAddress'][0]['Address']['PremisesAddress']
        validation_score = response_json['SuggestedAddress'][0]['ValidationInformation']['Score']
        geo_info = response_address['GeospatialInformation']

        if auto_address:
            this_address = response_address['EngPremisesAddress']['EngStreet']
            this_building_no = f'{this_address.get("BuildingNoFrom", None)}'
            this_street = f'{this_address.get("StreetName", None)}'
            this_output = f'{this_building_no} {this_street}'
            this_output = this_output.strip()
            self.address = this_output

        if self.lat == 0 or not self.lat:
            self.lat = geo_info['Latitude']
        if self.long == 0 or not self.long:
            self.long = geo_info['Longitude']

        self.full_clean()  # clean a second time before saving due to auto-updated fields
        return super().save(*args, **kwargs)

    def clean(self):
        if self.name:
            self.name = self.name.strip()
        if self.address:
            self.address = self.address.strip()

    class Meta:
        verbose_name_plural = " Locations"


class Job(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.PROTECT)
    location = models.ForeignKey(Location, on_delete=models.PROTECT)
    name = models.CharField(max_length=200, unique_for_date="start_date")
    note = models.TextField(verbose_name='Notes', blank=True)
    start_date = models.DateTimeField('date start')
    end_date = models.DateTimeField('date end')
    meeting_date = models.DateTimeField(null=True, blank=True, verbose_name='Meeting Date')
    objects = models.Manager()

    def __str__(self):
        return self.name

    def was_started_recently(self):
        now = timezone.now()
        return (now - datetime.timedelta(days=2)).timestamp() <= self.start_date <= now
        # return now - datetime.timedelta(days=2).timestamp() <= self.start_date <= now # fix for PyCharm false errors

    class Meta:
        verbose_name_plural = "Jobs"
