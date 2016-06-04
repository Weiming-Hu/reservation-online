from django.test import TestCase, Client
from django.contrib.auth import authenticate
from django.core.urlresolvers import reverse

from django.contrib.auth.models import User
from .views import check_reservation_time
from .models import Record

import datetime


class UserMethodTest(TestCase):
    def test_create_new_user(self):
        """
        This will create a new user with the formal way, properly providing all the information.
        And then you are able to log in.
        """
        # create a new user
        username, password, nickname, emailadd = (
            "test_user_1", "test_user_1@reservations", "Test User 1", "testuser1@sina.com")
        user = User.objects.create_user(username, emailadd, password, last_name=nickname)
        self.assertEqual(1, len(User.objects.all()))
        
        # log in
        user = authenticate(username=username, password=password)
        self.assertEqual(user.is_active, True)
    
    def test_delete_existed_users(self):
        """
        This will create two users, and then delete one of then
        """
        # create users
        username, password, nickname, emailadd = ( 
            "test_user_1", "test_user_1@reservations", "Test User 1", "testuser1@sina.com")
        user1 = User.objects.create_user(username, emailadd, password, last_name=nickname)
        username, password, nickname, emailadd = (
            "test_user_2", "test_user_2@reservations", "Test User 2", "testuser2@sina.com")
        user2 = User.objects.create_user(username, emailadd, password, last_name=nickname)
        self.assertEqual(2, len(User.objects.all()))
        
        # delete one of them
        user_del = User.objects.filter(username=username)
        user_del.delete()
        self.assertEqual(1, len(User.objects.all()))
        

class ReservationMethodTest(TestCase):
    
    # This function set up the test data
    # set cls.xxxx and then you can refer to it by using self.xxxx
    # https://docs.djangoproject.com/en/1.9/topics/testing/tools/#django.test.TestCase
    @classmethod
    def setUpTestData(cls):
        username, password, nickname, emailadd = ( 
                "test_user_3", "test_user@reservations_3", "Test User 3", "testuser3@sina.com")
        cls.user_in_class = User.objects.create_user(username, emailadd, password, last_name=nickname)
        now_time = datetime.datetime.now()
        cls.ini_time = datetime.datetime(
            now_time.year, now_time.month, now_time.day, 12, 0, 0)+datetime.timedelta(days=1)
    
    def test_create_new_record(self):
        """
        This will create a new reservation record with proper information
        """
        record = Record.objects.create(user=self.user_in_class,
                                       start_time=self.ini_time,
                                       end_time=self.ini_time + datetime.timedelta(hours=2))
        self.assertEqual(len(Record.objects.all()), 1)
    
    def test_create_two_new_record(self):
        """
        This will create a record and then another one
        """
        record1 = Record.objects.create(user=self.user_in_class,
                                        start_time=self.ini_time,
                                        end_time=self.ini_time + datetime.timedelta(hours=2))
        if check_reservation_time(self.ini_time + datetime.timedelta(hours=2),
                                  self.ini_time + datetime.timedelta(hours=4))[0]:
            record2 = Record.objects.create(user=self.user_in_class,
                                            start_time=self.ini_time + datetime.timedelta(hours=2),
                                            end_time=self.ini_time + datetime.timedelta(hours=4))
        self.assertEqual(len(Record.objects.all()), 2)
    
    def test_create_new_record_lasting_more_than_3_hours(self):
        """
        This will create a record that lasts for longer than 3 hours
        """
        if check_reservation_time(self.ini_time,
                                  end_time=self.ini_time + datetime.timedelta(hours=3, minutes=20))[0]:
            record = Record.objects.create(user=self.user_in_class,
                                           start_time=self.ini_time,
                                           end_time=self.ini_time + datetime.timedelta(hours=3, mintes=20))
        self.assertEqual(len(Record.objects.all()), 0)
    
    def test_create_new_record_that_overlaps_the_existed(self):
        """
        This will create a record and then another one that overlaps with the existed
        """
        record1 = Record.objects.create(user=self.user_in_class,
                                        start_time=self.ini_time,
                                        end_time=self.ini_time + datetime.timedelta(hours=2))
        if check_reservation_time(self.ini_time + datetime.timedelta(hours=1),
                                  self.ini_time + datetime.timedelta(hours=4))[0]:
            record2 = Record.objects.create(user=self.user_in_class,
                                            start_time=self.ini_time + datetime.timedelta(hours=2),
                                            end_time=self.ini_time + datetime.timedelta(hours=4))
        self.assertEqual(len(Record.objects.all()), 1)
    
    def test_create_new_record_that_contains_the_existed(self):
        """
        This will create a record and then another one that contains the former record
        """
        record1 = Record.objects.create(user=self.user_in_class,
                                        start_time=self.ini_time + datetime.timedelta(hours=1),
                                        end_time=self.ini_time + datetime.timedelta(hours=2))
        if check_reservation_time(self.ini_time,
                                  self.ini_time + datetime.timedelta(hours=3))[0]:
            record2 = Record.objects.create(user=self.user_in_class,
                                            start_time=self.ini_time,
                                            end_time=self.ini_time + datetime.timedelta(hours=3))
        self.assertEqual(len(Record.objects.all()), 1)
    
    def test_create_new_record_that_is_contained_by_the_existed(self):
        """
        This will create a record and then another one that is contained by the former record
        """
        record1 = Record.objects.create(user=self.user_in_class,
                                        start_time=self.ini_time,
                                        end_time=self.ini_time + datetime.timedelta(hours=3))
        if check_reservation_time(self.ini_time + datetime.timedelta(hours=1),
                                  self.ini_time + datetime.timedelta(hours=2))[0]:
            record2 = Record.objects.create(user=self.user_in_class,
                                            start_time=self.ini_time + datetime.timedelta(hours=1),
                                            end_time=self.ini_time + datetime.timedelta(hours=2))
        self.assertEqual(len(Record.objects.all()), 1)
    
    def test_create_new_record_for_the_past(self):
        if check_reservation_time(datetime.datetime.now() - datetime.timedelta(days=1),
                                  datetime.datetime.now() - datetime.timedelta(days=1) + datetime.timedelta(hours=2))[0]:
            record2 = Record.objects.create(user=self.user_in_class,
                                            start_time=datetime.datetime.now() - datetime.timedelta(days=1),
                                            end_time=datetime.datetime.now() - datetime.timedelta(days=1) + datetime.timedelta(hours=2))
        self.assertEqual(len(Record.objects.all()), 0)
    
    def test_create_new_record_for_two_weeks_later(self):
        if check_reservation_time(self.ini_time + datetime.timedelta(days=16),
                                  self.ini_time + datetime.timedelta(days=16, hours=2))[0]:
            record2 = Record.objects.create(user=self.user_in_class,
                                            start_time=self.ini_time + datetime.timedelta(days=16),
                                            end_time=self.ini_time + datetime.timedelta(days=16, hours=2))
        self.assertEqual(len(Record.objects.all()), 0)
    

class ReservationsViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # create two users
        username, password, nickname, emailadd = ( 
                "test_user_4", "test_user_4@reservations", "Test User 4", "testuser4@sina.com")
        user1 = User.objects.create_user(username, emailadd, password, last_name=nickname)
        username, password, nickname, emailadd = ( 
                "test_user_5", "test_user_5@reservations", "Test User 5", "testuser5@sina.com")
        user2 = User.objects.create_user(username, emailadd, password, last_name=nickname)
        now_time = datetime.datetime.now()
        ini_time = datetime.datetime(
            now_time.year, now_time.month, now_time.day, 8, 0, 0)+datetime.timedelta(days=1)
        
        # create records
        for i in range(10):
            Record.objects.create(user=user1,
                                  start_time=ini_time + datetime.timedelta(hours=i),
                                  end_time=ini_time + datetime.timedelta(hours=i+1))
        for i in range(10):
            Record.objects.create(user=user2,
                                  start_time=ini_time + datetime.timedelta(days=7, hours=i),
                                  end_time=ini_time + datetime.timedelta(days=7, hours=i+1))        
        # set initial time
        cls.ini_time = datetime.datetime(
            now_time.year, now_time.month, now_time.day, 12, 0, 0)+datetime.timedelta(days=1)
    
    def test_welcome_guest(self):
        """
        when visiting as a guest, you get all the records for this week and the next week are shown
        """
        response = self.client.get(reverse('reservations:index'))
        self.assertEqual(response.context["status"], False)
        self.assertEqual(len(response.context["this_week_past"]) + 
                         len(response.context["this_week_future"]) + 
                         len(response.context["next_week"]), 20)
    
    def test_welcome_user(self):
        """
        when visiting as a logged-in user, you get the same records as the above, plus special greeting information
        """
        c = Client()
        # one way to log in
        response = c.post('/reservations/auth/login/', # the url should be strict
                          {'username': 'test_user_4', 'password': 'test_user_4@reservations'})
        self.assertEqual(response.status_code, 302)
        response = c.get('/reservations/')
        self.assertEqual(response.context["status"], True)
        
    
    def test_user_cancle_reservation(self):
        """
        cancle reservation after log in
        """
        c = Client()
        # another way to log in
        c.login(username='test_user_4', password='test_user_4@reservations')
        response = c.get('/reservations/cancle/')
        self.assertEqual(len(response.context["available_records"]), 10)
        response = c.post('/reservations/cancle/submit/',
                          {'checkbox_list': [r.id for r in Record.objects.all()[:4]]})
        response = c.get('/reservations/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["this_week_past"]) + 
                         len(response.context["this_week_future"]) + 
                         len(response.context["next_week"]), 16)