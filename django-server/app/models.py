from django.db import models
from django.contrib.auth.models import User


class File(models.Model):
    name = models.CharField(max_length=200)
    ftype = models.IntegerField()
    updated_date = models.DateTimeField('date updated')

    def __str__(self):
        return self.name + ' ({})'.format(self.ftype)


class CloudUser(models.Model):
    user = models.ForeignKey(User)
    files = models.ManyToManyField(File)

    def __str__(self):
        return self.user.name



