from django.core.management.base import BaseCommand, CommandError
from sms import models

class Command(BaseCommand):
    args = 'None'
    help = 'Sends all unsent SMSes.'

    def handle(self, *args, **options):
        smses = models.SMS.objects.filter(sent=False)
        sent = 0
        for sms in smses:
            try:
                sms.send()
                sent += 1
            except models.SMSException:
                self.stdout.write('Failed to send SMS with id %d.\n' % sms.id)
        self.stdout.write('Succesfully sent %d SMSes.\n' % sent)
