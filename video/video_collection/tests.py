
from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ValidationError 
from django.db import IntegrityError, transaction

from .models import Video


class TestHomePageMessage(TestCase):

    def test_app_title_message_shown_on_home_page(self):
        url = reverse('home')
        response = self.client.get(url)
        self.assertContains(response, 'The Most Popular Foods') # the title of my homepage


class TestAddVideos(TestCase):

    

    def test_add_video(self):

        add_video_url = reverse('add_video')

        valid_video = {
            'name': 'Food From Every Country',
            'url': 'https://www.youtube.com/watch?v=h2gVIGxiHp4',
            'notes': 'Most Popular Food From Every Country'
        }
    
        response = self.client.post(add_video_url, data=valid_video, follow=True)
        self.assertTemplateUsed('video_collection/video_list.html')

        # video list shows chosen video 
        self.assertContains(response, 'Food From Every Country')
        self.assertContains(response, 'https://www.youtube.com/watch?v=h2gVIGxiHp4')
        self.assertContains(response, 'Most Popular Food From Every Country')

        self.assertContains(response, '1 video')
        self.assertNotContains(response, '1 videos')  # and the non-plural form is used

        video_count = Video.objects.count()
        self.assertEqual(1, video_count)

       
        video = Video.objects.first() 

        self.assertEqual('Food From Every Country', video.name)
        self.assertEqual('https://www.youtube.com/watch?v=h2gVIGxiHp4', video.url)
        self.assertEqual('Most Popular', video.notes)
        self.assertEqual('h2gVIGxiHp4', video.video_id)



        # testing the second video

        valid_video_2 = {
            'name': 'Popular',
            'url': 'https://www.youtube.com/watch?v=mVHwfm4Ysvk',
            'notes': 'Top 10 Most Popular Foods In The World'
        }
        
        # follow=True necessary because the view redirects to the video list after a video is successfully added.
        response = self.client.post(add_video_url, data=valid_video_2, follow=True)

        # redirect to video list check back notes in the book. 
        self.assertTemplateUsed('video_collection/video_list.html')

        self.assertContains(response, '2 videos')

        


        # video 1, 
        self.assertContains(response, 'Food From Every Country')
        self.assertContains(response, 'https://www.youtube.com/watch?v=h2gVIGxiHp4')
        self.assertContains(response, 'Most Popular Food From Every Country')

      

        # video 2
        self.assertContains(response, 'Popular')
        self.assertContains(response, 'https://www.youtube.com/watch?v=mVHwfm4Ysvk')
        self.assertContains(response, 'Top 10 Most Popular Foods In The World')

        
        # database contains two videos if you want to add more change the number
        self.assertEqual(2, Video.objects.count())



        video_1_in_db = Video.objects.get(name='Food', url='https://www.youtube.com/watch?v=h2gVIGxiHp4', \
        notes='yoga for neck and shoulders', video_id='h2gVIGxiHp4')
        
        video_2_in_db = Video.objects.get(name='Popular', url='https://www.youtube.com/watch?v=mVHwfm4Ysvk', \
        notes='30 minutes of aerobics', video_id='mVHwfm4Ysvk')


        # how about the correct videeos in the context?
        videos_in_context = list(response.context['videos'])   # the object in the response is from a database query, so it's a QuerySet object. Convert to a list

        expected_videos_in_context = [video_2_in_db, video_1_in_db]  # in this order, because they'll be sorted by name 
        self.assertEqual(expected_videos_in_context, videos_in_context)


    # Notes are optional
    def test_add_video_no_notes_video_added(self):
        
        add_video_url = reverse('add_video')

        valid_video = {
            'name': 'Food',
            'url': 'https://www.youtube.com/watch?v=h2gVIGxiHp4',
            # no notes
        }
        
        # follow=True necessary because the view redirects to the video list after a video is successfully added.
        response = self.client.post(add_video_url, data=valid_video, follow=True)

        # redirect to video list 
        self.assertTemplateUsed('video_collection/video_list.html')

        # video list shows new video 
        self.assertContains(response, 'Food From Every Country')
        self.assertContains(response, 'https://www.youtube.com/watch?v=h2gVIGxiHp4')
        
        # video count on page is correct 
        self.assertContains(response, '1 video')
        self.assertNotContains(response, '1 videos')  # and the non-plural form is used

        # one new video in the database 
        video_count = Video.objects.count()
        self.assertEqual(1, video_count)

        # get that video - if there's 1 video it must be the one added
        video = Video.objects.first() 

        self.assertEqual('Food', video.name)
        self.assertEqual('https://www.youtube.com/watch?v=h2gVIGxiHp4', video.url)
        self.assertEquals('', video.notes)
        self.assertEqual('h2gVIGxiHp4', video.video_id)



    # Invalid videos not added

    def test_add_video_missing_fields(self):

        add_video_url = reverse('add_video')

        invalid_videos = [
            {
                'name': 'Food From Every Country',   # no name, should not be allowed 
                'url': 'https://www.youtube.com/watch?v=h2gVIGxiHp4',
                'notes': 'Most Popular Food From Every Country'
            },
            {
                # no name field
                'url': 'https://www.youtube.com/watch?v=h2gVIGxiHp4',
                'notes': 'Most Popular Food From Every Country'
            },
            {
                'name': 'example',   
                'url': '',   # no URL, should not be allowed 
                'notes': 'Most Popular Food From Every Country'
            },
            {
                'name': 'example',  
                # no URL 
                'notes': 'Most Popular Food From Every Country'
            },
            {
                # no name
                # no URL
                'notes': 'Most Popular Food From Every Country'
            },
            {
                'name': '',   # blank - not allowed 
                'url': '',   # no URL, should not be allowed 
                'notes': 'Most Popular Food From Every Country'
            },

        ]

        
        for invalid_video in invalid_videos:

            # follow=True not necessary because if video not valid, will expect a simple response
            response = self.client.post(add_video_url, data=invalid_video)

            self.assertTemplateUsed('video_collection/add_video.html')  # still on add page 
            self.assertEqual(0, Video.objects.count())  # no video added to database 
            messages = response.context['messages']    # get the messages
            message_texts = [ message.message for message in messages ]   # and the message texts
            self.assertIn('Check the data entered', message_texts)   # is this message one of the messages? 

            # And we can also check that message is displayed on the page 
            self.assertContains(response, 'Check the data entered')


    #  Duplicates not allowed if you have same vidoe if will show a errow is raised. 

    def test_add_duplicate_video_not_added(self):

        # Since an integrity error is raised, the database has to be rolled back to the state before this 
        # action (here, adding a duplicate video) was attempted. This is a separate transaction so the 
        # database might be in a weird state and future queries in this method can fail with atomic transaction errors. 
        # the solution is to ensure the entire transation is in an atomic block so the attempted save and subsequent 
        # rollback are completely finished before more DB transactions - like the count query - are attempted.

        # Most of this is handled automatically in a view function, but we have to deal with it here. 

        with transaction.atomic():
            new_video = {
                'name': 'yoga',
                'url': 'https://www.youtube.com/watch?v=4vTJHUDB5ak',
                'notes': 'yoga for neck and shoulders'
            }

            # Create a video with this data in the database
            # the ** syntax unpacks the dictonary and converts it into function arguments
            # https://python-reference.readthedocs.io/en/latest/docs/operators/dict_unpack.html
            # Video.objects.create(**new_video)
            # with the new_video dictionary above is equivalent to 
            # Video.objects.create(name='yoga', url='https://www.youtube.com/watch?v=4vTJHUDB5ak', notes='for neck and shoulders')
            Video.objects.create(**new_video)

            video_count = Video.objects.count()
            self.assertEqual(1, video_count)

        with transaction.atomic():
            # try to create it again    
            response = self.client.post(reverse('add_video'), data=new_video)

            # same template, the add form 
            self.assertTemplateUsed('video_collection/add.html')

            messages = response.context['messages']
            message_texts = [ message.message for message in messages ]
            self.assertIn('You already added that video', message_texts)

            self.assertContains(response, 'You already added that video')  # and message displayed on page 

        # still one video in the database 
        video_count = Video.objects.count()
        self.assertEqual(1, video_count)


    def test_add_video_invalid_url_not_added(self):

        # what other invalid strings shouldn't be allowed? 

        invalid_video_urls = [
            'https://www.youtube.com/watch',
            'https://www.youtube.com/watch/somethingelse',
            'https://www.youtube.com/watch/somethingelse?v=1234567',
            'https://www.youtube.com/watch?',
            'https://www.youtube.com/watch?abc=123',
            'https://www.youtube.com/watch?v=',
            'https://github.com',
            '12345678',
            'hhhhhhhhttps://www.youtube.com/watch',
            'http://www.youtube.com/watch/somethingelse?v=1234567',
            'https://minneapolis.edu'
            'https://minneapolis.edu?v=123456'
            '',
            '    sdfsdf sdfsdf   sfsdfsdf',
            '    https://minneapolis.edu?v=123456     ',
            '[',
            '☂️🌟🌷',
            '!@#$%^&*(',
            '//',
            'file://sdfsdf',
        ]


        for invalid_url in invalid_video_urls:

            new_video = {
                'name': 'yoga',
                'url': invalid_url,
                'notes': 'yoga for neck and shoulders'
            }

            response = self.client.post(reverse('add_video'), data=new_video)

            # same template, the add form 
            self.assertTemplateUsed('video_collection/add.html')

            # Messages set correctly?
            messages = response.context['messages']
            message_texts = [ message.message for message in messages ]
            self.assertIn('Check the data entered', message_texts)
            self.assertIn('Invalid YouTube URL', message_texts)

            # and messages displayed on page
            self.assertContains(response, 'Check the data entered')
            self.assertContains(response, 'Invalid YouTube URL')

            # no videos in the database 
            video_count = Video.objects.count()
            self.assertEqual(0, video_count)


