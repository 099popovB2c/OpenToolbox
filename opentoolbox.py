#!/usr/bin/env python3
import json,os,shlex,shutil,subprocess,threading,time,tkinter as tk
from pathlib import Path
from tkinter import filedialog,messagebox,simpledialog,ttk
VERSION='0.3.0';TOOLS={'ffmpeg':['ffmpeg'],'ffprobe':['ffprobe'],'imagemagick':['magick','convert'],'exiftool':['exiftool'],'yt-dlp':['yt-dlp'],'pandoc':['pandoc']};VIDEO_PRESETS={'High quality':('20','slow'),'Balanced':('23','medium'),'Smaller file':('28','medium')};QUEUE_FILE=Path.home()/'.opentoolbox'/'queue.json'
def which_group(names):
 for n in names:
  p=shutil.which(n)
  if p:return p
 return None
def quote_cmd(cmd):return subprocess.list2cmdline(cmd) if os.name=='nt' else shlex.join(cmd)
def compress_cmd(ffmpeg,src,dst,preset='Balanced'):
 crf,speed=VIDEO_PRESETS[preset];return [ffmpeg,'-y','-i',src,'-c:v','libx264','-crf',crf,'-preset',speed,'-c:a','aac','-b:a','128k',dst]
def audio_cmd(ffmpeg,src,dst):return [ffmpeg,'-y','-i',src,'-vn','-codec:a','libmp3lame','-q:a','2',dst]
def trim_cmd(ffmpeg,src,dst,start,end):return [ffmpeg,'-y','-ss',start,'-to',end,'-i',src,'-c','copy',dst]
def probe_cmd(ffprobe,src):return [ffprobe,'-v','quiet','-print_format','json','-show_format','-show_streams',src]
def image_cmd(tool,src,dst):return [tool,src,dst]
def metadata_cmd(tool,src):return [tool,'-all=',src]
def download_cmd(tool,url,outdir,audio=False):return [tool,'-x','--audio-format','mp3','-P',outdir,url] if audio else [tool,'-P',outdir,url]
def document_cmd(tool,src,dst):return [tool,src,'-o',dst]
def output_name(src,template='{stem}.webp'):
 p=Path(src);return template.format(stem=p.stem,name=p.name,suffix=p.suffix.lstrip('.'))
class QueueStore:
 def __init__(self,path=QUEUE_FILE):self.path=Path(path);self.jobs=self._load();self.recover()
 def _load(self):
  try:return json.loads(self.path.read_text()).get('jobs',[])
  except:return []
 def save(self):self.path.parent.mkdir(parents=True,exist_ok=True);self.path.write_text(json.dumps({'version':1,'jobs':self.jobs},indent=2),encoding='utf8')
 def recover(self):
  changed=False
  for j in self.jobs:
   if j.get('status')=='running':j['status']='pending';changed=True
  if changed:self.save()
 def add(self,cmd,label='job'):
  j={'id':str(time.time_ns()),'label':label,'cmd':list(cmd),'status':'pending','created_at':int(time.time()),'attempts':0};self.jobs.append(j);self.save();return j
 def set(self,j,status,**extra):j.update(status=status,**extra);self.save()
 def failed(self):return [j for j in self.jobs if j.get('status')=='failed']
