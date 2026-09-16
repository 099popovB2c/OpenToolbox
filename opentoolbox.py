#!/usr/bin/env python3
import os,shlex,shutil,subprocess,threading,tkinter as tk
from pathlib import Path
from tkinter import filedialog,messagebox,ttk
TOOLS={'ffmpeg':['ffmpeg'],'imagemagick':['magick','convert'],'exiftool':['exiftool'],'yt-dlp':['yt-dlp'],'pandoc':['pandoc']}
VIDEO_PRESETS={'High quality':('20','slow'),'Balanced':('23','medium'),'Smaller file':('28','medium')}
def which_group(names):
 for n in names:
  p=shutil.which(n)
  if p:return p
 return None
def quote_cmd(cmd):return subprocess.list2cmdline(cmd) if os.name=='nt' else shlex.join(cmd)
def compress_cmd(ffmpeg,src,dst,preset='Balanced'):
 crf,speed=VIDEO_PRESETS[preset];return [ffmpeg,'-y','-i',src,'-c:v','libx264','-crf',crf,'-preset',speed,'-c:a','aac','-b:a','128k',dst]
def audio_cmd(ffmpeg,src,dst):return [ffmpeg,'-y','-i',src,'-vn','-codec:a','libmp3lame','-q:a','2',dst]
def image_cmd(tool,src,dst):return [tool,src,dst]
def metadata_cmd(tool,src):return [tool,'-all=',src]
def download_cmd(tool,url,outdir,audio=False):return [tool,'-x','--audio-format','mp3','-P',outdir,url] if audio else [tool,'-P',outdir,url]
def document_cmd(tool,src,dst):return [tool,src,'-o',dst]
class App(tk.Tk):
 def __init__(self):
  super().__init__();self.title('OpenToolbox');self.geometry('780x610');self.paths={k:which_group(v) for k,v in TOOLS.items()};self.current=None;self.cancelled=False;self.preset=tk.StringVar(value='Balanced');self.build()
 def build(self):
  ttk.Label(self,text='OpenToolbox',font=('TkDefaultFont',22,'bold')).pack(anchor='w',padx=18,pady=(18,4));ttk.Label(self,text='Useful open-source tools without memorizing commands.').pack(anchor='w',padx=18)
  f=ttk.Frame(self);f.pack(fill='x',padx=18,pady=10)
  for k,v in self.paths.items():ttk.Label(f,text=f"{'✓' if v else '✗'} {k}: {v or 'not found'}").pack(anchor='w')
  top=ttk.Frame(self);top.pack(fill='x',padx=18);ttk.Label(top,text='Video preset:').pack(side='left');ttk.Combobox(top,textvariable=self.preset,values=list(VIDEO_PRESETS),state='readonly',width=18).pack(side='left',padx=6);ttk.Button(top,text='Tool diagnostics',command=self.diagnostics).pack(side='right')
  g=ttk.LabelFrame(self,text='Actions');g.pack(fill='x',padx=18,pady=8)
  actions=[('Compress video','ffmpeg',self.compress),('Extract MP3','ffmpeg',self.audio),('Convert image','imagemagick',self.image),('Batch images → WebP','imagemagick',self.batch_images),('Remove metadata (batch)','exiftool',self.metadata),('Download media URL','yt-dlp',self.download),('Convert document','pandoc',self.document)]
  for i,(label,tool,fn) in enumerate(actions):
   b=ttk.Button(g,text=label,command=fn);b.grid(row=i//2,column=i%2,padx=8,pady=8,sticky='ew');b['state']='normal' if self.paths[tool] else 'disabled'
  g.columnconfigure(0,weight=1);g.columnconfigure(1,weight=1)
  ctr=ttk.Frame(self);ctr.pack(fill='x',padx=18);ttk.Button(ctr,text='Cancel current job',command=self.cancel).pack(side='right')
  self.log=tk.Text(self,height=17);self.log.pack(fill='both',expand=True,padx=18,pady=10)
 def logline(self,s):self.log.insert('end',s+'\n');self.log.see('end')
 def run_queue(self,commands):
  if not commands:return
  self.cancelled=False
  def work():
   for cmd in commands:
    if self.cancelled:break
    self.after(0,lambda c=cmd:self.logline('$ '+quote_cmd(c)))
    try:
     self.current=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,errors='replace');out,_=self.current.communicate();code=self.current.returncode;self.after(0,lambda o=out,c=code:self.logline((o.strip()+'\n' if o.strip() else '')+('Done.' if c==0 else f'Exit code {c}')))
    except Exception as e:self.after(0,lambda e=e:messagebox.showerror('Error',str(e)))
    finally:self.current=None
   if self.cancelled:self.after(0,lambda:self.logline('Cancelled.'))
  threading.Thread(target=work,daemon=True).start()
 def cancel(self):
  self.cancelled=True
  if self.current and self.current.poll() is None:self.current.terminate()
 def pick(self,title,multiple=False):return filedialog.askopenfilenames(title=title) if multiple else filedialog.askopenfilename(title=title)
 def compress(self):
  src=self.pick('Choose video');
  if not src:return
  dst=filedialog.asksaveasfilename(defaultextension='.mp4');
  if dst:self.run_queue([compress_cmd(self.paths['ffmpeg'],src,dst,self.preset.get())])
 def audio(self):
  src=self.pick('Choose video/audio');
  if not src:return
  dst=filedialog.asksaveasfilename(defaultextension='.mp3');
  if dst:self.run_queue([audio_cmd(self.paths['ffmpeg'],src,dst)])
 def image(self):
  src=self.pick('Choose image');
  if not src:return
  dst=filedialog.asksaveasfilename(defaultextension='.webp');
  if dst:self.run_queue([image_cmd(self.paths['imagemagick'],src,dst)])
 def batch_images(self):
  srcs=self.pick('Choose images',True)
  if not srcs:return
  out=filedialog.askdirectory(title='Choose output folder')
  if out:self.run_queue([image_cmd(self.paths['imagemagick'],s,str(Path(out)/(Path(s).stem+'.webp'))) for s in srcs])
 def metadata(self):
  srcs=self.pick('Choose files',True)
  if srcs and messagebox.askyesno('Confirm','Remove metadata from selected files? ExifTool keeps backup copies by default.'):self.run_queue([metadata_cmd(self.paths['exiftool'],s) for s in srcs])
 def download(self):
  win=tk.Toplevel(self);win.title('Download URL');v=tk.StringVar();audio=tk.BooleanVar();ttk.Entry(win,textvariable=v,width=70).pack(padx=12,pady=12);ttk.Checkbutton(win,text='Audio only (MP3)',variable=audio).pack(anchor='w',padx=12)
  def go():
   url=v.get().strip();a=audio.get();win.destroy()
   if url:self.run_queue([download_cmd(self.paths['yt-dlp'],url,str(Path.home()/'Downloads'),a)])
  ttk.Button(win,text='Download',command=go).pack(pady=12)
 def document(self):
  src=self.pick('Choose document');
  if not src:return
  dst=filedialog.asksaveasfilename(defaultextension='.md');
  if dst:self.run_queue([document_cmd(self.paths['pandoc'],src,dst)])
 def diagnostics(self):
  self.logline('--- Tool diagnostics ---')
  for k,p in self.paths.items():
   if not p:self.logline(f'{k}: not installed');continue
   try:
    r=subprocess.run([p,'--version'],capture_output=True,text=True,timeout=3);first=(r.stdout or r.stderr).splitlines()[0] if (r.stdout or r.stderr) else p;self.logline(f'{k}: {first}')
   except Exception:self.logline(f'{k}: {p}')
if __name__=='__main__':App().mainloop()
