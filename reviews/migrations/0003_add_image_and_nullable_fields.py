"""Empty migration was left by mistake — provide a no-op Migration so Django
can load the migration graph. If you expect additional schema changes, replace
operations = [] with the desired operations.
"""

from django.db import migrations


class Migration(migrations.Migration):
	dependencies = [
		("reviews", "0002_alter_review_options_review_image_alter_review_email_and_more"),
	]

	operations = []
