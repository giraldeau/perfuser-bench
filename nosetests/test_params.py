from perfuserBench import microbench

def test_params_product():
    d = { "a": [1,2,3], "b": [4,5,6] }
    p = microbench.dict_product(d)
    x = [i for i in p]
    assert(len(x) == 9)

def test_params_product_empty():
    p = microbench.dict_product({})
    x = [i for i in p]
    assert(len(x) == 1)