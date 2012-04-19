from django.contrib import admin
import models

class SMSAdmin(admin.ModelAdmin):
    list_display = ('number', 'message', 'created', 'sent')
    list_filter = ('sent', 'number')
    fields = ('number', 'message')
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['number', 'message']
        else:
            return []

class StatusAdmin(admin.ModelAdmin):
    list_display = ('number', 'status',)
    readonly_fields = ('sms', 'code', 'status', 'description')
    #list_filter = ('status',)

admin.site.register(models.SMS, SMSAdmin)
admin.site.register(models.Status, StatusAdmin)
