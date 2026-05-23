import pytest
from datetime import datetime
from django.urls import reverse
from django.contrib.auth.models import User
from form.models import Task, IssueTypes, DeliveryMethod, Frequency, TaskDetails, TaskLog


# ── Model Tests ────────────────────────────────────────────────────────────────

class TestDeliveryMethodModel:
    def test_str_returns_method_name(self, delivery_method):
        assert str(delivery_method) == 'Email'

    def test_default_status_is_active(self, delivery_method):
        assert delivery_method.status == 'active'


class TestFrequencyModel:
    def test_str_returns_description(self, frequency):
        assert str(frequency) == 'Once Every 1 Daily'

    def test_extended_frequency_defaults_false(self, frequency):
        assert frequency.extended_frequency_boolean is False

    def test_hourly_interval_type_stored(self, db):
        freq = Frequency.objects.create(
            interval_type='Hourly',
            interval_value=2,
            description='Once Every 2 Hourly',
        )
        assert freq.interval_type == 'Hourly'
        assert freq.interval_value == 2


class TestIssueTypesModel:
    def test_str_returns_issue_type(self, issue_type):
        assert str(issue_type) == 'Bug'

    def test_default_status_is_active(self, issue_type):
        assert issue_type.status == 'active'


class TestTaskModel:
    def test_task_created_with_correct_fields(self, task, recipient):
        assert task.subject == 'Fix login bug'
        assert task.content == 'Users cannot log in on mobile devices'
        assert task.recipient == recipient

    def test_task_default_status_is_active(self, task):
        assert task.status == 'active'

    def test_task_links_to_issue_type(self, task, issue_type):
        assert task.issue_type == issue_type

    def test_task_links_to_frequency(self, task, frequency):
        assert task.frequency == frequency

    def test_task_with_optional_due_date(self, db, recipient, issue_type, delivery_method, frequency):
        task = Task.objects.create(
            subject='Task with deadline',
            content='Has a hard deadline',
            issue_type=issue_type,
            start_date=datetime(2024, 2, 1, 9, 0),
            due_date=datetime(2024, 2, 28, 17, 0),
            frequency=frequency,
            delivery_method=delivery_method,
            recipient=recipient,
        )
        assert task.due_date == datetime(2024, 2, 28, 17, 0)

    def test_task_without_due_date(self, db, recipient, issue_type, delivery_method, frequency):
        task = Task.objects.create(
            subject='Open-ended task',
            content='No deadline set',
            issue_type=issue_type,
            start_date=datetime(2024, 2, 1, 9, 0),
            frequency=frequency,
            delivery_method=delivery_method,
            recipient=recipient,
        )
        assert task.due_date is None


class TestTaskLogModel:
    def test_tasklog_links_to_task(self, task):
        log = TaskLog.objects.filter(task_id=task).first()
        assert log is not None
        assert log.subject == 'Fix login bug'

    def test_multiple_logs_accumulate_per_task(self, db, task, issue_type, delivery_method, frequency, recipient):
        for i in range(2):
            TaskLog.objects.create(
                task_id=task,
                subject=task.subject,
                content=task.content,
                issue_type=issue_type,
                frequency=frequency,
                delivery_method=delivery_method,
                recipient=recipient,
                sent_date_time=datetime(2024, 1, 16 + i, 10, 0),
            )
        assert TaskLog.objects.filter(task_id=task).count() == 3


class TestTaskDetailsModel:
    def test_comment_links_to_task_and_user(self, db, task, user):
        comment = TaskDetails.objects.create(
            task_id=task,
            user=user,
            comments='Looking into this now.',
            status='active',
        )
        assert comment.task_id == task
        assert comment.user == user
        assert comment.comments == 'Looking into this now.'

    def test_multiple_users_can_comment(self, db, task, user, recipient):
        TaskDetails.objects.create(task_id=task, user=user, comments='First comment', status='active')
        TaskDetails.objects.create(task_id=task, user=recipient, comments='Second comment', status='pending')
        assert TaskDetails.objects.filter(task_id=task).count() == 2


