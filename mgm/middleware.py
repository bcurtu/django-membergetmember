# -*- coding: utf-8 -*-
import datetime
import pickle

from django.conf import settings

class MemberGetMemberMiddleware(object):

    MGM_COOKIE_AGE = getattr(settings, 'MGM_COOKIE_AGE', 7*24*60*60) 
    MGM_PARAM_NAME = getattr(settings, 'MGM_PARAM_NAME', 'dmgm') 
    MGM_COOKIE_NAME = getattr(settings, 'MGM_COOKIE_NAME', 'dmgm') 

    def process_response(self, request, response):
        if response.status_code==200:
            dmgm = request.GET.get(self.MGM_PARAM_NAME, False)
            if dmgm:
                try:
                    response.set_cookie(key=self.MGM_COOKIE_NAME,
                                    value=pickle.dumps(dmgm),
                                    max_age=self.MGM_COOKIE_AGE,
                                    expires=datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=self.MGM_COOKIE_AGE), "%a, %d-%b-%Y %H:%M:%S GMT"))
                except:
                    pass

        return response