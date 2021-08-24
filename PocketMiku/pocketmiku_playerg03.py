# python3
import tkinter as tk
#from tkinter import ttk
#from tkinter.constants import FALSE, TRUE
import pygame
#from pygame.locals import *
import time
import threading, queue
import os, glob
import mido

# set threading control
lock_port = threading.Lock()    # for midi outport operation
q_bpm = queue.Queue()   # for BPM cahnge operation
q_bpmc = queue.Queue()   # for send & receive BPM data
q_lyr = queue.Queue()   # for send & receive lyric data

## thread def
# play midi file
def play_song(outport, filemid, e, ep):
    # set initial bpm rate (slow > 1 or fast < 1) & velocity rate
    bpmrate = 1.0
    # play midi file
    for msg in mido.MidiFile(filemid):
        # get bpmrate change
        if not q_bpm.empty():
            bpmrate = q_bpm.get()
        # pause or standby
        if msg.type == 'note_on':
            ep.wait()   # wait for set ep
        # get tempo
        if msg.type == 'set_tempo':
            q_bpmc.put(mido.tempo2bpm(msg.tempo))
        # main player
        time.sleep(msg.time*bpmrate) # with tempo control
        if not msg.is_meta:
            # send midi message
            lock_port.acquire()
            outport.send(msg)
            lock_port.release() 
            if msg.type == 'sysex': # for lyric display
                q_lyr.put(msg.data)
#                print(msg)  # for test
    # signal of end
    e.set() 
# display lyric
def display_lyric():
    code2chr = {0:"ア", 1:"イ", 2:"ウ", 3:"エ", 4:"オ", 5:"カ", 6:"キ", 7:"ク", 8:"ケ", 9:"コ",
                10:"ガ", 11:"ギ", 12:"グ", 13:"ゲ", 14:"ゴ", 15:"キャ", 16:"キュ", 17:"キョ", 18:"ギャ", 19:"ギュ",
                20:"ギョ", 21:"サ", 22:"スィ", 23:"ス", 24:"セ", 25:"ソ", 26:"ザ", 27:"ズィ", 28:"ズ", 29:"ゼ",
                30:"ゾ", 31:"シャ", 32:"シ", 33:"シュ", 34:"シェ", 35:"ショ", 36:"ジャ", 37:"ジ", 38:"ジュ", 39:"ジェ",
                40:"ジョ", 41:"タ", 42:"ティ", 43:"トゥ", 44:"テ", 45:"ト", 46:"ダ", 47:"ディ", 48:"ドゥ", 49:"デ",
                50:"ド", 51:"テュ", 52:"デュ", 53:"チャ", 54:"チ", 55:"チュ", 56:"チェ", 57:"チョ", 58:"ツァ", 59:"ツィ",
                60:"ツ", 61:"ツェ", 62:"ツォ", 63:"ナ", 64:"ニ", 65:"ヌ", 66:"ネ", 67:"ノ", 68:"ニャ", 69:"ニュ",
                70:"ニョ", 71:"ハ", 72:"ヒ", 73:"フ", 74:"ヘ", 75:"ホ", 76:"バ", 77:"ビ", 78:"ブ", 79:"ベ",
                80:"ボ", 81:"パ", 82:"ピ", 83:"プ", 84:"ペ", 85:"ポ", 86:"ヒャ", 87:"ヒュ", 88:"ヒョ", 89:"ビャ",
                90:"ビュ", 91:"ビョ", 92:"ピャ", 93:"ピュ", 94:"ピョ", 95:"ファ", 96:"フィ", 97:"フュ", 98:"フェ", 99:"フォ",
                100:"マ", 101:"ミ", 102:"ム", 103:"メ", 104:"モ", 105:"ミャ", 106:"ミュ", 107:"ミョ", 108:"ヤ", 109:"ユ",
                110:"ヨ", 111:"ラ", 112:"リ", 113:"ル", 114:"レ", 115:"ロ", 116:"リャ", 117:"リュ", 118:"リョ", 119:"ワ",
                120:"ウィ", 121:"ウェ", 122:"ヲ", 123:"ン", 124:"ン", 125:"ン", 126:"ン", 127:"ン"}
    sysexlyrc = [67, 121, 9, 17, 10, 0]
    if not q_lyr.empty():
        msgdata = q_lyr.get()
        # check sysex type
        typelength = 6
        compcount = 0
        while compcount < typelength:
            if msgdata[compcount] != sysexlyrc[compcount]:
                break
            compcount += 1
        # check type matched
        if compcount == typelength:
            # generate lyric
            lyricdata = ''
            posdata = typelength
            while posdata < len(msgdata):
                lyricdata += code2chr[msgdata[posdata]]
                posdata += 1
            # display Lylic
            v_lyric.set(lyricdata)
            print(lyricdata)    # for debug
