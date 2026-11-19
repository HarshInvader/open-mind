# Label-blind: why are Rome channels marked bad? Reads EEG tails only; no labels.
import sys, json, numpy as np
sys.path.insert(0, sys.argv[1])
import extract as E
from scipy.signal import butter, sosfiltfilt, detrend
rs=[json.loads(l) for l in open(sys.argv[1]+"/features/Rome.jsonl")]
drop=[r for r in rs if r["status"].startswith("dropped")][:5]
okr=[r for r in rs if r["status"]=="ok" and r["n_good"]<24][:2]
idx=E.member_index("Rome"); zips={}
for r in drop+okr:
    url,member,off,csz,usz,zsize=E.find_member(idx,r["file"])
    z=zips.setdefault(url,E.RemoteZip(url,size=zsize))
    h0=z.read(member,max_out=256,chunk=65536); ns=int(h0[252:256])
    h=E.parse_edf_header(z.read(member,max_out=256*(ns+1),chunk=65536)); h["usize"]=usz
    ch,names,fs=E.select_channels("Rome",h); recb=int(h["nsamp"].sum())*2
    pos0,data,taint,_=E.read_tail(url,off,csz,usz,int(40/h["recdur"]+2)*recb+65536)
    lt=int(np.nonzero(taint)[0].max())+1 if taint.any() else 0
    X,_=E.decode(data[lt:],pos0+lt,h,ch,fs,40.0)
    w=E.win(X,fs,-22,-2)
    def crit(w):
        sd=w.std(1); return int((sd<0.5).sum()),int((sd>200).sum()),int((np.abs(w).max(1)>1000).sum()), int(((sd>=0.5)&(sd<=200)&(np.abs(w).max(1)<=1000)).sum())
    sos=butter(2,0.5,'hp',fs=fs,output='sos'); Xh=sosfiltfilt(sos,X,axis=1); wh=E.win(Xh,fs,-22,-2)
    print(r["status"][:7], "fs",fs,"n",len(names),"raw lowSD/highSD/max>1000/good",crit(w),
          "| detrended",crit(detrend(w,axis=1)),"| hp0.5",crit(wh),
          "| median|mean| uV",round(float(np.median(np.abs(w.mean(1)))),1),
          "| medSD raw/hp",round(float(np.median(w.std(1))),1),round(float(np.median(wh.std(1))),1), flush=True)
