import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from users.forms import UserRegisterForm
from users.models import Profile


# ── Form Tests ─────────────────────────────────────────────────────────────────

class TestUserRegisterForm:
    def test_valid_form_passes(self, db):
        data = {
            'username': 'newuser',
            'first_name': 'John',
            'last_name': 'Smith',
            'email': 'john@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        }
        form = UserRegisterForm(data=data)
        assert form.is_valid()

    def test_password_mismatch_fails(self, db):
        data = {
            'username': 'newuser',
            'first_name': 'John',
            'last_name': 'Smith',
            'email': 'john@example.com',
            'password1': 'StrongPass123!',
            'password2': 'DifferentPass456!',
        }
        form = UserRegisterForm(data=data)
        assert not form.is_valid()
        assert 'password2' in form.errors

    def test_missing_email_fails(self, db):
        data = {
            'username': 'newuser',
            'first_name': 'John',
            'last_name': 'Smith',
            'email': '',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        }
        form = UserRegisterForm(data=data)
        assert not form.is_valid()
        assert 'email' in form.errors

    def test_duplicate_username_fails(self, db, user):
        data = {
            'username': 'testuser',  # already exists via user fixture
            'first_name': 'Another',
            'last_name': 'Person',
            'email': 'another@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        }
        form = UserRegisterForm(data=data)
        assert not form.is_valid()
        assert 'username' in form.errors


# ── View Tests ─────────────────────────────────────────────────────────────────

class TestRegisterView:
    def test_get_returns_200(self, client):
        response = client.get(reverse('register'))
        assert response.status_code == 200

    def test_post_creates_user_and_redirects(self, client, db):
        response = client.post(reverse('register'), {
            'username': 'brandnewuser',
            'first_name': 'Brand',
            'last_name': 'New',
            'email': 'brand@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })
        assert User.objects.filter(username='brandnewuser').exists()
        assert response.status_code == 302

    def test_invalid_post_re_renders_form(self, client, db):
        response = client.post(reverse('register'), {
            'username': '',
            'email': 'not-an-email',
            'password1': 'weak',
            'password2': 'different',
        })
        assert response.status_code == 200


# ── Signal Tests ───────────────────────────────────────────────────────────────

class TestProfileSignal:
    def test_profile_auto_created_on_user_creation(self, db):
        user = User.objects.create_user(username='signaltest', password='pass123!')
        assert Profile.objects.filter(user=user).exists()

    def test_profile_has_default_image(self, db):
        user = User.objects.create_user(username='imgtest', password='pass123!')
        profile = Profile.objects.get(user=user)
        assert profile.image.name == 'default.png'

    def test_one_profile_per_user(self, db):
        user = User.objects.create_user(username='uniqueprofile', password='pass123!')
        assert Profile.objects.filter(user=user).count() == 1


# ── Profile View Tests ─────────────────────────────────────────────────────────

class TestProfileView:
    def test_redirects_anonymous_user(self, client):
        response = client.get(reverse('profile'))
        assert response.status_code == 302
        assert '/login/' in response['Location']

    def test_authenticated_user_gets_200(self, client, user):
        client.force_login(user)
        response = client.get(reverse('profile'))
        assert response.status_code == 200

    def test_update_username(self, client, user):
        client.force_login(user)
        client.post(reverse('profile'), {
            'username': 'updatedname',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'testuser@example.com',
        })
        user.refresh_from_db()
        assert user.username == 'updatedname'

    def test_update_email(self, client, user):
        client.force_login(user)
        client.post(reverse('profile'), {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'newemail@example.com',
        })
        user.refresh_from_db()
        assert user.email == 'newemail@example.com'