# ── View Tests ─────────────────────────────────────────────────────────────────

class TestHomeView:
    def test_redirects_anonymous_user(self, client):
        response = client.get(reverse('task_list'))
        assert response.status_code == 302
        assert '/login/' in response['Location']

    def test_authenticated_user_gets_200(self, client, user):
        client.force_login(user)
        response = client.get(reverse('task_list'))
        assert response.status_code == 200

    def test_tasks_appear_in_context(self, client, user, task):
        client.force_login(user)
        response = client.get(reverse('task_list'))
        assert task in response.context['tasks']

    def test_pagination_present_in_context(self, client, user):
        client.force_login(user)
        response = client.get(reverse('task_list'))
        assert 'page_obj' in response.context


class TestCreateIssueView:
    def test_redirects_anonymous_user(self, client):
        response = client.get(reverse('create_issue'))
        assert response.status_code == 302
        assert '/login/' in response['Location']

    def test_get_returns_200_with_users(self, client, user):
        client.force_login(user)
        response = client.get(reverse('create_issue'))
        assert response.status_code == 200
        assert 'users' in response.context

    def test_post_creates_task_and_tasklog(self, client, user, recipient):
        client.force_login(user)
        data = {
            'subject': 'Server downtime alert',
            'content': 'Production server is unreachable since 9am',
            'issue_type': 'Critical',
            'start_date': '2024-03-01T09:00',
            'delivery_method': 'Email',
            'interval_value': '1',
            'interval_type': 'Daily',
            'recipient': recipient.username,
            'status': 'active',
        }
        response = client.post(reverse('create_issue'), data)
        assert Task.objects.filter(subject='Server downtime alert').exists()
        assert TaskLog.objects.filter(subject='Server downtime alert').exists()
        assert response.status_code == 302

    def test_post_creates_related_lookup_records(self, client, user, recipient):
        client.force_login(user)
        data = {
            'subject': 'Database backup failure',
            'content': 'Nightly backup did not complete',
            'issue_type': 'High Priority',
            'start_date': '2024-03-05T08:00',
            'delivery_method': 'Email',
            'interval_value': '2',
            'interval_type': 'Hourly',
            'recipient': recipient.username,
            'status': 'pending',
        }
        client.post(reverse('create_issue'), data)
        assert IssueTypes.objects.filter(issue_type='High Priority').exists()
        assert Frequency.objects.filter(description='Once Every 2 Hourly').exists()


class TestUpdateIssueView:
    def test_redirects_anonymous_user(self, client, task):
        response = client.get(reverse('update_issue', kwargs={'task_id': task.pk}))
        assert response.status_code == 302

    def test_get_returns_200_with_task(self, client, user, task):
        client.force_login(user)
        response = client.get(reverse('update_issue', kwargs={'task_id': task.pk}))
        assert response.status_code == 200
        assert response.context['task'] == task

    def test_post_updates_task_fields(self, client, user, task, recipient):
        client.force_login(user)
        data = {
            'subject': 'Updated subject line',
            'content': 'Updated content after investigation',
            'issue_type': 'Bug',
            'start_date': '2024-01-15T09:00:00',
            'delivery_method': 'Email',
            'interval_value': '1',
            'interval_type': 'Daily',
            'recipient': recipient.username,
            'status': 'pending',
        }
        client.post(reverse('update_issue', kwargs={'task_id': task.pk}), data)
        task.refresh_from_db()
        assert task.subject == 'Updated subject line'
        assert task.status == 'pending'

    def test_post_appends_new_tasklog_entry(self, client, user, task, recipient):
        client.force_login(user)
        initial_count = TaskLog.objects.filter(task_id=task).count()
        data = {
            'subject': task.subject,
            'content': task.content,
            'issue_type': 'Bug',
            'start_date': '2024-01-15T09:00:00',
            'delivery_method': 'Email',
            'interval_value': '1',
            'interval_type': 'Daily',
            'recipient': recipient.username,
            'status': 'active',
        }
        client.post(reverse('update_issue', kwargs={'task_id': task.pk}), data)
        assert TaskLog.objects.filter(task_id=task).count() == initial_count + 1


