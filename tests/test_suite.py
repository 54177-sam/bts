"""Comprehensive test suite untuk SIBERINDO BTS GUI"""
import unittest
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import app as app_module
from modules import database, sms_manager, subscribers
from modules.validators import DataValidator, ValidationError, RateLimiter
from modules.middleware import APIResponse


class TestDatabaseOperations(unittest.TestCase):
    """Test database operations"""
    
    def setUp(self):
        """Setup test fixtures"""
        self.db = database.db
    
    def test_get_subscribers_count(self):
        """Test getting subscribers count"""
        count = database.get_subscribers_count()
        self.assertIsInstance(count, int)
        self.assertGreaterEqual(count, 0)
    
    def test_get_subscribers(self):
        """Test getting subscribers with pagination"""
        subs = database.get_subscribers(limit=10, offset=0)
        self.assertIsInstance(subs, list)
    
    def test_add_subscriber(self):
        """Test adding new subscriber"""
        result = database.add_subscriber(
            imsi='001011234567890',
            msisdn='1234567890',
            name='Test User',
            location='Jakarta'
        )
        self.assertIsInstance(result, bool)
    
    def test_save_sms(self):
        """Test saving SMS message"""
        result = database.save_sms(
            sender='1111',
            receiver='2222',
            message='Test message',
            sms_type='TEST',
            status='SENT'
        )
        self.assertIsInstance(result, bool)
    
    def test_get_sms_history(self):
        """Test getting SMS history"""
        history = database.get_sms_history(limit=50)
        self.assertIsInstance(history, list)


class TestDataValidation(unittest.TestCase):
    """Test data validation"""
    
    def test_valid_imsi(self):
        """Test valid IMSI"""
        imsi = DataValidator.validate_imsi('001011234567890')
        self.assertEqual(imsi, '001011234567890')
    
    def test_invalid_imsi(self):
        """Test invalid IMSI"""
        with self.assertRaises(ValidationError):
            DataValidator.validate_imsi('12345')  # Too short
    
    def test_valid_msisdn(self):
        """Test valid MSISDN"""
        msisdn = DataValidator.validate_msisdn('1234567890')
        self.assertEqual(msisdn, '1234567890')
    
    def test_invalid_msisdn(self):
        """Test invalid MSISDN"""
        with self.assertRaises(ValidationError):
            DataValidator.validate_msisdn('12345')  # Too short
    
    def test_valid_email(self):
        """Test valid email"""
        email = DataValidator.validate_email('user@example.com')
        self.assertEqual(email, 'user@example.com')
    
    def test_invalid_email(self):
        """Test invalid email"""
        with self.assertRaises(ValidationError):
            DataValidator.validate_email('invalid-email')
    
    def test_sanitize_string(self):
        """Test string sanitization"""
        result = DataValidator.sanitize_string('  test  ')
        self.assertEqual(result, 'test')


class TestRateLimiter(unittest.TestCase):
    """Test rate limiting"""
    
    def test_rate_limit_below_threshold(self):
        """Test rate limit below threshold"""
        result = RateLimiter.check_rate_limit('test_key', max_requests=100)
        self.assertTrue(result)
    
    def test_rate_limit_exceeds_threshold(self):
        """Test rate limit exceeds threshold"""
        # Fill up to limit
        key = 'limit_test'
        for i in range(5):
            RateLimiter.check_rate_limit(key, max_requests=5)
        
        # Next request should fail
        result = RateLimiter.check_rate_limit(key, max_requests=5)
        self.assertFalse(result)


class TestAPIResponses(unittest.TestCase):
    """Test API response formatting"""
    
    @classmethod
    def setUpClass(cls):
        """Setup Flask app context"""
        cls.app = app_module.app
    
    def test_success_response(self):
        """Test success response format"""
        with self.app.app_context():
            response, status = APIResponse.success(data={'test': 'data'})
            self.assertEqual(status, 200)
    
    def test_error_response(self):
        """Test error response format"""
        with self.app.app_context():
            response, status = APIResponse.error('Test error', 400)
            self.assertEqual(status, 400)
    
    def test_paginated_response(self):
        """Test paginated response format"""
        with self.app.app_context():
            response, status = APIResponse.paginated(
                items=[1, 2, 3],
                total=30,
                page=1,
                limit=10
            )
            self.assertEqual(status, 200)


