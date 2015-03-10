from perfuserBench.ext import stride

def test_stride():
    src = bytearray(list(range(10)))
    dst = bytearray([0] * 10)
    exp = bytearray([0, 2, 4, 6, 8, 1, 3, 5, 7, 9])
    stride(dst, src, 2)
    assert(dst == exp)

def test_stride_reverse():
    src = bytearray(list(range(10)))
    dst = bytearray([0] * 10)
    exp = bytearray(list(range(10)))
    stride(dst, src, 2)
    stride(src, dst, 5)
    assert(src == exp)
