# -*- coding: utf-8 -*-
import random
import string

import pytest
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from content.models import News, Article, Comment, Rating


@pytest.yield_fixture(scope='module')
def user():
	"""Создание пользователя для тестов

	:return: пользователь
	"""
	username = '9' * 8
	_user = User.objects.create_user(username, '%s@mail.ru' % username, '%spasswd' % username)
	yield _user


@pytest.yield_fixture(scope='module')
def users_list():
	"""Создание списка пользователя для теста, где необходимо создать несколько оценок для материала

	:return: список пользователей
	"""
	username = '6' * 8
	user1 = User.objects.create_user(username, '%s@mail.ru' % username, '%spasswd' % username)
	username = '7' * 8
	user2 = User.objects.create_user(username, '%s@mail.ru' % username, '%spasswd' % username)
	username = '8' * 8
	user3 = User.objects.create_user(username, '%s@mail.ru' % username, '%spasswd' % username)
	_users_list = [user1, user2, user3]
	yield _users_list


@pytest.yield_fixture(scope='module')
def article(user):
	"""Создание статьи для тестов

	:param user: пользователь, который будет использоваться в качестве автора статьи
	:return: статья
	"""
	now = timezone.now()
	unique_title = ''.join(random.choice(string.lowercase) for _ in range(90))
	_article = Article.objects.create(
		title=unique_title,
		body='test' * 50,
		date_of_creation=now,
		date_of_publication=now,
		author=user
	)
	yield _article


@pytest.yield_fixture(scope='module')
def news(user):
	"""Создание объекта новости для тестов

	:param user: пользователь, который будет являться автором новости
	:return: новость
	"""
	now = timezone.now()
	unique_title = ''.join(random.choice(string.lowercase) for _ in range(90))
	_news = News.objects.create(
		title=unique_title,
		body='test' * 50,
		date_of_creation=now,
		date_of_publication=now,
		author=user
	)
	yield _news


@pytest.yield_fixture(scope='module')
def comment(user, news):
	"""Создание объекта комментария для теста

	:param user: пользователь, который будет являться автором комментария
	:param news: новость - материал, к которой создается комментарий
	:return: объект комментария
	"""
	comment_text = ''.join(random.choice(string.lowercase) for _ in range(90)) * 90
	_comment = Comment.objects.create(
		user=user,
		body=comment_text,
		add_date=timezone.now(),
		content_object=news
	)
	yield _comment


@pytest.mark.django_db
def test_create_news(user):
	"""Тест корректного создания новости

	:param user: автор новости
	:return: success test (True/False)
	"""
	now = timezone.now()
	unique_title = ''.join(random.choice(string.lowercase) for _ in range(90))
	News.objects.create(
		title=unique_title,
		body='test'*50,
		date_of_creation=now,
		date_of_publication=now,
		author=user
	)
	assert News.objects.filter(title=unique_title, author=user, date_of_creation=now, date_of_publication=now).exists()


@pytest.mark.django_db
def test_create_article(user):
	"""Тест создания статьи

	:param user: автор статьи
	:return: success test (True/False)
	"""
	now = timezone.now()
	unique_title = ''.join(random.choice(string.lowercase) for _ in range(90))
	Article.objects.create(
		title=unique_title,
		body='test' * 50,
		date_of_creation=now,
		date_of_publication=now,
		author=user
	)
	assert Article.objects.filter(title=unique_title, author=user, date_of_creation=now, date_of_publication=now).exists()


@pytest.mark.django_db
def test_add_comment_to_news(user, news):
	"""Тест добавления комментрия к новости

	:param user: автор комментария
	:param news: новость (материал)
	:return: success test (True/False)
	"""
	before_test_count = Comment.objects.all().count()
	comment_text = ''.join(random.choice(string.lowercase) for _ in range(90)) * 90
	news.comment(user, comment_text)
	comment_exists = Comment.objects.filter(user=user, body=comment_text, news_comment=news).exists()
	assert before_test_count + 1 == Comment.objects.all().count() and comment_exists


@pytest.mark.django_db
def test_add_comment_to_article(user, article):
	"""Тест добавления комментария к статье

	:param user: автор комментария
	:param article: статья (материал)
	:return: success test (True/False)
	"""
	before_test_count = Comment.objects.all().count()
	comment_text = ''.join(random.choice(string.lowercase) for _ in range(90)) * 90
	article.comment(user, comment_text)
	comment_exists = Comment.objects.filter(user=user, body=comment_text, article_comment=article).exists()
	assert before_test_count + 1 == Comment.objects.all().count() and comment_exists