#---------------------------------------
#  Game controller part
#---------------------------------------
def pad_operation(e):
    # Game controller constant
    # for HORI Fighting Commander as XBOX controller
    # LEVER (X Left:-1, Right:1 Y Up:-1, Down:1)
    LEVER_LX = 0    #PITCH
    LEVER_LY = 1    #MODULATION
    BUTTON_ZL = 2    #Button ZL:button(6) for SWITCH   # not used
    LEVER_RX = 3    # not used
    LEVER_RY = 4    #EXPRESS
    BUTTON_ZR = 5    #Button ZR:button(7) for SWITCH   # not used
    # CROSS BUTTON (X Left:-1, Right:1 Y Up:1, Down:-1)
    CROSS_X = 0     # not used
    CROSS_Y = 1
    SONG_SELCT = CROSS_Y
    # BUTTON　(Press:1, Release:0)
    BUTTON_A = 0    #Button A:button(2) for SWITCH
    BUTTON_B = 1    #Button B:button(1)
    BUTTON_X = 2    #Button X:button(3)
    BUTTON_Y = 3    #Button Y:button(0)
    BUTTON_PLUS = 6    #Button +:button(9)  # not used
    BUTTON_MINUS = 7    #Button -:button(8) # not used
    BUTTON_L = 4    #Button L:button(4) # not used
    BUTTON_R = 5    #Button R:button(5) # not used
    BUTTON_L_LEVER = 9    #Button Left Lever:button(10)    # not used
    BUTTON_R_LEVER = 10    #Button Right Lever:button(11)   # not used
    BUTTON_HOME = 8    #Button LeverR:button(x)
    ENTER = BUTTON_A
    BPM_UP = BUTTON_X
    BPM_DOWN = BUTTON_Y
    BPM_RESET = BUTTON_B
    # set midi control value
    CENTERAJ = 0.01
    MAXVALUE = 127
    MAXPITCH = 8191 
    MINPITCH = -8192
    CENTEREXP = 64
    # list of controler input
    joynow = []
    joylast = []
    joychng = []
    crossnow = []
    crosslast = []
    crosschng = []
    btnnow = []
    btnlast = []
    btnchng = []
    # initialize game controller
    pygame.init()
    pygame.joystick.init()
    try:
    # create game controller (joystick) instance
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        levercount = joystick.get_numaxes()
        hatcount = joystick.get_numhats()
        buttoncount = joystick.get_numbuttons()
        statusmsg = 'Controller:' + joystick.get_name()
        v_lyric.set(statusmsg)
        print('Game controller name:', joystick.get_name())
        print('Lever # :', joystick.get_numaxes())  
        print('Hat(cross) # :', joystick.get_numhats()) 
        print('Button # :', joystick.get_numbuttons())
    except pygame.error:
        v_status.set('No Game controller exists')
        print('No Game controller exists')
        return 1
    #  initialize lever controller input value
    i = 0
    while i < levercount:
        joynow.insert(i, joystick.get_axis(i))
        joylast.insert(i, joystick.get_axis(i))
        joychng.insert(i, 0)
        i += 1
    #  initialize cross button input value
    crossnow = joystick.get_hat(0)
    crosslast = joystick.get_hat(0)
    crosschng = [0,0]
    #  initialize button input value
    i = 0
    while i < buttoncount:
        btnnow.insert(i, joystick.get_button(i))
        btnlast.insert(i, joystick.get_button(i))
        btnchng.insert(i, 0)
        i += 1
    #---------------------------------------
    #  MIDI part
    #---------------------------------------
    # set thread control
    e1 = threading.Event()  # for check of end of play_song
    ep = threading.Event()  # for pause for play_song
    # initialize Values
    playstate = 0 # 0:select, 1:playing
    # set midiout
    midiout = 'NSX-39:NSX-39 MIDI 1'
    try:
        outport = mido.open_output(midiout)
    except OSError:
        #display_1stline('Emergency stop!!')
        v_status.set('No MIDI OUT exists! Check & restart!')
        # close IO
        print('MIDI OUT does not exist!')   # for debug
        return 2
    # initialize display
    v_status.set('Initaizing')
    # change dir to this py file
    os.chdir(os.path.dirname(os.path.abspath('__file__')))
    print('getcwd:      ', os.getcwd()) # print this files directory for debug
    # set midi file
    filesel = 0
    midifile = glob.glob('./midi/*.mid')
    statusmsg = len(midifile), 'MIDI files exist'
    v_status.set(statusmsg)
    print(statusmsg)    # for debug
    # display midi file
    if len(midifile) > 0:
        songname = midifile[filesel]
        v_song.set(os.path.basename(songname))
    else:
        v_song.set('No MIDI files exist!')
    v_status.set('Select song with Cross Up/Down.')
    #---------------------------------------
    #  Cycilc operation
    #---------------------------------------
    # polling pad input
    while not e.isSet():
        # polling interval
        time.sleep(0.03)
        # get events refresh
        pygame.event.pump()
        # check lever input
        i = 0
        while i < len(joynow):
            joynow[i] = joystick.get_axis(i)
            if joynow[i] == joylast[i]:
                joychng[i] = 0
            else:
                joychng[i] = 1
            joylast[i] = joynow[i]
            i += 1
        # check cross input
        crossnow = joystick.get_hat(0)
        i = 0
        while i < len(crossnow):
            if crossnow[i] == crosslast[i]:
                crosschng[i] = 0
            else:
                crosschng[i] = 1
            i += 1
        crosslast = crossnow
        # check button input
        i = 0
        while i < len(btnnow):
            btnnow[i] = joystick.get_button(i)
            if btnnow[i] == btnlast[i]:
                btnchng[i] = 0
            else:
                btnchng[i] = 1
            btnlast[i] = btnnow[i]
            i += 1
        # before playing section
        if playstate == 0: # 0:select, 1:playing
            # select file
            if crosschng[SONG_SELCT] == 1:
                if len(midifile) <= 0:
                    v_song.set('No MIDI files exist!')
                else:
                    if crossnow[SONG_SELCT] == 1:
                        if filesel >= len(midifile) -1:
                            filesel = 0
                        else:
                            filesel += 1
