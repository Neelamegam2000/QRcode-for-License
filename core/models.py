from __future__ import unicode_literals

from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings


User = get_user_model()


class Document(models.Model):
    description = models.CharField(max_length=255,choices=(("License","License"),("Adhaar","Adhaar_card"),("Pan","Pan_card")),blank=False)
    document = models.FileField(upload_to='documents/') 
    Email=models.EmailField(default='')
    uploaded_at = models.DateTimeField(auto_now_add=True) 
    file_url = models.CharField(max_length=255,blank=True) 
    password=models.CharField(max_length=16,blank=True) 
    def __str__(self):
        return "%s %s" %(self.description,self.document)
class Userallowed(models.Model):
	name=models.CharField(max_length=100)
	email=models.EmailField(default="")
	password=models.CharField(max_length=16)
class police(models.Model):
	name=models.CharField(max_length=100)
	Email=models.EmailField(default="")
	password=models.CharField(max_length=16)
class Transaction(models.Model):
    made_by = models.ForeignKey(User, related_name='transactions', on_delete=models.CASCADE,default=True)
    made_on = models.DateTimeField(auto_now_add=True)
    amount = models.IntegerField()
    order_id = models.CharField(unique=True, max_length=100, null=True, blank=True)
    checksum = models.CharField(max_length=100, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.order_id is None and self.made_on and self.id:
            self.order_id = self.made_on.strftime('PAY2ME%Y%m%dODR') + str(self.id)
        return super().save(*args, **kwargs)
