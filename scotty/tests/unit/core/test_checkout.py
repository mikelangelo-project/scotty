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

    def test_generator_location_ssh(self):
        git_url = "ssh://git@gitlab.gwdg.de/repository.py.git"
        generator = "git:{}".format(git_url)
        config = {
            "generator":generator
        }
        component = Component()
        component.config = config
        self.assertEqual(component.generator['location'], git_url)
#
#    def test_get_url_git_ssh_port(self):
#        source = "git:ssh://git@gitlab.gwdg.de:22/repository.py.git[master]"
#        url = CheckoutManager.get_location(source)
#        self.assertEqual(url, "ssh://git@gitlab.gwdg.de:22/repository.py.git")
#
#    def test_get_url_git_ssh_colon(self):
#        source = "git:ssh://git@gitlab.gwdg.de:22:repository.py.git[master]"
#        url = CheckoutManager.get_location(source)
#        self.assertEqual(url, "ssh://git@gitlab.gwdg.de:22:repository.py.git")
#
#    def test_get_url_git_https(self):
#        source = "git:https://gitlab.gwdg.de/repository.py.git"
#        url = CheckoutManager.get_location(source)
#        self.assertEqual(url, "https://gitlab.gwdg.de/repository.py.git")
#
#    def test_get_url_file(self):
#        source = "file:path/to/workload_gen"
#        url = CheckoutManager.get_location(source)
#        self.assertEqual(url, "path/to/workload_gen")
#
#    def test_get_reference(self):
#        source = "git:git@gitlab.gwdg.de:repository.py.git[master]"
#        reference = CheckoutManager.get_reference(source)
#        self.assertEqual(reference, "master")
#
#    def test_get_reference_noreference(self):
#        source = "git:git@gitlab.gwdg.de:repository.py.git"
#        reference = CheckoutManager.get_reference(source)
#        self.assertEqual(reference, None)
#
#    def test_get_reference_port(self):
#        source = "git:ssh://git@gitlab.gwdg.de:22/repository.py.git[master]"
#        reference = CheckoutManager.get_reference(source) 
#        self.assertEqual(reference, "master")
#
#    def test_get_reference_colon(self):
#        source = "git:ssh://git@gitlab.gwdg.de:22:repository.py.git[master]"
#        reference = CheckoutManager.get_reference(source)
#        self.assertEqual(reference, "master")
#
#    def test_get_reference_https(self):
#        source = "git:https://gitlab.gwdg.de/repository.py.git[master]"
#        reference = CheckoutManager.get_reference(source)
#        self.assertEqual(reference, "master")
