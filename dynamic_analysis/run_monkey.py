import subprocess, threading
import os,signal,sys
import subprocess as sp
from time import sleep

#reference: https://developer.android.com/studio/test/other-testing-tools/monkey
class Command(object):
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None

    def run(self, timeout):
        def target():
            print('Thread started')
            self.process = subprocess.Popen(self.cmd, shell=True, preexec_fn=os.setsid)
            self.process.communicate()
            print('Thread finished')

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout)
        if thread.is_alive():
            print('Terminating process')
            os.killpg(self.process.pid, signal.SIGTERM)
            thread.join()
        print(self.process.returncode)

#package name as input
package_name = sys.argv[1]

#start Frida for bypassing certificate pinning
#os.system('frida -D 9B011FFAZ0028T --codeshare sowdust/universal-android-ssl-pinning-bypass-2 -f ' + package_name + ' --no-pause')

#listen 5 minutes without interaction
sleep(120)

print("2 minutes have elapsed")

#save output to a file
outfile = open('./monkeyOutput/' + package_name + ".txt", 'w')

#1 event every 1 millisecond -> 600.000 events -> 10 minutes
output = sp.getoutput("time adb shell monkey --throttle 1 -p " + package_name + " -v 600000")
outfile.write(output)

#1 event every 1 millisecond -> 600.000 events
#command = Command("echo 'Process started'; time adb shell monkey --throttle 1 -p " + package_name + " -v 600000; echo 'Process finished'")
#print(command.cmd)

#10 minutes timeout
#command.run(timeout=600)