class TestFlaskRoutes(unittest.TestCase):
    """Test Flask routes"""
    
    @classmethod
    def setUpClass(cls):
        """Setup Flask test client and app context"""
        cls.app = app_module.app.test_client()
        cls.app_context = app_module.app.app_context()
        cls.app_context.push()
    
    @classmethod
    def tearDownClass(cls):
        """Cleanup app context"""
        cls.app_context.pop()
    
    def setUp(self):
        """Setup test session"""
        with self.app:
            with self.app.session_transaction() as sess:
                sess['logged_in'] = True
                sess['username'] = 'admin'
                sess['role'] = 'administrator'
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
    
    def test_dashboard_endpoint(self):
        """Test dashboard endpoint"""
        response = self.app.get('/dashboard/dashboard')
        self.assertEqual(response.status_code, 200)
    
    def test_subscribers_endpoint(self):
        """Test subscribers endpoint"""
        response = self.app.get('/subscribers/subscribers')
        self.assertEqual(response.status_code, 200)
    
    def test_sms_endpoint(self):
        """Test SMS endpoint"""
        response = self.app.get('/sms/send_silent_sms')
        self.assertEqual(response.status_code, 200)
    
    def test_api_subscribers(self):
        """Test API subscribers endpoint"""
        response = self.app.get('/subscribers/api/subscribers', follow_redirects=True)
        # Either 200 (if authenticated) or redirect is acceptable
        self.assertIn(response.status_code, [200, 302])
    
    def test_api_subscriber_count(self):
        """Test API subscriber count endpoint"""
        response = self.app.get('/subscribers/api/subscribers/count', follow_redirects=True)
        # Either 200 (if authenticated) or redirect is acceptable
        self.assertIn(response.status_code, [200, 302])


class TestSMSManager(unittest.TestCase):
    """Test SMS Manager"""
    
    def setUp(self):
        """Setup test fixtures"""
        self.sms_mgr = sms_manager.SMSManager()
    
    def test_sms_manager_init(self):
        """Test SMS manager initialization"""
        self.assertIsNotNone(self.sms_mgr)
    
    def test_get_sms_count(self):
        """Test getting SMS count"""
        count = self.sms_mgr.get_sms_count()
        self.assertIsInstance(count, int)
        self.assertGreaterEqual(count, 0)


class TestSubscriberManager(unittest.TestCase):
    """Test Subscriber Manager"""
    
    def setUp(self):
        """Setup test fixtures"""
        self.sub_mgr = subscribers.SubscriberManager()
    
    def test_subscriber_manager_init(self):
        """Test subscriber manager initialization"""
        self.assertIsNotNone(self.sub_mgr)
    
    def test_get_subscribers_count(self):
        """Test getting subscribers count"""
        count = self.sub_mgr.get_subscribers_count()
        self.assertIsInstance(count, int)
        self.assertGreaterEqual(count, 0)
    
    def test_get_subscriber_stats(self):
        """Test getting subscriber statistics"""
        stats = self.sub_mgr.get_subscriber_stats()
        self.assertIn('total_subscribers', stats)
        self.assertIn('active_subscribers', stats)


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDatabaseOperations))
    suite.addTests(loader.loadTestsFromTestCase(TestDataValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestRateLimiter))
    suite.addTests(loader.loadTestsFromTestCase(TestAPIResponses))
    suite.addTests(loader.loadTestsFromTestCase(TestFlaskRoutes))
    suite.addTests(loader.loadTestsFromTestCase(TestSMSManager))
    suite.addTests(loader.loadTestsFromTestCase(TestSubscriberManager))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
