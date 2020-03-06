from selenium import webdriver

browser = webdriver.Firefox()
browser.get('http://127.0.0.1:8000/report')


# helper methods from https://lincolnloop.com/blog/introduction-django-selenium-testing/
class CustomWebDriver(SELENIUM_WEBDRIVER):
    """Our own WebDriver with some helpers added"""

    def find_css(self, css_selector):
        """Shortcut to find elements by CSS. Returns either a list or singleton"""
        elems = self.find_elements_by_css_selector(css_selector)
        found = len(elems)
        if found == 1:
            return elems[0]
        elif not elems:
            raise NoSuchElementException(css_selector)
        return elems

    def wait_for_css(self, css_selector, timeout=7):
        """ Shortcut for WebDriverWait"""
        return WebDriverWait(self, timeout).until(lambda driver: driver.find_css(css_selector))


class SimpleTestCase(unittest.TestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.addCleanup(self.browser.quit)

    def testPageTitle(self):
        self.browser.get('http://127.0.0.1:8000/report')
        self.assertIn('Step 1', self.browser.title)


if __name__ == '__main__':
    unittest.main(verbosity=2)
