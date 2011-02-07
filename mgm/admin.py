from django.contrib import admin

from models import MemberInvitation, Credit, PendingConversionCredit, MGMLog


class MemberInvitationAdmin(admin.ModelAdmin):
    list_display = ('creation_date', 'key', 'invitator', 'credits_new_member', 'credits_invitator', 'convert_on_signup', 'expiration_date')
    list_filter = ('creation_date', 'expiration_date', 'convert_on_signup')
    raw_id_fields = ("invitator",)

class PendingConversionCreditAdmin(admin.ModelAdmin):
    list_display = ('creation_date', 'invitator', 'user', 'credits_invitator', 'expiration_date')
    list_filter = ('creation_date', 'expiration_date',)
    raw_id_fields = ("invitator","user")
    
class CreditAdmin(admin.ModelAdmin):
    list_display = ('creation_date', 'user', 'credits', 'expiration_date', 'remaining', 'used_date', )
    list_filter = ('creation_date', 'expiration_date','used_date')
    raw_id_fields = ("user",)

class MGMLogAdmin(admin.ModelAdmin):
    list_display = ('creation_date', 'invitator', 'user', )
    list_filter = ('creation_date', )
    raw_id_fields = ("invitator","user")
    
admin.site.register(MemberInvitation, MemberInvitationAdmin)
admin.site.register(PendingConversionCredit, PendingConversionCreditAdmin)
admin.site.register(Credit, CreditAdmin)
admin.site.register(MGMLog, MGMLogAdmin)
