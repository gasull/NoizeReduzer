import doctest
from inspect import getmembers, ismodule

app = 'users'

# It will run the doctests for every function in every module of the above apps.
for member_module in getmembers(app, ismodule):
    module_name = member_module[0]
    module = __import__(app + '.' + module_name)
    doctest.testmod(module, verbose=False)

