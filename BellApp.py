from tkinter import PhotoImage
from tkinter import filedialog
from tkinter import messagebox
from tkinter import colorchooser
import playsound as ps
import tkinter as tk
import time

#How to fix for release 2.0:
#
#instead of globals use lambdas
#run mainloop in another thread (check unused_code.txt)
#add animations
#get time from time servers instead of locally

global are_timers_saved
are_timers_saved = False

global times_rung
times_rung = []

global running
running = False

global timers
timers = []
next_timer = ""

global add_window_object
add_window_object = False

global timer_pos
timer_pos = False

global garbage
garbage = []
def add_garbage(*stuff):
    #add stuff to garbage list
    global garbage
    for i in stuff:
        garbage.append(i)

def dump_garbage():
    #destroy garbage in garbage list
    for i in garbage:
        i.destroy()
        del i

global time_hours
global time_minutes
global timer_name
global entry_colour
global cancel_btn
cancel_btn = False
time_hours = ""
time_minutes = ""
timer_name = ""
entry_colour = ""

#dont forget you have to get_time() before calling current_time

def get_time():
    #Set up time
    curr_timer = ""
    t = time.localtime()
    global current_time
    current_time = (t[3]*60)+t[4]

def ring():
    #plays sound
    get_time()
    global current_time
    global timers
    global running

    if len(timers) == 0:
        return
    
    next_index = int(calc_next())
    if current_time == timers[next_index].timer_time:
        if calc_next() not in times_rung:
            times_rung.append(next_index)
            if timers[next_index].sound:
                timers[next_index].ring_entry()
            else:
                ring_sound()
            window.after(100000, lambda:times_rung.pop(0))
    if running:
        window.after(60000, ring)

def ring_sound():
    #plays souind
    ps.playsound("assets/bell2.mp3")

def del_timer_special(timer_pos):
    #used for delting timer sin a special way
    global timers
    del timers[timer_pos]
    sort_timers()
    
    dump_garbage()
    for i in timers:
        i.render_config()

def edit_timer(ident, name=False, time=False):
    #edit timer
    sort_timers()

def sort_timers():
    #sorts timers inside timers list with bubblesort
    #assumes timers is a list of tuples where each second entry of tuple is
    #int time
    global timers
    for passnum in range(len(timers)-1,0,-1):
        for i in range(passnum):
            if timers[i].timer_time > timers[i+1].timer_time:
                temp = timers[i]
                timers[i] = timers[i+1]
                timers[i+1] = temp

    #there is definetly a better way of doing this but i cant be bothered
    for i in range(len(timers)):
        timers[i].order = i

def calc_next():
    #Calculate witch timer to ring next, called when a timer is started
    #This is why we need 2 cores to run this program
    #remember to run sort_timers() and get_time() before this
    #
    #returns the index of the timer that runs next
    global timers
    for i in timers:
        if i.timer_time >= current_time:
            return timers.index(i)

def save():
    #Save timer to file
    #
    #Save format: name,time,order,colour(hex);
    global are_timers_saved
    global timers
    
    file_location = filedialog.asksaveasfilename(defaultextension=".timers", filetypes=(("All files", ".*"),(".timers file", ".timers")))
    file_location = file_location.encode('unicode_escape')
    file_object = open(file_location, "w")
    text2save = ""

    #update window title
    window.title("BellApp - " + str(file_location).split("/")[len(str(file_location).split("/")) - 1][:-8])
    
    #name, timer_time, order, colour
    for i in timers:
        text2save += str(i.name) + "," + str(i.timer_time) + "," + str(i.order) + "," + str(i.colour) + "," + str(i.sound) + ","
    file_object.write(text2save)
    file_object.close()
    are_timers_saved = True

