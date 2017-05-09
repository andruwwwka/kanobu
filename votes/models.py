# -*- coding: utf-8 -*-
from django.db import models

from core.models import MultiRelationModel


class CanVoteMixin(models.Model):
	"""Миксин для моделей объектов, за которые пользователь может проголосовать

	"""

	class Meta:
		abstract = True

	def vote(self, user, mark):
		"""Добавление голоса к материалу

		Если пользователь повторно ставит оценку, то это считается сбросом оценки пользователя. Если же он ставит
		противоположную оценку, то предыдущая сбрасывается и устанавливается актуальная
		:param user: проголосовавший пользователь
		:param mark: оценка пользователя
		:return: True
		"""
		if self.votes.filter(user=user, mark=mark).exists():
			self.votes.get(user=user, mark=mark).delete()
		else:
			if self.votes.filter(user=user).exists():
				self.votes.get(user=user).delete()
			Rating.objects.create(user=user, mark=mark, content_object=self)
		return True

	@property
	def count_of_pluses(self):
		"""Получение количества положительных голосов

		:return: положительные голоса
		"""
		pluses_count = self.votes.filter(mark=True).count()
		return pluses_count

	@property
	def count_of_minuses(self):
		"""Количество отрицательных голосов

		:return: отрицательные голоса
		"""
		minuses_count = self.votes.filter(mark=False).count()
		return minuses_count

	@property
	def votes_count(self):
		"""Общее количество голосов

		:return: количество голосов
		"""
		votes_count = self.votes.count()
		return votes_count


class Rating(MultiRelationModel):
	"""Модель оценки

	"""
	mark = models.BooleanField(u'Оценка')
