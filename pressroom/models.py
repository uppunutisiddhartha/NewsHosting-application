from django.db import models
from django.contrib.auth.models import User



# Create your models here.
class reporter(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    profile_picture = models.ImageField(upload_to='reporters/', blank=True, null=True)
    idproofe=models.ImageField(upload_to='idproofs/', blank=True, null=True)

    def __str__(self):
        return self.name


class address(models.Model):
    reporter = models.ForeignKey(reporter, on_delete=models.CASCADE, related_name='addresses')
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255,blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    is_default = models.BooleanField(default=False)
 
    def __str__(self):
        return f"{self.address_line_1}, {self.city}"