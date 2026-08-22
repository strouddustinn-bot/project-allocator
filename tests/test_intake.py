import unittest

from project_allocator.intake import _slugify


class IntakeTests(unittest.TestCase):
    def test_slugify(self):
        self.assertEqual(_slugify("Project Allocator — First Gate!"), "project-allocator-first-gate")

    def test_slugify_fallback(self):
        self.assertEqual(_slugify("!!!"), "project")


if __name__ == "__main__":
    unittest.main()
