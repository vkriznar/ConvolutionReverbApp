# Kivy imports
from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.clock import Clock

# Python imports
from pyglet.media import load, Player
from audio_metadata import load as metaload
from math import floor

# Personal file imports
from src.convolver import MusicConvolver
from src.data import data as ir_data, buttonStr


class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)


class MyGridLayout(Widget):
    loadfile = ObjectProperty(None)
    savefile = ObjectProperty(None)
    text_input = ObjectProperty(None)

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load(self):
        # Show files as a LoadDialog popup
        content = LoadDialog(load=self.dismiss_popup, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def show_ir_signals(self):
        # Show impulse response signals as scrollable popup
        layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        for i in range(10):
            btn = Builder.load_string(buttonStr.format(ir_data[i], ir_data[i]))
            layout.add_widget(btn)
        content = ScrollView(size_hint=(0.9, None), size=(self.width, self.height * 0.8))
        content.add_widget(layout)
        self._popup = Popup(title="Select Impulse Response", content=content, size_hint=(0.9, 0.9))
        self._popup.open()


class Convolver(App):
    def build(self):
        # Initialize necessary classes and return main layout for app to display
        self.convolver = MusicConvolver()
        self.layout = MyGridLayout()
        self.player = Player()
        return self.layout

    def load(self, filenames):
        # Load file to app and get required metadata from music file
        filename = filenames[0].split("\\")[-1]
        metadata = metaload(filenames[0])

        # Load file into convolver class
        self.convolver.load_file(filename)
        artist, song_name = filename.split(" - ")

        # Set file's metadata info in app
        self.layout.ids.song_artist_label.text = "Artist: " + artist
        self.layout.ids.song_name_label.text = "Title: " + song_name.split(".")[0]

        if hasattr(metadata.tags, "album"):
            self.layout.ids.song_album_label.text = "Album: " + metadata.tags.album[0]
        if hasattr(metadata.tags, "genre"):
            self.layout.ids.song_genre_label.text = "Genre: " + metadata.tags.genre[0]

        duration = metadata.streaminfo.duration
        self.layout.ids.song_duration_label.text = "Duration: {:02d}:{:02d}:{:02d}".format(
            floor(duration/3600), floor(duration/60), floor(duration % 60))

        self.layout.dismiss_popup()

    def ir_selected(self, button):
        # Load impulse response signal file into convolver class
        self.convolver.load_ir(button.text)

        # Set IR name and picture in app
        self.layout.ids.ir_signal_label.text = "IR: " + button.text
        self.layout.ids.ir_signal_image.size_hint_x = 0.7
        self.layout.ids.ir_signal_image.size_hint_y = 0.7
        self.layout.ids.ir_signal_image.source = "../media/images/{}.jpg".format(button.text)

        self.layout.dismiss_popup()

    def convolve(self):
        # Load audio file and init variables
        filename = self.convolver.convolve()
        source = load(filename, streaming=False)

        # Pause the player and set gui items to correct values
        self.player.pause()
        self.layout.ids.play_pause_button.text = "Play"
        self.duration = source.duration
        self.layout.ids.slider.value = 0

        # Reset the player
        self.player = Player()
        self.player.queue(source)
        self.player.volume = self.layout.ids.volume_slider.value
        self.playing_audio = False
        self.played = 0

        # Show media player and initialize media player variables
        self.layout.ids.slider.opacity = 1
        self.layout.ids.audio_layout.opacity = 1
        self.layout.ids.slider.max = self.duration
        self.set_duration_label()

    def playing(self, dt):
        # If we have played whole song, pause it, sets it source pos to 0, and update neccesary labels and buttons
        if self.layout.ids.slider.value >= self.duration - 1:
            self.player.pause()
            self.player.source.seek(0)

            self.playing_audio = False
            self.layout.ids.slider.value = 0
            self.layout.ids.play_pause_button.text = "Play"
            self.set_duration_label()
        if self.playing_audio:
            self.set_duration_label()
            self.layout.ids.slider.value += 1
        return self.playing_audio

    def play_pause(self):
        # Change bool value
        self.playing_audio = not self.playing_audio
        if self.playing_audio:
            self.layout.ids.play_pause_button.text = "Pause"
            self.player.play()
            Clock.schedule_interval(self.playing, 1)
        else:
            self.layout.ids.play_pause_button.text = "Play"
            self.player.pause()

    def volume_slider_change(self):
        volume = self.layout.ids.volume_slider.value
        self.player.volume = volume
        self.layout.ids.volume_label.text = "Vol: " + str(int(volume * 100))

    def time_slider_change(self):
        if self.player.source is None:
            return
        self.player.source.seek(int(self.layout.ids.slider.value))
        self.set_duration_label()

    # Helper function, called multiple times
    def set_duration_label(self):
        self.layout.ids.duration_label.text = "{:02d}:{:02d}/{:02d}:{:02d}".format(
            floor(self.layout.ids.slider.value / 60),
            floor(self.layout.ids.slider.value % 60),
            floor(self.duration / 60),
            floor(self.duration % 60))


if __name__ == "__main__":
    Window.maximize()
    app = Convolver().run()
