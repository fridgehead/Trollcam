"""
Webcam Streamer

Uses Pygame and HTTPServer to stream USB Camera images via HTTP (Webcam)

HTTP Port, camera resolutions and framerate are hardcoded to keep it
simple but the program can be updated to take options.

Default HTTP Port 8080, 320x240 resolution and 6 frames per second.
Point your browser at http://localhost:8080/

http://www.madox.net/
"""

import signal
import sys
import tempfile
import threading
import time

import BaseHTTPServer
import SocketServer
import Image
import StringIO
import ImageEnhance
import ImageFilter
import ImageFont
import ImageDraw
import random

class HTTPServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
  def __init__(self, server_address):
    SocketServer.TCPServer.__init__(self, server_address, HTTPHandler)

   
class HTTPHandler(BaseHTTPServer.BaseHTTPRequestHandler):
  """
  HTTP Request Handler
  """
  def do_GET(self): 
    if self.path[:2] == "/":     
              #mjpeg boundary. LOL
              boundary = "TROLLOLOLOLOL" 
              self.send_response(200)
              self.send_header("Access-Control-Allow-Origin", "*")
              self.send_header("Content-type",
                               "multipart/x-mixed-replace;boundary=%s"
                               % boundary)
              self.end_headers()        
              #create a string buffer for the final jpeg encoded image
              sbuf = StringIO.StringIO()
              #load the background image
              pilimg = Image.open("cam.jpg")
	      #get a brightness adjusting thingy
              bright = ImageEnhance.Brightness(pilimg) 
              sbuf.seek(0)
              factor = 0
              while True:
                #hour and minute for the current time.
                toh = time.gmtime().tm_hour
                tom = time.gmtime().tm_min
                #set the brightness factor for sunrise, day, sunset and night
                if 7 <= toh < 8 :
                  #sunrise
                  factor = 0.2 + (tom) * (0.4/60) 
                elif 16 <= toh < 17:
                  #sunset
                  factor = 0.2 + (60 - tom) * (0.4/60) 
                elif 8 <= toh <=16:
                  factor = 0.6
                else:
                  factor = 0.2
                #vary the brightness a little to give the jpeg encoder something to chew on
                factor += (random.random() / 10.0)
                #blur the image to simulate ebay-camera-lense
                pil = pilimg.filter(ImageFilter.BLUR)
                #now apply The Darkening
                pil = bright.enhance(factor)

                #lets caption this so people think its a Motion stream
                t = time.strftime("%H:%M:%S-00", time.gmtime())
                t2 = time.strftime("%d-%m-%Y", time.gmtime())
                draw = ImageDraw.Draw(pil)
		#font has been processed from silkscr.ttf to a pil and pbm file in this folder
                fn = ImageFont.load('slkscr.pil')
                draw.text((2,470), "IP Camera", font=fn)
                draw.text((580,455), t2, font=fn)
                draw.text((580,465), t, font=fn)
                del draw

                #save the processed image to the string buffer, making sure to set the quality low to give it that "just streamed over dialup" feel
                sbuf.seek(0)
                pil.save(sbuf, format='jpeg', quality=20)

                #send the data to the client
                response = "Content-type: image/jpeg\n\n"
                response = response + sbuf.getvalue()
                response = response + "\n--%s\n" % boundary
                self.wfile.write(response)    
                #sleep for a second, otherwise Chrome whinges that the site is in a redirect loop
                time.sleep(1)
                
    else:
      self.send_error(404, "This is not the page youre looking for.")
      self.end_headers()
    
  do_HEAD = do_POST = do_GET

if __name__ == '__main__':
  print "Started webcam streamer"

  def quit(signum, frame):
    print "Quitting..."
    sys.exit(0)

  
  signal.signal(signal.SIGINT, quit)
  signal.signal(signal.SIGTERM, quit)
  
  http_server = HTTPServer(server_address=("",9000)) 
  
  http_server_thread = threading.Thread(target = http_server.serve_forever())
  http_server_thread.setDaemon(true)
  http_server_thread.start()
  
  try:
    while True:
      http_server_thread.join(60)
  except KeyboardInterrupt:
    quit()
