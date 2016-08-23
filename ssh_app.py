import paramiko
import threading
import os.path
import sys
import subprocess
import time
import re

def check_ip_valid():
    check = False
    global ip_list
    
    while True:
        ip_file = raw_input('\nEnter ip file name and extension: ')
        
        try:
            # open and read ip file
            open_file = open(ip_file, 'r')
            open_file.seek(0)
            ip_list = open_file.readlines()
            open_file.close()
            #print ip_list
            
        except IOError:
            print 'File does not exist. Please try again.', ip_file
            
        for ip in ip_list:
            a = ip.split('.')
            #print a
            
        if (len(a) == 4) and (1 <= int(a[0]) <= 223) and ((int(a[0]) != 169) or (int(a[1]) != 254)) and (0 <= int(a[1]) <= 255) and (0 <= int(a[2]) <= 255) and (0 <= int(a[3]) <= 255):
            check = True
            break
        else:
            print 'Invalid IP Address! Please retry.'
            check = False
            continue
        
        if check == False:
            continue
        elif check == True:
            break
        
    # Check IP reachability
    print '\nChecking IP reachability......\n'
    
    check2 = False
    
    while True:
        for ip in ip_list:
            ping = subprocess.call(['ping', '-c', '2','-q', '-n',  ip])
            
            if ping == 0:
                check2 = True
                continue
            elif ping == 2:
                print 'No response from device.....', ip
                check2 = False
                break
            else:
                print 'Ping from the device has failed.', ip
                check2 = False
                break
            
        if check2 == False:
            print 'R-echeck ip address.'
            check_ip_valid()
        elif check2 == True:
            print '\nAll devices are reachable.... \n'
            break

# check user file validity
def user_file_valid():
    global user_file
    
    while True:
        user_file = raw_input('\nEnter user file name and extension: ')
    
        if os.path.isfile(user_file) == True:
            print '\nuser file is validated........'
            break
        else:
            print '\nFile does not exist. Please try again.'
            continue    
    
# check command file validity
def command_file_valid():
    global command_file
    
    while True:
        command_file = raw_input('\nEnter command file name and extension: ')
    
        if os.path.isfile(command_file) == True:
            print '\nCommand file is validated........\n'
            break
        else:
            print '\nFile does not exist. Please try again.\n'
            continue
    
# call functions
try:
    check_ip_valid()
except KeyboardInterrupt:
    print '\nProgram aborted. Exiting.....'
    sys.exit()
    
try:
    user_file_valid()
except KeyboardInterrupt:
    print '\nProgram aborted. Exiting.....'
    sys.exit()
    
try:
    command_file_valid()
except:
    print '\nProgram aborted. Exiting.....'
    sys.exit()
    
# Open SSH connection to device
def open_ssh_conn(ip):
    try:
        selected_user_file = open(user_file, 'r')
        selected_user_file.seek(0)
        
        username = selected_user_file.readlines()[0].split(',')[0]
        selected_user_file.seek(0)
        password = selected_user_file.readlines()[0].split(',')[1].rstrip('\n')
        
        session = paramiko.SSHClient()
        
        session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        session.connect(ip,username = username, password = password)
        
        # start interactive shell on router
        connection = session.invoke_shell()
        connection.send('terminal length 0\n')
        time.sleep(1)
        
        connection.send('\n')
        connection.send('configure terminal\n')
        time.sleep(1)
        
        # open command file
        selected_comm_file = open(command_file, 'r')
        selected_comm_file.seek(0)
        
        for each_line in selected_comm_file.readlines():
            connection.send(each_line + '\n')
            time.sleep(2)
            
        selected_user_file.close()
        selected_comm_file.close()
        
        router_output = connection.recv(65535)
        
        if re.search('Invalid input detected at',router_output):
            print 'There is ios syntax error on device', ip
        else:
            print '\n Done for .....', ip
            
        session.close()
    
    except paramiko.AuthenticationException:
        print 'Invalid username or password.'
        print 'Exiting program ......'

# Create threads
def create_threads():
    threads = []
    
    for ip in ip_list:
        thread = threading.Thread(target = open_ssh_conn, args = (ip,))
        thread.start()
        threads.append(thread)
        
    for thread in threads:
        thread.join()
        
create_threads()
    



