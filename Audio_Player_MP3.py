from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSlider, QFileDialog, QListWidget, QMessageBox
from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5.QtMultimedia import QMediaPlayer, QMediaPlaylist, QMediaContent
import sys
import sqlite3

con = sqlite3.connect("song_list.db")
cur = con.cursor()
cur.execute("CREATE TABLE if not exists songs_list(path,name);")

class AudioPlayerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audio Player")
        self.setGeometry(100, 100, 850, 300)
        self.player = QMediaPlayer()
        self.playlist = QMediaPlaylist()
        self.player.setPlaylist(self.playlist)
        self.create_widgets()
        self.is_slider_pressed = False 
        self.global_volume = 10
        self.player.positionChanged.connect(self.update_position)
        self.player.durationChanged.connect(self.set_duration_range)
        self.load_songs_to_list_from_db()
        self.timer = QTimer(self)
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_slider_position)

    def create_widgets(self):
        layout = QVBoxLayout()

        control_layout = QHBoxLayout()
        control_layout.addWidget(QLabel("Audio Player"))
        quit_button = QPushButton("Quit")
        quit_button.clicked.connect(self.close)
        control_layout.addWidget(quit_button)
        self.play_button = QPushButton("Play")
        self.play_button.setEnabled(False)
        self.play_button.clicked.connect(self.toggle_play)
        control_layout.addWidget(self.play_button)
        import_button = QPushButton("Import")
        import_button.clicked.connect(self.import_songs)
        control_layout.addWidget(import_button)
        next_button = QPushButton("Next")
        next_button.clicked.connect(self.next_song)
        control_layout.addWidget(next_button)
        previous_button = QPushButton("Previous")
        previous_button.clicked.connect(self.previous_song)
        control_layout.addWidget(previous_button)

        remove_button = QPushButton("Remove")
        remove_button.clicked.connect(self.remove_song_from_list_and_db)
        control_layout.addWidget(remove_button)
        
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(10)
        self.volume_slider.sliderReleased.connect(self.set_volume)
        control_layout.addWidget(self.volume_slider)
        
        layout.addLayout(control_layout)

        self.scale = QSlider(Qt.Horizontal)
        self.scale.setRange(0, 100000)
        self.scale.sliderPressed.connect(self.slider_pressed)
        self.scale.sliderReleased.connect(self.slider_released)
        layout.addWidget(self.scale)

        time_layout = QHBoxLayout()
        self.starttime_label = QLabel("00:00")
        time_layout.addWidget(self.starttime_label)
        time_layout.addStretch()
        self.endtime_label = QLabel("00:00")
        time_layout.addWidget(self.endtime_label)
        layout.addLayout(time_layout)

        self.song_list = QListWidget()
        self.song_list.setSelectionMode(QListWidget.SingleSelection)
        self.song_list.itemClicked.connect(self.play_selected_song)
        layout.addWidget(self.song_list)

        self.setLayout(layout)

    def toggle_play(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
            self.timer.stop()
        else:
            self.player.play()
            self.timer.start()

    def import_songs(self):
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("MP3 Files (*.mp3)")
        file_dialog.setViewMode(QFileDialog.List)
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        if file_dialog.exec_():
            file_paths = file_dialog.selectedFiles()
            for file_path in file_paths:
                url = QUrl.fromLocalFile(file_path)
                song_name = url.fileName()
                cur.execute("SELECT * FROM songs_list WHERE name = ?", (song_name,))
                existing_record = cur.fetchone()
                if existing_record:
                    msg_box = QMessageBox()
                    msg_box.setIcon(QMessageBox.Warning)
                    msg_box.setText(f"This song: {song_name} already exists in Database.")
                    msg_box.setStandardButtons(QMessageBox.Ok)
                    retval = msg_box.exec_()
                    continue
                self.song_list.addItem(song_name)
                media = QMediaContent(url)
                self.playlist.addMedia(media)
                cur.execute("INSERT INTO songs_list (path, name) VALUES (?, ?)", (file_path, song_name))
            self.playlist.setCurrentIndex(0) 
            self.player.setPlaylist(self.playlist)
            self.player.mediaStatusChanged.connect(self.check_media_status)
            con.commit()

    def load_songs_to_list_from_db(self):
        cur.execute("SELECT * FROM songs_list")
        records = cur.fetchall()
        for row in records:
            url = QUrl.fromLocalFile(row[0])
            media = QMediaContent(url)
            self.playlist.addMedia(media)
            self.song_list.addItem(row[1])

    def remove_song_from_list_and_db(self):
        row = self.song_list.currentRow()
        item_to_remove = self.song_list.item(row).text()
        self.song_list.takeItem(row)
        cur.execute("DELETE FROM songs_list WHERE name=?", (item_to_remove,))
        con.commit()

    def check_media_status(self, status):
        if status == QMediaPlayer.LoadedMedia:
            self.player.mediaStatusChanged.disconnect(self.check_media_status)
            self.set_duration_range()

    def set_duration_range(self):
        duration = self.player.duration() / 1000
        self.scale.setMaximum(int(self.player.duration()))

    def play_selected_song(self):
        selected_item = self.song_list.currentItem()
        if selected_item:
            index = self.song_list.row(selected_item)
            self.playlist.setCurrentIndex(index)
            self.player.setVolume(self.global_volume) 
            self.player.play()
            self.update_time_labels()
            self.play_button.setEnabled(True)
            self.set_duration_range()
            self.timer.start()

    def next_song(self):
        next_index = self.playlist.nextIndex()
        if next_index != -1:
            self.playlist.setCurrentIndex(next_index)
            self.player.setVolume(self.global_volume)
            self.player.play()
            self.song_list.setCurrentRow(next_index)
            self.set_duration_range()
            self.timer.start()

    def previous_song(self):
        prev_index = self.playlist.previousIndex()
        if prev_index != -1:
            self.playlist.setCurrentIndex(prev_index)
            self.player.setVolume(self.global_volume)
            self.player.play()
            self.song_list.setCurrentRow(prev_index)
            self.set_duration_range()
            self.timer.start()

    def set_volume(self):
        volume = self.volume_slider.value()
        self.player.setVolume(volume)
        self.global_volume = volume

    def slider_pressed(self):
        self.is_slider_pressed = True

    def slider_released(self):
        self.is_slider_pressed = False
        if not self.volume_slider.isSliderDown():
            self.set_position()

    def set_position(self):
        if not self.is_slider_pressed:
            position = self.scale.value()  
            self.player.setPosition(position)

    def update_time_labels(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            duration = self.player.duration() / 1000
            minutes, seconds = divmod(duration, 60)
            self.endtime_label.setText("{:02}:{:02}".format(int(minutes), int(seconds)))
        else:
            self.endtime_label.setText("00:00")

    def update_position(self, position):
        if not self.is_slider_pressed:
            position_seconds = position / 1000
            minutes, seconds = divmod(position_seconds, 60)
            self.starttime_label.setText("{:02}:{:02}".format(int(minutes), int(seconds)))
            self.scale.setValue(position)
            self.update_time_labels()

    def update_slider_position(self):
        if not self.is_slider_pressed and self.player.state() == QMediaPlayer.PlayingState:
            position = self.player.position()
            self.scale.setValue(position)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = AudioPlayerApp()
    player.show()
    sys.exit(app.exec_())
