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
