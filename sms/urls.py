from django.conf.urls import patterns, include, url

urlpatterns = patterns('sms.views',
    url(r'^status/(?P<sms_id>\d+)/$', 'status', {}, 'sms_callback'),
    url(r'^callback$', 'callback', {}, 'sms_callback'),
)
