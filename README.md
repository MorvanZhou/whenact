# WhenAct

WhenAct is a module that defines a decision flow. A
[中文文档](https://github.com/MorvanZhou/whenact/tree/main/README_CN.md) is available to.

The executing flow looks like:

```text
decision1: [when0] > [action0]
decision2: [when1] > [action10 > action11]
decision3: [when20 > when21] > [action2]
decision4: [when31 > when32] > [action3]
```

When all `when` in one decision is satisfied, than it runs to it's following `action`.

This decision process has two modes,

1. `auto_break=True`, when runs into the first `when=True`, this flow will finish after it's following `act`.
2. `auto_break=False`, the flow will continue flow even when `when=False`.

For example:

```text
# auto_break = True
decision1: [when0=True] > [action0]
decision2: X
decision3: X
decision4: X
```

```text
# auto_break = False
decision1: [when0=True] > [action0]
decision2: [when1=False] > X
decision3: [when20=True > when21=True] > [action2]
decision4: [when31=False > X] > X
```

# Install

```shell
pip install whenact
```

# Create WhenAct decision flow

Simpling use `whenact.add()` to add new decision to the flow process.

```python
import whenact

def w1(ctx):
    return True

def a1(ctx):
    return "done"


whenact.add(when=w1, act=a1)

whenact.print_flow()
# p0: [w1] > [a1]

hist = whenact.run()
assert hist.last_output == "done"
assert hist.outputs == ["done"]
```

More complex pipeline can include more than one decision. Using `whenact.add()` to accumulate decisions.

```python
import whenact


def w_false(ctx):
    return False


def w_true(ctx):
    return True


def a1(ctx):
    return 1


def a2(ctx):
    return 2


def a3(ctx):
    return 3


whenact.add(when=w_false, act=a1)
whenact.add(when=w_true, act=[a2, a3])

whenact.print_flow()
# p0: [w1] > [a1]
# p1: [w2] > [a2 > a3]

hist = whenact.run()
print(hist.summary)
# [p1: w1, p2: w2 > a2 > a3]

assert hist.first_output == 2
assert hist.last_output == 3
assert hist.outputs == [2, 3]
```

The context(ctx) in each `when` and `act` function passes context information from outside. You can store external
information in context, then pass it to the flow. Moreover, values can be set to the context when inside those
functions, then be carried out once the flow is finished.

```python
import whenact


def w_false(ctx):
    return False


def w_true(ctx):
    return True


def a1(ctx):
    ctx["action"] = "a1 action"


def a2(ctx):
    ctx["action"] = "a2 action"


def a3(ctx):
    ctx["action"] += " with a3"


whenact.add(when=w_false, act=a1)
whenact.add(when=w_true, act=[a2, a3])

whenact.print_flow()


# p0: [w1] > [a1]
# p1: [w2] > [a2 > a3]

class TestContext(whenact.BaseContext):
    pass


ctx = TestContext()

hist = whenact.run(ctx)
print(hist.summary)
# [p1: w1, p2: w2 > a2 > a3]

assert hist.last_output is None
assert hist.outputs == [None, None]
assert ctx["action"] == "a2 action with a3"
```

There is another way to set a decision flow.

```python
import whenact


def w_false(ctx):
    return False


def w_true(ctx):
    return True


def a1(ctx):
    return 1


def a2(ctx):
    return 2


flow = whenact.DecisionFlow([
    whenact.Decision(when=[w_false], act=[a1], name="D1"),
    whenact.Decision(when=[w_true], act=[a2], name="D2"),
]
)
print(flow)
# D1: [w_false] > [a1]
# D2: [w_true] > [a2]

hist = flow.run()
assert hist.first_output == 2
```

# More examples

More examples can be found in [tests](https://github.com/MorvanZhou/whenact/tree/main/tests)
