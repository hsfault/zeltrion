import numpy as np, soundfile as sf, json, sys, os
ALT=len(sys.argv)>1 and sys.argv[1]=='alt'
OUT='audio_alt' if ALT else 'audio'; os.makedirs(OUT,exist_ok=True)
from scipy.signal import resample_poly, fftconvolve, butter, sosfilt
SR=48000; DUR=27.0; N=int(SR*DUR)
rs=np.random.RandomState(11)
t=np.arange(N)/SR
def mtof(m): return 440*2**((m-69)/12)
def env_adsr(n,a,r,sus=1.0):
    e=np.ones(n)*sus; ai=int(a*SR); ri=int(r*SR)
    e[:ai]=np.linspace(0,sus,ai)**1.5 if ai>0 else e[:ai]
    if ri>0: e[-ri:]*=np.linspace(1,0,ri)**1.3
    return e
def lp(x,f,order=2): return sosfilt(butter(order,f,'low',fs=SR,output='sos'),x)
def hp(x,f,order=2): return sosfilt(butter(order,f,'high',fs=SR,output='sos'),x)
def bp(x,lo,hi): return sosfilt(butter(2,[lo,hi],'band',fs=SR,output='sos'),x)

music=np.zeros((N,2)); sfx=np.zeros((N,2))
def add(buf,x,start,gain=1.0,pan=0.0):
    i=int(start*SR); x=x[:max(0,N-i)]
    l=np.cos((pan+1)*np.pi/4); r=np.sin((pan+1)*np.pi/4)
    buf[i:i+len(x),0]+=x*gain*l*1.414; buf[i:i+len(x),1]+=x*gain*r*1.414

# ---------- pad: warm additive saw-ish, 3 detuned voices ----------
def pad_note(m,dur,a=0.9,r=1.1,bright=9):
    n=int(dur*SR); tt=np.arange(n)/SR; f0=mtof(m); out=np.zeros(n)
    for cents in (-7,0,7):
        f=f0*2**(cents/1200); ph=rs.rand()*6.28
        vib=1+0.0018*np.sin(2*np.pi*(0.21+rs.rand()*0.1)*tt)
        for h in range(1,bright+1):
            if f*h>9000: break
            out+=np.sin(2*np.pi*f*h*tt*vib+ph*h)/(h**1.35)
    return out*env_adsr(n,a,r)/3
chords=[ # (start, dur, midi notes)
 (0.0, 3.55,[50,57,60,64,65]),        # Dm(add9) colour
 (3.25,3.65,[46,53,57,62,65]),        # Bbmaj7
 (6.6, 3.7,[43,50,58,62,65]),         # Gm9-ish
 (10.0,4.75,[45,52,57,62,64]),        # Asus
 (14.45,2.4,[50,57,62,65,69]),        # Dm
 (16.6,2.5,[41,53,57,60,64]),         # Fmaj7 (warm)
 (18.75,2.4,[46,53,58,62,65]),        # Bb
 (20.9,2.7,[48,55,60,64,67]),         # C (lift)
 (23.35,3.65,[50,57,62,66,69]),       # D major resolve for the logo
]
for st,du,notes in chords:
    for m in notes:
        add(music,pad_note(m,du+0.5,bright=7 if m<55 else 10),st,0.05,pan=(m%5-2)*0.18)
# sub bass (root) under each chord
for st,du,notes in chords:
    n=int((du+0.4)*SR); tt=np.arange(n)/SR; f=mtof(notes[0]-12)
    x=(np.sin(2*np.pi*f*tt)+0.25*np.sin(2*np.pi*2*f*tt))*env_adsr(n,0.25,0.6)
    add(music,x,st,0.10)
music[:,0]=lp(music[:,0],5200); music[:,1]=lp(music[:,1],5200)

