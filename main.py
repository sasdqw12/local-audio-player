from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton, MDRoundFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDList, OneLineListItem
from kivymd.uix.seekbar import MDSlider
from kivy.core.audio import SoundLoader
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.storage.jsonstore import JsonStore
import os
import glob

class AudioPlayerScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sound = None
        self.audio_files = []
        self.current_index = 0
        self.is_playing = False
        self.current_dir = ""
        self.store = JsonStore("player_config.json")
        
        # 主布局
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # 目录选择区域
        self.dir_label = MDLabel(
            text="未选择目录",
            halign="center",
            size_hint_y=0.1
        )
        self.layout.add_widget(self.dir_label)
        
        self.select_dir_btn = MDRaisedButton(
            text="选择音频目录",
            pos_hint={"center_x": 0.5},
            size_hint_y=0.1,
            on_press=self.select_directory
        )
        self.layout.add_widget(self.select_dir_btn)
        
        # 播放列表区域
        self.playlist_label = MDLabel(
            text="播放列表",
            size_hint_y=0.08
        )
        self.layout.add_widget(self.playlist_label)
        
        self.scroll = ScrollView(size_hint_y=0.3)
        self.playlist = MDList()
        self.scroll.add_widget(self.playlist)
        self.layout.add_widget(self.scroll)
        
        # 当前播放信息
        self.current_song_label = MDLabel(
            text="当前未播放",
            halign="center",
            size_hint_y=0.1
        )
        self.layout.add_widget(self.current_song_label)
        
        # 进度条
        self.progress_slider = MDSlider(
            min=0,
            max=100,
            value=0,
            size_hint_y=0.08,
            disabled=True
        )
        self.layout.add_widget(self.progress_slider)
        
        # 控制按钮区域
        controls = BoxLayout(orientation='horizontal', spacing=20, size_hint_y=0.15, padding=[20, 0])
        
        self.prev_btn = MDRoundFlatButton(
            text="上一首",
            on_press=self.play_prev
        )
        controls.add_widget(self.prev_btn)
        
        self.play_pause_btn = MDRaisedButton(
            text="播放",
            on_press=self.toggle_play_pause
        )
        controls.add_widget(self.play_pause_btn)
        
        self.next_btn = MDRoundFlatButton(
            text="下一首",
            on_press=self.play_next
        )
        controls.add_widget(self.next_btn)
        
        self.layout.add_widget(controls)
        
        # 循环模式按钮
        self.loop_btn = MDRoundFlatButton(
            text="循环模式: 列表循环",
            pos_hint={"center_x": 0.5},
            size_hint_y=0.09,
            on_press=self.toggle_loop_mode
        )
        self.layout.add_widget(self.loop_btn)
        self.loop_mode = "list" # list, single, shuffle
        
        self.add_widget(self.layout)
        
        # 加载上次保存的目录
        if self.store.exists("last_dir"):
            last_dir = self.store.get("last_dir")["path"]
            if os.path.exists(last_dir):
                self.load_directory(last_dir)
        
        # 定时更新进度
        Clock.schedule_interval(self.update_progress, 0.5)
    
    def select_directory(self, instance):
        # 安卓环境下调用系统目录选择器
        try:
            from android.permissions import request_permissions, Permission
            from android.storage import primary_external_storage_path
            request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
            
            from plyer import filechooser
            filechooser.choose_dir(on_selection=self.on_dir_selected)
        except Exception as e:
            # 桌面测试环境，使用模拟路径
            test_dir = os.path.expanduser("~/Music")
            if os.path.exists(test_dir):
                self.on_dir_selected([test_dir])
            else:
                self.dir_label.text = f"请在安卓设备上选择目录，错误: {str(e)}"
    
    def on_dir_selected(self, selection):
        if selection and len(selection) > 0:
            selected_dir = selection[0]
            self.load_directory(selected_dir)
            # 保存选择的目录
            self.store.put("last_dir", path=selected_dir)
    
    def load_directory(self, dir_path):
        self.current_dir = dir_path
        self.dir_label.text = f"当前目录: {os.path.basename(dir_path)}"
        
        # 扫描音频文件
        self.audio_files = []
        audio_extensions = ['*.mp3', '*.wav', '*.ogg', '*.m4a', '*.flac', '*.aac']
        for ext in audio_extensions:
            self.audio_files.extend(glob.glob(os.path.join(dir_path, ext)))
            self.audio_files.extend(glob.glob(os.path.join(dir_path, ext.upper())))
        
        self.audio_files.sort()
        
        # 更新播放列表
        self.playlist.clear_widgets()
        for idx, file_path in enumerate(self.audio_files):
            filename = os.path.basename(file_path)
            item = OneLineListItem(
                text=filename,
                on_press=lambda x, i=idx: self.play_song(i)
            )
            self.playlist.add_widget(item)
        
        if self.audio_files:
            self.current_index = 0
            self.play_song(0)
    
    def play_song(self, index):
        if index < 0 or index >= len(self.audio_files):
            return
        
        # 停止当前播放
        if self.sound:
            self.sound.stop()
            self.sound.unload()
        
        self.current_index = index
        file_path = self.audio_files[index]
        filename = os.path.basename(file_path)
        
        # 加载新音频
        self.sound = SoundLoader.load(file_path)
        if self.sound:
            self.sound.play()
            self.is_playing = True
            self.play_pause_btn.text = "暂停"
            self.current_song_label.text = f"正在播放: {filename}"
            self.progress_slider.max = self.sound.length
            self.progress_slider.disabled = False
    
    def toggle_play_pause(self, instance):
        if not self.sound:
            if self.audio_files:
                self.play_song(self.current_index)
            return
        
        if self.is_playing:
            self.sound.stop()
            self.is_playing = False
            self.play_pause_btn.text = "播放"
        else:
            self.sound.play()
            self.is_playing = True
            self.play_pause_btn.text = "暂停"
    
    def play_prev(self, instance):
        if not self.audio_files:
            return
        new_index = self.current_index - 1
        if new_index < 0:
            new_index = len(self.audio_files) - 1
        self.play_song(new_index)
    
    def play_next(self, instance):
        if not self.audio_files:
            return
        new_index = self.current_index + 1
        if new_index >= len(self.audio_files):
            if self.loop_mode == "list":
                new_index = 0
            else:
                return
        self.play_song(new_index)
    
    def toggle_loop_mode(self, instance):
        modes = [
            ("list", "列表循环"),
            ("single", "单曲循环"),
            ("shuffle", "随机播放")
        ]
        current_idx = next(i for i, m in enumerate(modes) if m[0] == self.loop_mode)
        next_idx = (current_idx + 1) % len(modes)
        self.loop_mode = modes[next_idx][0]
        self.loop_btn.text = f"循环模式: {modes[next_idx][1]}"
    
    def update_progress(self, dt):
        if self.sound and self.is_playing:
            current_pos = self.sound.get_pos()
            self.progress_slider.value = current_pos
            
            # 检测播放结束
            if current_pos >= self.sound.length - 0.5:
                self.on_song_end()
    
    def on_song_end(self):
        if self.loop_mode == "single":
            self.sound.seek(0)
            self.sound.play()
        elif self.loop_mode == "shuffle":
            import random
            random_idx = random.randint(0, len(self.audio_files)-1)
            self.play_song(random_idx)
        else: # list loop
            self.play_next(None)

class LocalAudioPlayerApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        return AudioPlayerScreen()
    
    def on_pause(self):
        if self.root.sound and self.root.is_playing:
            self.root.sound.play()
        return True
    
    def on_resume(self):
        pass

if __name__ == "__main__":
    LocalAudioPlayerApp().run()
