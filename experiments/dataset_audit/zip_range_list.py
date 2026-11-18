import sys, struct, urllib.request
url=sys.argv[1]; size=int(sys.argv[2])
def rng(a,b):
    req=urllib.request.Request(url,headers={'Range':f'bytes={a}-{b}'})
    r=urllib.request.urlopen(req,timeout=60); return r.status, r.read()
st,tail=rng(size-70000,size-1); print('status',st,len(tail))
i=tail.rfind(b'PK\x05\x06'); z64=tail.rfind(b'PK\x06\x06')
if z64>=0:
    cd_size,cd_off=struct.unpack('<QQ',tail[z64+40:z64+56])
else:
    cd_size,cd_off=struct.unpack('<II',tail[i+12:i+20])
print('cd',cd_size,cd_off)
st,cd=rng(cd_off,cd_off+cd_size-1); p=0; n=0; tot=0
names=[]
while cd[p:p+4]==b'PK\x01\x02':
    csz,usz=struct.unpack('<II',cd[p+20:p+28]); nl,el,cl=struct.unpack('<HHH',cd[p+28:p+34]); name=cd[p+46:p+46+nl].decode()
    names.append((name,csz,usz)); p+=46+nl+el+cl
print(len(names)); 
for n in names[:15]: print(n)
print('...'); 
for n in names[-5:]: print(n)
