import httplib

conn=httplib.HTTPSConnection("127.0.0.1:8080")
conn.request("GET","/index.html")
res=conn.getresponse()
print(res.status,res.reason)
print(res.getheaders())
print(res.read())
