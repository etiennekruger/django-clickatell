from django.conf import settings
from django.db import models
from urllib import urlencode
import logging
import re
import urllib2

url = "http://api.clickatell.com/http/sendmsg"
username = settings.SMS_USERNAME
password = settings.SMS_PASSWORD
api_id = settings.SMS_APIID

class ClickatellException(Exception):
    def __init__(self, err_description, err_result):
        self.err_description = err_description
        self.err_result = err_result
        super(ClickatellException, self).__init__("%s: %s" % (err_description, err_result))

class SMSException(Exception):
    pass


class Status(models.Model):
    STATUS = {
        1: 'Message unknown',
        2: 'Message queued',
        3: 'Delivered to gateway',
        4: 'Received by recipient',
        5: 'Error with message',
        6: 'User cancelled message delivery',
        7: 'Error delivering message',
        8: 'OK',
        9: 'Routing error',
        10: 'Message expired',
        11: 'Message queued for later delivery',
        12: 'Out of credit',
        14: 'Maximum MT limit exceeded',
        }
    DESCRIPTION = {
        1: 'The message ID is incorrect or reporting is delayed.',
        2: 'The message could not be delivered and has been queued for attempted redelivery.',
        3: 'Delivered to the upstream gateway or network (delivered to the recipient).',
        4: 'Confirmation of receipt on the handset of the recipient.',
        5: 'There was an error with the message, probably caused by the content of the message itself.',
        6: 'The message was terminated by a user (stop message command) or by our staff.',
        7: 'An error occurred delivering the message to the handset.',
        8: 'Message received by gateway.',
        9: 'The routing gateway or network has had an error routing the message.',
        10: 'Message has expired before we were able to deliver it to the upstream gateway. No charge applies.',
        11: 'Message has been queued at the gateway for delivery at a later time (delayed delivery).',
        12: 'The message cannot be delivered due to a lack of funds in your account. Please re-purchase credits.',
        14: 'The allowable amount for MT messaging has been exceeded.',
        }
              
    sms = models.ForeignKey('SMS')
    code = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    @property
    def status(self):
        try:
            return self.STATUS[self.code]
        except:
            return 'Unknown'
    
    @property
    def description(self):
        try:
            return self.DESCRIPTION[self.code]
        except:
            return 'There is no description for the current status.'
        
    @property
    def number(self):
        return self.sms.number
    
    def __unicode__(self):
        return u'%s' % (self.status)
    
    class Meta:
        verbose_name_plural = "Statuses"
        ordering = ('-timestamp',)


class SMS(models.Model):
    number = models.CharField(max_length=12)
    message = models.CharField(max_length=160)
    created = models.DateTimeField(auto_now_add=True)
    sent = models.BooleanField(default=False)
    
    @property
    def status(self):
        if self.status_set.count()>0:
            return self.status_set.all()[0]
        else:
            return None
    
    def send(self):
        self.save()
        try:
            params = urlencode({
                "api_id": api_id,
                "user": username,
                "password": password,
                "to" : self.number,
                "text" : self.message.encode("utf-8", "ignore"),
                "cliMsgId" : self.id,
                "callback" : "3", # enabled intermediary and final message status updates
                })
            result = urllib2.urlopen(url, params).read()
            expected = re.compile("^ID: (.*)$")
            match = expected.match(result)
            if not match:
                raise ClickatellException('Unexpected result', result)  
            self.sent = True
            self.save()
        except ClickatellException:
            logging.exception("Error occurred when sending sms: %s" % self.id)
            raise SMSException("Error occurred when sending sms - please check log.")
    
    def __unicode__(self):
        return u'%s: %s' % (self.number, self.message)
    
    class Meta:
        verbose_name = "SMS"
        verbose_name_plural = "SMSes"
        ordering = ('created',)
