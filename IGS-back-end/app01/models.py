from django.db import models


#
# class aigroup(models.Model):
#     name = models.CharField(max_length=100)
#     hard = models.CharField(max_length=100)
#     percent = models.FloatField(default=0)  # 或 DecimalField(max_digits=5, decimal_places=2)
#     kind = models.CharField(max_length=100)
#     content = models.CharField(max_length=500)
#     answer = models.CharField(max_length=100)
#     if_use = models.IntegerField(default=0)
#     analysis = models.CharField(max_length=500)


class UserInfo(models.Model):
    name = models.CharField(max_length=32)
    password = models.CharField(max_length=64)
    age = models.IntegerField()
