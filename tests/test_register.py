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
    def setUp(self) -> None:
        whenact.clear()

    def test_add1(self):
        ctx = TestContext()
        whenact.add(when=[w_true, w_false], act=a1)
        hist = whenact.run(ctx)
        self.assertIsNone(hist.last_output)
        self.assertFalse(hist.acted)

    def test_add2(self):
        ctx = TestContext()
        whenact.add(when=[w_true, w_false], act=[a1, a2])
        whenact.add(when=[w_true, w_true], act=a2)
        hist = whenact.run(ctx)
        self.assertEqual([2], hist.outputs)
        self.assertEqual(2, hist.last_output)

    def test_no_act(self):
        ctx = TestContext()
        whenact.add(when=[w_true])
        hist = whenact.run(ctx)
        self.assertEqual(None, hist.last_output)