# ---------- soft pulse (kick) + ticks ----------
def kick(gain=1.0):
    n=int(0.45*SR); tt=np.arange(n)/SR
    f=48+70*np.exp(-tt*28); ph=2*np.pi*np.cumsum(f)/SR
    return np.sin(ph)*np.exp(-tt*7.5)*gain
def tick(f=2400,dec=60):
    n=int(0.06*SR); tt=np.arange(n)/SR
    x=np.sin(2*np.pi*f*tt)*np.exp(-tt*dec)+0.4*hp(rs.randn(n),3000)*np.exp(-tt*140)
    return x
BPM=96; beat=60/BPM
b=3.25
while b<23.2:
    add(music,kick(),b,0.22); b+=beat*2
# clock ticks in the hook (one per beat) and accelerating ticks while the hand sweeps an hour
for k in range(5): add(sfx,tick(2600),0.32+k*0.62,0.05,pan=0.2*(-1)**k)
tt_=5.32
while tt_<6.32:
    u=(tt_-5.32)/1.0; add(sfx,tick(2900,70),tt_,0.06,pan=0.25*np.sin(tt_*9)); tt_+=0.16-0.11*np.sin(np.pi*u)
# subtle 8th-note shaker from B to F
b=3.25+beat/2
while b<23.0:
    n=int(0.08*SR); x=hp(rs.randn(n),6000)*np.exp(-np.arange(n)/SR*55)
    add(music,x,b,0.018,pan=0.35); b+=beat

# ---------- SFX ----------
def whoosh(dur=0.7,up=True):
    n=int(dur*SR); x=rs.randn(n); tt=np.arange(n)/SR; u=tt/dur
    out=np.zeros(n); seg=512
    for i in range(0,n,seg):
        c=(400+3500*(u[i] if up else 1-u[i])); out[i:i+seg]=bp(x[max(0,i-2048):i+seg],c*0.6,min(c*1.6,20000))[-len(out[i:i+seg]):]
    return out*np.sin(np.pi*u)**1.6
def ping(f=1318.5,dec=5.5,gain=1.0):
    n=int(1.4*SR); tt=np.arange(n)/SR
    x=np.sin(2*np.pi*f*tt)+0.45*np.sin(2*np.pi*f*2.0*tt)*np.exp(-tt*4)+0.25*np.sin(2*np.pi*f*3.01*tt)*np.exp(-tt*9)
    return x*np.exp(-tt*dec)*np.minimum(1,tt*400)*gain
def boom(f0=55):
    n=int(1.6*SR); tt=np.arange(n)/SR
    f=f0+40*np.exp(-tt*9); ph=2*np.pi*np.cumsum(f)/SR
    return (np.sin(ph)*np.exp(-tt*2.6)+0.3*lp(rs.randn(n),900)*np.exp(-tt*9))
def bell(f=880):
    n=int(3.0*SR); tt=np.arange(n)/SR; x=np.zeros(n)
    for r,a,d in [(1,1,1.6),(2.76,0.5,2.4),(5.4,0.25,3.6),(8.93,0.12,5)]: x+=a*np.sin(2*np.pi*f*r*tt)*np.exp(-tt*d)
    return x*np.minimum(1,tt*300)
def riser(dur):
    n=int(dur*SR); tt=np.arange(n)/SR; u=tt/dur
    x=hp(rs.randn(n),1500)*u**2.2
    tone=sum(np.sin(2*np.pi*(220*k)*(1+u*1.0)*tt) for k in (1,1.5,2))*u**2*0.15
    return (x*0.5+tone)*np.minimum(1,(1-u)*30+0.0)
for st,up in [(3.05,True),(6.45,True),(9.95,False),(14.25,True),(18.55,True)]:
    add(sfx,whoosh(0.75,up),st,0.10,pan=0.3 if up else -0.3)
