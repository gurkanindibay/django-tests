from django.db import models
from sweet_shared.models import SweetType
# Create your models here.
class Sweet(models.Model):
    name = models.CharField(max_length=100)

    sweet_type = models.ForeignKey(SweetType, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
