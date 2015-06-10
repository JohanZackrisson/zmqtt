import json
import ast

indata = '{"foo": "bar"}'
j = json.loads(indata)
print(j)

sj = str(j)
print(sj)


oj = ast.literal_eval("fnord")
print(oj)

print json.dumps(j)
