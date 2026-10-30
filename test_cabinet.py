"""Public example data only; no network calls or private fixtures."""
import unittest
from cabinet import render


class CabinetTests(unittest.TestCase):
    def test_self_contained_searchable_page(self):
        page = render([{'title': 'One good question', 'note': 'A useful beginning.', 'tags': ['curiosity']}])
        self.assertIn('<!doctype html>', page)
        self.assertIn('One good question', page)
        self.assertIn('type="search"', page)
        self.assertIn('addEventListener', page)
        self.assertNotIn('<script src=', page)
        self.assertNotIn('fonts.googleapis.com', page)

    def test_untrusted_content_is_escaped(self):
        page = render([{'title': '<img src=x onerror=alert(1)>', 'note': '</article><script>alert(1)</script>', 'tags': ['<svg>']}])
        self.assertNotIn('<img src=x', page)
        self.assertNotIn('<script>alert(1)', page)
        self.assertIn('&lt;svg&gt;', page)

    def test_unsafe_source_links_rejected(self):
        for value in ['javascript:alert(1)', 'file:///etc/passwd', 'https://']:
            with self.subTest(url=value), self.assertRaises(ValueError):
                render([{'title': 'x', 'note': 'x', 'url': value}])

    def test_input_validation(self):
        for data in [{}, [None], [{'title': ''}], [{'title': 'x', 'tags': 'not-a-list'}]]:
            with self.subTest(data=data), self.assertRaises(ValueError):
                render(data)

    def test_empty_cabinet(self):
        self.assertIn('Nothing on this shelf yet.', render([]))

    def test_source_attribute_escaping(self):
        page = render([{'title': 'x', 'url': 'https://example.com/?q=" onmouseover="evil'}])
        self.assertIn('&quot;', page)
        self.assertIn('rel="noopener noreferrer"', page)


if __name__ == '__main__':
    unittest.main()
