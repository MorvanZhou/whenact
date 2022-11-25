import unittest

from whenact.history import PipelineHistory


def w_true(ctx):
    return True


def w_false(ctx):
    return False


def a1(ctx):
    pass


def a2():
    pass


class HistTest(unittest.TestCase):
    def test_output(self):
        hist = PipelineHistory()

        hist.add_decision("d1")
        hist.add_when_result(w_true, True)
        hist.add_when_result(w_false, False)

        hist.add_decision("d2")
        hist.add_when_result(w_true, True)
        hist.add_when_result(w_true, True)
        hist.add_act_result(a2, 2)

        hist.add_decision("d3")
        hist.add_when_result(w_true, True)
        hist.add_act_result(a2, 3)

        hist.add_decision("d4")
        hist.add_when_result(w_false, False)

        hist.add_decision("d5")
        hist.add_when_result(w_true, True)
        hist.add_act_result(a2, 5)

        self.assertEqual(2, hist.first_output)
        self.assertEqual(5, hist.last_output)
        self.assertEqual([2, 3, 5], hist.outputs)

        self.assertEqual(
            {'when': {'w_true': True, 'w_false': False}, 'act': {}}, hist.get_decision("d1"))
