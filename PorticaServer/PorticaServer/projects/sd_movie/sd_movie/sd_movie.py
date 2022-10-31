
import subprocess

command = ["python", "test.py"]
proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, encoding="utf8") 
stdout = proc.communicate(input='one\ntwo\nthree\nfour\nfive\nsix\n')[0]
print(1)