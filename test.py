def something(fn):
    print("hey")
    return fn


@something
def hey():
    ...


hey()
