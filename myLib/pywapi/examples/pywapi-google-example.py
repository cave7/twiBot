#!/usr/bin/env python
# This Python file uses the following encoding: utf-8
import pywapi
import pprint
pp = pprint.PrettyPrinter(indent=4)

result = pywapi.get_weather_from_google('90000','en')
pp.pprint(result)
