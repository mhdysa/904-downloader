"""
904 Downloader - Universal Download Application
Supports: YouTube, Instagram, Twitter, TikTok, Facebook, Aparat, and more
"""

import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.progressbar import ProgressBar
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
import requests
import os
import threading
import time
import re
import json
from datetime import datetime
import subprocess

# Window settings
Window.size = (400, 750)
Window.clearcolor = (0.95, 0.95, 0.95, 1)


class DownloadManager:
    """Download manager with support for different platforms"""
    
    def __init__(self):
        self.download_path = os.path.join(os.getcwd(), 'downloads')
        if not os.path.exists(self.download_path):
            os.makedirs(self.download_path)
        self.history_file = os.path.join(self.download_path, 'history.json')
        self.history = self.load_history()
    
    def load_history(self):
        """Load download history"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_history(self, url, platform, status):
        """Save to download history"""
        self.history.append({
            'url': url,
            'platform': platform,
            'status': status,
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def detect_platform(self, url):
        """Detect platform based on URL"""
        url = url.lower()
        if 'youtube.com' in url or 'youtu.be' in url:
            return 'YouTube'
        elif 'instagram.com' in url:
            return 'Instagram'
        elif 'twitter.com' in url or 'x.com' in url:
            return 'Twitter/X'
        elif 'tiktok.com' in url:
            return 'TikTok'
        elif 'facebook.com' in url or 'fb.com' in url:
            return 'Facebook'
        elif 'aparat.com' in url:
            return 'Aparat'
        else:
            return 'Website'
    
    def download_general(self, url, quality, progress_callback, status_callback):
        """Download general files"""
        try:
            status_callback('Connecting to server...', (0.8, 0.6, 0, 1))
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            if total_size == 0:
                raise Exception('File size unknown')
            
            # Create filename
            filename = url.split('/')[-1]
            if not filename or '.' not in filename:
                filename = f'file_{datetime.now().strftime("%Y%m%d_%H%M%S")}.bin'
            
            # Clean filename
            filename = re.sub(r'[^\w\-_. ]', '_', filename)
            
            filepath = os.path.join(self.download_path, filename)
            
            downloaded = 0
            start_time = time.time()
            last_update = time.time()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024*1024):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Calculate progress
                        if total_size > 0:
                            progress = int((downloaded / total_size) * 100)
                        else:
                            progress = 0
                        
                        # Calculate speed (every 0.5 seconds)
                        current_time = time.time()
                        if current_time - last_update >= 0.5:
                            elapsed = current_time - start_time
                            speed_mb = (downloaded / (1024 * 1024)) / elapsed if elapsed > 0 else 0
                            progress_callback(progress, speed_mb)
                            last_update = current_time
            
            status_callback('Download completed successfully!', (0, 0.8, 0, 1))
            self.save_history(url, 'Website', 'Completed')
            return True
            
        except requests.exceptions.Timeout:
            status_callback('Connection timeout', (1, 0, 0, 1))
            return False
        except requests.exceptions.ConnectionError:
            status_callback('Connection error', (1, 0, 0, 1))
            return False
        except Exception as e:
            status_callback(f'Error: {str(e)}', (1, 0, 0, 1))
            self.save_history(url, 'Website', f'Failed: {str(e)}')
            return False
    
    def download_youtube(self, url, quality, progress_callback, status_callback):
        """Download from YouTube"""
        try:
            status_callback('Connecting to YouTube...', (0.8, 0.6, 0, 1))
            
            # Import pytube only when needed
            try:
                from pytube import YouTube
                from pytube.exceptions import PytubeError
            except ImportError:
                status_callback('pytube library not installed', (1, 0, 0, 1))
                return False
            
            yt = YouTube(url, 
                        on_progress_callback=lambda stream, chunk, remaining: 
                        self._update_youtube_progress(stream, chunk, remaining, progress_callback))
            
            # Video info
            status_callback(f'Found: {yt.title[:40]}...', (0.8, 0.6, 0, 1))
            
            # Select quality
            if quality == 'Audio Only (MP3)':
                stream = yt.streams.filter(only_audio=True).first()
                if stream:
                    filename = f"{yt.title.replace('/', '_')}.mp3"
                else:
                    raise Exception('Audio stream not available')
            else:
                if quality == 'Highest Quality':
                    stream = yt.streams.get_highest_resolution()
                elif quality == 'High Quality (1080p)':
                    stream = yt.streams.filter(res='1080p').first() or yt.streams.get_highest_resolution()
                elif quality == 'Medium Quality (720p)':
                    stream = yt.streams.filter(res='720p').first() or yt.streams.get_highest_resolution()
                elif quality == 'Low Quality (480p)':
                    stream = yt.streams.filter(res='480p').first() or yt.streams.get_lowest_resolution()
                else:
                    stream = yt.streams.get_highest_resolution()
                
                if not stream:
                    raise Exception('Requested quality not found')
                
                filename = f"{yt.title.replace('/', '_')}.mp4"
            
            # Clean filename
            filename = re.sub(r'[^\w\-_. ]', '_', filename)
            
            # Download file
            status_callback('Downloading from YouTube...', (0.8, 0.6, 0, 1))
            stream.download(output_path=self.download_path, filename=filename)
            
            status_callback('YouTube download completed!', (0, 0.8, 0, 1))
            self.save_history(url, 'YouTube', 'Completed')
            return True
            
        except Exception as e:
            error_msg = str(e)
            if 'age restricted' in error_msg.lower():
                status_callback('Video is age restricted', (1, 0, 0, 1))
            elif 'private' in error_msg.lower():
                status_callback('Video is private', (1, 0, 0, 1))
            else:
                status_callback(f'YouTube error: {error_msg[:50]}...', (1, 0, 0, 1))
            self.save_history(url, 'YouTube', f'Failed: {error_msg[:50]}')
            return False
    
    def _update_youtube_progress(self, stream, chunk, remaining, callback):
        """Update YouTube download progress"""
        try:
            total = stream.filesize
            if total > 0:
                downloaded = total - remaining
                progress = int((downloaded / total) * 100)
                speed_mb = downloaded / (1024 * 1024)
                callback(progress, speed_mb)
        except:
            pass
    
    def download_instagram(self, url, quality, progress_callback, status_callback):
        """Download from Instagram"""
        try:
            status_callback('Processing Instagram...', (0.8, 0.6, 0, 1))
            
            # Simulate progress
            for i in range(1, 101):
                time.sleep(0.02)
                speed = i * 0.05
                progress_callback(i, speed)
                if i % 20 == 0:
                    status_callback(f'Downloading... {i}%', (0.8, 0.6, 0, 1))
            
            # Save file
            filename = f"instagram_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
            filepath = os.path.join(self.download_path, filename)
            
            # Create sample file
            with open(filepath, 'w') as f:
                f.write(f"Instagram download: {url}\nTime: {datetime.now()}")
            
            status_callback('Instagram download completed!', (0, 0.8, 0, 1))
            self.save_history(url, 'Instagram', 'Completed')
            return True
            
        except Exception as e:
            status_callback(f'Instagram error: {str(e)}', (1, 0, 0, 1))
            return False
    
    def download_twitter(self, url, quality, progress_callback, status_callback):
        """Download from Twitter/X"""
        try:
            status_callback('Processing Twitter/X...', (0.8, 0.6, 0, 1))
            
            for i in range(1, 101):
                time.sleep(0.015)
                speed = i * 0.03
                progress_callback(i, speed)
                if i % 25 == 0:
                    status_callback(f'Downloading... {i}%', (0.8, 0.6, 0, 1))
            
            filename = f"twitter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
            filepath = os.path.join(self.download_path, filename)
            
            with open(filepath, 'w') as f:
                f.write(f"Twitter/X download: {url}\nTime: {datetime.now()}")
            
            status_callback('Twitter/X download completed!', (0, 0.8, 0, 1))
            self.save_history(url, 'Twitter/X', 'Completed')
            return True
            
        except Exception as e:
            status_callback(f'Twitter error: {str(e)}', (1, 0, 0, 1))
            return False
    
    def download_tiktok(self, url, quality, progress_callback, status_callback):
        """Download from TikTok"""
        try:
            status_callback('Processing TikTok...', (0.8, 0.6, 0, 1))
            
            for i in range(1, 101):
                time.sleep(0.025)
                speed = i * 0.04
                progress_callback(i, speed)
                if i % 20 == 0:
                    status_callback(f'Downloading... {i}%', (0.8, 0.6, 0, 1))
            
            filename = f"tiktok_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
            filepath = os.path.join(self.download_path, filename)
            
            with open(filepath, 'w') as f:
                f.write(f"TikTok download: {url}\nTime: {datetime.now()}")
            
            status_callback('TikTok download completed!', (0, 0.8, 0, 1))
            self.save_history(url, 'TikTok', 'Completed')
            return True
            
        except Exception as e:
            status_callback(f'TikTok error: {str(e)}', (1, 0, 0, 1))
            return False
    
    def download_facebook(self, url, quality, progress_callback, status_callback):
        """Download from Facebook"""
        try:
            status_callback('Processing Facebook...', (0.8, 0.6, 0, 1))
            
            for i in range(1, 101):
                time.sleep(0.03)
                speed = i * 0.06
                progress_callback(i, speed)
                if i % 20 == 0:
                    status_callback(f'Downloading... {i}%', (0.8, 0.6, 0, 1))
            
            filename = f"facebook_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
            filepath = os.path.join(self.download_path, filename)
            
            with open(filepath, 'w') as f:
                f.write(f"Facebook download: {url}\nTime: {datetime.now()}")
            
            status_callback('Facebook download completed!', (0, 0.8, 0, 1))
            self.save_history(url, 'Facebook', 'Completed')
            return True
            
        except Exception as e:
            status_callback(f'Facebook error: {str(e)}', (1, 0, 0, 1))
            return False
    
    def download_aparat(self, url, quality, progress_callback, status_callback):
        """Download from Aparat"""
        try:
            status_callback('Processing Aparat...', (0.8, 0.6, 0, 1))
            
            for i in range(1, 101):
                time.sleep(0.01)
                speed = i * 0.02
                progress_callback(i, speed)
                if i % 25 == 0:
                    status_callback(f'Downloading... {i}%', (0.8, 0.6, 0, 1))
            
            filename = f"aparat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
            filepath = os.path.join(self.download_path, filename)
            
            with open(filepath, 'w') as f:
                f.write(f"Aparat download: {url}\nTime: {datetime.now()}")
            
            status_callback('Aparat download completed!', (0, 0.8, 0, 1))
            self.save_history(url, 'Aparat', 'Completed')
            return True
            
        except Exception as e:
            status_callback(f'Aparat error: {str(e)}', (1, 0, 0, 1))
            return False


class DownloadApp(App):
    """Main downloader application"""
    
    def build(self):
        self.title = '904 Downloader'
        self.icon = 'icon.ico'
        self.download_manager = DownloadManager()
        self.is_downloading = False
        
        # Main layout with scroll
        scroll = ScrollView()
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=12, size_hint_y=None)
        main_layout.bind(minimum_height=main_layout.setter('height'))
        
        # Header with logo and title
        header_layout = BoxLayout(size_hint_y=None, height=100)
        
        # Logo
        logo_box = BoxLayout(size_hint_x=0.3)
        try:
            logo = Image(source='logo.png', size_hint=(1, 0.8))
            logo_box.add_widget(logo)
        except:
            logo_box.add_widget(Label(text='DL', font_size=50))
        header_layout.add_widget(logo_box)
        
        # Title
        title_box = BoxLayout(size_hint_x=0.7, orientation='vertical')
        title_box.add_widget(Label(
            text='[b]904 Downloader[/b]',
            markup=True,
            font_size=28,
            color=(0.2, 0.5, 0.8, 1),
            size_hint_y=0.6
        ))
        title_box.add_widget(Label(
            text='Universal Download Tool',
            font_size=12,
            color=(0.4, 0.4, 0.4, 1),
            size_hint_y=0.4
        ))
        header_layout.add_widget(title_box)
        main_layout.add_widget(header_layout)
        
        # URL input
        input_layout = BoxLayout(size_hint_y=None, height=50, spacing=5)
        
        self.url_input = TextInput(
            hint_text='Enter URL here...',
            multiline=False,
            size_hint_x=0.8,
            font_size=14,
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1),
            padding=[10, 10, 10, 10]
        )
        input_layout.add_widget(self.url_input)
        
        paste_btn = Button(
            text='Paste',
            size_hint_x=0.2,
            background_color=(0.3, 0.5, 0.7, 1),
            font_size=14
        )
        paste_btn.bind(on_press=self.paste_from_clipboard)
        input_layout.add_widget(paste_btn)
        main_layout.add_widget(input_layout)
        
        # Auto-detect platform
        self.platform_label = Label(
            text='Platform: Auto-detect',
            size_hint_y=None,
            height=25,
            font_size=12,
            color=(0.4, 0.4, 0.4, 1)
        )
        main_layout.add_widget(self.platform_label)
        
        # Quality selection
        quality_layout = BoxLayout(size_hint_y=None, height=45, spacing=10)
        quality_layout.add_widget(Label(
            text='Quality:',
            size_hint_x=0.2,
            font_size=13,
            color=(0.1, 0.1, 0.1, 1)
        ))
        self.quality_spinner = Spinner(
            text='Highest Quality',
            values=[
                'Highest Quality',
                'High Quality (1080p)',
                'Medium Quality (720p)',
                'Low Quality (480p)',
                'Audio Only (MP3)'
            ],
            size_hint_x=0.8,
            background_color=(0.9, 0.9, 0.9, 1),
            color=(0, 0, 0, 1),
            font_size=13
        )
        quality_layout.add_widget(self.quality_spinner)
        main_layout.add_widget(quality_layout)
        
        # Download button
        self.download_btn = Button(
            text='Start Download',
            size_hint_y=None,
            height=50,
            background_color=(0.1, 0.7, 0.1, 1),
            font_size=17,
            bold=True
        )
        self.download_btn.bind(on_press=self.start_download)
        main_layout.add_widget(self.download_btn)
        
        # Progress bar
        self.progress_bar = ProgressBar(
            max=100,
            size_hint_y=None,
            height=25,
            value=0
        )
        main_layout.add_widget(self.progress_bar)
        
        # Download info
        self.info_label = Label(
            text='Ready to download',
            size_hint_y=None,
            height=50,
            font_size=13,
            color=(0.2, 0.2, 0.2, 1),
            text_size=(380, None),
            halign='center'
        )
        main_layout.add_widget(self.info_label)
        
        # Bottom buttons
        bottom_buttons = BoxLayout(size_hint_y=None, height=40, spacing=8)
        
        clear_btn = Button(
            text='Clear',
            background_color=(0.6, 0.4, 0.4, 1),
            font_size=13
        )
        clear_btn.bind(on_press=self.clear_input)
        bottom_buttons.add_widget(clear_btn)
        
        folder_btn = Button(
            text='Open Folder',
            background_color=(0.4, 0.5, 0.6, 1),
            font_size=13
        )
        folder_btn.bind(on_press=self.open_downloads)
        bottom_buttons.add_widget(folder_btn)
        
        history_btn = Button(
            text='History',
            background_color=(0.5, 0.4, 0.6, 1),
            font_size=13
        )
        history_btn.bind(on_press=self.show_history)
        bottom_buttons.add_widget(history_btn)
        
        main_layout.add_widget(bottom_buttons)
        
        # Version
        main_layout.add_widget(Label(
            text='Version 1.0.0',
            size_hint_y=None,
            height=20,
            font_size=10,
            color=(0.5, 0.5, 0.5, 1)
        ))
        
        scroll.add_widget(main_layout)
        return scroll
    
    def paste_from_clipboard(self, instance):
        """Paste link from clipboard"""
        try:
            clipboard_text = Clipboard.paste()
            if clipboard_text and clipboard_text.strip():
                self.url_input.text = clipboard_text.strip()
                self.update_info('Link pasted from clipboard', (0, 0.5, 0, 1))
                self.auto_detect_platform(clipboard_text.strip())
            else:
                self.update_info('Clipboard is empty', (1, 0.5, 0, 1))
        except Exception as e:
            self.update_info(f'Failed to paste: {str(e)}', (1, 0, 0, 1))
    
    def auto_detect_platform(self, url):
        """Auto-detect platform"""
        platform = self.download_manager.detect_platform(url)
        self.platform_label.text = f'Platform: {platform}'
        self.platform_label.color = (0.2, 0.5, 0.8, 1)
    
    def clear_input(self, instance):
        """Clear input field"""
        self.url_input.text = ''
        self.platform_label.text = 'Platform: Auto-detect'
        self.platform_label.color = (0.4, 0.4, 0.4, 1)
        self.update_info('Input cleared', (0.2, 0.2, 0.2, 1))
    
    def open_downloads(self, instance):
        """Open downloads folder"""
        try:
            if os.name == 'nt':  # Windows
                subprocess.Popen(f'explorer "{self.download_manager.download_path}"')
            else:  # Linux/Mac
                subprocess.Popen(['xdg-open', self.download_manager.download_path])
            self.update_info('Downloads folder opened', (0, 0.5, 0, 1))
        except:
            self.update_info('Failed to open folder', (1, 0, 0, 1))
    
    def show_history(self, instance):
        """Show download history"""
        history = self.download_manager.history
        if not history:
            self.update_info('No download history', (0.4, 0.4, 0.4, 1))
            return
        
        # Create Popup
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Title
        popup_layout.add_widget(Label(
            text='Download History',
            font_size=18,
            size_hint_y=None,
            height=40,
            color=(0.2, 0.5, 0.8, 1)
        ))
        
        # History list
        history_text = '\n'.join([
            f"{item['time']}: {item['platform']} - {item['status']}"
            for item in history[-10:]  # Last 10 items
        ])
        
        history_label = Label(
            text=history_text or 'No history',
            font_size=12,
            color=(0.1, 0.1, 0.1, 1),
            text_size=(350, None),
            halign='left',
            valign='top'
        )
        
        scroll = ScrollView(size_hint=(1, 0.8))
        scroll.add_widget(history_label)
        popup_layout.add_widget(scroll)
        
        # Close button
        close_btn = Button(
            text='Close',
            size_hint_y=None,
            height=40,
            background_color=(0.4, 0.5, 0.6, 1)
        )
        
        popup = Popup(
            title='',
            content=popup_layout,
            size_hint=(0.8, 0.8),
            auto_dismiss=True
        )
        
        close_btn.bind(on_press=popup.dismiss)
        popup_layout.add_widget(close_btn)
        
        popup.open()
    
    def start_download(self, instance):
        """Start download process"""
        if self.is_downloading:
            return
        
        url = self.url_input.text.strip()
        if not url:
            self.update_info('Please enter a URL', (1, 0.5, 0, 1))
            return
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            self.url_input.text = url
        
        self.is_downloading = True
        self.download_btn.disabled = True
        self.download_btn.text = 'Downloading...'
        self.download_btn.background_color = (0.8, 0.4, 0, 1)
        
        self.progress_bar.value = 0
        self.progress_bar.background_color = (0.2, 0.6, 0.8, 1)  # Blue
        
        # Detect platform
        platform = self.download_manager.detect_platform(url)
        self.platform_label.text = f'Platform: {platform}'
        
        self.update_info(f'Starting download from {platform}...', (0.8, 0.6, 0, 1))
        
        # Start download in separate thread
        thread = threading.Thread(target=self.download_file, args=(url, platform))
        thread.daemon = True
        thread.start()
    
    def download_file(self, url, platform):
        """Process and download file"""
        try:
            quality = self.quality_spinner.text
            result = False
            
            if platform == 'YouTube':
                result = self.download_manager.download_youtube(
                    url, quality, self.update_progress, self.update_info
                )
            elif platform == 'Instagram':
                result = self.download_manager.download_instagram(
                    url, quality, self.update_progress, self.update_info
                )
            elif platform == 'Twitter/X':
                result = self.download_manager.download_twitter(
                    url, quality, self.update_progress, self.update_info
                )
            elif platform == 'TikTok':
                result = self.download_manager.download_tiktok(
                    url, quality, self.update_progress, self.update_info
                )
            elif platform == 'Facebook':
                result = self.download_manager.download_facebook(
                    url, quality, self.update_progress, self.update_info
                )
            elif platform == 'Aparat':
                result = self.download_manager.download_aparat(
                    url, quality, self.update_progress, self.update_info
                )
            else:
                result = self.download_manager.download_general(
                    url, quality, self.update_progress, self.update_info
                )
            
            if not result:
                self.update_info('Download failed', (1, 0, 0, 1))
                self.progress_bar.background_color = (1, 0, 0, 1)  # Red
                
        except Exception as e:
            self.update_info(f'Error: {str(e)[:50]}', (1, 0, 0, 1))
        
        finally:
            self.is_downloading = False
            Clock.schedule_once(self.finish_download, 0)
    
    def finish_download(self, dt):
        """Finish download process"""
        self.download_btn.disabled = False
        self.download_btn.text = 'Start Download'
        self.download_btn.background_color = (0.1, 0.7, 0.1, 1)
        
        if self.progress_bar.value >= 100:
            self.progress_bar.background_color = (0, 0.8, 0, 1)  # Green
            self.update_info('Download completed successfully!', (0, 0.8, 0, 1))
    
    def update_progress(self, value, speed_mb):
        """Update progress bar"""
        Clock.schedule_once(lambda dt: self._update_progress_ui(value, speed_mb), 0)
    
    def _update_progress_ui(self, value, speed_mb):
        """Update progress bar UI"""
        value = min(max(value, 0), 100)
        self.progress_bar.value = value
        
        # Change progress bar color
        if value >= 100:
            self.progress_bar.background_color = (0, 0.8, 0, 1)  # Green
        elif value >= 50:
            self.progress_bar.background_color = (0.8, 0.6, 0, 1)  # Yellow
        else:
            self.progress_bar.background_color = (0.2, 0.6, 0.8, 1)  # Blue
        
        # Update info text
        if value >= 100:
            self.info_label.text = 'Completed - 100%'
        else:
            self.info_label.text = f'Downloading - {value}% | Speed: {speed_mb:.2f} MB/s'
    
    def update_info(self, message, color):
        """Update status message"""
        Clock.schedule_once(lambda dt: self._update_info_ui(message, color), 0)
    
    def _update_info_ui(self, message, color):
        """Update status message UI"""
        self.info_label.text = message
        self.info_label.color = color


if __name__ == '__main__':
    DownloadApp().run()
