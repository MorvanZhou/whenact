import unittest

import whenact


class TestContext(whenact.BaseContext):
    pass


@whenact.when
def w_f(ctx):
    return False


@whenact.when
def w_t(ctx):
    return True


@whenact.act
def a1(ctx):
    return 1


@whenact.act
def a2(ctx):
    return 2


@whenact.act
def a3(ctx):
    return 3


class PipelineTest(unittest.TestCase):
    def test_create_when(self):
        @whenact.when
        def _w1():
            return

        with self.assertRaises(TypeError):
            _w1()

        @whenact.when
        def _w2(ctx: whenact.BaseContext):
            return 1

        with self.assertRaises(TypeError):
            _w2(TestContext())

    def test_pipe_no_name(self):
        @whenact.act
        def _a1(ctx: whenact.PipelineContext):
            ctx["r1"] = 1
            return "done"

        @whenact.act
        def _a2(ctx: whenact.PipelineContext):
            ctx["r2"] = 2

        whenact.task._reset_task_name()
        p = whenact.Pipeline([
            whenact.Task([w_f], [_a1, _a2]),
            whenact.Task([w_t], [_a1])
        ])
        self.assertEqual("p0", p[0].name)
        self.assertEqual("p1", p[1].name)
        self.assertEqual("p0", p["p0"].name)
        self.assertEqual("p1", p["p1"].name)

        res = p.run(context=TestContext())
        self.assertEqual("done", res.last_output)
        self.assertEqual(2, len(p.view()))

        context = TestContext()
        hist = p.run(context=context)
        self.assertEqual("done", hist.last_output)

    def test_pipe_with_name(self):
        @whenact.act
        def _a1(ctx: whenact.PipelineContext):
            ctx["r1"] = 1
            return "done"

        @whenact.act
        def _a2(ctx: whenact.PipelineContext):
            ctx["r2"] = 2

        with self.assertRaises(TypeError):
            _ = whenact.create_pipeline([
                [w_f, _a1, w_f, _a2],
                [w_t, _a1]
            ])

        whenact.task._reset_task_name()
        p = whenact.create_pipeline([
            [w_f, _a1, _a2],
            [w_t, _a1]
        ])
        self.assertEqual("p0", p[0].name)
        self.assertEqual("p1", p[1].name)
        self.assertEqual("p0", p["p0"].name)
        self.assertEqual("p1", p["p1"].name)

        res = p.run(context=TestContext())
        self.assertEqual("done", res.last_output)
        self.assertEqual(2, len(p.view()))

    def test_break(self):
        p = whenact.create_pipeline([
            [w_t, a1],
            [w_t, a2]
        ])

        res = p.run(auto_break=True)
        self.assertEqual(1, res.last_output)

        res = p.run(auto_break=False)
        self.assertEqual(2, res.last_output)

    def test_multiple_when(self):
        p = whenact.create_pipeline([
            [w_t, w_t, a2],
            [w_f, w_t, a1],
            [w_t, w_t, a3],
        ])

        res = p.run(auto_break=True)
        self.assertEqual(2, res.last_output)

        res = p.run(auto_break=False)
        self.assertEqual(3, res.last_output)

    def test_no_res(self):
        p = whenact.create_pipeline([
            [w_f, a2],
        ])
        hist = p.run()
        self.assertEqual(False, hist.acted)
        self.assertEqual([], hist.outputs)
        self.assertEqual(None, hist.last_output)

        p = whenact.create_pipeline([
            [w_t, a2],
        ])
        hist = p.run()
        self.assertEqual(True, hist.acted)
        self.assertEqual([2], hist.outputs)