def load():
    #Load timers from file
    global are_timers_saved
    global timers
    timers = []

    file_location = filedialog.askopenfilename(defaultextension=".timers", filetypes=(("All files", ".*"),(".timers file", ".timers")))
    file_location = file_location.encode('unicode_escape')
    file_object = open(file_location, "r")
    timers_string = file_object.read()

    for i in timers_string.split(sep=";")[:-1]:
        timers.append(entry(i.split(sep=",")[0], int(i.split(sep=",")[1]), int(i.split(sep=",")[2]), i.split(sep=",")[3], i.split(sep=",")[4]))
    for i in timers:
        i.render_config()
    are_timers_saved = True

    #display timer profile name in window title
    window.title("BellApp - " + str(file_location).split("/")[len(str(file_location).split("/")) - 1][:-8])

def start():
    #Start timers
    global bar_mode
    get_time()
    sort_timers()

    global running
    running = True
    
    global timers
                 
    #clear config stuff
    clear_config_extras()

    #configure status bar mode
    bar_mode = PhotoImage(file="assets/bar_start_mode.png")
    bar.configure(image=bar_mode)
    bar.image = bar_mode

    window.after(0, ring)
    
    dump_garbage()
    for i in timers:
        i.render()

def stop():
    #Stops timers

    #clear config stuff
    clear_config_extras()

    global running
    running = False
    
    #configure status bar mode
    global bar_mode
    bar_mode = PhotoImage(file="assets/bar_stop_mode.png")
    bar.configure(image=bar_mode)
    bar.image = bar_mode

    #render cleanup
    dump_garbage()
    for i in timers:
        i.render()

def config():
    #Config mode

    global running
    running = False

    #configure status bar mode
    bar_mode = PhotoImage(file="assets/bar_config_mode.png")
    bar.configure(image=bar_mode)
    bar.image = bar_mode

    #configure saveload buttons/bg
    saveload_bg.place(x=24, y=60)
    save_btn.place(x=39, y=60)
    load_btn.place(x=80, y=60)
    add_btn.place(x=118, y=60)

    dump_garbage()

    #render timers in config mode
    for i in timers:
        i.render_config()

def confirm_close():
    global are_timers_saved
    if are_timers_saved:
        window.destroy()
    else:
        if messagebox.askokcancel("Quit", "Are you sure you want to quit? Bell configuration has not been saved."):
            window.destroy()

def clear_config_extras():
    #clear saveload menu
    saveload_bg.place(x=1000, y=1000)
    save_btn.place(x=1000, y=1000)
    load_btn.place(x=1000, y=1000)
    add_btn.place(x=1000, y=1000)

def get_colour():
    #updates colour for entry
    global entry_colour
    global colour_btn
    entry_colour = colorchooser.askcolor()[1]
    colour_btn.config(bg=entry_colour, activebackground=entry_colour)

def get_sound():
    #updates audio for entry
    global entry_sound
    global sound_btn
    global sound_file_location
    sound_file_location = filedialog.askopenfilename(defaultextension=".timers", filetypes=(("All files", ".*"),("MP3 file", ".mp3"),("WAV file", ".wav")))
    sound_file_location = sound_file_location.encode('unicode_escape')
    entry_sound = str(sound_file_location).split("/")[-1][:-1]

    if entry_sound == "b'":
        entry_sound = "Default"
        sound_file_location = False

    sound_file_location = str(sound_file_location)[2:-1]
    sound_btn.config(text=entry_sound)