#                       print(filesel) # for debug
                        # display MIDI file
                        songname = midifile[filesel]
                        v_song.set(os.path.basename(songname))
                    elif crossnow[SONG_SELCT] == -1:
                        if filesel <= 0:
                            filesel = len(midifile) - 1
                        else:
                            filesel -= 1
#                       print(filesel) # for debug
                        # display MIDI file
                        songname = midifile[filesel]
                        v_song.set(os.path.basename(songname))
            #  set the song to play
            if btnchng[ENTER] == 1 and btnnow[ENTER] == 1:
                if len(midifile) <= 0:
                    v_song.set('No MIDI files exist!')
                else:
                    # set state playing
                    playstate = 1  # 0:select, 1:playing
                    # initialize
                    pause = 1   # 1:pause
                    # intialize modulation control
                    lyinit = joynow[LEVER_LY]
                    modchg = 0
                    # intialize pitchwheel
                    lxinit = joynow[LEVER_LX]
                    pitchchg = 0
                    # intialize expression control (level inverted)
                    ryinit = joynow[LEVER_RY]
                    expres = 64
                    # intialize bpm
                    bpmint = 120    # MIDI standard Ver.1.0 default
                    bpmchange = 1.0
                    bpmdif = 0.0
                    # display status
                    v_status.set('Loading')
                    # initialize display
                    bpmmsg = int(bpmint)
                    v_bpm.set(bpmmsg)
                    #v_express.set(64)
                    #v_pitch.set(0)
                    #v_mod.set(0)                    
                    # print selected song
                    print(midifile[filesel])  # for debug
                    # generate thread object
                    ep.clear()    # initial pause
                    t1 = threading.Thread(target = play_song, args=(outport, midifile[filesel], e1, ep,))   # midifile[filesel] play
                    # set thread daemon
                    t1.setDaemon(True)
                    # start thread object
                    t1.start()
                    # display standby
                    v_status.set('Standby. Press A to play.')
        # on playing  (playstate == 1,  0:select, 1:playing)
        else: 
            # display Lyric
            display_lyric()
            # modulation control
            lynow = joynow[LEVER_LY]
            # adjust center sense by CENTERAJ
            if lynow >= lyinit - CENTERAJ and lynow <= lyinit + CENTERAJ:
                modnow = 0
            elif lynow < lyinit - CENTERAJ:   # up side
                modnow = int(MAXVALUE*(-lynow + lyinit - CENTERAJ )/(1 + lyinit - CENTERAJ))
            elif lynow > lyinit + CENTERAJ:   # down side
                modnow = int(MAXVALUE*(lynow - lyinit - CENTERAJ)/(1 - lyinit - CENTERAJ))
            # correct input
            if modnow > MAXVALUE:    # for max
                modnow = MAXVALUE
            # revise modulation
            if modnow != modchg:
                # revise modulation value
                modchg = modnow
                msgtx3 = mido.Message('control_change', channel = 0, control = 1, value = modchg)
                # send midi message
                lock_port.acquire()
                outport.send(msgtx3)
                lock_port.release()
                # display modulation value
                v_mod.set(modchg)
