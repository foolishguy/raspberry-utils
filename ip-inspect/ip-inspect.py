# -*- coding:utf-8 -*-
import socket
import fcntl
import time
import struct
import smtplib
import urllib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import struct
import re
import urllib2
import json

# file_path config
file_path = "./iplist.txt"
setting_path = "./settings.json"

class SendEmail:
    def __init__(self, setting_path):
        self._setting_path = setting_path
        self.__get_setting()

    def __get_setting(self):
        with open(self._setting_path) as setting_file:
            setting_content = setting_file.read()
            setting_config = json.loads(setting_content)
            self._smtpserver = setting_config['email_config']['smtpserver']
            self._username = setting_config['email_config']['username']
            self._password = setting_config['email_config']['password']
            self._sender = setting_config['email_config']['sender']
            self._receiver = setting_config['email_config']['receiver']
            self._subject = setting_config['email_config']['subject']

    def send(self, email_content):
        msgRoot = MIMEMultipart('related')
        msgRoot["To"] = ','.join(self._receiver)
        msgRoot["From"] = self._sender
        msgRoot['Subject'] =  self._subject
        msgText = MIMEText(email_content,'html','utf-8')
        msgRoot.attach(msgText)
        smtp = smtplib.SMTP()
        smtp.connect(self._smtpserver)
        smtp.login(self._username, self._password)
        smtp.sendmail(self._sender, self._receiver, msgRoot.as_string())
        smtp.quit()        

#check network is active or not
def check_network():
    while True:
        try:
            print "Network is Ready!"
            break
        except Exception , e:
           print e
           print "Network is not ready,Sleep 5s...."
           time.sleep(10)
    return True

#get ip address, wlan0
class GetIp:
    def get_ip_address(self):
        if_name = "wlan0"
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        local_ip = socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', if_name[:15])
        )[20:24])

        print "wlan0: %s"%local_ip
        return local_ip

#operate file that save ip address
class IpFileOperation:
    def __init__(self, file_path):
        self._file_path = file_path

    def get_last_ip(self):
        with open(self._file_path) as file_path:
            ip_file = open(self._file_path)
            last_ip = ip_file.read()
            ip_file.close()
            return last_ip       

    def update_last_ip(self, new_ip):
        with open(self._file_path) as file_path:
            ip_file = open(self._file_path,"w")
            ip_file.write(str(new_ip))
            ip_file.close()             

def check_ip_changed():
    ip_file_class = IpFileOperation(file_path)
    get_ip_class = GetIp()
    current_ip = get_ip_class.get_ip_address()
    last_ip = ip_file_class.get_last_ip()
    print "current_ip: %s"%current_ip
    print "last_ip: %s"%last_ip
    if last_ip == current_ip:
        print "IP not change."
    else:
        print "IP changed."
        ip_file_class.update_last_ip(current_ip)
        send_email_class = SendEmail(setting_path)
        send_email_class.send(current_ip)
        print "Successfully send the e-mail."

if __name__ == '__main__':
    check_network()
    check_ip_changed()
