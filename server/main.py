import os,json,threading,time,cv2,numpy as np
from flask import Flask,render_template,Response,jsonify,request
from vision.camera import Camera
from vision.stabilization import ModelStabilizer
from vision.water_detector import analyze,Trend
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); CFG=os.path.join(BASE,'config/model.json')
app=Flask(__name__,template_folder=os.path.join(BASE,'web'),static_folder=os.path.join(BASE,'web'))
cam=None; latest=None; state={'tracking':False,'markers':0,'regions':{},'flood_status':'WAITING'}; lock=threading.Lock(); prev={}; trends={x:Trend() for x in ('river','drain','land')}
def cfg():
    with open(CFG) as f:return json.load(f)
def save(x):
    with open(CFG,'w') as f:json.dump(x,f,indent=2)
def draw(frame,s,found):
    out=frame.copy(); cols={'river':(255,100,0),'drain':(0,200,255),'land':(0,220,0)}
    for i,p in found.items():
        x,y=map(int,p);cv2.circle(out,(x,y),7,(0,220,255),-1);cv2.putText(out,f'M{i}',(x+8,y),0,.5,(0,220,255),2)
    for n,d in s.get('regions',{}).items():
        p=d['polygon']
        if len(p)>=3:
            pts=np.array(p,np.int32);cv2.polylines(out,[pts],True,cols[n],2);x,y=pts[0];cv2.putText(out,f'{n.upper()} {d["water_percent"]:.1f}%',(int(x),max(20,int(y)-7)),0,.5,cols[n],2)
    cv2.rectangle(out,(10,10),(350,48),(20,20,20),-1);cv2.putText(out,s.get('flood_status','WAITING'),(18,37),0,.65,(0,255,0) if s.get('flood_status')=='NORMAL' else (0,160,255),2)
    return out
def loop():
    global cam,latest,state
    c=cfg(); stab=ModelStabilizer(c['canonical_width'],c['canonical_height']); cam=Camera()
    while True:
        try:
            raw=cam.read(); frame,found,tracking=stab.stabilize(raw)
            if frame is None:frame=raw
            s={'tracking':tracking,'markers':len(found),'regions':{},'flood_status':'NORMAL' if tracking else 'SEARCHING'}
            if tracking:
                high=False
                for n in ('river','drain','land'):
                    poly=c.get('regions',{}).get(n,[]); wp,ch,m=analyze(frame,poly,prev.get(n));prev[n]=m;t=trends[n].update(wp)
                    s['regions'][n]={'polygon':poly,'water_percent':round(wp,2),'change_percent':round(ch,2),'trend':t}
                    if wp>55 or ch>15:high=True
                if high:s['flood_status']='HIGH WATER CHANGE'
            ok,e=cv2.imencode('.jpg',draw(frame,s,found),[cv2.IMWRITE_JPEG_QUALITY,80])
            with lock:
                if ok:latest=e.tobytes()
                state=s
        except Exception as e:
            with lock:state={'tracking':False,'error':str(e)}
            time.sleep(1)
def video():
    while True:
        with lock:f=latest
        if f:yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n'+f+b'\r\n'
        time.sleep(.05)
@app.route('/')
def index():return render_template('index.html')
@app.route('/video')
def vid():return Response(video(),mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/api/state')
def api():
    with lock:return jsonify(state)
@app.post('/api/regions')
def regions():
    c=cfg();c['regions']=request.get_json(force=True).get('regions',{});save(c);return jsonify(ok=True)
if __name__=='__main__':
    threading.Thread(target=loop,daemon=True).start();app.run(host='0.0.0.0',port=5000,threaded=True)
