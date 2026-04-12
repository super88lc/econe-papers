#!/usr/bin/env python3
import re

result = '{"test": 1}'
m = re.search(r'\{[\s\S]*?\}', result)
print(m.group())
