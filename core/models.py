from __future__ import unicode_literals

from django.db import models


class Document(models.Model):
    description = models.CharField(max_length=255, blank=True)
    document = models.FileField(upload_to='documents/') 
    Email=models.EmailField(default='')
    uploaded_at = models.DateTimeField(auto_now_add=True) 
    file_url = models.CharField(max_length=255,blank=True) 
    password=models.CharField(max_length=16,blank=True) 
    def __str__(self):
        return "%s %s" %(self.description,self.document)
