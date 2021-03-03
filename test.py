from itertools import product
lists = [[1,2,3,4],[5,6,7,8], [9,10,11,12],[1,2,3,4,5],[1,2,3,4],[5,6,7,8], [9,10,11,12],[1,2,3,4,5]]
lists = [[1]*10]*10
ps = list(product(*lists))
#print(ps)
