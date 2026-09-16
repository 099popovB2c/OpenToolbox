import unittest,tempfile,pathlib,sys
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]));import opentoolbox
class T(unittest.TestCase):
 def test_commands(self):
  self.assertIn('-crf',opentoolbox.compress_cmd('ffmpeg','a','b'));self.assertIn('-ss',opentoolbox.trim_cmd('ffmpeg','a','b','00:00:01','00:00:02'));self.assertIn('-show_streams',opentoolbox.probe_cmd('ffprobe','a'))
 def test_name_template(self):self.assertEqual(opentoolbox.output_name('/tmp/photo.jpg','{stem}-small.webp'),'photo-small.webp')
 def test_queue_persists_and_recovers(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'q.json';q=opentoolbox.QueueStore(p);j=q.add(['echo','x'],'test');q.set(j,'running');q2=opentoolbox.QueueStore(p);self.assertEqual(q2.jobs[0]['status'],'pending')
if __name__=='__main__':unittest.main()
