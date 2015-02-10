# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
import os.path
import json
import datetime
import unittest

from presence_analyzer import main, views, utils


TEST_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_data.csv'
)


# pylint: disable=maybe-no-member, too-many-public-methods
class PresenceAnalyzerViewsTestCase(unittest.TestCase):
    """
    Views tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})
        self.client = main.app.test_client()

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_mainpage(self):
        """
        Test main page redirect.
        """
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 302)
        assert resp.headers['Location'].endswith('/presence_weekday.html')

    def test_api_users(self):
        """
        Test users listing.
        """
        resp = self.client.get('/api/v1/users')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 2)
        self.assertDictEqual(data[0], {u'user_id': 10, u'name': u'User 10'})


    # wypociny Marcina

    def test_mean_time_weekday_view(self): 
        """
        Test mean time weekday view.
        """       
        resp = self.client.get('/api/v1/mean_time_weekday/10000')
        self.assertEqual(resp.status_code, 404)

        resp = self.client.get('/api/v1/mean_time_weekday/10')
        self.assertEqual(resp.status_code, 200)
        result = views.mean_time_weekday_view(10)
        self.assertEqual(
            result,
            [["Mon", 29934.639175257733], ["Tue", 31108.29], ["Wed", 30584.429906542056], ["Thu", 30602.904761904763], ["Fri", 29844.545454545456], ["Sat", 0], ["Sun", 0]]
        )


    def test_presence_weekday_view(self):
        """
        Test presence weekday view.
        """
        resp = self.client.get('/api/v1/presence_weekday/10000')
        self.assertEqual(resp.status_code, 404)

        resp = self.client.get('/api/v1/presence_weekday/10')
        self.assertEqual(resp.status_code, 200)
        result = views.presence_weekday_view(10)
        self.assertEqual(
            result,
            [["Weekday", "Presence (s)"], ["Mon", 2903660], ["Tue", 3110829], ["Wed", 3272534], ["Thu", 3213305], ["Fri", 2954610], ["Sat", 0], ["Sun", 0]]
        )


class PresenceAnalyzerUtilsTestCase(unittest.TestCase):
    """
    Utility functions tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_get_data(self):
        """
        Test parsing of CSV file.
        """
        data = utils.get_data()
        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [10, 11])
        sample_date = datetime.date(2013, 9, 10)
        self.assertIn(sample_date, data[10])
        self.assertItemsEqual(data[10][sample_date].keys(), ['start', 'end'])
        self.assertEqual(
            data[10][sample_date]['start'],
            datetime.time(9, 39, 5)
        )


    #  wypociny Marcina

    def test_group_by_weekday(self):
        """
        Test groups presence entries by weekday. 
        """
        a_week = {
            datetime.date(2015, 2, 2): {
                'start': datetime.time(9, 0, 0),
                'end': datetime.time(17, 0, 0)
            },
            datetime.date(2015, 2, 3): {
                'start': datetime.time(9, 0, 0),
                'end': datetime.time(17, 0, 0)
            },
            datetime.date(2015, 2, 4): {
                'start': datetime.time(9, 0, 0),
                'end': datetime.time(17, 0, 0)
            },
            datetime.date(2015, 2, 5): {
                'start': datetime.time(9, 0, 0),
                'end': datetime.time(17, 0, 0)
            },
            datetime.date(2015, 2, 6): {
                'start': datetime.time(9, 0, 0),
                'end': datetime.time(17, 0, 0)
            },
            datetime.date(2015, 2, 7): {
                'start': datetime.time(9, 0, 0),
                'end': datetime.time(12, 0, 0)
            },
            datetime.date(2015, 2, 8): {
                'start': datetime.time(9, 0, 0),
                'end': datetime.time(10, 0, 0)
            },
        }

        result = utils.group_by_weekday(a_week)
        self.assertIsInstance(result, list)
        self.assertItemsEqual(
            result,
            [[28800], [28800], [28800], [28800], [28800], [10800], [3600]]
        )


    def test_seconds_since_midnight(self):
        """
        Test seconds since midnight
        """
        result = utils.seconds_since_midnight( datetime.time(0, 0, 0) )
        self.assertEqual(result, 0)
        result = utils.seconds_since_midnight( datetime.time(12, 0, 0) )
        self.assertEqual(result, 43200)
        result = utils.seconds_since_midnight( datetime.time(23, 59, 59) )
        self.assertEqual(result, 86399)


    def test_interval(self): 
        """ 
        Test calculating inverval in seconds between two datetime.time objects. 
        """ 
        #return seconds_since_midnight(end) - seconds_since_midnight(start) 
        result = utils.seconds_since_midnight( 
            datetime.time(0, 0, 0)
        )
        self.assertEqual(result, 0)

        result = utils.seconds_since_midnight( 
            datetime.time(0, 0, 1)
        )
        self.assertEqual(result, 1)

        result = utils.seconds_since_midnight( 
            datetime.time(0, 1, 1)
        )
        self.assertEqual(result, 61)

        result = utils.seconds_since_midnight( 
            datetime.time(1, 1, 1)
        )
        self.assertEqual(result, 3661)


    def test_mean(self):
        """
        Test calculating arithmetic mean.
        """
        items = []
        result = utils.mean(items)
        self.assertEqual(result, 0)

        items = [1, 2, 3]
        result = utils.mean(items)
        self.assertEqual(result, 2.0)

        items = [-1, 1]
        result = utils.mean(items)
        self.assertEqual(result, 0.0)

        items = [-3, -2, -1]
        result = utils.mean(items)
        self.assertEqual(result, -2.0)

        items = [1.5, 2.5, 3.5, 4.5]
        result = utils.mean(items)
        self.assertEqual(result, 3.0)


def suite():
    """
    Default test suite.
    """
    base_suite = unittest.TestSuite()
    base_suite.addTest(unittest.makeSuite(PresenceAnalyzerViewsTestCase))
    base_suite.addTest(unittest.makeSuite(PresenceAnalyzerUtilsTestCase))
    return base_suite


if __name__ == '__main__':
    unittest.main()
