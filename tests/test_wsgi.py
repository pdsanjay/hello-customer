import unittest

from wsgi import app


class WebAppTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_home(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Hello, Customer!", response.data)

    def test_name(self):
        response = self.client.get("/?name=Pat")
        self.assertIn(b"Hello, Pat!", response.data)

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.json, {"status": "ok"})

    def test_escapes_html(self):
        response = self.client.get("/?name=%3Cscript%3E")
        self.assertNotIn(b"<script>", response.data)
        self.assertIn(b"&lt;script&gt;", response.data)


if __name__ == "__main__":
    unittest.main()