@pytest.mark.parametrize('vote', [True, False], ids=['plus', 'minus'])
@pytest.mark.django_db
def test_add_vote_to_article(user, article, vote):
	"""Тест добавления голоса к статье (плюса, затем минуса)

	:param user: голосующий пользователь
	:param article: статья
	:param vote: оценка пользователя
	:return: success test (True/False)
	"""
	before_test_count = Rating.objects.all().count()
	article.vote(user, vote)
	content_type = ContentType.objects.get_for_model(type(article))
	vote_exists = Rating.objects.filter(user=user, mark=vote, object_id=article.id, content_type=content_type).exists()
	assert before_test_count + 1 == Rating.objects.all().count() and vote_exists


@pytest.mark.parametrize('vote', [True, False], ids=['plus', 'minus'])
@pytest.mark.django_db
def test_add_vote_to_news(user, news, vote):
	"""Тест добавления голоса к новости (плюса, затем минуса)

	:param user: проголосовавший пользователь
	:param news: новость (материал)
	:param vote: оценка пользователя
	:return: success test (True/False)
	"""
	before_test_count = Rating.objects.all().count()
	news.vote(user, vote)
	content_type = ContentType.objects.get_for_model(type(news))
	vote_exists = Rating.objects.filter(user=user, mark=vote, object_id=news.id, content_type=content_type).exists()
	assert before_test_count + 1 == Rating.objects.all().count() and vote_exists


@pytest.mark.parametrize('vote', [True, False], ids=['plus', 'minus'])
@pytest.mark.django_db
def test_add_vote_to_comment(user, comment, vote):
	"""Тест добавления голоса к комментарию (плюса, затем минуса)

	:param user: проголосовавший пользователь
	:param comment: комментарий (материал)
	:param vote: оценка пользователя
	:return: success test (True/False)
	"""
	before_test_count = Rating.objects.all().count()
	comment.vote(user, vote)
	content_type = ContentType.objects.get_for_model(type(comment))
	vote_exists = Rating.objects.filter(user=user, mark=vote, object_id=comment.id, content_type=content_type).exists()
	assert before_test_count + 1 == Rating.objects.all().count() and vote_exists


@pytest.mark.parametrize('vote', [True, False], ids=['plus', 'minus'])
@pytest.mark.django_db
def test_delete_vote_from_article(users_list, article, vote):
	"""Тест удаления голоса у статьи (плюса, затем минуса)

	:param users_list: список проголосовавших пользователей
	:param article: статья, которую пользователи оценивают
	:param vote: оценка пользователя, которая подлежит удалению
	:return: success test (True/False)
	"""
	article.vote(users_list[0], vote)
	article.vote(users_list[1], not vote)
	before_delete = Rating.objects.all().count()
	content_type = ContentType.objects.get_for_model(type(article))
	vote_exists_before_delete = Rating.objects.filter(
		user=users_list[0],
		mark=vote,
		object_id=article.id,
		content_type=content_type
	).exists()
	article.vote(users_list[0], vote)
	vote_exists_after_delete = Rating.objects.filter(
		user=users_list[0],
		mark=vote,
		object_id=article.id,
		content_type=content_type
	).exists()
	correct_exists_check = not vote_exists_after_delete and vote_exists_before_delete
	assert Rating.objects.all().count() == before_delete - 1 and correct_exists_check


@pytest.mark.parametrize('vote', [True, False], ids=['plus', 'minus'])
@pytest.mark.django_db
def test_delete_vote_from_news(users_list, news, vote):
	"""Тест удаления голоса у новости (плюса, затем минуса)

	:param users_list: список проголосовавших пользователей
	:param news: новость, которая подлежит оценке
	:param vote: оценка пользователя, которая подлежит удалению
	:return: success test (True/False)
	"""
	news.vote(users_list[0], vote)
	news.vote(users_list[1], not vote)
	before_delete = Rating.objects.all().count()
	content_type = ContentType.objects.get_for_model(type(news))
	vote_exists_before_delete = Rating.objects.filter(
		user=users_list[0],
		mark=vote,
		object_id=news.id,
		content_type=content_type
	).exists()
	news.vote(users_list[0], vote)
	vote_exists_after_delete = Rating.objects.filter(
		user=users_list[0],
		mark=vote,
		object_id=news.id,
		content_type=content_type
	).exists()
	correct_exists_check = not vote_exists_after_delete and vote_exists_before_delete
	assert Rating.objects.all().count() == before_delete - 1 and correct_exists_check


