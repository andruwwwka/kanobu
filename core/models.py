# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.contrib.contenttypes import fields
from django.contrib.contenttypes.models import ContentType
from django.db import models


class MultiRelationModel(models.Model):
	"""Базовый класс моделей объектов, которые могут быть привязаны к любому объекту

	"""
	user = models.ForeignKey(User, verbose_name=u'Пользователь')
	content_type = models.ForeignKey(ContentType)
	object_id = models.PositiveIntegerField()
	content_object = fields.GenericForeignKey('content_type', 'object_id')

	class Meta:
		abstract = True
