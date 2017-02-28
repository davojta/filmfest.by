import logging

from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import translation
from django.template import loader

from submissions.models import Submission
from celery import Task


logger = logging.getLogger('submissions.tasks')


class SendSubmissionEmail(Task):
    def create_pdf(self, submission):
        from submissions.pdf import get_submission_confirmation_report
        return get_submission_confirmation_report(submission)

    def get_email_message(self, submission):
        lang = translation.get_language().lower()
        return loader.render_to_string(
            'submissions/email/submission_%s.txt' % lang, {
                'name': submission.applicant,
                'film_title': submission.title,
            }
        )
        
    def run(self, submission):
        logger.info('SendSubmissionEmail for submission %s' % (
            submission.id
        ))
        try:
            translation.activate(submission.submission_language)

            email = EmailMessage(
                'Cinema Perpetuum Mobile 2017',
                self.get_email_message(submission),
                'no-reply@filmfest.by',
                [submission.applicant_email],
                list(settings.MAIL_BCC_LIST),
                headers = {'Reply-To': 'info@filmfest.by'})

            email.attach(
                'cpm.pdf', self.create_pdf(submission), 'application/pdf'
            )

            email.send()
        except:
            logger.exception('')
            raise
        finally:
            translation.deactivate()
            try:
                submission = Submission.objects.get(pk=submission.pk)
            except Submission.DoesNotExist:
                logger.exception('Failed to update "email sent" status')
            else:
                submission.comment_email_sent = True
                submission.save()
