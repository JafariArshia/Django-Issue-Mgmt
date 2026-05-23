import os
import pytest
from datetime import datetime
from pathlib import Path
from django.contrib.auth.models import User
from form.models import Task, IssueTypes, DeliveryMethod, Frequency, TaskLog


@pytest.fixture(autouse=True, scope='session')
def create_default_profile_image():
    from django.conf import settings
    from PIL import Image
    media_dir = Path(settings.MEDIA_ROOT)
    media_dir.mkdir(parents=True, exist_ok=True)
    default_img = media_dir / 'default.png'
    if not default_img.exists():
        img = Image.new('RGB', (10, 10), color='white')
        img.save(str(default_img))


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username='testuser',
        password='testpass123',
        email='testuser@example.com',
        first_name='Test',
        last_name='User',
    )


@pytest.fixture
def recipient(db):
    return User.objects.create_user(
        username='recipient',
        password='testpass123',
        email='recipient@example.com',
        first_name='Jane',
        last_name='Doe',
    )


@pytest.fixture
def issue_type(db):
    return IssueTypes.objects.create(issue_type='Bug')


@pytest.fixture
def delivery_method(db):
    return DeliveryMethod.objects.create(method_name='Email')


@pytest.fixture
def frequency(db):
    return Frequency.objects.create(
        interval_type='Daily',
        interval_value=1,
        description='Once Every 1 Daily',
    )


@pytest.fixture
def task(db, recipient, issue_type, delivery_method, frequency):
    task_obj = Task.objects.create(
        subject='Fix login bug',
        content='Users cannot log in on mobile devices',
        issue_type=issue_type,
        start_date=datetime(2024, 1, 15, 9, 0),
        frequency=frequency,
        delivery_method=delivery_method,
        recipient=recipient,
        status='active',
    )
    TaskLog.objects.create(
        task_id=task_obj,
        subject=task_obj.subject,
        content=task_obj.content,
        issue_type=issue_type,
        frequency=frequency,
        delivery_method=delivery_method,
        recipient=recipient,
        sent_date_time=datetime(2024, 1, 15, 10, 0),
    )
    return task_obj