@pytest.mark.parametrize('vote', [True, False], ids=['plus', 'minus'])
@pytest.mark.django_db
def test_delete_vote_from_comment(users_list, comment, vote):
	"""Тест удаления оценки комментария (плюса, затем минуса)

	:param users_list: список проголосовавших пользователей
	:param comment: комментарий, который подлежит оценке
	:param vote: оценка пользователя, которая подлежит удалению
	:return: success test (True/False)
	"""
	comment.vote(users_list[0], vote)
	comment.vote(users_list[1], not vote)
	before_delete = Rating.objects.all().count()
	content_type = ContentType.objects.get_for_model(type(comment))
	vote_exists_before_delete = Rating.objects.filter(
		user=users_list[0],
		mark=vote,
		object_id=comment.id,
		content_type=content_type
	).exists()
	comment.vote(users_list[0], vote)
	vote_exists_after_delete = Rating.objects.filter(
		user=users_list[0],
		mark=vote,
		object_id=comment.id,
		content_type=content_type
	).exists()
	correct_exists_check = not vote_exists_after_delete and vote_exists_before_delete
	assert Rating.objects.all().count() == before_delete - 1 and correct_exists_check


@pytest.mark.parametrize(('vote', 'expected_count'), [(True, 2), (False, 2), (None, 3)], ids=['plus', 'minus', 'all'])
@pytest.mark.django_db
def test_eval_count_votes_of_article(users_list, article, vote, expected_count):
	"""Тест количества голосов у статьи (плюса, минуса, а затем общего количества)

	:param users_list: список проголосовавших пользователей
	:param article: статья, которую пользователи оценивают
	:param vote: оценка пользователя, которая подлежит подсчету
	:param expected_count: ожидаемое количество голосов
	:return: success test (True/False)
	"""
	content_type = ContentType.objects.get_for_model(type(article))
	filter_params = {
		'object_id': article.id,
		'content_type': content_type
	}
	if vote is not None:
		filter_params.update({'mark': vote})
	else:
		vote = True
	article.vote(users_list[0], vote)
	article.vote(users_list[1], not vote)
	article.vote(users_list[2], vote)
	assert Rating.objects.filter(**filter_params).count() == expected_count


@pytest.mark.parametrize(('vote', 'expected_count'), [(True, 2), (False, 2), (None, 3)], ids=['plus', 'minus', 'all'])
@pytest.mark.django_db
def test_eval_count_votes_of_news(users_list, news, vote, expected_count):
	"""Тест количества голосов у новости (плюса, минуса, а затем общего количества)

	:param users_list: список проголосовавших пользователей
	:param news: новость, которая подлежит оценке
	:param vote: оценка пользователя, которая подлежит подсчету
	:param expected_count: ожидаемое количество голосов
	:return: success test (True/False)
	"""
	content_type = ContentType.objects.get_for_model(type(news))
	filter_params = {
		'object_id': news.id,
		'content_type': content_type
	}
	if vote is not None:
		filter_params.update({'mark': vote})
	else:
		vote = True
	news.vote(users_list[0], vote)
	news.vote(users_list[1], not vote)
	news.vote(users_list[2], vote)
	assert Rating.objects.filter(**filter_params).count() == expected_count


@pytest.mark.parametrize(('vote', 'expected_count'), [(True, 2), (False, 2), (None, 3)], ids=['plus', 'minus', 'all'])
@pytest.mark.django_db
def test_eval_count_votes_of_comment(users_list, comment, vote, expected_count):
	"""Тест подсчета голосов у комментария (плюса, минуса, а затем общего количества)

	:param users_list: список проголосовавших пользователей
	:param comment: комментарий, который подлежит оценке
	:param vote: оценка пользователя, которая подлежит подсчету
	:param expected_count: ожидаемое количество голосов
	:return: success test (True/False)
	"""
	content_type = ContentType.objects.get_for_model(type(comment))
	filter_params = {
		'object_id': comment.id,
		'content_type': content_type
	}
	if vote is not None:
		filter_params.update({'mark': vote})
	else:
		vote = True
	comment.vote(users_list[0], vote)
	comment.vote(users_list[1], not vote)
	comment.vote(users_list[2], vote)
	assert Rating.objects.filter(**filter_params).count() == expected_count
