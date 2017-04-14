from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):

	def add_arguments(self, parser):
		parser.add_argument('count_of_users', type=int)

	def handle(self, *args, **options):
		for ind in range(options.get('count_of_users')):
			username = str(ind)*8
			if not User.objects.filter(username=username).exists():
				User.objects.create_user(username, '%s@mail.ru' % username, '%spasswd' % username)