class App(tk.Tk):
 def __init__(self):
  super().__init__();self.title(f'OpenToolbox {VERSION}');self.geometry('840x700');self.paths={k:which_group(v) for k,v in TOOLS.items()};self.current=None;self.cancelled=False;self.preset=tk.StringVar(value='Balanced');self.template=tk.StringVar(value='{stem}.webp');self.queue=QueueStore();self.build()
 def build(self):
  ttk.Label(self,text='OpenToolbox',font=('TkDefaultFont',22,'bold')).pack(anchor='w',padx=18,pady=(18,4));ttk.Label(self,text='Useful open-source tools without memorizing commands.').pack(anchor='w',padx=18)
  f=ttk.Frame(self);f.pack(fill='x',padx=18,pady=10)
  for k,v in self.paths.items():ttk.Label(f,text=f"{'✓' if v else '✗'} {k}: {v or 'not found'}").pack(anchor='w')
  top=ttk.Frame(self);top.pack(fill='x',padx=18);ttk.Label(top,text='Video preset:').pack(side='left');ttk.Combobox(top,textvariable=self.preset,values=list(VIDEO_PRESETS),state='readonly',width=18).pack(side='left',padx=6);ttk.Label(top,text='Batch name:').pack(side='left',padx=(14,2));ttk.Entry(top,textvariable=self.template,width=20).pack(side='left');ttk.Button(top,text='Diagnostics',command=self.diagnostics).pack(side='right')
  g=ttk.LabelFrame(self,text='Actions');g.pack(fill='x',padx=18,pady=8)
  actions=[('Compress video','ffmpeg',self.compress),('Trim video','ffmpeg',self.trim),('Inspect media','ffprobe',self.inspect_media),('Extract MP3','ffmpeg',self.audio),('Convert image','imagemagick',self.image),('Batch images → WebP','imagemagick',self.batch_images),('Remove metadata (batch)','exiftool',self.metadata),('Download media URL','yt-dlp',self.download),('Convert document','pandoc',self.document)]
  for i,(label,tool,fn) in enumerate(actions):
   b=ttk.Button(g,text=label,command=fn);b.grid(row=i//2,column=i%2,padx=8,pady=8,sticky='ew');b['state']='normal' if self.paths[tool] else 'disabled'
  g.columnconfigure(0,weight=1);g.columnconfigure(1,weight=1)
  ctr=ttk.Frame(self);ctr.pack(fill='x',padx=18);ttk.Button(ctr,text='Show queue',command=self.show_queue).pack(side='left');ttk.Button(ctr,text='Retry failed',command=self.retry_failed).pack(side='left',padx=6);ttk.Button(ctr,text='Cancel current job',command=self.cancel).pack(side='right')
  self.log=tk.Text(self,height=19);self.log.pack(fill='both',expand=True,padx=18,pady=10)
 def logline(self,s):self.log.insert('end',s+'\n');self.log.see('end')
 def run_jobs(self,jobs):
  if not jobs:return
  self.cancelled=False
  def work():
   for j in jobs:
    if self.cancelled:break
    cmd=j['cmd'];self.queue.set(j,'running',attempts=int(j.get('attempts',0))+1,started_at=int(time.time()));self.after(0,lambda c=cmd:self.logline('$ '+quote_cmd(c)))
    try:
     self.current=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,errors='replace');out,_=self.current.communicate();code=self.current.returncode;status='done' if code==0 else 'failed';self.queue.set(j,status,exit_code=code,output=(out or '')[-4000:],finished_at=int(time.time()));self.after(0,lambda o=out,c=code:self.logline((o.strip()+'\n' if o and o.strip() else '')+('Done.' if c==0 else f'Exit code {c}')))
    except Exception as e:self.queue.set(j,'failed',error=str(e),finished_at=int(time.time()));self.after(0,lambda e=e:messagebox.showerror('Error',str(e)))
    finally:self.current=None
   if self.cancelled:self.after(0,lambda:self.logline('Cancelled. Pending jobs stay in queue.'))
  threading.Thread(target=work,daemon=True).start()
 def run_queue(self,commands,label='job'):self.run_jobs([self.queue.add(c,label) for c in commands])
 def retry_failed(self):
  jobs=self.queue.failed()
  for j in jobs:self.queue.set(j,'pending')
  self.run_jobs(jobs)
 def show_queue(self):
  win=tk.Toplevel(self);win.title('Persistent job queue');t=tk.Text(win,width=100,height=24);t.pack(fill='both',expand=True);t.insert('1.0','\n'.join(f"{j.get('status','?'):<8} {j.get('label','job'):<18} attempts={j.get('attempts',0)}  {quote_cmd(j.get('cmd',[]))}" for j in self.queue.jobs[-100:]) or 'Queue is empty.')
 def cancel(self):
  self.cancelled=True
  if self.current and self.current.poll() is None:self.current.terminate()
 def pick(self,title,multiple=False):return filedialog.askopenfilenames(title=title) if multiple else filedialog.askopenfilename(title=title)
 def compress(self):
  src=self.pick('Choose video');dst=filedialog.asksaveasfilename(defaultextension='.mp4') if src else ''
  if dst:self.run_queue([compress_cmd(self.paths['ffmpeg'],src,dst,self.preset.get())],'compress')
 def trim(self):
  src=self.pick('Choose video')
  if not src:return
  start=simpledialog.askstring('Trim','Start time (e.g. 00:00:05)',initialvalue='00:00:00');end=simpledialog.askstring('Trim','End time (e.g. 00:01:00)',initialvalue='00:01:00')
  if not start or not end:return
  dst=filedialog.asksaveasfilename(defaultextension='.mp4')
  if dst:self.run_queue([trim_cmd(self.paths['ffmpeg'],src,dst,start,end)],'trim')
 def inspect_media(self):
  src=self.pick('Choose media')
  if not src:return
  def work():
   try:
    r=subprocess.run(probe_cmd(self.paths['ffprobe'],src),capture_output=True,text=True,timeout=30,check=True);d=json.loads(r.stdout);fmt=d.get('format',{});streams=d.get('streams',[]);summary={'file':src,'format':fmt.get('format_long_name') or fmt.get('format_name'),'duration_seconds':fmt.get('duration'),'size_bytes':fmt.get('size'),'bit_rate':fmt.get('bit_rate'),'streams':[{'type':s.get('codec_type'),'codec':s.get('codec_name'),'width':s.get('width'),'height':s.get('height'),'sample_rate':s.get('sample_rate'),'channels':s.get('channels')} for s in streams]};self.after(0,lambda:self.logline(json.dumps(summary,indent=2)))
   except Exception as e:self.after(0,lambda:messagebox.showerror('ffprobe',str(e)))
  threading.Thread(target=work,daemon=True).start()
 def audio(self):
  src=self.pick('Choose video/audio');dst=filedialog.asksaveasfilename(defaultextension='.mp3') if src else ''
  if dst:self.run_queue([audio_cmd(self.paths['ffmpeg'],src,dst)],'audio')
 def image(self):
  src=self.pick('Choose image');dst=filedialog.asksaveasfilename(defaultextension='.webp') if src else ''
  if dst:self.run_queue([image_cmd(self.paths['imagemagick'],src,dst)],'image')
 def batch_images(self):
  srcs=self.pick('Choose images',True)
  if not srcs:return
  out=filedialog.askdirectory(title='Choose output folder')
  if out:self.run_queue([image_cmd(self.paths['imagemagick'],s,str(Path(out)/output_name(s,self.template.get()))) for s in srcs],'batch-image')
 def metadata(self):
  srcs=self.pick('Choose files',True)
  if srcs and messagebox.askyesno('Confirm','Remove metadata from selected files? ExifTool keeps backup copies by default.'):self.run_queue([metadata_cmd(self.paths['exiftool'],s) for s in srcs],'metadata')
 def download(self):
  win=tk.Toplevel(self);win.title('Download URL');v=tk.StringVar();audio=tk.BooleanVar();ttk.Entry(win,textvariable=v,width=70).pack(padx=12,pady=12);ttk.Checkbutton(win,text='Audio only (MP3)',variable=audio).pack(anchor='w',padx=12)
  def go():
   url=v.get().strip();a=audio.get();win.destroy()
   if url:self.run_queue([download_cmd(self.paths['yt-dlp'],url,str(Path.home()/'Downloads'),a)],'download')
  ttk.Button(win,text='Download',command=go).pack(pady=12)
 def document(self):
  src=self.pick('Choose document');dst=filedialog.asksaveasfilename(defaultextension='.md') if src else ''
  if dst:self.run_queue([document_cmd(self.paths['pandoc'],src,dst)],'document')
 def diagnostics(self):
  self.logline('--- Tool diagnostics ---')
  for k,p in self.paths.items():
   if not p:self.logline(f'{k}: not installed');continue
   try:r=subprocess.run([p,'--version'],capture_output=True,text=True,timeout=3);first=(r.stdout or r.stderr).splitlines()[0] if (r.stdout or r.stderr) else p;self.logline(f'{k}: {first}')
   except Exception:self.logline(f'{k}: {p}')
if __name__=='__main__':App().mainloop()
