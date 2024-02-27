import pygame
import tkinter
from tkinter import ttk, messagebox, Listbox
import sys
from tkinter import filedialog as fd
import tkinter.filedialog as fd
from mutagen.mp3 import MP3


pygame.mixer.init()
selected_song = None
next_song_flag = False
pause = False
def play():
    global selected_song
    global next_song_flag
    global pause
    if pause == True:
        pygame.mixer.music.unpause()
        pause = False
        return
    try:
        selected_song = selected_item(next_song_flag)
        pygame.mixer.music.load(selected_song)
        pygame.mixer.music.play()
        
    except Exception as e:
        print(e)
        print("No such file")
        messagebox.showerror("Error", "No such file",icon="error")

def pause():
    global pause
    pause = True
    pygame.mixer.music.pause()


def volume_up():
    pygame.mixer.music.set_volume(pygame.mixer.music.get_volume() + 0.1)
    if pygame.mixer.music.get_volume() > 0.9:
        pygame.mixer.music.set_volume(1)

def volume_down():
    pygame.mixer.music.set_volume(pygame.mixer.music.get_volume() - 0.1)
    if pygame.mixer.music.get_volume() < 0.1:
        pygame.mixer.music.set_volume(0)
    
def import_song():
    global selected_song
    file = fd.askopenfiles()
    selected_song = file[0].name
    Lb1.insert(Lb1.size()+1,selected_song)
    update_scale_info()
    
    
def selected_item(flag):
    global selected_song
    global next_song_flag
    if flag != True:
        selected_song = Lb1.get(Lb1.curselection())
    else:
        index = Lb1.curselection()[0]
        selected_song = Lb1.get(index+1)
        next_index = index + 1
        if next_index < Lb1.size():
            Lb1.selection_clear(0, "end")
            Lb1.selection_set(next_index)
            Lb1.activate(next_index) 
    flag = False
    return selected_song 

def next_song():
    global next_song_flag
    global pause
    next_song_flag = True
    #update_scale_info(selected_song)
    pause = False
    play()
    next_song_flag = False

def previous_song():

    pass

def update_scale_info():
    total_time_seconds = pygame.mixer.Sound(selected_song).get_length()
    audio_length_minutes = total_time_seconds // 60
    total_time_seconds %= 60
    #print("total time seconds", total_time_seconds)
    current_time_seconds = pygame.mixer.music.get_pos() / 1000
    current_time_minutes = current_time_seconds // 60
    current_time_seconds %= 60
    starttime=ttk.Label(frm, text=(f"{int(current_time_minutes):02d}:{int(current_time_seconds):02d}")).grid(column=2, row=11)
    endtime=ttk.Label(frm, text=(f"{int(audio_length_minutes):02d}:{int(total_time_seconds):02d}")).grid(column=6, row=11)
    root.after(1000, update_scale_info)
    

root = tkinter.Tk()
root.geometry("900x500")
frm = ttk.Frame(root, padding=10,height=500,width=500)
frm.grid()
ttk.Label(frm, text="Audio Player").grid(column=0, row=0)
ttk.Button(frm, text="Quit", command=root.destroy).grid(column=1, row=0)
ttk.Button(frm, text="Play", command=play).grid(column=2, row=0)
ttk.Button(frm, text="Pause", command=pause).grid(column=3, row=0)
ttk.Button(frm, text="Import",command=import_song).grid(column=4, row=0)
ttk.Button(frm, text="Next",command=next_song).grid(column=5, row=0)
ttk.Button(frm, text="Previous" ).grid(column=6, row=0)
ttk.Button(frm, text="+sound",command=volume_up).grid(column=7, row=0)
ttk.Button(frm, text="-sound",command=volume_down).grid(column=8, row=0)
Scale = ttk.Scale(frm, from_=0, to=100, orient='horizontal')
Lb1 = Listbox(frm)
Lb1.grid(column=0, columnspan=10, rowspan=10, padx=5, pady=5, sticky='nswe', ipady=25, row=1)
Scale.grid(column=3, row=11, columnspan=3, sticky='nswe')
starttime=ttk.Label(frm, text="00:00").grid(column=2, row=11)
endtime=ttk.Label(frm, text="00:00").grid(column=6, row=11)

#Lb1.grid(column=0,row=1)
#Lb1.pack()

root.mainloop()
#root.after(1000, update_scale_info(selected_song))