import unittest
import mock

from scotty.core.checkout import CheckoutManager
from scotty.core.components import Component

class CheckoutManagerTest(unittest.TestCase):
    def test_generator_location(self):
        git_url = "git@gitlab.gwdg.de:repository.py.git"
        generator = "git:{}[master]".format(git_url)
        config = {
            "generator":generator
        }
        component = Component()
        component.config = config
        self.assertEqual(component.generator['location'], git_url)

    def test_generator_location_without_reference(self):
        git_url = "ssh://git@gitlab.gwdg.de/repository.py.git"
        generator = "git:{}".format(git_url)
        config = {
            "generator":generator
        }
        component = Component()
        component.config = config
        self.assertEqual(component.generator['location'], git_url)

    def test_generator_reference(self):
        git_url = "git@gitlab.gwdg.de:repository.py.git"
        generator = "git:{}[master]".format(git_url)
        config = {
            "generator":generator
        }
        component = Component()
        component.config = config
        self.assertEqual(component.generator['reference'], "master")

    def test_generator_reference_noreference(self):
        git_url = "git@gitlab.gwdg.de:repository.py.git"
        generator = "git:{}".format(git_url)
        config = {
            "generator":generator
        }
        component = Component()
        component.config = config
        self.assertEqual(component.generator['reference'], None)

    def test_generator_type(self):
        git_url = "ssh://git@gitlab.gwdg.de/repository.py.git"
        generator = "git:{}[master]".format(git_url)
        config = {
            "generator":generator
        }
        component = Component()
        component.config = config
        self.assertEqual(component.generator['type'], "git")
