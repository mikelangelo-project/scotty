import unittest

from scotty import version


class VersionTest(unittest.TestCase):
    def test_major_version(self):
        major = version.__version_info__[0]
        self.assertEquals(major, 0)

    def test_minor_version(self):
        minor = version.__version_info__[1]
        self.assertEquals(minor, 3)

    def test_patch_version(self):
        patch = version.__version_info__[2]
        self.assertEquals(patch, 0)
