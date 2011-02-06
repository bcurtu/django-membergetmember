# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.conf import settings

from datetime import datetime, timedelta
import random
import pickle
from decimal import Decimal

from mgm.managers import MemberInvitationManager, PendingConversionCreditManager, CreditManager

MGM_EXPIRATION_DAYS = getattr(settings, 'MGM_EXPIRATION_DAYS', 30) 

class MemberInvitation(models.Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    key = models.CharField(max_length=9)
    
    invitator = models.ForeignKey(User)
    
    credits_new_member = models.DecimalField(max_digits=5, decimal_places=2)
    credits_invitator = models.DecimalField(max_digits=5, decimal_places=2)
    
    redeem_on_signup = models.BooleanField(default=False) # Whether the invitator credits are converted on invitated sign up.
    
    expiration_date = models.DateTimeField()
    
    objects = MemberInvitationManager()
    
    def save(self, force_insert=False, force_update=False, using='default'):
        if not self.key:
            self.key = ''
            for i in range(6):
                self.key += random.choice('123456789ABCDEFGHIJKLMNPQRSTUVWXYZ')
        if not self.expiration_date:
            self.expiration_date = datetime.now() + timedelta(days=MGM_EXPIRATION_DAYS)
        super(MemberInvitation,self).save(force_insert, force_update, using=using)
    
class PendingConversionCredit(models.Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    
    invitator = models.ForeignKey(User, related_name='inivitator')
    user = models.ForeignKey(User, related_name='user')
    
    credits_invitator = models.DecimalField(max_digits=5, decimal_places=2)
    expiration_date = models.DateTimeField()
    
    objects = PendingConversionCreditManager()
    
class Credit(models.Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    
    user = models.ForeignKey(User)
    credits = models.DecimalField(max_digits=5, decimal_places=2)
    remaining = models.DecimalField(max_digits=5, decimal_places=2)
    expiration_date = models.DateTimeField()
    
    used_date = models.DateTimeField(null=True, blank=True)
    
    objects = CreditManager()
    
    def save(self, force_insert=False, force_update=False, using='default'):
        if force_insert or not self.id:
            self.remaining = self.credits
        super(Credit,self).save(force_insert, force_update, using=using)
