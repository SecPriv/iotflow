import threading, subprocess, sys, os, psutil, time, signal
from fcntl import fcntl, F_GETFL, F_SETFL

#https://stackoverflow.com/questions/34562473/most-pythonic-way-to-kill-a-thread-after-some-period-of-time
#https://stackoverflow.com/questions/1359383/run-a-process-and-kill-it-if-it-doesnt-end-within-one-hour

class NamedPopen(subprocess.Popen):
     """
     Like subprocess.Popen, but returns an object with a .name member
     """
     def __init__(self, *args, name=None, **kwargs):
         self.name = name
         super().__init__(*args, **kwargs)

def stdout_printer(p, index, proc):
    # let the shell output the result:
    # get the output
    global stop_process
    while True:
        if stop_process:
            print(f"{bcolors[index]}" + p.name + 'process has stopped', flush=True)
            break
        time.sleep(1)
        try:
            output = os.read(p.stdout.fileno(), 1024).decode("utf-8")
            if output != '' and proc.is_running():
                print(f"{bcolors[index]}" + p.name + '\n' + output)
            else:
                break
        except OSError:
            # the os throws an exception if there is no data
            print (f"{bcolors[index]}" + p.name + ': [No more data]')
            continue

def start_thread(command, thread_name, color):

    p = NamedPopen([command], stdout = subprocess.PIPE, stdin=subprocess.PIPE, shell=True, name=thread_name)
    # set the O_NONBLOCK flag of p.stdout file descriptor:
    flags = fcntl(p.stdout, F_GETFL) # get current p.stdout flags
    fcntl(p.stdout, F_SETFL, flags | os.O_NONBLOCK)

    proc = psutil.Process(p.pid)

    t = threading.Thread(target=stdout_printer, name=thread_name ,args=(p, color, proc))
    t.start()

    return (t,p)

apk_name = sys.argv[1]
package_name = apk_name.replace('.apk', '')

bcolors = [
    '\033[95m', '\033[94m', '\033[96m', '\033[92m', '\033[93m', '\033[91m', '\033[0m', '\033[1m', '\033[4m'
]

'''#Fresh install of the app
install_command = 'adb install apks_to_test/' + apk_name
p = subprocess.Popen([install_command], stdout = subprocess.PIPE, shell=True)
print(f"{bcolors[5]}" + p.stdout.read().decode())

time.sleep(5)


#TEST: 'find . "ipop"'''

stop_process = False

#apply IPTABLES rules to forward all the traffic to the hotspot interface
iptables_command = './iptables.sh'
p = subprocess.Popen([iptables_command], stdout = subprocess.PIPE, shell=True)
print(f"{bcolors[7]}" + p.stdout.read().decode())

time.sleep(5)

#FRIDA on PHONE
frida_phone = "adb shell \"su -c 'setenforce 0 && ./data/local/tmp/frida-server'\""
#start Frida phone
(t1, p1) = start_thread(frida_phone, "frida_phone", 1)

time.sleep(7)

#TODO: ssl key
#MITMPROXY
mitmproxy_command = "SSLKEYLOGFILE=\"./pcaps/ssl_keys/" + package_name + ".txt\" mitmdump --mode transparent -p 8080 -w ./mitmdump/" + package_name + " --ssl-insecure"
#mitmproxy
(t2, p2) = start_thread(mitmproxy_command, "mitmproxy", 2)

time.sleep(7)

# TCPDUMP on LAPTOP
#TODO: correct interface -> wifi hotspot
tcpdump_laptop = "tcpdump -i wlp0s20f3 -A -vvv -w ./pcaps/" + package_name + ".pcap"
#start tcpdump phone
(t3, p3) = start_thread(tcpdump_laptop, "tcpdump_laptop", 3)

time.sleep(7)

# FRIDA on LAPTOP
frida_laptop = "frida -D 9B011FFAZ0028T --codeshare akabe1/frida-multiple-unpinning -f " + package_name + " --no-pause"
#start Frida laptop
(t0, p0) = start_thread(frida_laptop, "frida_laptop", 0)
#p0.communicate(input=b'y\n')[0]

print(f"{bcolors[6]}" + 'Finished Setting up')

stop_frida_phone = "adb shell \"su -c 'pkill frida-server'\""

def handler(signum, frame):
    global stop_process
    #stop all the processes
    print(f"{bcolors[4]}" + 'Terminating program...') 
    p0.terminate()
    p1.terminate()
    p2.terminate()
    p3.terminate()

    print(f"{bcolors[4]}" + 'Stopping Frida...') 
    subprocess.Popen([stop_frida_phone], stdout = subprocess.PIPE, shell=True)

    print(f"{bcolors[4]}" + 'Killing tcpdump') 
    subprocess.Popen(["pkill tcpdump"], stdout = subprocess.PIPE, shell=True)

    print(f"{bcolors[4]}" + 'Killing mitmdump') 
    subprocess.Popen(["pkill mitmdump"], stdout = subprocess.PIPE, shell=True)
    
    print(f"{bcolors[4]}" + 'Removing iptables rules') 
    subprocess.Popen(["./iptables_stop.sh"], stdout = subprocess.PIPE, shell=True)

    time.sleep(2)

    #if the program finished because the timeout has expired, then copy the files
    if signum == 14:
        print(f"{bcolors[4]}" + 'Timeout has expired, copying files...')
        subprocess.Popen(["adb shell \"su -c cat /data/misc/bluetooth/logs/btsnoop_hci.log\" > bluetooth/" + package_name + ".log"], stdout = subprocess.PIPE, shell=True)
        
    print(f"{bcolors[4]}" + 'Deleting old bluetooth file')
    subprocess.Popen(["adb shell \"su -c rm /data/misc/bluetooth/logs/btsnoop_hci.log && touch /data/misc/bluetooth/logs/btsnoop_hci.log\""], stdout = subprocess.PIPE, shell=True)
    subprocess.Popen(["adb shell \"su -c touch /data/misc/bluetooth/logs/btsnoop_hci.log\""], stdout = subprocess.PIPE, shell=True)

    stop_process = True

    time.sleep(2)

    t0.join()
    t1.join()
    t2.join()
    t3.join()

    time.sleep(1)

    #Uninstall of the app
    '''install_command = 'adb uninstall ' + package_name
    p = subprocess.Popen([install_command], stdout = subprocess.PIPE, shell=True)
    print(f"{bcolors[5]}" + p.stdout.read().decode())'''

    time.sleep(1)

    print(f"{bcolors[4]}" + 'Program terminated') 
    #print(t0.is_alive())

signal.signal(signal.SIGINT, handler) #signum 2
signal.signal(signal.SIGALRM, handler) #signum 14

#Terminate program after 30 minutes
signal.alarm(60*30)
#signal.alarm(300)