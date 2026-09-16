#!/usr/bin/env python3
import os,shutil,subprocess,threading,tkinter as tk
from tkinter import filedialog,messagebox,ttk
TOOLS={'ffmpeg':['ffmpeg'],'imagemagick':['magick','convert'],'exiftool':['exiftool'],'yt-dlp':['yt-dlp'],'pandoc':['pandoc']}
def which_group(names):
 for n in names:
  p=shutil.which(n)
  if p:return p
 return None
class App(tk.Tk):
 def __init__(self):
  super().__init__();self.title('OpenToolbox');self.geometry('720x520');self.paths={k:which_group(v) for k,v in TOOLS.items()};self.build()
 def build(self):
  ttk.Label(self,text='OpenToolbox',font=('TkDefaultFont',22,'bold')).pack(anchor='w',padx=18,pady=(18,4));ttk.Label(self,text='Useful open-source tools without memorizing commands.').pack(anchor='w',padx=18)
  f=ttk.Frame(self);f.pack(fill='x',padx=18,pady=12)
  for k,v in self.paths.items():ttk.Label(f,text=f"{'✓' if v else '✗'} {k}: {v or 'not found'}").pack(anchor='w')
  g=ttk.LabelFrame(self,text='Actions');g.pack(fill='x',padx=18,pady=8)
  actions=[('Compress video','ffmpeg',self.compress),('Extract MP3','ffmpeg',self.audio),('Convert image','imagemagick',self.image),('Remove metadata','exiftool',self.metadata),('Download media URL','yt-dlp',self.download),('Convert document','pandoc',self.document)]
  for i,(label,tool,fn) in enumerate(actions):
   b=ttk.Button(g,text=label,command=fn);b.grid(row=i//2,column=i%2,padx=8,pady=8,sticky='ew');b['state']='normal' if self.paths[tool] else 'disabled'
  g.columnconfigure(0,weight=1);g.columnconfigure(1,weight=1)
  self.log=tk.Text(self,height=14);self.log.pack(fill='both',expand=True,padx=18,pady=10)
 def run(self,cmd):
  self.log.insert('end','$ '+' '.join(cmd)+'\n');self.log.see('end')
  def work():
   try:
    p=subprocess.run(cmd,capture_output=True,text=True);out=(p.stdout+'\n'+p.stderr).strip();self.after(0,lambda:self.done(out,p.returncode))
   except Exception as e:self.after(0,lambda:messagebox.showerror('Error',str(e)))
  threading.Thread(target=work,daemon=True).start()
 def done(self,out,code):self.log.insert('end',out+'\n'+('Done.\n' if code==0 else f'Exit code {code}\n'));self.log.see('end')
 def pick(self,title):return filedialog.askopenfilename(title=title)
 def compress(self):
  src=self.pick('Choose video');
  if not src:return
  dst=filedialog.asksaveasfilename(defaultextension='.mp4');
  if dst:self.run([self.paths['ffmpeg'],'-y','-i',src,'-c:v','libx264','-crf','28','-preset','medium','-c:a','aac','-b:a','128k',dst])
 def audio(self):
  src=self.pick('Choose video/audio');
  if not src:return
  dst=filedialog.asksaveasfilename(defaultextension='.mp3');
  if dst:self.run([self.paths['ffmpeg'],'-y','-i',src,'-vn','-codec:a','libmp3lame','-q:a','2',dst])
 def image(self):
  src=self.pick('Choose image');
  if not src:return
  dst=filedialog.asksaveasfilename(defaultextension='.webp');
  if dst:self.run([self.paths['imagemagick'],src,dst])
 def metadata(self):
  src=self.pick('Choose file');
  if src and messagebox.askyesno('Confirm','Remove metadata in place? ExifTool keeps a backup copy by default.'):
   self.run([self.paths['exiftool'],'-all=',src])
 def download(self):
  win=tk.Toplevel(self);win.title('Download URL');v=tk.StringVar();ttk.Entry(win,textvariable=v,width=70).pack(padx=12,pady=12)
  def go():
   url=v.get().strip();win.destroy()
   if url:self.run([self.paths['yt-dlp'],'-P',str(os.path.expanduser('~/Downloads')),url])
  ttk.Button(win,text='Download',command=go).pack(pady=(0,12))
 def document(self):
  src=self.pick('Choose document');
  if not src:return
  dst=filedialog.asksaveasfilename(defaultextension='.md');
  if dst:self.run([self.paths['pandoc'],src,'-o',dst])
if __name__=='__main__':App().mainloop()
