from django.db import models
from django.contrib.auth.models import User
import datetime

class Dataset(models.Model):
    owner = models.ForeignKey(User, related_name="owner")
    viewers = models.ManyToManyField(User, blank=True, related_name="users")
    name = models.CharField(max_length=128)
    description = models.CharField(blank=True, max_length=256)

    def __unicode__(self):
        return self.name

class Datapoint(models.Model):
    dataset = models.ForeignKey(Dataset)
    date = models.DateField()
    value = models.IntegerField()

    class Meta:
       ordering = ['-date']

    def __unicode__(self):
        return u'%s.%s.%s : %s' % (str(self.date.day), str(self.date.month), str(self.date.year), str(self.value))

    