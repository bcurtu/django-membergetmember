# -*- coding: utf-8 -*-
from django.db import models
from django.db.models import Sum
from django.conf import settings

from datetime import datetime, timedelta
from decimal import Decimal

MGM_EXPIRATION_DAYS = getattr(settings, 'MGM_EXPIRATION_DAYS', 30) 

class MemberInvitationManager(models.Manager):
    
    def convert_signup_credits(self, invitation_key, new_user):
        ''' Call this method on new user sign up end process.
        This process will check whether a cookie exists with a conversion code.
        If so, it will convert this invitation.
        If you use the middleware to track the invitation key with cookies, you can get the cookie by:
            invitation_key = pickle.loads(request.COOKIES.get(settings.MGM_COOKIE_NAME))
         '''
        from mgm.models import Credit, PendingConversionCredit, MGMLog
        try:
            invitation = self.get(key = invitation_key, expiration_date__gte=datetime.now())
        except:
            return False
        
        if invitation.convert_on_signup:
            # Create Credits for invitator if only signup is needed
            Credit.objects.create(user = invitation.invitator,
                                  credits = invitation.credits_invitator,
                                  expiration_date = datetime.now() + timedelta(days=MGM_EXPIRATION_DAYS))
        else:
            PendingConversionCredit.objects.create(invitator = invitation.invitator,
                                                   user = new_user,
                                                   credits_invitator = invitation.credits_invitator,
                                                   expiration_date = datetime.now() + timedelta(days=MGM_EXPIRATION_DAYS))
        
        # Create Credits for new member
        Credit.objects.create(user = new_user,
                              credits = invitation.credits_new_member,
                              expiration_date = datetime.now() + timedelta(days=MGM_EXPIRATION_DAYS))
        
        MGMLog.objects.create(user=new_user, invitator=invitation.invitator)
        
        return True


class PendingConversionCreditManager(models.Manager):

    def convert_conversion_credits(self, user):
        from mgm.models import Credit
        ''' Call this method on any user conversion.
        This process will check whether this user was invited by other, 
        and whether this other user had pendingconversion credits.
        If so, it will convert these credits '''
        try:
            pending = self.get(user = user, expiration_date__gte=datetime.now())
        except:
            return False
        
        Credit.objects.create(user = pending.invitator,
                              credits = pending.credits_invitator,
                              expiration_date = datetime.now() + timedelta(days=MGM_EXPIRATION_DAYS))
        pending.delete()
            
        return True
    
class CreditManager(models.Manager):
    def redeem(self, user, cost, commit=False):
        ''' Call this method twice:
        * First, to show the checkout summary, using the credits. Use commit=False
        * Second, When the user actually has paid, to redeem the credits. Use commit=True
        '''
        credits = self.filter(user=user, remaining__gt=0, expiration_date__gte=datetime.now()).order_by('expiration_date')
        for credit in credits:
            remaining = credit.remaining
            if cost>=remaining:
                cost -= credit.remaining
                credit.remaining = Decimal('0.0')
            else:
                credit.remaining -= cost
                cost = Decimal('0.0')
            if commit:
                credit.used_date = datetime.now()
                credit.save()
            if cost==Decimal('0.0'): break
        
        return cost
            
    def available(self, user):
        credits = self.filter(user=user, expiration_date__gte=datetime.now()).aggregate(Sum('remaining'))
        if not credits: return Decimal('0.0')
        return credits['remaining__sum']
    
