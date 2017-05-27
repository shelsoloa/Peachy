from peachy.utils import Counter


def run(count):
    print('start: ' + str(count.current))
    while not count.advance():
        print(count.current)
    print('end: ' + str(count.current))


def test_regular():
    count = Counter(0, 3)
    run(count)


def test_regular_step():
    count = Counter(0, 6, step=2)
    run(count)


def test_regular_step_overshoot():
    count = Counter(0, 10, step=3)
    run(count)


def test_regular_repeat():
    count = Counter(0, 3, enable_repeat=True, repeat_cap=3)
    run(count)


def test_regular_repeat_step():
    count = Counter(0, 3, enable_repeat=True, repeat_cap=3, step=3)
    run(count)


def test_regular_repeat_step_overshoot():
    count = Counter(0, 8, enable_repeat=True, repeat_cap=3, step=3)
    run(count)


def test_pingpong():
    count = Counter(0, 3, enable_pingpong=True)
    run(count)


def test_pingpong_step():
    count = Counter(0, 6, enable_pingpong=True, step=2)
    run(count)


def test_pingpong_step_overshoot():
    count = Counter(0, 8, enable_pingpong=True, step=3)
    run(count)


def test_pingpong_repeat():
    count = Counter(0, 3, enable_pingpong=True, enable_repeat=True,
                    repeat_cap=3)
    run(count)


def test_pingpong_repeat_step():
    count = Counter(0, 6, enable_pingpong=True, enable_repeat=True,
                    repeat_cap=3, step=2)
    run(count)


def test_pingpong_repeat_step_overshoot():
    count = Counter(1, 8, enable_pingpong=True, enable_repeat=True,
                    repeat_cap=3, step=3)
    run(count)
