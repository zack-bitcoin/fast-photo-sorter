from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import string,cgi,time, json, random, copy, pickle, image64, os
PORT=8090
output_file='save.txt'
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
linkHome = easyForm('/', 'HOME', '', 'get')
def page1():
    fs=fs_load()
    tags=[]
    for key in fs:
        if fs[key] not in tags:
            tags.append(fs[key])
    out="<p>photo organizer</p><br />{}"
    out=out.format(easyForm('/tagPhotos', 'tag untagged photos from this location on your hard-drive', '<input type="text" name="location">'))
    out=out.format("<p>example: /home/Mike/Pictures </p>{}")
    out=out.format(easyForm('/writeQuit', 'Write & Quit'))
    out=out.format(easyForm('/delete', 'Delete saved tags'))
    '''    for tag in tags:
        out=out.format(easyForm('/viewPhotos', 'look at photos tagged as: '+tag, '<input type="hidden" name="tag" value="{}"><input type="hidden" name="picture_numbered" value="0">'.format(tag)))
'''
    for tag in tags:
        out=out.format(easyForm('/renameGroup', 'retag every {} photo to: '.format(tag), '<input type="text" name="newName"><input type="hidden" name="oldName" value="{}">'.format(tag)))
    return out.format('')
def hex2htmlPicture(string):
    return '<img height="300" src="data:image/png;base64,{}">{}'.format(string, '{}')
def file2hexPicture(fil):
    return image64.convert(fil)
def file2htmlPicture(fil):
    return hex2htmlPicture(file2hexPicture(fil))
def newline():
    return '''<br />
{}'''
empty_page='<html><body>{}</body></html>'
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
def grab_photos(location):
    files = [f for f in os.listdir(location)]# if os.path.isfile(f)]
    photos=[]
    for f in files:
        if f[-4:] in ['.jpg', '.JPG']:
            photos.append(location+'/'+f)
    return photos
def tagPhotos(dic_in):
    print('dic_in: ' +str(dic_in))
    photos=grab_photos(dic_in['location'])
    fs=fs_load()
    untagged=[]
    undoable=''
    for photo in photos:
        print('photo: ' +str(photo))
        if photo not in fs:
            untagged.append(photo)
    if 'tag' in dic_in:
        undoable=untagged[0]
        fs[untagged[0]]=dic_in['tag']
        untagged.remove(untagged[0])
        fs_save(fs)
    if 'undoable' in dic_in:
        undoable=dic_in['undoable']
        fs.pop(undoable)
        fs_save(fs)
        untagged=[undoable]+untagged
    out=empty_page
    for photo in untagged:
        print('photo: ' +str(photo))
        out=out.format('<p>{}/{}</p>{}'.format(len(photos)-len(untagged),len(photos),'{}'))
        out=out.format(file2htmlPicture(photo))
        out=out.format(easyForm('/tagPhotos', 'next_photo', '<input type="text" name="tag" value="" autofocus><input type="hidden" name="location" value="{}">'.format(dic_in['location'])))
        out=out.format(easyForm('/tagPhotos', 'UNDO', '<input type="hidden" name="undoable" value="{}"><input type="hidden" name="location" value="{}">'.format(undoable, dic_in['location'])))
        out=out.format(linkHome)
        return out.format('')
    out=out.format('<p>all photos have been tagged</p>{}')
    out=out.format(easyForm('/tagPhotos', 'UNDO', '<input type="hidden" name="undoable" value="{}"><input type="hidden" name="location" value="{}">'.format(undoable, dic_in['location'])))
    out=out.format(linkHome)
    return out.format('')
def renameGroup(dic):
    newName=dic['newName']
    oldName=dic['oldName']
    fs=fs_load()
    for i in fs:
        if fs[i]==oldName:
            fs[i]=newName
    fs_save(fs)
    out=empty_page
    out=out.format('<p>successfully renamed group</p>{}')
    print('linkhome: ' +str(type(linkHome)))
    out=out.format(linkHome)
    print('out: ' +str(out))
    return out.format('')
def writeQuit(dic):
    fs=fs_load()
    out={}
    for i in fs:
        if fs[i] not in out:
            out[fs[i]]=[]
        out[fs[i]].append(i)
    f=open(output_file, 'w')
    for i in out:
        for j in out[i]:
            f.write('{}\t{}\n'.format(i, j))
    f.close()
    out=empty_page.format('<p>successfully saved to file {}</p>{}'.format(output_file, '{}'))
    out=out.format(linkHome)
    return out.format('')
def delete(dic):
    fs_save(initial_db)
    out=empty_page.format('<p>successfully deleted saved tags</p>{}')
    out=out.format(linkHome)
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
        out=out.format(linkHome)
        return out.format('')
    out=out.format(file2htmlPicture(photos[n]))        
    out=out.format(easyForm('/viewPhotos', 'next_photo', '<input type="hidden" name="tag" value="{}"><input type="hidden" name="picture_numbered" value="{}">'.format(dic_in['tag'], str(int(dic_in['picture_numbered'])+1))))
    out=out.format(easyForm('/viewPhotos', 'untag_photo', '<input type="hidden" name="tag" value="{}"><input type="hidden" name="picture_numbered" value="{}"><input type="hidden" name="untag" value="{}">'.format(dic_in['tag'], dic_in['picture_numbered'], dic_in['picture_numbered'])))
    print('dic: ' +str(dic_in))
    out=out.format(easyForm('/viewPhotos', 'retag_photo', '<input type="text" name="retag" value="{}" autofocus><input type="hidden" name="tag" value={}><input type="hidden" name="picture_numbered" value="{}">'.format('', dic_in['tag'], dic_in['picture_numbered'])))
    out=out.format(linkHome)
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
            elif self.path=='/renameGroup':
                self.wfile.write(renameGroup(dic))
            elif self.path=='/writeQuit':
                self.wfile.write(writeQuit(dic))
            elif self.path=='/delete':
                self.wfile.write(delete(dic))
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