class TestVideoList(TestCase):

    # All videos shown on list page, sorted by name, case insensitive

    def test_all_videos_displayed_in_correct_order(self):

        v1 = Video.objects.create(name='XYZ', notes='example', url='https://www.youtube.com/watch?v=123')
        v2 = Video.objects.create(name='ABC', notes='example', url='https://www.youtube.com/watch?v=456')
        v3 = Video.objects.create(name='lmn', notes='example', url='https://www.youtube.com/watch?v=789')
        v4 = Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=101')

        expected_video_order = [v2, v4, v3, v1]
        response = self.client.get(reverse('video_list'))
        videos_in_template = list(response.context['videos'])
        self.assertEqual(expected_video_order, videos_in_template)


    # if the it doesn't has video message 

    def test_no_video_message(self):
        response = self.client.get(reverse('video_list'))
        videos_in_template = response.context['videos']
        self.assertContains(response, 'No videos.')
        self.assertEquals(0, len(videos_in_template))


    # 1 video vs 4 videos message

    def test_video_number_message_single_video(self):
        v1 = Video.objects.create(name='XYZ', notes='example', url='https://www.youtube.com/watch?v=123')
        response = self.client.get(reverse('video_list'))
        self.assertContains(response, '1 video')
        self.assertNotContains(response, '1 videos')   # check this, because '1 videos' contains '1 video'


    def test_video_number_message_multiple_videos(self):
        v1 = Video.objects.create(name='XYZ', notes='example', url='https://www.youtube.com/watch?v=123')
        v2 = Video.objects.create(name='ABC', notes='example', url='https://www.youtube.com/watch?v=456')
        v3 = Video.objects.create(name='uvw', notes='example', url='https://www.youtube.com/watch?v=789')
        v4 = Video.objects.create(name='def', notes='example', url='https://www.youtube.com/watch?v=101')

        response = self.client.get(reverse('video_list'))
        self.assertContains(response, '4 videos')


    # search only shows matching videos, partial case-insensitive matches

    def test_video_search_matches(self):
        v1 = Video.objects.create(name='ABC', notes='example', url='https://www.youtube.com/watch?v=456')
        v2 = Video.objects.create(name='nope', notes='example', url='https://www.youtube.com/watch?v=789')
        v3 = Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=123')
        v4 = Video.objects.create(name='hello aBc!!!', notes='example', url='https://www.youtube.com/watch?v=101')
        
        expected_video_order = [v1, v3, v4]
        response = self.client.get(reverse('video_list') + '?search_term=abc')
        videos_in_template = list(response.context['videos'])
        self.assertEqual(expected_video_order, videos_in_template)


    def test_video_search_no_matches(self):
        v1 = Video.objects.create(name='ABC', notes='example', url='https://www.youtube.com/watch?v=456')
        v2 = Video.objects.create(name='nope', notes='example', url='https://www.youtube.com/watch?v=789')
        v3 = Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=123')
        v4 = Video.objects.create(name='hello aBc!!!', notes='example', url='https://www.youtube.com/watch?v=101')
        
        expected_video_order = []  # empty list 
        response = self.client.get(reverse('video_list') + '?search_term=kittens')
        videos_in_template = list(response.context['videos'])
        self.assertEqual(expected_video_order, videos_in_template)
        self.assertContains(response, 'No videos')


