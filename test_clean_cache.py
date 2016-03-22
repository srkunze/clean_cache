from threading import local

from xcache import ref_cache_gen, ref_cache, clean_caches


class Request:
    pass


class TemporaryObject:
    pass


globaldata = local()
request_cache = ref_cache_gen(lambda: getattr(globaldata, 'request', None))


@ref_cache(maxsize=None)
def fib(n):
    return fib(n-1) + fib(n-2) if n > 1 else 1


@ref_cache(maxsize=None)
def fib2(n):
    return fib2(n-2) + fib2(n-3) if n > 1 else 1


def assert_empty_cache(func):
    try:
        ci = func.cache_info()
    except AttributeError:
        pass
    else:
        if ci.currsize != 0:
            raise RuntimeError


def assert_filled_cache(func):
    try:
        ci = func.cache_info()
    except AttributeError:
        pass
    else:
        if ci.currsize == 0:
            raise RuntimeError


for request in range(2):
    print('request start')

    assert_empty_cache(fib)
    assert_empty_cache(fib2)

    globaldata.request = Request()
    with clean_caches(globaldata.request):

        assert_empty_cache(fib)
        list(map(fib, range(0, 20000, 150)))
        assert_filled_cache(fib)

        with clean_caches(TemporaryObject()):
            assert_empty_cache(fib)
            list(map(fib, range(0, 20000, 150)))
            assert_filled_cache(fib)
        assert_filled_cache(fib)

        assert_empty_cache(fib2)
        list(map(fib2, range(200)))
        assert_filled_cache(fib2)

        with clean_caches():
            assert_empty_cache(fib2)
            list(map(fib2, range(200)))
            assert_filled_cache(fib2)
        assert_empty_cache(fib2)

    assert_empty_cache(fib)
    assert_empty_cache(fib2)

    print('request end')
