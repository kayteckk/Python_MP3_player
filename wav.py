import pygame
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Listbox

class AudioPlayerApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("900x500")
        self.frm = ttk.Frame(root, padding=10, height=500, width=500)
        self.frm.grid()

        self.selected_song = None
        self.next_song_flag = False
        self.pause = False
        pygame.mixer.init()
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self.frm, text="Audio Player").grid(column=0, row=0)
        ttk.Button(self.frm, text="Quit", command=self.root.destroy).grid(column=1, row=0)
        ttk.Button(self.frm, text="Play", command=self.play).grid(column=2, row=0)
        ttk.Button(self.frm, text="Pause", command=self.toggle_pause).grid(column=3, row=0)
        ttk.Button(self.frm, text="Import", command=self.import_song).grid(column=4, row=0)
        ttk.Button(self.frm, text="Next", command=self.next_song).grid(column=5, row=0)
        ttk.Button(self.frm, text="Previous").grid(column=6, row=0)
        ttk.Button(self.frm, text="+sound", command=self.volume_up).grid(column=7, row=0)
        ttk.Button(self.frm, text="-sound", command=self.volume_down).grid(column=8, row=0)

        self.Scale = ttk.Scale(self.frm, from_=0, to=100, orient='horizontal')
        self.Scale.grid(column=3, row=11, columnspan=3, sticky='nswe')
        self.starttime_label = ttk.Label(self.frm, text="00:00")
        self.starttime_label.grid(column=2, row=11)
        self.endtime_label = ttk.Label(self.frm, text="00:00")
        self.endtime_label.grid(column=6, row=11)

        self.Lb1 = Listbox(self.frm)
        self.Lb1.grid(column=0, columnspan=10, rowspan=10, padx=5, pady=5, sticky='nswe', ipady=25, row=1)

        self.update_scale_info()

    def play(self):
        if self.pause:
            pygame.mixer.music.unpause()
            self.pause = False 
            return 
        try:
            self.selected_song = self.selected_item(self.next_song_flag)
            pygame.mixer.music.load(self.selected_song)
            pygame.mixer.music.play()
        except Exception as e:
            print(e)
            print("No such file")
            messagebox.showerror("Error", "No such file", icon="error")

    def toggle_pause(self):
        self.pause = True
        pygame.mixer.music.pause()

    def volume_up(self):
        pygame.mixer.music.set_volume(min(1, pygame.mixer.music.get_volume() + 0.1))
        if pygame.mixer.music.get_volume() > 0.9:
            pygame.mixer.music.set_volume(1)

    def volume_down(self):
        pygame.mixer.music.set_volume(max(0, pygame.mixer.music.get_volume() - 0.1))
        if pygame.mixer.music.get_volume() < 0.1:
            pygame.mixer.music.set_volume(0)

    def import_song(self):
        file = filedialog.askopenfile()
        if file:
            self.selected_song = file.name
            self.Lb1.insert(self.Lb1.size() + 1, self.selected_song)
            self.update_scale_info()

    def selected_item(self, flag):
        if flag:
            index = self.Lb1.curselection()[0]
            selected_song = self.Lb1.get(index + 1)
            next_index = index + 1
            if next_index < self.Lb1.size():
                self.Lb1.selection_clear(0, "end")
                self.Lb1.selection_set(next_index)
                self.Lb1.activate(next_index)
        else:
            selected_song = self.Lb1.get(self.Lb1.curselection())
        return selected_song

    def next_song(self):
        self.next_song_flag = True
        self.pause = False
        self.play()
        self.next_song_flag = False

    def update_scale_info(self):
        if self.selected_song:
            total_time_seconds = pygame.mixer.Sound(self.selected_song).get_length()
            audio_length_minutes = total_time_seconds // 60
            total_time_seconds %= 60
            current_time_seconds = pygame.mixer.music.get_pos() / 1000
            current_time_minutes = current_time_seconds // 60
            current_time_seconds %= 60
            self.starttime_label.config(text=f"{int(current_time_minutes):02d}:{int(current_time_seconds):02d}")
            self.endtime_label.config(text=f"{int(audio_length_minutes):02d}:{int(total_time_seconds):02d}")

        self.root.after(1000, self.update_scale_info)

root = tk.Tk()
app = AudioPlayerApp(root)
root.mainloop()
