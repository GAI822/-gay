import json,re,cv2,numpy as np,pandas as pd,pytesseract,concurrent.futures as cf
rows=json.load(open('rows.json'))
import threading
TL=threading.local()
def det(w,h):
    if not hasattr(TL,'d'): TL.d=cv2.FaceDetectorYN.create('yunet.onnx','',(w,h),0.8)
    TL.d.setInputSize((w,h)); return TL.d
EMO=re.compile('[\U0001F000-\U0001FAFF☀-➿]')
def img(r):
    im=cv2.imread(f"th/{r['id']}.jpg")
    if im is None: return {}
    h,w=im.shape[:2]; hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV); g=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
    b,gg,rr=[c.astype(float) for c in cv2.split(im)]
    rg=rr-gg; yb=.5*(rr+gg)-b
    colorful=np.sqrt(rg.std()**2+yb.std()**2)+.3*np.sqrt(rg.mean()**2+yb.mean()**2)
    ff=det(w,h).detect(im)[1]
    faces=[] if ff is None else [f for f in ff if f[2]>w*.06]
    fa=max([f[2]*f[3] for f in faces],default=0)/(w*h)
    d=pytesseract.image_to_data(im,lang='eng+jpn',output_type=pytesseract.Output.DICT)
    words=[t for t,c in zip(d['text'],d['conf']) if t.strip() and float(c)>70 and len(t.strip())>=2]
    edges=cv2.Canny(g,100,200).mean()/255
    return dict(bright=g.mean(),contrast=g.std(),sat=hsv[...,1].mean(),colorful=colorful,
      faces=len(faces),face_area=fa,ocr_words=len(words),edge_density=edges,
      red_share=float(((hsv[...,0]<10)|(hsv[...,0]>170)).__and__(hsv[...,1]>100).mean()))
def title(t):
    return dict(t_len=len(t),t_emoji=len(EMO.findall(t)),t_hash=len(re.findall(r'#\w+',t)),
      t_q=int('?' in t or '？' in t),t_ex=int('!' in t or '！' in t),t_num=int(bool(re.search(r'\d',t))),
      t_jp=int(bool(re.search(r'[぀-ヿ一-鿿]',t))),
      t_caps=len([w for w in re.findall(r'[A-Za-z]{3,}',t) if w.isupper()]),
      t_you=int(bool(re.search(r'\b(you|your)\b',t,re.I))),t_i=int(bool(re.search(r'\b(I|my|me)\b',t))),
      t_vs=int(bool(re.search(r'\bvs\b|対決',t,re.I))),t_pov=int('pov' in t.lower()))
def one(r):
    d={**{k:r[k] for k in ['id','channel','title','views','idx']},**title(r['title'])}
    try: d.update(img(r))
    except Exception as e: d['err']=str(e)[:80]
    return d
import os
done=set()
if os.path.exists('feat.jsonl'): done={json.loads(l)['id'] for l in open('feat.jsonl')}
todo=[r for r in rows if r['id'] not in done]
with open('feat.jsonl','a') as fo, cf.ThreadPoolExecutor(os.cpu_count()) as ex:
    for i,d in enumerate(ex.map(one,todo)):
        fo.write(json.dumps(d,default=float,ensure_ascii=False)+'\n'); fo.flush()
        if i%100==0: print('progress',len(done)+i,flush=True)
pd.DataFrame([json.loads(l) for l in open('feat.jsonl')]).to_csv('features.csv',index=False); print('DONE',len(rows))
