import doctest

from folders import utils, cron

doctest.testmod(utils, verbose=True)
doctest.testmod(cron, verbose=True)
