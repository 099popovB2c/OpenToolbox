import ast,pathlib,unittest,sys
p=pathlib.Path(__file__).parents[1]/'opentoolbox.py';sys.path.insert(0,str(p.parent));import opentoolbox
class T(unittest.TestCase):
 def test_syntax(self):ast.parse(p.read_text())
 def test_preset(self):
  c=opentoolbox.compress_cmd('ffmpeg','in.mp4','out.mp4','Smaller file');self.assertIn('28',c);self.assertEqual(c[-1],'out.mp4')
 def test_audio_download(self):self.assertIn('--audio-format',opentoolbox.download_cmd('yt-dlp','x','.',True))
if __name__=='__main__':unittest.main()
