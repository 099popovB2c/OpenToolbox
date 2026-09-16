import pathlib,tempfile,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]));import queuectl
class T(unittest.TestCase):
 def jobs(self):
  return [{'id':'1','label':'compress','cmd':['x'],'status':'done','attempts':1,'started_at':10,'finished_at':20},{'id':'2','label':'compress','cmd':['x'],'status':'failed','attempts':1,'started_at':30,'finished_at':50},{'id':'3','label':'image','cmd':['x'],'status':'pending','attempts':0}]
 def test_stats(self):
  s=queuectl.job_stats(self.jobs());self.assertEqual(s['counts']['done'],1);self.assertEqual(s['success_rate'],.5);self.assertEqual(s['average_duration_seconds'],15)
 def test_retry_one(self):
  j=self.jobs();self.assertEqual(queuectl.retry_failed(j,['2']),['2']);self.assertEqual(j[1]['status'],'pending');self.assertNotIn('finished_at',j[1])
 def test_prune_preserves_live(self):
  j=self.jobs();out=queuectl.prune_jobs(j,1);self.assertTrue(any(x['id']=='3' for x in out));self.assertEqual(len(out),2)
 def test_run_pending(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'q.json';jobs=[{'id':'x','label':'test','cmd':[sys.executable,'-c','print("ok")'],'status':'pending','attempts':0}];queuectl.save_queue(p,jobs);r=queuectl.run_pending(p);self.assertEqual(r[0]['status'],'done');self.assertIn('ok',r[0]['output']);self.assertEqual(queuectl.load_queue(p)[0]['attempts'],1)
 def test_invalid_command_fails(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'q.json';queuectl.save_queue(p,[{'id':'x','status':'pending','cmd':[]}]);r=queuectl.run_pending(p);self.assertEqual(r[0]['status'],'failed')
if __name__=='__main__':unittest.main()
