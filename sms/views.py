from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import simplejson
from datetime import datetime
import models


def status(request, sms_id):
    sms = get_object_or_404(models.SMS, pk=sms_id)
    response = { 'id': sms.id,
                 'status': { 'code': sms.status.code,
                             'text': sms.status.status,
                             'description': sms.status.description } }
    return HttpResponse(simplejson.dumps(response), 'application/json')

def callback(request):
    try:
        sms_id = int(request.GET.get('cliMsgId', None))
        timestamp = datetime.fromtimestamp(int(request.GET.get('timestamp', None)))
        code = int(request.GET.get('status', None))
    except TypeError:
        return HttpResponse('Invalid parameters.')
    
    if sms_id and timestamp and code:
        try:
            sms = models.SMS.objects.get(pk=sms_id)
        except models.SMS.DoesNotExist:
            return HttpResponse('Invalid cliMsgId.')
        status = models.Status(sms=sms, timestamp=timestamp, code=code)
        status.save()
        return HttpResponse('OK.')
    
    return HttpResponse('Missing parameter.')
