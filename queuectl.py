#!/usr/bin/env python3
import argparse,json,subprocess,time
from collections import Counter
from pathlib import Path

VERSION='0.4.1'
DEFAULT_QUEUE=Path.home()/'.opentoolbox'/'queue.json'
TERMINAL={'done','failed','cancelled'}

def load_queue(path=DEFAULT_QUEUE):
    p=Path(path)
    try:
        d=json.loads(p.read_text(encoding='utf8'))
        jobs=d.get('jobs',[]) if isinstance(d,dict) else []
        return jobs if isinstance(jobs,list) else []
    except Exception:
        return []

def save_queue(path,jobs):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps({'version':1,'jobs':jobs},indent=2),encoding='utf8')

def job_stats(jobs):
    counts=Counter(j.get('status','unknown') for j in jobs)
    terminal=counts['done']+counts['failed']
    durations=[max(0,float(j['finished_at'])-float(j['started_at'])) for j in jobs if j.get('started_at') is not None and j.get('finished_at') is not None]
    labels=Counter(j.get('label','job') for j in jobs)
    return {'total':len(jobs),'counts':dict(counts),'success_rate':round(counts['done']/terminal,3) if terminal else None,'average_duration_seconds':round(sum(durations)/len(durations),2) if durations else None,'by_label':dict(sorted(labels.items()))}

def retry_failed(jobs,ids=None):
    wanted=set(ids or []);changed=[]
    for j in jobs:
        if j.get('status')!='failed':continue
        if wanted and str(j.get('id')) not in wanted:continue
        j['status']='pending';j.pop('exit_code',None);j.pop('error',None);j.pop('finished_at',None);changed.append(str(j.get('id')))
    return changed

def prune_jobs(jobs,keep=100):
    keep=max(0,int(keep));live=[j for j in jobs if j.get('status') not in TERMINAL];terminal=[j for j in jobs if j.get('status') in TERMINAL]
    terminal.sort(key=lambda j:(j.get('finished_at',0),j.get('created_at',0)),reverse=True);chosen=terminal[:keep];selected={id(j) for j in live+chosen};return [j for j in jobs if id(j) in selected]

def clear_done(jobs):return [j for j in jobs if j.get('status')!='done']

def run_pending(path=DEFAULT_QUEUE,limit=0):
    p=Path(path);jobs=load_queue(p);done=[];max_jobs=max(0,int(limit))
    for j in jobs:
        if j.get('status')!='pending':continue
        if max_jobs and len(done)>=max_jobs:break
        cmd=j.get('cmd')
        if not isinstance(cmd,list) or not cmd:
            j.update(status='failed',error='Invalid or empty command',finished_at=int(time.time()));save_queue(p,jobs);done.append(j);continue
        j.update(status='running',attempts=int(j.get('attempts',0))+1,started_at=int(time.time()));save_queue(p,jobs)
        try:
            r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,errors='replace')
            j.update(status='done' if r.returncode==0 else 'failed',exit_code=r.returncode,output=(r.stdout or '')[-4000:],finished_at=int(time.time()))
        except Exception as e:j.update(status='failed',error=str(e),finished_at=int(time.time()))
        save_queue(p,jobs);done.append(j)
    return done

def format_jobs(jobs,limit=100):
    rows=jobs[-max(1,int(limit)):]
    return '\n'.join(f"{str(j.get('id','')):<20} {j.get('status','?'):<9} {j.get('label','job'):<18} attempts={j.get('attempts',0)}  {' '.join(map(str,j.get('cmd',[])))}" for j in rows) or 'Queue is empty.'

def main():
    ap=argparse.ArgumentParser(description='OpenToolbox v0.4 persistent queue controller');ap.add_argument('--queue-file',default=str(DEFAULT_QUEUE));sp=ap.add_subparsers(dest='cmd',required=True);sp.add_parser('stats');ls=sp.add_parser('list');ls.add_argument('--limit',type=int,default=100);rt=sp.add_parser('retry');rt.add_argument('ids',nargs='*');rp=sp.add_parser('run-pending');rp.add_argument('--limit',type=int,default=0);pr=sp.add_parser('prune');pr.add_argument('--keep',type=int,default=100);sp.add_parser('clear-done');ex=sp.add_parser('export');ex.add_argument('path');a=ap.parse_args();path=Path(a.queue_file);jobs=load_queue(path)
    if a.cmd=='stats':print(json.dumps(job_stats(jobs),indent=2))
    elif a.cmd=='list':print(format_jobs(jobs,a.limit))
    elif a.cmd=='retry':
        ids=retry_failed(jobs,a.ids);save_queue(path,jobs);print(f"Requeued {len(ids)} failed job(s).")
    elif a.cmd=='run-pending':
        rows=run_pending(path,a.limit);print(f"Executed {len(rows)} pending job(s).")
        if any(j.get('status')=='failed' for j in rows):raise SystemExit(5)
    elif a.cmd=='prune':
        new=prune_jobs(jobs,a.keep);save_queue(path,new);print(f"Pruned {len(jobs)-len(new)} job(s); {len(new)} remain.")
    elif a.cmd=='clear-done':
        new=clear_done(jobs);save_queue(path,new);print(f"Removed {len(jobs)-len(new)} completed job(s).")
    elif a.cmd=='export':
        out=Path(a.path);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps({'version':1,'jobs':jobs,'stats':job_stats(jobs)},indent=2),encoding='utf8');print(out)
if __name__=='__main__':main()