#                print(msgtx3)   # for debug
            # pitchwheel control
            lxnow = joynow[LEVER_LX]
            # adjust center sense by CENTERAJ
            if lxnow >= lxinit - CENTERAJ and lxnow <= lxinit + CENTERAJ:
                pitchnow = 0
            elif lxnow < lxinit - CENTERAJ:   # down side
                pitchnow = int(MINPITCH*(-lxnow + lxinit - CENTERAJ)/(1 + lxinit - CENTERAJ))
            elif lxnow > lxinit*(1+CENTERAJ):   # up side
                pitchnow = int(MAXPITCH*(lxnow - lxinit - CENTERAJ)/(1 - lxinit - CENTERAJ))
            # input limiter
            if pitchnow < MINPITCH:   # for min
                pitchnow = MINPITCH
            elif pitchnow > MAXPITCH:    # for max
                pitchnow = MAXPITCH
            # revise pitchwheel
            if pitchnow != pitchchg:
                # revise pitchwheel value
                pitchchg = pitchnow
                msgtx2 = mido.Message('pitchwheel', channel = 0, pitch = pitchchg)
                # send midi message
                lock_port.acquire()
                outport.send(msgtx2)
                lock_port.release() 
                # display modulation value
                v_pitch.set(pitchchg)
#                print(msgtx2)   # for debug
            # expression control
            rynow = joynow[LEVER_RY]
            # adjust center sense by CENTERAJ
            if rynow >= ryinit - CENTERAJ and rynow <= ryinit + CENTERAJ:
                expnow = CENTEREXP
            elif rynow < ryinit - CENTERAJ:   # up side
                expnow = int(CENTEREXP - (MAXVALUE - CENTEREXP)*(rynow + ryinit - CENTERAJ)/(1 + ryinit - CENTERAJ))
            elif rynow > ryinit + CENTERAJ:   # down side
                expnow = int(CENTEREXP - (MAXVALUE - CENTEREXP)*(rynow - ryinit - CENTERAJ)/(1 - ryinit - CENTERAJ))
            # correct input
            if expnow > MAXVALUE:    # for max
                expnow = MAXVALUE
            elif expnow < 0:    # for min
                expnow = -0
            # revise expression
            if expres != expnow:
                # revise expression value
                expres = expnow
                msgtx4 = mido.Message('control_change', channel = 0, control = 11, value = expres)
                # send midi message
                lock_port.acquire()
                outport.send(msgtx4)
                lock_port.release() 
                # display expression value
                v_express.set(expres)
