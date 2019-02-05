import re
import signal
import datetime
import os
import serial
import time 
import numpy as np
import json
from pylab import *
from collections import defaultdict
from collections import deque
import pyqtgraph as pg
import sys
import random
from builtins import input
import socket



class  json_plotter:
    first_graphing_loop = True


    
    def __init__(self,name):
        self.name = name 
        
        self.pw = pg.plot()
        self.pw.setClipToView(True)
        self.pw.enableAutoScale()
        self.data_array = defaultdict(list)
        
        self.legend = self.pw.addLegend()

        self.plot_array = defaultdict(self.pw.plot)
        
    def save_plot_data(self,file_name):
        #print(json.dumps(self.data_array))
        json.dump(self.data_array,open(file_name,'w'))
        
        
    def parse_raw_input_all(self,parsing_string):
        parsed_json = json.loads(parsing_string)
        data_array = defaultdict(list)
        for j in parsed_json:
            for i in j:
                data_array[i].append(j[i])
        return data_array
                
                
    def parse_raw_input_graph(self,parsing_string):
        try:
            parsed_json = json.loads(parsing_string)
        except ValueError:
            return(-1)
                
        for j in parsed_json:
            for i in j:
                c_data_type = type(j[i]).__name__
                if  c_data_type == 'int' or c_data_type == 'float':
                    self.data_array[i].append(j[i])
        return self.data_array
    
    def plot_data(self):
        for i,data in enumerate(self.data_array.copy()):
            print("{} ".format(self.data_array[data][-1:]))
            temp_array = self.data_array[data][-200:]
            try: 
                c_time = self.data_array.get('time')[-200:]
                if 'time' not in data:
                    if self.first_graphing_loop:
                        self.plot_array[data]= self.pw.plot(c_time,temp_array,pen=(i,len(self.data_array.keys())),name=data)
                    self.plot_array[data].setData(x=c_time,y=temp_array)
            except AttributeError:
                print("ERROR")
                continue
        pg.QtGui.QApplication.processEvents()
        self.first_graphing_loop = False
        
    def plot_last_data(self):
        for i,data in enumerate(self.data_array.copy()):
            try: 
                c_time = self.data_array.get('time')
                if 'time' not in data:
                    if self.first_graphing_loop:
                        self.plot_array[data]= self.pw.plot(c_time,self.data_array[data],pen=(i,len(self.data_array.keys())),name=data)
                    self.plot_array[data].setData(x=c_time,y=self.data_array[data])
            except AttributeError:
                print("ERROR")
                continue
        pg.QtGui.QApplication.processEvents()
        self.first_graphing_loop = False
    
    def test_plot(self,max_test):
        for i in range(0,max_test):
            parsing_string = '[{{"_id": "5bf4965eca3b86350c3ebe60","time": {},"var1": {},"var2": {},"var3": {}}}]'.format(i,random.randint(1,1), random.randint(3,3), random.randint(1,10))
            self.parse_raw_input_graph(parsing_string)
            self.plot_data()
            time.sleep(.01)
                    
                    
                
        

class tcp_data_collection_server:
    PORT = 3333
    IP_VERSION = 'IPv4'
    IPV4 = '10.1.10.66'
    IPV6 = 'FE80::32AE:A4FF:FE80:5288'
    data_size = 4096
    
    def __init__(self):
        if self.IP_VERSION == 'IPv4':
            self.family_addr = socket.AF_INET
        elif self.IP_VERSION == 'IPv6':
            self.family_addr = socket.AF_INET6
        else:
            print('IP_VERSION must be IPv4 or IPv6')
            sys.exit(1)


        try:
            sock = socket.socket(self.family_addr, socket.SOCK_STREAM)
        except socket.error as msg:
            print('Error: ' + str(msg[0]) + ': ' + msg[1])
            sys.exit(1)

        print('Socket created')
            
        try:
            sock.bind(('', self.PORT))
            print('Socket binded')
            sock.listen(1)
            print('Socket listening')
            self.conn, addr = sock.accept()
            print('Connected by', addr)
        except socket.error as msg:
            print('Error: ' + str(msg[0]) + ': ' + msg[1])
            sock.close()
            sys.exit(1)
            
    def get_data(self):
        data = self.conn.recv(self.data_size)
        if not data: return -1 
        try:
            data = data.decode()
        except UnicodeDecodeError:
            print("Decode_Error")
            return -1
        return data

    def tcp_exit(self):
        self.conn.close()

        
    def send_data(self,data):
       reply = 'OK: ' + data
       self.conn.send(reply.encode())




        

if __name__ == '__main__':
    
        t_serv = tcp_data_collection_server()
        pl = json_plotter("data")
        log_path = "./dataout/data{}.json".format(datetime.datetime.now().strftime('_%d_%m_%Y_'))
        def signal_handler(sig, frame):
                t_serv.tcp_exit()
                pl.save_plot_data(log_path)
                print("Shutdown!")
                sys.exit(0)
        signal.signal(signal.SIGINT, signal_handler) 
        
        
        
        while(1):
            datas = t_serv.get_data()
            if  type(datas).__name__ == "str" and  ']' in datas and '[' in datas :
                if datas is not -1:
                    rest = datas.split("]",1)[0]
                    rest += ']'
                    pl.parse_raw_input_graph(rest)
                    pl.plot_data()
        
        
        
        
        
            

            
