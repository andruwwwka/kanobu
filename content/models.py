# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.contrib.contenttypes import fields
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone


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
		content_type = ContentType.objects.get_for_model(type(self))
		if Rating.objects.filter(user=user, mark=mark, object_id=self.id, content_type=content_type).exists():
			Rating.objects.get(user=user, mark=mark, object_id=self.id, content_type=content_type).delete()
		else:
			if Rating.objects.filter(user=user, object_id=self.id, content_type=content_type).exists():
				Rating.objects.get(user=user, object_id=self.id, content_type=content_type).delete()
			Rating.objects.create(user=user, mark=mark, content_object=self)
		return True

	@property
	def count_of_pluses(self):
		"""Получение количества положительных голосов

		:return: положительные голоса
		"""
		content_type = ContentType.objects.get_for_model(type(self))
		pluses_count = Rating.objects.filter(mark=True, object_id=self.id, content_type=content_type).exists()
		return pluses_count

	@property
	def count_of_minuses(self):
		"""Количество отрицательных голосов

		:return: отрицательные голоса
		"""
		content_type = ContentType.objects.get_for_model(type(self))
		minuses_count = Rating.objects.filter(mark=False, object_id=self.id, content_type=content_type).exists()
		return minuses_count

	@property
	def votes_count(self):
		"""Общее количество голосов

		:return: количество голосов
		"""
		content_type = ContentType.objects.get_for_model(type(self))
		votes_count = Rating.objects.filter(object_id=self.id, content_type=content_type).exists()
		return votes_count


class MultiRelationModel(models.Model):
	"""Базовый класс моделей объектов, которые могут быть привязаны к любому объекту

	"""
	user = models.ForeignKey(User, verbose_name=u'Пользователь')
	content_type = models.ForeignKey(ContentType)
	object_id = models.PositiveIntegerField()
	content_object = fields.GenericForeignKey('content_type', 'object_id')

	class Meta:
		abstract = True


class Rating(MultiRelationModel):
	"""Модель оценки

	"""
	mark = models.BooleanField(u'Оценка')


class Comment(MultiRelationModel, CanVoteMixin):
	"""Модель комментария

	"""
	body = models.TextField(u'Текст комментария')
	add_date = models.DateTimeField(u'Дата добавления')
	vote_relation = fields.GenericRelation(Rating, related_query_name='comment_vote')


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


class ContentObject(CanCommentMixin):
	"""Базовый класс для моделей материала

	"""

	class Meta:
		abstract = True

	title = models.CharField(u'Заголовок', max_length=255)
	body = models.TextField(u'Текст')
	date_of_creation = models.DateTimeField(u'Дата создания')
	date_of_publication = models.DateTimeField(u'Дата публикации')
	author = models.ForeignKey(User, verbose_name=u'Пользователь')


class News(ContentObject):
	"""Модель новости

	"""
	comment_relation = fields.GenericRelation(Comment, related_query_name='news_comment')
	vote_relation = fields.GenericRelation(Rating, related_query_name='news_vote')


class Article(ContentObject):
	"""Модель статьи

	"""
	comment_relation = fields.GenericRelation(Comment, related_query_name='article_comment')
	vote_relation = fields.GenericRelation(Rating, related_query_name='article_vote')
