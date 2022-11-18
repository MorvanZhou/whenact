# WhenAct

WhenAct is a module that defines a decision pipeline.

The executing flow looks like:

```text
policy0: [when0] > [action0]
policy1: [when1] > [action10 > action11]
policy2: [when20 > when21] > [action2]
```

When all `when` in one policy set is satisfied, than it runs to it's following `action`. No matter the previous `when`
is satisfied or not, the next `when` will be checked and executed. When all policies have been checked and executed,
this pipeline then finishes.

# Create WhenAct pipeline

Before create a pipeline, you need to define `when` and `act` function first, then put them in the pipeline.

```python
import whenact

@whenact.when
def w1(ctx):
    return True

@whenact.act
def a1(ctx):
    return "done"

pipeline = whenact.create_pipeline(config=[
    [w1, a1]
])

print(pipeline)
# p0: [w1] > [a1]

result = pipeline.run()
assert result == "done"
```

More complex pipeline can be like this:

```python
import whenact

@whenact.when
def w1(ctx):
    return False

@whenact.when
def w2(ctx):
    return True

@whenact.act
def a1(ctx):
    ctx["action"] = "a1 action"

@whenact.act
def a2(ctx):
    ctx["action"] = "a2 action"

@whenact.act
def a3(ctx):
    ctx["action"] += " with a3"


pipeline = whenact.create_pipeline(config=[
    [w1, a1],
    [w2, a2, a3]
])

print(pipeline)
# p0: [w1] > [a1]
# p1: [w2] > [a2 > a3]

class TestContext(whenact.BaseContext):
    pass

ctx = TestContext()

result = pipeline.run(ctx)
assert result is None
assert ctx["action"] == "a2 action with a3"
```

There is another way to set a pipeline, additionally, to set policy name.

```python
import whenact

@whenact.when
def w1(ctx):
    return True

@whenact.act
def a1(ctx):
    ctx["r1"] = 1
    return "done"

pipeline = whenact.Pipeline(
    [whenact.Policy(when=[w1], action=[a1], name="my_policy1")]
)
print(pipeline)
# p0: [w1] > [a1]
```

# More examples

More examples can be found in [tests](https://github.com/MorvanZhou/whenact/tree/main/tests)
