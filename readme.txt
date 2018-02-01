Setting Up
3 Machine: 2 Client (Webcam client and MCU client) and Server

The Webcam Client and Server must in a same network

Webcam Client (webcam interface):
  install working webcam driver
  install software that broadcast webcam image to local network frame by frame
  must be in same network as server

MCU Client (hardware interface):
  perferred using Arduino
  install a bluetooth communication hardware using UART
  Pair with server
  upload the code Ultimake2017.ino to arduino

Server (image processing and coordination):
  install python - opencv
  change some parameter in eye-gaze.py
  run the code eye-gaze.py

Our Implementation:
  On window client do:
    host wifi
      open cmd
      if not yet set
        netsh wlan set hostednetwork mode=allow ssid="<SSID>" key="<PASSWORD>"
      if set
        netsh wlan show hostednetwork (for ssid)
        netsh wlan show hostednetwork setting=security (for password)
      netsh wlan start hostednetwork
      netsh wlan stop hostednetwork
    install and open yawcam


Extra Asset:
