# candidates/__init__.py

import sys

__version__ = '0.1'

# Check the python version being run
major, minor = sys.version_info[:2]
print('During initialisation the Python version detected was Python {0}.{1}\n'.format(major, minor))
if major == 3 and minor >= 5:
    pass
else:
    print('This code requires Python 3.5 or above to run successfully')
    sys.exit(0)


