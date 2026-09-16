import ast,pathlib,unittest
class T(unittest.TestCase):
 def test_syntax(self):
  p=pathlib.Path(__file__).parents[1]/'opentoolbox.py';ast.parse(p.read_text())
if __name__=='__main__':unittest.main()