add(sfx,boom(52),2.40,0.35); add(sfx,whoosh(0.5,False),2.25,0.06)
add(sfx,ping(1318.5),3.45,0.11,pan=0.0)          # lead message arrives
for i,f in enumerate([1174.7,1318.5,1568.0]):     # messages land at the 3 other suppliers
    add(sfx,ping(f,7,0.8),8.05+i*0.24+0.62,0.08,pan=(i-1)*0.6)
add(sfx,ping(1760,6),10.95,0.09,pan=0.1)           # first reply
# phone trill
n=int(0.9*SR); tt=np.arange(n)/SR
trill=(np.sin(2*np.pi*1320*tt)+np.sin(2*np.pi*1660*tt))*(0.5+0.5*np.sign(np.sin(2*np.pi*18*tt)))*np.exp(-tt*2.2)*np.minimum(1,tt*200)
add(sfx,trill,13.15,0.035)
add(sfx,whoosh(0.35,False),14.98,0.12,pan=0.5); add(sfx,ping(1760,6),15.05,0.09,pan=0.3)   # instant reply
add(sfx,boom(58),22.25,0.30); add(sfx,bell(1174.7),22.27,0.035)                           # FAST
add(sfx,riser(1.3),23.05,0.05)
add(sfx,whoosh(1.0,True),23.3,0.08)
add(sfx,bell(587.33),24.62,0.06); add(sfx,bell(880),24.66,0.035,pan=0.4); add(sfx,boom(45),24.6,0.22)
# shimmer on the logo
n=int(2.6*SR); tt=np.arange(n)/SR
sh=sum(np.sin(2*np.pi*f*tt+rs.rand()*6)*(0.5+0.5*np.sin(2*np.pi*(5+k)*tt)) for k,f in enumerate([2349,2794,3520,4186]))*np.exp(-tt*1.4)*np.minimum(1,tt*4)
add(sfx,sh,24.7,0.012,pan=-0.2)

# ---------- reverb ----------
def reverb(x,secs=2.4,mix=0.22):
    n=int(secs*SR); tt=np.arange(n)/SR
    out=np.zeros_like(x)
    for ch in range(2):
        ir=rs.randn(n)*np.exp(-tt*3.2/secs*2.3); ir=lp(ir,6000); ir/=np.sqrt((ir**2).sum())
        out[:,ch]=fftconvolve(x[:,ch],ir)[:len(x)]
    return x*(1-mix)+out*mix*1.4
music=reverb(music,2.8,0.3); sfx=reverb(sfx,2.0,0.22)

# ---------- voice-over placement ----------
tl=json.load(open('timeline_starts.json'))
FILES={k:k for k in tl}
if ALT:
    tl['c1'],tl['c2']=19.05,21.85; FILES['c1'],FILES['c2']='a1','a2'
vo=np.zeros(N)
for k,st in tl.items():
    x,sr=sf.read(f'assets/{FILES[k]}.wav'); x=resample_poly(x,SR,sr)
    i=int(st*SR); vo[i:i+len(x)]+=x[:N-i]
sf.write(f'{OUT}/vo_raw.wav',vo.astype(np.float32),SR)
# ducking envelope from VO
env=np.abs(vo); win=int(0.03*SR); env=np.convolve(env,np.ones(win)/win,'same')
env=np.clip(env/0.05,0,1)
sm=np.zeros_like(env); a_up=1-np.exp(-1/(0.02*SR)); a_dn=1-np.exp(-1/(0.35*SR)); s=0.0
for i in range(len(env)):
    s+= (a_up if env[i]>s else a_dn)*(env[i]-s); sm[i]=s
duck=1-0.45*sm
music*=duck[:,None]
bed=music+sfx
bed=np.tanh(bed*1.2)/1.2
fade=np.ones(N); fo=int(1.2*SR); fade[-fo:]=np.linspace(1,0,fo)**1.5
bed*=fade[:,None]
sf.write(f'{OUT}/bed.wav',bed.astype(np.float32),SR)
print('bed peak',np.abs(bed).max(),'vo peak',np.abs(vo).max())
