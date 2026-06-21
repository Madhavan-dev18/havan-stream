from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Movie, Genre, UserProfile, Watchlist, WatchHistory

class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.genre = Genre.objects.create(name='Action')
        self.movie = Movie.objects.create(title='Test Movie', is_active=True, popularity=10.0)
        self.movie.genres.add(self.genre)
        self.profile = UserProfile.objects.create(user=self.user, name='Main Profile', is_main=True)

    def test_genre_str(self):
        self.assertEqual(str(self.genre), 'Action')

    def test_movie_str(self):
        self.assertEqual(str(self.movie), 'Test Movie')

    def test_profile_str(self):
        self.assertEqual(str(self.profile), 'testuser — Main Profile')

    def test_watchlist_creation(self):
        watchlist = Watchlist.objects.create(profile=self.profile, movie=self.movie)
        self.assertEqual(str(watchlist), 'Main Profile → Test Movie')

    def test_watchhistory_creation(self):
        history = WatchHistory.objects.create(profile=self.profile, movie=self.movie, progress_secs=120)
        self.assertEqual(str(history), 'Main Profile → Test Movie (120s)')


class APITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.profile = UserProfile.objects.create(user=self.user, name='Main Profile', is_main=True)
        self.genre = Genre.objects.create(name='Action')
        self.movie = Movie.objects.create(title='Test Movie', is_active=True, popularity=10.0, is_featured=True)
        self.movie.genres.add(self.genre)

    def authenticate(self):
        response = self.client.post('/api/login/', {'username': 'testuser', 'password': 'testpassword'})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])

    def test_register(self):
        response = self.client.post('/api/register/', {
            'username': 'newuser',
            'email': 'new@test.com',
            'password': 'newpassword123',
            'full_name': 'New User',
            'age': 25
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)

    def test_login(self):
        response = self.client.post('/api/login/', {
            'username': 'testuser',
            'password': 'testpassword'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_profile_list(self):
        self.authenticate()
        response = self.client.get('/api/profiles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_profile_create(self):
        self.authenticate()
        response = self.client.post('/api/profiles/', {'name': 'Kids Profile', 'age': 10})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserProfile.objects.filter(user=self.user).count(), 2)

    def test_movie_list(self):
        self.authenticate()
        response = self.client.get('/api/movies/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_movie_detail(self):
        self.authenticate()
        response = self.client.get(f'/api/movies/{self.movie.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Movie')

    def test_featured_movie(self):
        self.authenticate()
        response = self.client.get('/api/movies/featured/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_watchlist_add_and_list(self):
        self.authenticate()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.client.post('/api/login/', {'username': 'testuser', 'password': 'testpassword'}).data['access'], HTTP_PROFILE_ID=str(self.profile.id))
        
        # Add to watchlist
        response = self.client.post('/api/watchlist/', {'movie_id': self.movie.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # List watchlist
        response = self.client.get('/api/watchlist/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_watchhistory_update(self):
        self.authenticate()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.client.post('/api/login/', {'username': 'testuser', 'password': 'testpassword'}).data['access'], HTTP_PROFILE_ID=str(self.profile.id))
        
        # Update history
        response = self.client.post('/api/history/', {'movie_id': self.movie.id, 'progress_secs': 500, 'completed': False})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        history = WatchHistory.objects.get(profile=self.profile, movie=self.movie)
        self.assertEqual(history.progress_secs, 500)
