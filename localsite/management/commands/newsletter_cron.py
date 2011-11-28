from django.core.management.base import BaseCommand, CommandError
from localsite.models import Newsletter
from satchmo_ext.newsletter.models import Subscription
from mailer import send_mail, send_html_mail
from django.conf import settings

from_email = getattr(settings, "DEFAULT_FROM_EMAIL", 'test@test.com')

class Command(BaseCommand):
    def handle(self, *args, **options):
        nl = Newsletter.objects.active()
        ss = Subscription.objects.filter(subscribed=True)
        for n in nl:
            for s in ss:
                self.stdout.write('%s - %s\n' % (n.name, s.email))
                if n.content_html:
                    send_mail(n.name, n.content, from_email, [s.email])
                else:
                    send_html_mail(n.name, n.content, n.content_html, from_email, [s.email])
            n.sent = True
            n.save()
