# -*- coding: utf-8 -*-
from django.contrib.contenttypes import fields
from django.db import models
from django.utils import timezone

from core.models import MultiRelationModel
from votes.models import CanVoteMixin, Rating


class Comment(MultiRelationModel, CanVoteMixin):
	"""Модель комментария

	"""
	body = models.TextField(u'Текст комментария')
	add_date = models.DateTimeField(u'Дата добавления')
	votes = fields.GenericRelation(Rating, related_query_name='comment_vote')


class CanCommentMixin(CanVoteMixin):
	"""Миксин для моделей к которым можно оставлять комментарий

	"""

	class Meta:
		abstract = True

	def comment(self, user, comment_text):
		"""Добавления комментария к материалу

		:param user: автор комментария
		:param comment_text: текст комментария
		:return: True
		"""
		Comment.objects.create(user=user, body=comment_text, add_date=timezone.now(), content_object=self)
		return True
