import pprint

import joblib


def testfunc(arg):
    print(str(arg))
    return [arg ** 2, arg]


return_code = joblib.Parallel(n_jobs=5)(joblib.delayed(testfunc)(arg) for arg in range(10))

pprint.pprint(return_code, indent=4)
