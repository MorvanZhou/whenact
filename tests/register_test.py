import unittest

import whenact


def w_true(ctx):
    return True


def w_false(ctx):
    return False


def a1(ctx):
    return 1


def a2(ctx):
    return 2


class TestContext(whenact.BaseContext):
    pass


class RegisterTest(unittest.TestCase):
    def test_add(self):
        ctx = TestContext()
        whenact.add(when=[w_true, w_false], act=a1)
        hist = whenact.run(ctx)
        self.assertIsNone(hist.last_output)
        self.assertFalse(hist.acted)

        whenact.add(when=[w_true, w_true], act=a2)
        hist = whenact.run(ctx)
        self.assertEqual(2, hist.last_output)
