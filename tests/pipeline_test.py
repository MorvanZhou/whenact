import unittest

import whenact


class TestContext(whenact.BaseContext):
    pass


@whenact.when
def w1(ctx: whenact.PipelineContext):
    return False


@whenact.when
def w2(ctx: whenact.PipelineContext):
    return True


@whenact.act
def a1(ctx: whenact.PipelineContext):
    ctx["r1"] = 1
    return "done"


@whenact.act
def a2(ctx: whenact.PipelineContext):
    ctx["r2"] = 2


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
        whenact.pipeline._reset_policy_name()
        p = whenact.Pipeline([
            whenact.Policy([w1], [a1, a2]),
            whenact.Policy([w2], [a1])
        ])
        self.assertEqual("p0", p[0].name)
        self.assertEqual("p1", p[1].name)
        self.assertEqual("p0", p["p0"].name)
        self.assertEqual("p1", p["p1"].name)

        res = p.run(context=TestContext())
        self.assertEqual("done", res)
        self.assertEqual(2, len(p.view_pipe()))

        context = TestContext()
        for i, res in enumerate(p.iter_run(context=context)):
            if i == 0:
                self.assertFalse(res)
            elif i == 1:
                self.assertTrue(res)
            elif i == 2:
                self.assertEqual("done", res)

    def test_pipe_with_name(self):
        with self.assertRaises(TypeError):
            _ = whenact.create_pipeline([
                [w1, a1, w1, a2],
                [w2, a1]
            ])

        whenact.pipeline._reset_policy_name()
        p = whenact.create_pipeline([
            [w1, a1, a2],
            [w2, a1]
        ])
        self.assertEqual("p0", p[0].name)
        self.assertEqual("p1", p[1].name)
        self.assertEqual("p0", p["p0"].name)
        self.assertEqual("p1", p["p1"].name)

        res = p.run(context=TestContext())
        self.assertEqual("done", res)
        self.assertEqual(2, len(p.view_pipe()))

    def test_break(self):
        @whenact.when
        def w1(ctx):
            return True

        @whenact.when
        def w2(ctx):
            return True

        @whenact.act
        def a1(ctx):
            return 1

        @whenact.act
        def a2(ctx):
            return 2

        p = whenact.create_pipeline([
            [w1, a1],
            [w2, a2]
        ])

        res = p.run(auto_break=True)
        self.assertEqual(1, res)

        res = p.run(auto_break=False)
        self.assertEqual(2, res)
