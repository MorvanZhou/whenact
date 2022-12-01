# WhenAct

WhenAct 是一个决策流执行库。可以按照下列方式做流式的决策过程。

```text
决策 1：[条件 0] > [执行 0]
决策 2：[条件 1] > [执行 10 > 执行 11]
决策 3：[条件 20 > 条件 21] > [执行 2]
决策 4：[条件 31 > 条件 32] > [执行 3]
```

当一条 `决策` 中的所有 `条件` 都满足时，程序就会流进这条 `决策` 的 `执行`，并运行此 `决策` 中的所有 `执行` 步骤。

WhenAct 中的决策流过程可分为下列两种模式：

1. `auto_break=True`, 当运行至第一个所有 `when=True` 的决策时, 程序会在运行完此决策流后面所有 `act` 后结束。
2. `auto_break=False`, 决策流会向下一直继续，即使遇到决策中某个 `when=False` 也会继续执行下一个决策流。但是这个失败的决策不会继续执行它的后续流。

举例：

```text
# auto_break = True
决策 1: [条件0=True] > [执行0]
决策 2: X
决策 3: X
决策 4: X
```

```text
# auto_break = False
决策 1: [条件0=True] > [执行0]
决策 2: [条件1=False] > X
决策 3: [条件20=True > 条件21=True] > [执行 2]
决策 4: [条件31=False > X] > X
```

# 安装

```shell
pip install whenact
```

# 创建 WhenAct 决策流

简单地使用 `whenact.add()` 来添加新的决策过程。

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

更复杂的决策流可以包含多个决策过程，持续使用 `whenact.add()` 来累积决策过程。

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

在 `when` 和 `act` 的上下文信息 `context`（`ctx`）。是一个从外部传入的上下文，你可以在外部添加一些额外的数据，将这些数据传入决策流， 让决策流依据这些信息来产生决策过程。

此外，你也可以在决策过程中在上下文数据中添加你想要的变量或者数值。在执行完决策流后，可以从原始的 context 中重新获取到中间结果。

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

这里还有另外一种方式来创建决策流。

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

# 更多案例

更多案例请参考 [tests](https://github.com/MorvanZhou/whenact/tree/main/tests)
