from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import string,cgi,time, json, random, copy, pickle, image64, os
PORT=8090

def fs2dic(fs):
    dic={}
    for i in fs.keys():
        a=fs.getlist(i)
        if len(a)>0:
            dic[i]=fs.getlist(i)[0]
        else:
            dic[i]=""
    return dic
form='''
<form name="first" action="{}" method="{}">
<input type="submit" value="{}">{}
</form> {}
'''
def easyForm(link, button_says, moreHtml='', typee='post'):
    a=form.format(link, '{}', button_says, moreHtml, "{}")
    if typee=='get':
        return a.format('get', '{}')
    else:
        return a.format('post', '{}')

def page1():
    fs=fs_load()
    tags=[]
    for key in fs:
        if fs[key] not in tags:
            tags.append(fs[key])
    out="<p>photo organizer</p><br />{}"
    out=out.format(easyForm('/tagPhotos', 'tag untagged photos'))
    for tag in tags:
        out=out.format(easyForm('/viewPhotos', 'look at photos tagged as: '+tag, '<input type="hidden" name="tag" value="{}"><input type="hidden" name="picture_numbered" value="0">'.format(tag)))
    return out.format('')
def hex2htmlPicture(string):
    return '<img src="data:image/png;base64,{}">{}'.format(string, '{}')
def file2hexPicture(fil):
    return image64.convert(fil)
def file2htmlPicture(fil):
    return hex2htmlPicture(file2hexPicture(fil))
def newline():
    return '''<br />
{}'''
initial_db={}#{photo_location.jpg:'tag1',...}
database='tags.db'
def fs_load():
   try:
      return pickle.load(open(database, 'rb'))
   except:
      fs_save(initial_db)
      return pickle.load(open(database, 'rb'))      
def fs_save(dic):
    pickle.dump(dic, open(database, 'wb'))
def grab_photos():#from local file
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    photos=[]
    for f in files:
        if f[-1:] not in['~', '#'] and f[-3:] not in ['.py', '.db'] and f[-4:]!='.pyc':
            photos.append(f)
    return photos
def tagPhotos(dic_in):
    photos=grab_photos()
    fs=fs_load()
    untagged=[]
    for photo in photos:
        if photo not in fs:
            untagged.append(photo)
    if 'tag' in dic_in:
        fs[untagged[0]]=dic_in['tag']
        untagged.remove(untagged[0])
        fs_save(fs)
    out='<html><body>{}</body></html>'
    for photo in untagged:
        out=out.format(file2htmlPicture(photo))
        out=out.format(easyForm('/tagPhotos', 'next_photo', '<input type="text" name="tag" value="" autofocus>'))
        return out.format("")
    out=out.format('<p>all photos have been tagged</p>{}')
    out=out.format(easyForm('/', 'HOME', '', 'get'))
    return out.format('')
def viewPhotos(dic_in):
    out='<html><body>{}</body></html>'
    photos=[]
    fs=fs_load()
    print('dic: ' +str(dic_in))
    tag=dic_in['tag']
    for i in fs:
        if fs[i]==tag:
            photos.append(i)
    if 'picture_numbered' in dic_in:
        n=int(dic_in['picture_numbered'])
    else:
        n=0
    out=out.format('<h1>photos tagged as {}</h1>{}'.format(tag,'{}'))
    if n >= len(photos):
        n=0
    if 'retag' in dic_in:
        fs[photos[n]]=dic_in['retag']
        fs_save(fs)
        photos.remove(photos[n])
    if 'untag' in dic_in:
        fs.pop(photos[n])
        fs_save(fs)
        photos.remove(photos[n])
    if n >= len(photos):
        out=out.format("<p>no photos with this tag</p>{}")
        out=out.format(easyForm('/', 'HOME', '', 'get'))
        return out.format('')
    out=out.format(file2htmlPicture(photos[n]))        
    out=out.format(easyForm('/viewPhotos', 'next_photo', '<input type="hidden" name="tag" value="{}"><input type="hidden" name="picture_numbered" value="{}">'.format(dic_in['tag'], str(int(dic_in['picture_numbered'])+1))))
    out=out.format(easyForm('/viewPhotos', 'untag_photo', '<input type="hidden" name="tag" value="{}"><input type="hidden" name="picture_numbered" value="{}"><input type="hidden" name="untag" value="{}">'.format(dic_in['tag'], dic_in['picture_numbered'], dic_in['picture_numbered'])))
    print('dic: ' +str(dic_in))
    out=out.format(easyForm('/viewPhotos', 'retag_photo', '<input type="text" name="retag" value="{}" autofocus><input type="hidden" name="tag" value={}><input type="hidden" name="picture_numbered" value="{}">'.format('', dic_in['tag'], dic_in['picture_numbered'])))
    out=out.format(easyForm('/', 'HOME', ''))
    return out.format('')
class MyHandler(BaseHTTPRequestHandler):
   def do_GET(self):
      try:
         if self.path == '/' :    
#            page = make_index( '.' )
            self.send_response(200)
            self.send_header('Content-type',    'text/html')
            self.end_headers()
            self.wfile.write(page1())
            return    
         else : # default: just send the file    
            filepath = self.path[1:] # remove leading '/'    
            if [].count(filepath)>0:
#               f = open( os.path.join(CWD, filepath), 'rb' )
                 #note that this potentially makes every file on your computer readable bny the internet
               self.send_response(200)
               self.send_header('Content-type',    'application/octet-stream')
               self.end_headers()
               self.wfile.write(f.read())
               f.close()
            else:
               self.send_response(200)
               self.send_header('Content-type',    'text/html')
               self.end_headers()
               self.wfile.write("<h5>Don't do that</h5>")
            return
         return # be sure not to fall into "except:" clause ?      
      except IOError as e :  
             # debug    
         print e
         self.send_error(404,'File Not Found: %s' % self.path)
   def do_POST(self):
            print("path: " + str(self.path))
#         try:
            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))    
            print(ctype)
            if ctype == 'multipart/form-data' or ctype=='application/x-www-form-urlencoded':    
               fs = cgi.FieldStorage( fp = self.rfile,
                                      headers = self.headers, # headers_,
                                      environ={ 'REQUEST_METHOD':'POST' })
            else: raise Exception("Unexpected POST request")
            self.send_response(200)
            self.end_headers()
            dic=fs2dic(fs)
            
            if self.path=='/tagPhotos':
                self.wfile.write(tagPhotos(dic))
            elif self.path=='/viewPhotos':
                self.wfile.write(viewPhotos(dic))
            else:
                print('ERROR: path {} is not programmed'.format(str(self.path)))
def main():
   try:
      server = HTTPServer(('', PORT), MyHandler)
      print 'started httpserver...'
      server.serve_forever()
   except KeyboardInterrupt:
      print '^C received, shutting down server'
      server.socket.close()
if __name__ == '__main__':
   main()