def add_window(timer_pos=False):
    #creates a new window for timer creation or editing a timer
    #if flag timer_pos have to get info from timers list to edit
    global sound_file_location
    global timers
    global add_window_object
    if add_window_object:
        messagebox.showerror('Error','Cannot create another bell while already creating one.')
        return False
    add_window_object = tk.Toplevel(window)
    if not timer_pos:
        add_window_object.title("Add bell")
    else:
        add_window_object.title("Edit bell")
    add_window_object.geometry("267x220")
    add_window_object['background']='#1C1C1E'
    add_window_object.iconbitmap("assets\\bell.ico")
    add_window_object.resizable(False, False)

    sound_file_location = False

    #time label
    time_label = tk.Label(add_window_object, text="Time:", bg="#1C1C1E", border=0, font=("Segoe_UI", 15), fg="#FFFFFF")
    time_label.place(x=57, y=20)

    #name label
    name_label = tk.Label(add_window_object, text="Name:", bg="#1C1C1E", border=0, font=("Segoe_UI", 15), fg="#FFFFFF")
    name_label.place(x=50, y=55)

    #colour label
    colour_label = tk.Label(add_window_object, text="Colour:", bg="#1C1C1E", border=0, font=("Segoe_UI", 15), fg="#FFFFFF")
    colour_label.place(x=43, y=91)

    #time entry, two spinboxes
    time_entry_hour = tk.Spinbox(add_window_object, from_=0, to=23, width=5)
    time_entry_hour.place(x=117, y=23)
    time_entry_minute = tk.Spinbox(add_window_object, from_=0, to=59, width=5)
    time_entry_minute.place(x=177, y=23)

    #name entry
    name_entry = tk.Entry(add_window_object, width=17)
    name_entry.place(x=116, y=59)

    #colour select button
    global entry_colour
    entry_colour = "#D3D3D3"
    global colour_btn
    colour_btn = tk.Button(add_window_object, text="Edit", width=14, command=get_colour, relief="flat", bg=entry_colour, activebackground=entry_colour, borderwidth=0)
    colour_btn.place(x=117, y=95)

    #sound label
    sound_label = tk.Label(add_window_object, text="Sound:", bg="#1C1C1E", border=0, font=("Segoe_UI", 15), fg="#FFFFFF")
    sound_label.place(x=43, y=134)

    #sound select button
    global entry_sound
    entry_sound = "Default"
    global sound_btn
    sound_btn = tk.Button(add_window_object, text=entry_sound, width=14, command=get_sound, relief="flat", bg="#b8b8b8", activebackground=entry_colour, borderwidth=0)
    sound_btn.place(x=117, y=135)

    #ok button
    ok_btn_image = PhotoImage(file="assets/ok.png")
    ok_btn = tk.Button(add_window_object, text="", command=ok_close_add_window, image=ok_btn_image, relief="flat", bg="#1C1C1E", activebackground="#1C1C1E", borderwidth=0)
    ok_btn.image = ok_btn_image
    ok_btn.place(x=43, y=175)

    #cancel button
    global cancel_btn
    cancel_btn_image = PhotoImage(file="assets/cancel.png")
    cancel_btn = tk.Button(add_window_object, text="", command=close_add_window, image=cancel_btn_image, relief="flat", bg="#1C1C1E", activebackground="#1C1C1E", borderwidth=0)
    cancel_btn.image = cancel_btn_image
    cancel_btn.place(x=150, y=175)

    #mess of globals cos i cant pass function arguments through buttons
    #thanks tkinter
    global time_hours
    global time_minutes
    global timer_name
    time_hours = time_entry_hour
    time_minutes = time_entry_minute
    timer_name = name_entry

    #inserts stuff if timer pos
    #just gonna delet and create a new one so i dont have to bother
    #with editing :))))))))))))))))))
    if type(timer_pos) == int:
        time_entry_hour.delete(0, "end")
        time_entry_hour.insert(0, timers[timer_pos].timer_time // 60)
        
        time_entry_minute.delete(0, "end")
        time_entry_minute.insert(0, timers[timer_pos].timer_time - (timers[timer_pos].timer_time //60) * 60)
        
        name_entry.insert(0, timers[timer_pos].name)
        entry_colour = timers[timer_pos].colour
        colour_btn.config(bg=entry_colour, activebackground=entry_colour)

        ok_btn.config(command=lambda:ok_close_add_window(timer_pos))

    add_window_object.protocol("WM_DELETE_WINDOW", close_add_window)

def close_add_window():
    #closes add window object
    global add_window_object
    global cancel_btn
    global timers
    add_window_object.destroy()
    add_window_object = False
    cancel_btn = False

    dump_garbage()
    sort_timers()
    for i in timers:
        i.render_config()

def ok_close_add_window(timer_pos=False):
    #exit function for add_window_object
    #either closes window and adds timer to timers list
    #or pops up an error
    #
    #cant be bothered to verify if time entry is actually valid
    #program wont crash if they input 100 hours, so i only check if its numeric
    #
    #i have to global everything because tkinter is dumb and wont
    #let me pass function arguments through buttons
    #Edit: found a better way but no time to implement it (use lambdas)
    global are_timers_saved
    are_timers_saved = False
    
    global time_hours
    global time_minutes
    global timer_name
    global entry_colour
    global cancel_btn
    global sound_file_location
    
    if not cancel_btn:
        return

    if not time_hours.get().isnumeric():
        messagebox.showerror('Error','Invalid time format, must be in HH and MM, and be between 00:00 and 23:59')
        return
    if not time_minutes.get().isnumeric():
        messagebox.showerror('Error','Invalid time format, must be in HH and MM, and be between 00:00 and 23:59')
        return

    if ";" in timer_name.get():
        messagebox.showerror('Error','Bell name cannot contain characters "," or ";"')
        return
    if "," in timer_name.get():
        messagebox.showerror('Error','Bell name cannot contain characters "," or ";"')
        return

    global timers

    #if timer_pos is supllied delete the timer
    #instead of updating it i just delete it and create a new one because im lazy
    if type(timer_pos) == int:
        del timers[timer_pos]
        
    #name, timer_time, place, colour, sound
    timers.append(entry(timer_name.get(), int(time_hours.get())*60 + int(time_minutes.get()), False, entry_colour, sound_file_location))
    close_add_window()

class entry:
    #creates a class that is used to create entries on the window
    #
    #name is a str, name of the entry
    #timer_time is an int, time of the timer
    #place is an int, place in the timers
    #colour is a hex str of colour indicator colour
    #
    #!!!Remember to call get_time() beforehand or the program will crash!!!
    def __init__(self, name, timer_time, order, colour, sound):
        self.name = name
        self.timer_time = timer_time
        self.order = order
        self.colour = colour
        self.sound = sound

    def render(self, config_mode=False):
        #positioning is dependant on a function of position
        offset = (self.order) * 33
        if config_mode: offset2 = 60
        else: offset2 = 0      
        #create the color indicator and render it
        #
        #i have to do the stupid stuff with the invisible 1x1 image because
        #i can just update bg colour to change the colour instead of doing something
        #with PIL
        invis_placeholder = PhotoImage(file="assets/invis_placeholder.png")
        color_indicator = tk.Label(window, image=invis_placeholder, bg=self.colour, width=11, height=24, border=0)
        color_indicator.place(x=0, y=107 + offset)

        #create the seperator bar and render it
        sep = tk.Label(window, image=invis_placeholder, border=0, bg="#8E8E93", fg="#8E8E93", width=252, height=1)
        sep.place(x=24, y=103 + offset)

        #Render name of timer
        #
        #we cant resize it in pixels so we just hope that the correct font is
        #on the system or else its gonna break
        name_object = tk.Label(window, text=self.name, font=("Segoe_UI", 15), bg="#1C1C1E", fg="#FFFFFF")
        name_object.place(x=24, y=104 + offset)

        #render time text object
        #
        #convert int time to 24 hour time (diplay only):
        #str(current_time // 60) + ":" + str(current_time - (current_time // 60) * 60)
        time_object = tk.Label(window, text=str(self.timer_time // 60) + ":" + ("0" * (2 - len(str(self.timer_time - (self.timer_time // 60) * 60)))) + str(self.timer_time - (self.timer_time // 60) * 60), font=("Segoe_UI", 15), bg="#1C1C1E", fg="#FFFFFF")
        time_object.place(x=220 - offset2, y=104 + offset)

        #garbage collection so unused objects get deleetd
        add_garbage(time_object, name_object, sep, color_indicator)

    def render_config(self):
        #renders config buttons
        offset = (self.order) * 33
        self.render(config_mode=True)
        global timer_pos
        timer_pos = self.order

        global garbage
        
        edit_btn_img = PhotoImage(file="assets/edit_entry.png")
        edit_btn = tk.Button(add_window_object, text="", command=lambda:add_window(self.order), image=edit_btn_img, relief="flat", bg="#1C1C1E", activebackground="#1C1C1E", borderwidth=0)
        edit_btn.image = edit_btn_img
        edit_btn.place(x=224, y=108 + offset)
        add_garbage(edit_btn)

        delete_btn_img = PhotoImage(file="assets/delete_entry.png")
        delete_btn = tk.Button(add_window_object, text="",command=lambda:del_timer_special(self.order),  image=delete_btn_img, relief="flat", bg="#1C1C1E", activebackground="#1C1C1E", borderwidth=0)
        delete_btn.image = delete_btn_img
        delete_btn.place(x=253, y=106 + offset)
        add_garbage(delete_btn)

    def ring_entry(self):
        #plays custom sound
        ps.playsound(self.sound)



#useful values:
##1C1C1E bg color

#boot gui
window = tk.Tk()
window.title("BellApp")
window.geometry("300x500")
window['background']='#1C1C1E'
window.iconbitmap("assets\\bell.ico")
window.resizable(False, False)

#config button
config_image = PhotoImage(file="assets/config.png")
btn_config_widget = tk.Button(window, text="", command=config, image=config_image, relief="flat", bg="#1C1C1E", activebackground="#1C1C1E", borderwidth=0)
btn_config_widget.place(x=24, y=18)

#start button
start_image = PhotoImage(file="assets/start.png")
btn_start_widget = tk.Button(window, text="", command=start, image=start_image, relief="flat", bg="#1C1C1E", activebackground="#1C1C1E", borderwidth=0)
btn_start_widget.place(x=116, y=18)

#stop button
stop_image = PhotoImage(file="assets/stop.png")
btn_stop_widget = tk.Button(window, text="", command=stop, image=stop_image, relief="flat", bg="#1C1C1E", activebackground="#1C1C1E", borderwidth=0)
btn_stop_widget.place(x=208, y=18)

#status bar
bar_mode = PhotoImage(file="assets/bar_stop_mode.png")
bar = tk.Label(window, text="", image=bar_mode, bg="#1C1C1E", border=0)
bar.place(x=24, y=60)

#saveload background
saveload_bg_img = PhotoImage(file="assets/bar_saveload.png")
saveload_bg = tk.Label(window, text="", image=saveload_bg_img, border=0)

#save button
save_btn_img = PhotoImage(file="assets/save_icon.png")
save_btn = tk.Button(window, text="", command=save, image=save_btn_img, relief="flat", bg="#32A0F7", activebackground="#32A0F7", borderwidth=0, border=0)

#load button
load_btn_img = PhotoImage(file="assets/load_icon.png")
load_btn = tk.Button(window, text="", command=load, image=load_btn_img, relief="flat", bg="#32A0F7", activebackground="#32A0F7", borderwidth=0, border=0)

#add button
add_btn_img = PhotoImage(file="assets/add_icon.png")
add_btn = tk.Button(window, text="", command=add_window, image=add_btn_img, relief="flat", bg="#32A0F7", activebackground="#32A0F7", borderwidth=0, border=0)

#forced ring button
ring_btn_img = PhotoImage(file="assets/forced_ring.png")
ring_btn = tk.Button(window, text="", command=ring_sound, image=ring_btn_img, relief="flat", bg="#1C1C1E", activebackground="#1C1C1E", borderwidth=0, border=0)
ring_btn.place(x=25, y=451)

#alpha build text
alpha_text= tk.Label(window, text="This is an alpha build meant for bugtesting. Alpha build 0.2", font=("Arial", 7), bg="#1C1C1E", border=0, fg="#FFFFFF")
alpha_text.place(x=30, y=490)

window.protocol("WM_DELETE_WINDOW", confirm_close)
window.mainloop()
