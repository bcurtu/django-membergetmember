from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User

import pickle
from decimal import Decimal
from datetime import datetime, timedelta

from models import MemberInvitation, Credit, PendingConversionCredit, MGMLog

class MGMTest(TestCase):
    
    def test_middleware(self):
        u1 = User.objects.create_user('u1','u@dmgm.com','u1')
        invitation = MemberInvitation.objects.create(invitator=u1, 
                                        credits_new_member=Decimal('5.0'),
                                        credits_invitator=Decimal('10.0'),
                                        convert_on_signup = True
                                        )

        client = Client()
        resp = client.get('/admin/')
        self.assertFalse(resp.cookies.get('dmgm', False))
        
        resp = client.get('/admin/?dmgm=%s' % invitation.key)
        self.assertTrue(resp.cookies.get('dmgm', False))
    
    def test_convert_on_signup(self):
        u1 = User.objects.create_user('u1','u1@dmgm.com','u1')
        invitation = MemberInvitation.objects.create(invitator=u1, 
                                        credits_new_member=Decimal('5.0'),
                                        credits_invitator=Decimal('10.0'),
                                        convert_on_signup = True
                                        )
        
        u2 = User.objects.create_user('u2','u2@dmgm.com','u2')

        resp = MemberInvitation.objects.convert_signup_credits('', u2)
        self.assertFalse(resp)
        
        resp = MemberInvitation.objects.convert_signup_credits(invitation.key, u2)
        self.assertTrue(resp)
        
        credits = Credit.objects.all()
        self.assertEqual(credits.count(), 2)
        u1_credits = credits.get(user=u1)
        self.assertEqual(u1_credits.credits, 10)
        u2_credits = credits.get(user=u2)
        self.assertEqual(u2_credits.credits, 5)

        pendings = PendingConversionCredit.objects.all()
        self.assertEqual(pendings.count(), 0)
        
        log = MGMLog.objects.all()
        self.assertEqual(log.count(), 1)
        self.assertEqual(log[0].user, u2)
        self.assertEqual(log[0].invitator, u1)
        
    def test_convert_on_conversion(self):
        u1 = User.objects.create_user('u1','u1@dmgm.com','u1')
        invitation = MemberInvitation.objects.create(invitator=u1, 
                                        credits_new_member=Decimal('5.0'),
                                        credits_invitator=Decimal('10.0'),
                                        convert_on_signup = False
                                        )
        
        u2 = User.objects.create_user('u2','u2@dmgm.com','u2')
        
        resp = MemberInvitation.objects.convert_signup_credits(invitation.key, u2)
        self.assertTrue(resp)
        
        credits = Credit.objects.all()
        self.assertEqual(credits.count(), 1)
        u2_credits = credits.get(user=u2)
        self.assertEqual(u2_credits.credits, 5)
        
        pendings = PendingConversionCredit.objects.all()
        self.assertEqual(pendings.count(), 1)
        pending = pendings[0]
        self.assertEqual(pending.invitator, u1)
        self.assertEqual(pending.user, u2)
        self.assertEqual(pending.credits_invitator, 10)
        
        resp = PendingConversionCredit.objects.convert_conversion_credits(u2)
        self.assertTrue(resp)

        credits = Credit.objects.all()
        self.assertEqual(credits.count(), 2)
        u1_credits = credits.get(user=u1)
        self.assertEqual(u1_credits.credits, 10)
        u2_credits = credits.get(user=u2)
        self.assertEqual(u2_credits.credits, 5)
        
        resp = PendingConversionCredit.objects.convert_conversion_credits(u2)
        self.assertFalse(resp)
        
    def test_redeem_credits(self):
        u1 = User.objects.create_user('u1','u1@dmgm.com','u1')
        Credit.objects.create(user = u1,
                              credits = Decimal('10.0'),
                              expiration_date = datetime.now() + timedelta(days=30))
        Credit.objects.create(user = u1,
                              credits = Decimal('5.0'),
                              expiration_date = datetime.now() + timedelta(days=30))
        credits = Credit.objects.available(u1)
        self.assertEqual(credits, Decimal('15.0'))
        
        price_to_be_paid = Decimal('7.0')
        price_after_credits = Credit.objects.redeem(u1, price_to_be_paid, commit=False)
        self.assertEqual(price_after_credits, Decimal('0.0'))
        credits = Credit.objects.available(u1)
        self.assertEqual(credits, Decimal('15.0'))

        price_to_be_paid = Decimal('7.0')
        price_after_credits = Credit.objects.redeem(u1, price_to_be_paid, max_to_redeem=Decimal('5.0'), commit=False)
        self.assertEqual(price_after_credits, Decimal('2.0'))
        credits = Credit.objects.available(u1)
        self.assertEqual(credits, Decimal('15.0'))

        price_after_credits = Credit.objects.redeem(u1, price_to_be_paid, commit=True)
        self.assertEqual(price_after_credits, Decimal('0.0'))
        credits = Credit.objects.available(u1)
        self.assertEqual(credits, Decimal('8.0'))

        price_to_be_paid = Decimal('20.0')
        price_after_credits = Credit.objects.redeem(u1, price_to_be_paid, commit=True)
        self.assertEqual(price_after_credits, Decimal('12.0'))
        credits = Credit.objects.available(u1)
        self.assertEqual(credits, Decimal('0.0'))
        