#                print(msgtx4)   # for debug
            if ((btnnow[BPM_DOWN] == 1 and btnchng[BPM_DOWN] == 1) or 
                (btnnow[BPM_UP] == 1 and btnchng[BPM_UP] == 1) or
                (btnnow[BPM_RESET] == 1  and btnchng[BPM_RESET] == 1)):
                if btnnow[BPM_DOWN] == 1 and btnchng[BPM_DOWN] == 1:
                    bpmdif -= 1.0
                if btnnow[BPM_UP] == 1 and btnchng[BPM_UP] == 1:
                    bpmdif += 1.0
                if btnnow[BPM_RESET] == 1  and btnchng[BPM_RESET] == 1:
                    bpmdif = 0.0
                if bpmint - bpmdif < 3: # lower limiter
                    bpmdif = 0.0
                bpmchange = bpmint/(bpmint+bpmdif)
                q_bpm.put(bpmchange)
                # display bpm
                bpmmsg = int(bpmint+bpmdif)
                v_bpm.set(bpmmsg)
            # puase
            if btnnow[ENTER] == 1  and btnchng[ENTER] == 1:
                if pause == 1:
                    pause = 0   # 1:pause
                    ep.set()
                    # disaplay
                    v_status.set('Playing')
                else:
                    pause = 1   # 1:pause
                    ep.clear()
                    # disaplay
                    v_status.set('Pause. Press A to continue.')
        # get bpm 
        if not q_bpmc.empty():
            bpmint = int(q_bpmc.get())
            # display bpm
            bpmmsg = int(bpmint+bpmdif)
            v_bpm.set(bpmmsg)
        # catch end of song
        if e1.isSet():  # check end of play_song
            playstate = 0 # 0:stop, 1:playing
            # wait for quit thread object
            t1.join()
            # display MIDI file
            if len(midifile) > 0:
                songname = midifile[filesel]
                v_song.set(os.path.basename(songname))
            else:
                v_song.set('No MIDI files exist!')
            v_status.set('Select song with Cross Up/Down.')
            v_lyric.set("")
            # clear signal of end of play_song
            e1.clear()
    # quit procedure
    outport.close()
    print('quit pad operation') # for debug
    return 0
#---------------------------------------
#  GUI part
#---------------------------------------
FGCOLOR = 'spring green'
BGCOLOR = 'dim gray' # back ground color
LABELWIDTH = 5
DISPWIDTH = 25
DISPWIDTHN = 8

root = tk.Tk()
root.geometry('300x200+0+0')  # window size:XxY, display edge position:+X+Y
root.title("PocketMiku Player")
root.configure(bg = BGCOLOR)

v_song = tk.StringVar()
v_song.set("selected song")
v_bpm = tk.StringVar()
v_bpm.set(120)    # MIDI standard Ver.1.0 default
v_express = tk.StringVar()
v_express.set(64)
v_pitch = tk.StringVar()
v_pitch.set(0)
v_mod = tk.StringVar()
v_mod.set(0)

