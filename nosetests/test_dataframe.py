from pandas import DataFrame, factorize
from numpy.random import randn
import numpy as np
import matplotlib.pyplot as plt
#
# these are not really tests, but a way to get familiar with pandas 
#

def test_dataframe_simple():
    df = DataFrame([{'a': 1, 'b': 'foo'},
                       {'a': 2, 'b': 'foo'},
                       {'a': 3, 'b': 'bar'},
                       {'a': 4, 'b': 'bar'},
                       ])
    m = df.groupby('b').mean()
    assert(abs(m.loc['foo'].item() - 1.5) < 0.0001)

def test_dataframe_groupby():
    df = DataFrame({'A' : ['foo', 'bar', 'foo', 'bar',
                           'foo', 'bar', 'foo', 'foo'],
                    'B' : ['one', 'one', 'two', 'three',
                           'two', 'two', 'one', 'three'],
                    'C' : randn(8), 'D' : randn(8)})
    gA = df.groupby(['A'])
    gB = df.groupby(['B'])
    gAB = df.groupby(['A', 'B'], as_index=False)
    assert(len(gA) == 2)
    assert(len(gB) == 3)
    assert(len(gAB) == 6)
    #print(factorize(df.A)) # converts labels to ids
    
    #print(gAB.get_group(('foo', 'one')))
    
    
#     print(df)
#     print(gAB.head())
#     print(gAB.groups)
#     for name, group in gAB:
#         print(name)
#         print(group)
#     print("aggregate")
#     print(gAB.agg([np.sum, np.mean, np.std]).reset_index())
#     print(gA.agg({'C': np.sum,
#                   'D': lambda x: np.std(x, ddof=1)}))


#     box = gA.boxplot()
#     print(box)
#     print(type(box))
#     plt.show()
    
    #print(fig.items())
    #fig.savefig("out.png")