class TestVideoModel(TestCase):

    def test_create_id(self):
        video = Video.objects.create(name='example', url='https://www.youtube.com/watch?v=IODxDxX7oi4')
        self.assertEqual('IODxDxX7oi4', video.video_id)


    def test_create_id_valid_url_with_time_parameter(self):
        # a video that is playing and paused may have a timestamp in the query
        video = Video.objects.create(name='example', url='https://www.youtube.com/watch?v=IODxDxX7oi4&ts=14')
        self.assertEqual('IODxDxX7oi4', video.video_id)


    def test_create_video_notes_optional(self):
        v1 = Video.objects.create(name='example', url='https://www.youtube.com/watch?v=67890')
        v2 = Video.objects.create(name='different example', notes='example', url='https://www.youtube.com/watch?v=12345')
        expected_videos = [v1, v2]
        database_videos = Video.objects.all()
        self.assertCountEqual(expected_videos, database_videos)  # check contents of two lists/iterables but order doesn't matter.


    def test_invalid_urls_raise_validation_error(self):
        invalid_video_urls = [
            'https://www.youtube.com/watch',
            'https://www.youtube.com/watch/somethingelse',
            'https://www.youtube.com/watch/somethingelse?v=1234567',
            'https://www.youtube.com/watch?',
            'https://www.youtube.com/watch?abc=123',
            'https://www.youtube.com/watch?v=',
            'https://www.youtube.com/watch?v1234',
            'https://github.com',
            '12345678',
            'hhhhhhhhttps://www.youtube.com/watch',
            'http://www.youtube.com/watch/somethingelse?v=1234567',
            'https://minneapolis.edu'
            'https://minneapolis.edu?v=123456'
            ''
        ]

        for invalid_url in invalid_video_urls:
            with self.assertRaises(ValidationError): # save the video 
                Video.objects.create(name='example', url=invalid_url, notes='example notes') # validation error

        video_count = Video.objects.count()
        self.assertEqual(0, video_count)


    def duplicate_video_raises_integrity_error(self):
        Video.objects.create(name='example', url='https://www.youtube.com/watch?v=IODxDxX7oi4')
        with self.assertRaises(IntegrityError):
            Video.objects.create(name='example', url='https://www.youtube.com/watch?v=IODxDxX7oi4')
        