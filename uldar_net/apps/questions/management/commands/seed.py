import os

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.comments.models import Comments
from apps.questions.models import Question
from apps.tags.models import Tag
from apps.users.models import CustomUser


class Command(BaseCommand):
    help = 'Seed the database with sample'

    def handle(self, *args, **options):
        users = []
        emails = ["new1234@gmail.com", "real1234@gmail.com", "test1234@gmail.com"]
        for i, email in enumerate(emails):
            user = CustomUser.objects.create(email=email, password="default123")
            user.save()
            print(f"New user {email}")

            users.append(user)

        tag_names = ["python", "django", "celery", "docker", "redis"]
        tags = []
        for name in tag_names:
            tag = Tag.objects.create(name=name, slug=slugify(name))
            tags.append(tag)

        q1 = Question.objects.create(
            title="Set up celery",
            description="Backend background tasks. How to do them",
            author=users[0],
            slug="how-to-set-up-celery12",
        )
        q1.tag.add(tags[0], tags[1], tags[2])

        q2 = Question.objects.create(
            title="Docker. How to configure",
            description="How to create dockerfiles",
            author=users[1],
            slug="how-to-set-up-docker12",
        )
        q2.tag.add(tags[0], tags[1], tags[2])

        q3 = Question.objects.create(
            title="Redis. How to configure",
            description="Redis connection",
            author=users[2],
            slug="how-to-set-up-redis12",
        )
        q3.tag.add(tags[0], tags[1], tags[3])

        c1 = Comments.objects.create(
            question=q1,
            author=users[1],
            body="Do not know"
        )
        c2 = Comments.objects.create(
            question=q2,
            author=users[3],
            body="Do not know"
        )
        c3 = Comments.objects.create(
            question=q3,
            author=users[2],
            body="Do not know"
        )



        # Flush all data from the database without confirmation
        os.system("python manage.py flush --noinput")

        # Recheck and apply any pending migrations
        os.system("python manage.py makemigrations")
        os.system("python manage.py migrate")
