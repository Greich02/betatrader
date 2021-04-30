from django.db import models


class Order(models.Model):
    name = models.CharField(max_length=50, null=False)
    email = models.EmailField()
    plan = models.CharField(max_length=50, null=False)
    pmethod = models.CharField(max_length=50, null=False)
    coupon = models.CharField(max_length=50, null=True)
    amount = models.CharField(max_length=50, null=True)
    affiliate = models.ForeignKey(
        'Partner',  on_delete=models.DO_NOTHING, default=False, null=True, blank=True)

    def __str__(self):
        return self.name


class Partner(models.Model):
    name = name = models.CharField(max_length=50)
    email = models.EmailField()
    username = models.CharField(max_length=50, null=False)
    password = models.CharField(max_length=50, null=False)
    totalEarned = models.FloatField(default=0, null=True, blank=True)
    balance = models.FloatField(default=0, null=True, blank=True)
    totalWithdraw = models.FloatField(default=0, null=True, blank=True)
    totalSales = models.IntegerField(default=0, null=True, blank=True)

    def __str__(self):
        return self.name


class Voucher(models.Model):
    name = models.CharField(max_length=50)
    discount = models.FloatField()
    expireDate = models.DateField()

    def __str__(self):
        return self.name


class Plan(models.Model):
    name = models.CharField(max_length=50)
    price = models.FloatField()

    def __str__(self):
        return self.name
