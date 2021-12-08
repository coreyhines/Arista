#!/usr/bin/env python

import pyeapi
from pprint import pprint as pp

node = pyeapi.connect_to('7150-01')
pp(node.enable('show version'))
