from django.test import SimpleTestCase, override_settings
from django.core import mail

from utils.emails.sistema_email import _send_mail, _get_smtp_connection, _is_test_or_dev_backend


class EmailSystemTests(SimpleTestCase):
    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        DEFAULT_FROM_EMAIL="default@example.com",
        EMAIL_HOST_USER="smtpuser@example.com",
    )
    def test_send_mail_uses_locmem_backend_without_forcing_smtp(self):
        # Given locmem backend, we should not create a custom SMTP connection
        self.assertTrue(_is_test_or_dev_backend())
        self.assertIsNone(_get_smtp_connection())

        before = len(mail.outbox)
        sent = _send_mail(
            subject="Test",
            plain_message="plain",
            html_message="<b>html</b>",
            recipients=["to@example.com"],
        )
        self.assertEqual(sent, 1)
        self.assertEqual(len(mail.outbox), before + 1)
        self.assertEqual(mail.outbox[-1].from_email, "default@example.com")

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        DEFAULT_FROM_EMAIL="",
        EMAIL_HOST_USER="smtpuser@example.com",
    )
    def test_from_email_falls_back_to_email_host_user_when_default_empty(self):
        before = len(mail.outbox)
        sent = _send_mail(
            subject="Test 2",
            plain_message="plain",
            html_message="<b>html</b>",
            recipients=["to2@example.com"],
        )
        self.assertEqual(sent, 1)
        self.assertEqual(len(mail.outbox), before + 1)
        self.assertEqual(mail.outbox[-1].from_email, "smtpuser@example.com")

