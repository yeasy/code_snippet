import json

obj = [[1,2,3],123,123.123,'abc',{'key1':(1,2,3),'key2':(4,5,6)}]

print "original obj =", repr(obj)

#use dumps to encode object into json format, sorting the dict key, and ignore non-str keys
json_encoded = json.dumps(obj,sort_keys=True,,skipkeys=True)

print "after json encoding"
print "obj = ",json_encoded

#use loads to decode json format into original object
json_decoded = json.loads(json_encoded)

print type(json_decoded)

print "after json decoding"
print "obj = ",json_decoded