v_lyric = tk.StringVar()
v_lyric.set("lyric of selected song")
v_status =  tk.StringVar()
v_status.set("StatusLabel")
#---------------------------------------
#  Title frame
#---------------------------------------
frame_title = tk.Frame(root, bg = BGCOLOR)
# label
label = tk.Label(frame_title, text = "PocketMiku Player", fg = FGCOLOR, bg = BGCOLOR)
# set objects in frame
label.pack(side = tk.LEFT)
# set frame in window
frame_title.pack(side = tk.TOP, fill = tk.X)
#---------------------------------------
#  Song frame
#---------------------------------------
frame_song = tk.Frame(root, bg = BGCOLOR)
# labels
label_song = tk.Label(frame_song, width = LABELWIDTH, anchor = "w", text = "Song  ", fg = FGCOLOR, bg = BGCOLOR)
label_selsong = tk.Label(frame_song, width = DISPWIDTH, anchor = "w", relief = tk.SUNKEN, bd =3, textvariable = v_song )
# set objects in frame
label_song.pack(padx = 10, side = tk.LEFT)
label_selsong.pack(side = tk.LEFT)
# set frame in window
frame_song.pack(pady = 3, fill = tk.X)
#---------------------------------------
#  Control frame
#---------------------------------------
frame_control = tk.Frame(root, bg = BGCOLOR)
# labels
label_bpm = tk.Label(frame_control, width = LABELWIDTH, anchor = "e", text = "BPM", fg = FGCOLOR, bg = BGCOLOR)
label_dispbpm = tk.Label(frame_control, width = DISPWIDTHN, anchor = "e", relief = tk.SUNKEN, bd =3, textvariable = v_bpm )
label_express = tk.Label(frame_control, width = LABELWIDTH, anchor = "e", text = "Vol", fg = FGCOLOR, bg = BGCOLOR)
label_dispexpress = tk.Label(frame_control, width = DISPWIDTHN, anchor = "e", relief = tk.SUNKEN, bd =3, textvariable = v_express )
# set objects in frame
label_bpm.pack(padx = 15, side = tk.LEFT)
label_dispbpm.pack(side = tk.LEFT)
label_express.pack(padx = 5, side = tk.LEFT)
label_dispexpress.pack(side = tk.LEFT)
# set frame in window
frame_control.pack(pady = 3, fill = tk.X)
#---------------------------------------
#  Control2 frame
#---------------------------------------
frame_control2 = tk.Frame(root, bg = BGCOLOR)
# labels
label_pitch = tk.Label(frame_control2, width = LABELWIDTH, anchor = "e", text = "Pitch", fg = FGCOLOR, bg = BGCOLOR)
label_disppitch = tk.Label(frame_control2, width = DISPWIDTHN, anchor = "e", relief = tk.SUNKEN, bd =3, textvariable = v_pitch )
label_mod = tk.Label(frame_control2, width = LABELWIDTH, anchor = "e", text = "Mod", fg = FGCOLOR, bg = BGCOLOR)
label_dispmod = tk.Label(frame_control2, width = DISPWIDTHN, anchor = "e", relief = tk.SUNKEN, bd =3, textvariable = v_mod )
# set objects in frame
label_pitch.pack(padx = 15, side = tk.LEFT)
label_disppitch.pack(side = tk.LEFT)
label_mod.pack(padx = 5, side = tk.LEFT)
label_dispmod.pack(side = tk.LEFT)
# set frame in window
frame_control2.pack(pady = 3, fill = tk.X)
#---------------------------------------
#  Lyric frame
#---------------------------------------
frame_lyric = tk.Frame(root, bg = BGCOLOR)
# labels
label_lyric = tk.Label(frame_lyric, width = LABELWIDTH, anchor = "w", text = "Lyric ", fg = FGCOLOR, bg = BGCOLOR)
label_dsplylic = tk.Label(frame_lyric, width = DISPWIDTH, anchor = "w", relief = tk.SUNKEN, bd =3, textvariable = v_lyric )
# set objects in frame
label_lyric.pack(padx = 10, side = tk.LEFT)
label_dsplylic.pack(side = tk.LEFT)
# set frame in window
frame_lyric.pack(pady = 3, fill = tk.X)
#---------------------------------------
#  Status bar frame
#---------------------------------------
# Frame
frame_statusbar = tk.Frame(root, relief = tk.SUNKEN, bd = 2)
# label in frame
label_status = tk.Label(frame_statusbar, textvariable = v_status)
# set objects in frame
label_status.pack(side = tk.LEFT)
# set frame in window
frame_statusbar.pack(side = tk.BOTTOM, fill = tk.X)
#---------------------------------------
#  remaining area
#---------------------------------------
frame = tk.Frame(root, relief = tk.SUNKEN, bd = 2, bg = BGCOLOR)
frame.pack(expand = True, fill = tk.BOTH)

#---------------------------------------
#  thread start
#---------------------------------------
# Game controller start
e3 = threading.Event()
t3 = threading.Thread(target = pad_operation, args=(e3,))
t3.setDaemon(True)
t3.start()
#---------------------------------------
#  GUI start
#---------------------------------------
root.mainloop()
#---------------------------------------
#  thread quit
#---------------------------------------
# Game controller quit
e3.set()
t3.join()