class TestSearchView:
    def test_redirects_anonymous_user(self, client):
        response = client.get(reverse('search'))
        assert response.status_code == 302

    def test_search_finds_matching_task(self, client, user, task):
        client.force_login(user)
        response = client.get(reverse('search'), {'query': 'mobile'})
        assert response.status_code == 200
        assert task in response.context['results']

    def test_search_is_case_insensitive(self, client, user, task):
        client.force_login(user)
        response = client.get(reverse('search'), {'query': 'MOBILE'})
        assert task in response.context['results']

    def test_search_no_match_returns_error_message(self, client, user):
        client.force_login(user)
        response = client.get(reverse('search'), {'query': 'xyznonexistentterm'})
        assert 'Error' in response.context['message']

    def test_search_excludes_unrelated_task(self, client, user, task, db, recipient, issue_type, delivery_method, frequency):
        other_task = Task.objects.create(
            subject='Unrelated issue',
            content='Something completely different',
            issue_type=issue_type,
            start_date=datetime(2024, 3, 1, 9, 0),
            frequency=frequency,
            delivery_method=delivery_method,
            recipient=recipient,
        )
        client.force_login(user)
        response = client.get(reverse('search'), {'query': 'mobile'})
        assert other_task not in response.context['results']


class TestFilterView:
    def test_redirects_anonymous_user(self, client):
        response = client.get(reverse('filter'))
        assert response.status_code == 302

    def test_filter_by_subject_returns_matching_task(self, client, user, task):
        client.force_login(user)
        response = client.get(reverse('filter'), {
            'filters': 'subject',
            'filterInput': 'Fix login',
        })
        assert response.status_code == 200
        assert task in response.context['filtResults']

    def test_filter_empty_value_shows_error(self, client, user):
        client.force_login(user)
        response = client.get(reverse('filter'), {'filters': 'subject', 'filterInput': ''})
        assert 'Error' in response.context['message']

    def test_filter_no_params_shows_error(self, client, user):
        client.force_login(user)
        response = client.get(reverse('filter'))
        assert 'Error' in response.context['message']


class TestIssueDetailView:
    def test_detail_view_returns_200(self, client, user, task):
        client.force_login(user)
        response = client.get(reverse('task_detail', kwargs={'pk': task.pk}))
        assert response.status_code == 200

    def test_comments_included_in_context(self, client, user, task):
        TaskDetails.objects.create(task_id=task, user=user, comments='Test comment', status='active')
        client.force_login(user)
        response = client.get(reverse('task_detail', kwargs={'pk': task.pk}))
        assert response.context['cmts'].count() == 1

    def test_post_comment_creates_taskdetails_record(self, client, user, task):
        client.force_login(user)
        client.post(reverse('task_detail', kwargs={'pk': task.pk}), {
            'commentContent': 'Issue has been reproduced.',
            'commentStatus': 'active',
        })
        assert TaskDetails.objects.filter(task_id=task, comments='Issue has been reproduced.').exists()

    def test_post_comment_updates_task_status(self, client, user, task):
        client.force_login(user)
        client.post(reverse('task_detail', kwargs={'pk': task.pk}), {
            'commentContent': 'Marking as resolved.',
            'commentStatus': 'inactive',
        })
        task.refresh_from_db()
        assert task.status == 'inactive'

    def test_nonexistent_task_returns_404(self, client, user):
        client.force_login(user)
        response = client.get(reverse('task_detail', kwargs={'pk': 99999}))
        assert response.status_code == 404
