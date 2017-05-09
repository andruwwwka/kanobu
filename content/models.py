# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.contrib.contenttypes import fields
from django.contrib.contenttypes.models import ContentType
from django.db import models

from comments.models import Comment, CanCommentMixin
from votes.models import CanVoteMixin, Rating


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
	comments = fields.GenericRelation(Comment, related_query_name='news_comment')
	votes = fields.GenericRelation(Rating, related_query_name='news_vote')


class Article(ContentObject):
	"""Модель статьи

	"""
	comments = fields.GenericRelation(Comment, related_query_name='article_comment')
	votes = fields.GenericRelation(Rating, related_query_name='article_vote')
