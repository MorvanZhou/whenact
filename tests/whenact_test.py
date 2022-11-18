import unittest

import whenact


class TestContext(whenact.BaseContext):
    step = 0

    def __init__(self):
        super().__init__()
        self.test_attr = "test_attr"

    def _set_step(self, step):
        self.step = step

    def test_method(self):
        return "test_method"


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


class WhenActTest(unittest.TestCase):
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


class ContextTest(unittest.TestCase):
    def test_context(self):
        ctx = TestContext()
        p_ctx = whenact.PipelineContext(base_ctx=ctx)
        self.assertEqual("test_method", p_ctx.test_method())
        self.assertEqual("test_attr", p_ctx.test_attr)

        p_ctx.set_pipeline_output("aa")
        self.assertEqual("aa", p_ctx.last_output)

    def test_run_context(self):
        @whenact.when
        def w3(ctx):
            ctx["aaa"] = 1
            return True

        @whenact.act
        def a3(ctx):
            ctx._set_step(ctx.step + 1)
            self.assertEqual(1, ctx["aaa"])
            with self.assertRaises(KeyError):
                _ = ctx["vvv"]
            ctx["ccc"] = ctx.step
            self.assertEqual(ctx.step, ctx.ccc)

        @whenact.act
        def a4(ctx):
            return ctx["ccc"]

        ctx = TestContext()
        p = whenact.create_pipeline([
            [w3, w3, a3, a4]
        ])
        for i in range(1, 4):
            self.assertEqual(i, p.run(ctx))

    def test_no_ctx(self):
        @whenact.when
        def nw(ctx):
            return True

        @whenact.act
        def na1(ctx):
            return 21

        @whenact.act
        def na2(ctx):
            return 22

        p = whenact.create_pipeline([
            [nw, na1, na2]
        ])

        res = p.run()
        self.assertEqual(22, res)
