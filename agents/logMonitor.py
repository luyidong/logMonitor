import pyinotify
import time
import os,requests,json
import sys,re,socket
from datetime import date, datetime

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

conf = '$remote_addr - $remote_user [$time_local] "$request" $status $body_bytes_sent "$http_referer" "$http_user_agent" $request_time "$http_x_forwarded_for"'
regex = ''.join(
    '(?P<' + g + '>.*?)' if g else re.escape(c)
    for g, c in re.findall(r'\$(\w+)|(.)', conf))

http_status = (r'(^4|5)[0-9][0-9]')

hostname=socket.gethostname()

class ProcessTransientFile(pyinotify.ProcessEvent):
    def process_IN_MODIFY(self,event):
	data={}
        line = file.readline()
        if line:
	    listStr = re.findall(regex, line)
            for obj in  listStr:
                cod=re.search(http_status,obj[4])
                if cod:
                    # print cod.group()
                    data['node_name']=hostname
                    data['remote_addr']=obj[0]
                    data['remote_user']=obj[1]
                    data['time_local']=datetime.strptime(obj[2],'%d/%b/%Y:%X +0800')
                    data['request']=obj[3]
                    data['status']= obj[4]
                    data['body_bytes_sent']= obj[5]
                    data['http_referer']=obj[6]
                    data['http_user_agent']=obj[7]
                    data['request_time']=obj[8]
                    data['http_x_forwarded_for']=obj[9]
                    #data['status_count'] = bytes(data.get(('time_local','request','status'),0)+1)
                    data['status_count'] = bytes(data.get(('time_local','status'),0)+1)
		    resp = requests.post("http://ops01.idc1.fn/api/nginx/",
                                         data=json.dumps(data,default=json_serial),  # serialize the dictionary from above into json
                                         headers={
                                               "Authorization":"Basic eWlkb25nLmx1OmJpbmdvLy8vMTMxNA==",
                                               "Content-Type":"application/json",
                                               "Accept": "application/json"
                                              })

if __name__ == '__main__':
    filename = sys.argv[1]
    file = open(filename,'r')
    st_results = os.stat(filename)
    st_size = st_results[6]
    file.seek(st_size)
    wm = pyinotify.WatchManager()
    notifier = pyinotify.Notifier(wm)
    wm.watch_transient_file(filename, pyinotify.IN_MODIFY, ProcessTransientFile)
    notifier.loop()
