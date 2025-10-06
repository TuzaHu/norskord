import pygame
import random
import time
import os
from pydub import AudioSegment
from pydub.playback import play
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from translation_service import TranslationService
import json
from datetime import datetime, timedelta

class DuolingoStyleDictationGame:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        # Game settings
        self.audio_directory = "audio"
        self.merged_log_file = "merged_log.txt"
        self.game_duration = 20  # seconds per word (for practice mode)
        self.repeat_interval = 3  # seconds between audio repeats
        
        # Action mode settings
        self.action_mode_times = {
            'easy': 5,    # 5 seconds for easy words
            'medium': 10, # 10 seconds for medium words
            'hard': 15    # 15 seconds for hard words
        }
        self.current_time_bank = 0  # Time carryover system
        self.current_difficulty_level = 'easy'  # Progressive difficulty
        
        # Hearts system for hints
        self.max_hearts = 3
        self.current_hearts = 3
        
        # Translation service
        self.translation_service = TranslationService()
        
        # Game state
        self.current_word = ""
        self.current_audio_file = ""
        self.player_input = ""
        self.score = 0
        self.total_words = 0
        self.correct_words = 0
        self.game_running = False
        self.answer_submitted = False
        self.audio_thread = None
        self.timer_thread = None
        self.reveal_thread = None
        self.feedback_thread = None
        
        # Session management
        self.session_words = []
        self.correct_answers = []
        self.incorrect_answers = []
        self.words_per_session = 10
        self.attempted_words = set()
        self.review_words_file = "words_to_review.json"  # Changed to JSON for SRS
        self.stats_file = "game_stats.json"
        
        # Load words dynamically
        self.words_data = self.load_words_data()
        self.difficulty_levels = self.categorize_difficulty()
        
        # Initialize chapter system if available
        try:
            from chapter_based_system import ChapterBasedWordManager
            self.chapter_manager = ChapterBasedWordManager()
            print("✅ Chapter system initialized")
        except ImportError:
            print("⚠️ Chapter system not available, using legacy system")
            self.chapter_manager = None
        
        # Load game statistics
        self.game_stats = self.load_game_stats()
        
        # GUI setup
        self.root = tk.Tk()
        self.root.title("Norwegian Owl - Learn Norwegian with Dictation")
        self.root.geometry("500x900")
        self.root.configure(bg='white')
        self.root.resizable(True, True)
        self.setup_gui()
        
    def load_words_data(self):
        """Load words dynamically from merged_log.txt"""
        words_data = {}
        
        try:
            with open(self.merged_log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and line.endswith('.mp3'):
                        word = line[:-4]  # Remove .mp3 extension
                        words_data[word] = {
                            'audio_file': line,
                            'length': len(word),
                            'word_count': len(word.split()),
                            'translation': None
                        }
        except FileNotFoundError:
            print(f"Error: {self.merged_log_file} not found")
            return {}
            
        return words_data
    
    def load_game_stats(self):
        """Load game statistics from file"""
        default_stats = {
            "total_sessions": 0,
            "total_words_attempted": 0,
            "total_correct": 0,
            "accuracy_history": [],
            "session_history": [],
            "difficulty_stats": {
                "easy": {"attempted": 0, "correct": 0},
                "medium": {"attempted": 0, "correct": 0},
                "hard": {"attempted": 0, "correct": 0}
            },
            "current_streak": 0,  # New for streaks
            "longest_streak": 0,
            "last_session_date": None
        }
        try:
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    stats = json.load(f)
                    # Merge with defaults to handle missing keys
                    default_stats.update(stats)
                    return default_stats
        except Exception as e:
            print(f"Error loading game stats: {e}")
        return default_stats
    
    def save_game_stats(self):
        """Save game statistics to file"""
        try:
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.game_stats, f, indent=2)
        except Exception as e:
            print(f"Error saving game stats: {e}")
    
    def update_stats(self, difficulty, correct):
        """Update game statistics"""
        self.game_stats["total_words_attempted"] += 1
        if correct:
            self.game_stats["total_correct"] += 1
        
        # Update difficulty stats
        self.game_stats["difficulty_stats"][difficulty]["attempted"] += 1
        if correct:
            self.game_stats["difficulty_stats"][difficulty]["correct"] += 1
    
    def update_streak(self):
        """Update daily streak based on session completion"""
        today = datetime.now().date()
        last_date = self.game_stats.get("last_session_date")
        if last_date:
            last_date = datetime.fromisoformat(last_date).date()
            if today == last_date + timedelta(days=1):
                self.game_stats["current_streak"] += 1
            elif today > last_date + timedelta(days=1):
                self.game_stats["current_streak"] = 1
            # Else same day: no change
        else:
            self.game_stats["current_streak"] = 1
        
        self.game_stats["longest_streak"] = max(
            self.game_stats["longest_streak"], self.game_stats["current_streak"]
        )
        self.game_stats["last_session_date"] = today.isoformat()
        self.save_game_stats()
    
    def get_translation(self, norwegian_word):
        """Get English translation using translation service"""
        return self.translation_service.get_translation(norwegian_word)
    
    def categorize_difficulty(self):
        """Categorize words by difficulty based on length and complexity"""
        easy = []
        medium = []
        hard = []
        
        for word, data in self.words_data.items():
            length = data['length']
            word_count = data['word_count']
            
            if length <= 8 and word_count == 1:
                easy.append(word)
            elif length <= 15 and word_count <= 2:
                medium.append(word)
            else:
                hard.append(word)
        
        return {
            'easy': easy,
            'medium': medium,
            'hard': hard
        }
    
    def setup_gui(self):
        """Setup the game GUI with Duolingo-style design"""
        # Clear existing widgets without destroying root
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Duolingo color scheme
        self.colors = {
            'green': '#58cc02',
            'light_green': '#9ee32d',
            'dark_green': '#40a100',
            'blue': '#1cb0f6',
            'red': '#ff4b4b',
            'orange': '#ff9600',
            'purple': '#ce82ff',
            'white': '#ffffff',
            'light_gray': '#f0f0f0',
            'gray': '#e5e5e5',
            'dark_gray': '#9d9d9d',
            'black': '#000000'
        }
        
        # Configure styles
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure button styles
        style.configure('Duolingo.TButton', 
                       font=('Arial Rounded MT Bold', 14),
                       background=self.colors['green'],
                       foreground='white',
                       borderwidth=0,
                       focusthickness=3,
                       focuscolor=self.colors['light_green'],
                       padding=(20, 10))
        style.map('Duolingo.TButton', 
                 background=[('active', self.colors['dark_green'])])
        
        style.configure('Secondary.TButton', 
                       font=('Arial Rounded MT Bold', 12),
                       background=self.colors['light_gray'],
                       foreground=self.colors['dark_gray'],
                       borderwidth=0,
                       padding=(15, 8))
        style.map('Secondary.TButton', 
                 background=[('active', self.colors['gray'])])
        
        # Create main container
        self.main_container = tk.Frame(self.root, bg='white')
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header with logo, settings button, and streak
        header_frame = tk.Frame(self.main_container, bg='white')
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Top row with settings button and streak
        top_row = tk.Frame(header_frame, bg='white')
        top_row.pack(fill=tk.X, pady=(0, 10))
        
        # Streak display
        streak_label = tk.Label(top_row, text=f"🔥 Streak: {self.game_stats['current_streak']} dager", 
                               font=('Arial', 12), 
                               fg=self.colors['orange'], bg='white')
        streak_label.pack(side=tk.LEFT)
        
        # Settings button (top right)
        settings_button = tk.Button(top_row, text="⚙️", 
                                   font=('Arial', 16),
                                   bg='white', fg=self.colors['dark_gray'],
                                   relief='flat', bd=0,
                                   padx=10, pady=5,
                                   command=self.open_settings)
        settings_button.pack(side=tk.RIGHT)
        
        # Duolingo-style owl logo (simplified)
        logo_canvas = tk.Canvas(header_frame, width=60, height=60, bg='white', highlightthickness=0)
        logo_canvas.pack()
        # Draw simple owl
        logo_canvas.create_oval(10, 10, 50, 50, fill=self.colors['green'], outline='')
        logo_canvas.create_oval(20, 20, 30, 30, fill='white', outline='')
        logo_canvas.create_oval(40, 20, 50, 30, fill='white', outline='')
        logo_canvas.create_oval(25, 25, 35, 35, fill='black', outline='')
        logo_canvas.create_oval(45, 25, 55, 35, fill='black', outline='')
        logo_canvas.create_polygon(30, 40, 35, 50, 25, 50, fill='white', outline='')
        
        # App title
        title_label = tk.Label(header_frame, text="Norsk Ugle", 
                              font=('Arial Rounded MT Bold', 24), 
                              fg=self.colors['green'], bg='white')
        title_label.pack(pady=(10, 0))
        
        subtitle_label = tk.Label(header_frame, text="Diktat Øvelse", 
                                 font=('Arial', 14), 
                                 fg=self.colors['dark_gray'], bg='white')
        subtitle_label.pack()
        
        
        # Progress section (hearts and XP)
        progress_frame = tk.Frame(self.main_container, bg='white')
        progress_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Hearts (lives) - dynamic for action mode
        hearts_frame = tk.Frame(progress_frame, bg='white')
        hearts_frame.pack(side=tk.LEFT)
        
        tk.Label(hearts_frame, text="Hjerter:", 
                font=('Arial', 12), 
                fg=self.colors['dark_gray'], bg='white').pack(side=tk.LEFT)
        
        # Dynamic hearts display
        self.hearts_label = tk.Label(hearts_frame, text="❤️❤️❤️", 
                                    font=('Arial', 16), 
                                    fg=self.colors['red'], bg='white')
        self.hearts_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # XP score and circular progress bar
        xp_frame = tk.Frame(progress_frame, bg='white')
        xp_frame.pack(side=tk.RIGHT)
        
        # Circular progress bar for action mode
        self.progress_canvas = tk.Canvas(xp_frame, width=60, height=60, bg='white', highlightthickness=0)
        self.progress_canvas.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Initialize progress bar (empty)
        self.update_circular_progress(100)  # Start with full (100%)
        
        tk.Label(xp_frame, text="XP:", 
                font=('Arial', 12), 
                fg=self.colors['dark_gray'], bg='white').pack(side=tk.LEFT)
        
        xp_label = tk.Label(xp_frame, text="0", 
                           font=('Arial', 12, 'bold'), 
                           fg=self.colors['green'], bg='white')
        xp_label.pack(side=tk.LEFT)
        
        # Current settings indicator
        settings_info_frame = tk.Frame(self.main_container, bg='white')
        settings_info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.settings_info_label = tk.Label(settings_info_frame, 
                                           text="Nåværende: Øvelse • Lett • 10 ord • Oversettelse AV", 
                                           font=('Arial', 10), 
                                           fg=self.colors['dark_gray'], bg='white')
        self.settings_info_label.pack()
        
        # Lesson card (main content)
        lesson_card = tk.Frame(self.main_container, bg=self.colors['light_gray'], 
                              relief='flat', bd=0, highlightthickness=0)
        lesson_card.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Lesson content
        self.content_frame = tk.Frame(lesson_card, bg='white', 
                                relief='flat', bd=0, highlightthickness=0,
                                padx=20, pady=20)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Instruction
        instruction_label = tk.Label(self.content_frame, 
                                    text="Skriv det du hører på norsk",
                                    font=('Arial', 14), 
                                    fg=self.colors['dark_gray'], bg='white')
        instruction_label.pack(pady=(10, 20))
        
        # Sound button (play audio)
        self.sound_button = tk.Button(self.content_frame, text="🔊 Spill Lyd", 
                                font=('Arial', 16),
                                bg=self.colors['blue'], fg='white',
                                relief='flat', bd=0,
                                padx=20, pady=10,
                                command=self.play_current_audio)
        self.sound_button.pack(pady=(0, 30))
        
        # Input field
        input_frame = tk.Frame(self.content_frame, bg='white')
        input_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.input_var = tk.StringVar()
        self.input_entry = tk.Entry(input_frame, 
                                   textvariable=self.input_var,
                                   font=('Arial', 18),
                                   justify='center',
                                   relief='flat',
                                   bd=2,
                                   highlightcolor=self.colors['blue'],
                                   highlightthickness=2)
        self.input_entry.pack(fill=tk.X, pady=5)
        self.input_entry.config(state='disabled')
        
        # Check button
        self.check_button = ttk.Button(self.content_frame, text="Sjekk", 
                                      style='Duolingo.TButton',
                                      command=self.submit_answer)
        self.check_button.pack(pady=(0, 10))
        
        # Hint button (for action mode)
        self.hint_button = ttk.Button(self.content_frame, text="💡 Hint (1 ❤️)", 
                                     style='Duolingo.TButton',
                                     command=self.use_hint)
        self.hint_button.pack(pady=(0, 10))
        self.hint_button.pack_forget()  # Hide by default
        
        # Progress indicators
        progress_indicators = tk.Frame(self.content_frame, bg='white')
        progress_indicators.pack(fill=tk.X, pady=(10, 0))
        
        # Progress dots
        dots_frame = tk.Frame(progress_indicators, bg='white')
        dots_frame.pack()
        
        for i in range(5):
            dot = tk.Canvas(dots_frame, width=12, height=12, bg='white', highlightthickness=0)
            dot.pack(side=tk.LEFT, padx=5)
            if i == 0:
                dot.create_oval(2, 2, 10, 10, fill=self.colors['green'], outline='')
            else:
                dot.create_oval(2, 2, 10, 10, fill=self.colors['light_gray'], outline='')
        
        # Timer
        self.timer_label = tk.Label(progress_indicators, text="0s", 
                                   font=('Arial', 12), 
                                   fg=self.colors['dark_gray'], bg='white')
        self.timer_label.pack()
        
        # Result display
        self.result_text = tk.Text(self.content_frame, height=4, 
                                  font=('Arial', 12), 
                                  wrap=tk.WORD,
                                  bg='white', relief='flat')
        self.result_text.pack(fill=tk.X, pady=(20, 0))
        self.result_text.config(state='disabled')
        
        # Bottom navigation
        nav_frame = tk.Frame(self.main_container, bg='white')
        nav_frame.pack(fill=tk.X)
        
        # Practice buttons
        practice_frame = tk.Frame(nav_frame, bg='white')
        practice_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.start_button = ttk.Button(practice_frame, text="Start Leksjon", 
                  style='Duolingo.TButton', 
                  command=self.start_game)
        self.start_button.pack(fill=tk.X)
        
        # Bottom menu
        menu_frame = tk.Frame(nav_frame, bg='white')
        menu_frame.pack(fill=tk.X)
        
        menu_items = [
            ("🏠", "Hjem"),
            ("📊", "Fremgang"),
            ("👥", "Venner"),
            ("🏆", "Liga"),
            ("👤", "Profil")
        ]
        
        for icon, text in menu_items:
            btn_frame = tk.Frame(menu_frame, bg='white')
            btn_frame.pack(side=tk.LEFT, expand=True)
            
            icon_label = tk.Label(btn_frame, text=icon, 
                                 font=('Arial', 16), 
                                 fg=self.colors['dark_gray'], bg='white')
            icon_label.pack()
            
            text_label = tk.Label(btn_frame, text=text, 
                                 font=('Arial', 10), 
                                 fg=self.colors['dark_gray'], bg='white')
            text_label.pack()
        
        # Bind Enter key to submit answer
        self.input_entry.bind('<Return>', lambda event: self.submit_answer())
        
        # Set initial state
        self.update_display_state()
    
    def open_settings(self):
        """Open the settings window"""
        # Create settings window
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Spill Innstillinger")
        settings_window.geometry("600x800")
        settings_window.configure(bg='white')
        settings_window.resizable(True, True)
        
        # Make it modal
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Center the window
        settings_window.update_idletasks()
        x = (settings_window.winfo_screenwidth() // 2) - (600 // 2)
        y = (settings_window.winfo_screenheight() // 2) - (800 // 2)
        settings_window.geometry(f"600x800+{x}+{y}")
        
        # Create scrollable frame
        canvas = tk.Canvas(settings_window, bg='white', highlightthickness=0)
        scrollbar = tk.Scrollbar(settings_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True, padx=(30, 0), pady=20)
        scrollbar.pack(side="right", fill="y", pady=20)
        
        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Create main container with better spacing
        main_frame = scrollable_frame
        
        # Title
        title_label = tk.Label(main_frame, text="⚙️ Spill Innstillinger", 
                              font=('Arial', 18, 'bold'), 
                              fg=self.colors['green'], bg='white')
        title_label.pack(pady=(0, 20))
        
        # Chapter selection section (more compact)
        chapter_frame = tk.Frame(main_frame, bg='white')
        chapter_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(chapter_frame, text="Velg Kapittel:", 
                font=('Arial', 12, 'bold'), 
                fg=self.colors['dark_gray'], bg='white').pack(anchor='w', pady=(0, 5))
        
        # Chapter dropdown frame
        chapter_dropdown_frame = tk.Frame(chapter_frame, bg='white')
        chapter_dropdown_frame.pack(fill=tk.X)
        
        # Initialize chapter variable if not exists
        if not hasattr(self, 'chapter_var'):
            self.chapter_var = tk.StringVar(value="Kapital En")
        
        # Create styled chapter dropdown with custom colors
        style = ttk.Style()
        style.configure("Chapter.TCombobox", 
                       fieldbackground='white',
                       background='white',
                       foreground='black',
                       font=('Arial', 11))
        
        self.chapter_dropdown = ttk.Combobox(
            chapter_dropdown_frame,
            textvariable=self.chapter_var,
            style="Chapter.TCombobox",
            state='readonly',
            width=35
        )
        self.chapter_dropdown.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Refresh chapters button (smaller)
        refresh_chapters_button = tk.Button(
            chapter_dropdown_frame,
            text="🔄",
            font=('Arial', 9),
            bg=self.colors['blue'],
            fg='white',
            relief='flat',
            bd=0,
            width=2,
            height=1,
            command=lambda: self.refresh_chapter_dropdown(settings_window)
        )
        refresh_chapters_button.pack(side=tk.LEFT, padx=(8, 0))
        
        # Chapter info label (more compact)
        self.chapter_info_label = tk.Label(
            chapter_frame,
            text="",
            font=('Arial', 9),
            fg=self.colors['dark_gray'],
            bg='white',
            wraplength=450,
            justify='left'
        )
        self.chapter_info_label.pack(anchor='w', pady=(3, 0))
        
        # Initialize chapter dropdown
        self.refresh_chapter_dropdown(settings_window)
        
        # Difficulty section
        difficulty_frame = tk.Frame(main_frame, bg='white')
        difficulty_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(difficulty_frame, text="Velg Vanskelighetsgrad:", 
                font=('Arial', 14, 'bold'), 
                fg=self.colors['dark_gray'], bg='white').pack(anchor='w', pady=(0, 10))
        
        # Initialize difficulty variable if not exists
        if not hasattr(self, 'difficulty_var'):
            self.difficulty_var = tk.StringVar(value="easy")
        
        # Debug: Print current difficulty
        print(f"Current difficulty setting: {self.difficulty_var.get()}")
        
        difficulty_buttons_frame = tk.Frame(difficulty_frame, bg='white')
        difficulty_buttons_frame.pack(fill=tk.X)
        
        # Create individual radio buttons with better visual feedback
        def on_difficulty_change():
            print(f"Difficulty changed to: {self.difficulty_var.get()}")
            # Update visual styling for all buttons
            update_button_styles()
        
        def update_button_styles():
            current = self.difficulty_var.get()
            
            # Reset all buttons to default style
            for btn in [easy_radio, medium_radio, hard_radio]:
                btn.config(bg='white', fg=self.colors['dark_gray'], relief='flat')
            
            # Highlight the selected button
            if current == "easy":
                easy_radio.config(bg=self.colors['light_green'], fg='white', relief='raised')
            elif current == "medium":
                medium_radio.config(bg=self.colors['orange'], fg='white', relief='raised')
            elif current == "hard":
                hard_radio.config(bg=self.colors['red'], fg='white', relief='raised')
        
        easy_radio = tk.Radiobutton(
            difficulty_buttons_frame,
            text="Lett",
            variable=self.difficulty_var,
            value="easy",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg=self.colors['dark_gray'],
            selectcolor=self.colors['green'],
            activebackground=self.colors['light_green'],
            activeforeground='white',
            padx=20,
            pady=8,
            relief='flat',
            bd=2,
            command=on_difficulty_change
        )
        easy_radio.pack(side=tk.LEFT, padx=10)
        
        medium_radio = tk.Radiobutton(
            difficulty_buttons_frame,
            text="Middels",
            variable=self.difficulty_var,
            value="medium",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg=self.colors['dark_gray'],
            selectcolor=self.colors['orange'],
            activebackground=self.colors['orange'],
            activeforeground='white',
            padx=20,
            pady=8,
            relief='flat',
            bd=2,
            command=on_difficulty_change
        )
        medium_radio.pack(side=tk.LEFT, padx=10)
        
        hard_radio = tk.Radiobutton(
            difficulty_buttons_frame,
            text="Vanskelig",
            variable=self.difficulty_var,
            value="hard",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg=self.colors['dark_gray'],
            selectcolor=self.colors['red'],
            activebackground=self.colors['red'],
            activeforeground='white',
            padx=20,
            pady=8,
            relief='flat',
            bd=2,
            command=on_difficulty_change
        )
        hard_radio.pack(side=tk.LEFT, padx=10)
        
        # Set initial styling
        settings_window.after(100, update_button_styles)
        
        # Words per session section
        words_frame = tk.Frame(main_frame, bg='white')
        words_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(words_frame, text="Ord per Økt:", 
                font=('Arial', 14, 'bold'), 
                fg=self.colors['dark_gray'], bg='white').pack(anchor='w', pady=(0, 10))
        
        # Initialize words per session variable if not exists
        if not hasattr(self, 'words_per_session_var'):
            self.words_per_session_var = tk.StringVar(value="10")
        
        words_spinbox = tk.Spinbox(
            words_frame,
            from_=5,
            to=50,
            textvariable=self.words_per_session_var,
            font=('Arial', 16),
            width=12,
            bg='white',
            fg=self.colors['dark_gray'],
            buttonbackground=self.colors['light_gray'],
            highlightcolor=self.colors['blue'],
            relief='solid',
            bd=2
        )
        words_spinbox.pack(anchor='w')
        
        
        # Show translation option
        translation_frame = tk.Frame(main_frame, bg='white')
        translation_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(translation_frame, text="Læringsvalg:", 
                font=('Arial', 14, 'bold'), 
                fg=self.colors['dark_gray'], bg='white').pack(anchor='w', pady=(0, 10))
        
        # Initialize show translation variable if not exists
        if not hasattr(self, 'show_translation_var'):
            self.show_translation_var = tk.BooleanVar(value=False)
        
        # Initialize game mode variable if not exists
        if not hasattr(self, 'game_mode_var'):
            self.game_mode_var = tk.StringVar(value="practice")
        
        # Create a custom styled checkbox with better visual feedback
        checkbox_frame = tk.Frame(translation_frame, bg='white')
        checkbox_frame.pack(anchor='w', pady=(0, 5))
        
        translation_checkbox = tk.Checkbutton(
            checkbox_frame,
            text="Vis ordbetydning (engelsk) før lytte",
            variable=self.show_translation_var,
            font=('Arial', 12, 'bold'),
            bg='white',
            fg=self.colors['dark_gray'],
            selectcolor=self.colors['green'],
            activebackground=self.colors['light_green'],
            activeforeground='white',
            relief='flat',
            bd=2,
            padx=8,
            pady=5,
            command=self.on_translation_toggle
        )
        translation_checkbox.pack(side=tk.LEFT)
        
        # Add a visual indicator next to the checkbox
        self.translation_indicator = tk.Label(
            checkbox_frame,
            text="❌",
            font=('Arial', 16),
            bg='white',
            fg=self.colors['red']
        )
        self.translation_indicator.pack(side=tk.LEFT, padx=(10, 0))
        
        # Update indicator based on current state (with small delay for better visual feedback)
        settings_window.after(50, self.update_translation_indicator)
        
        # Help text for the option
        help_label = tk.Label(translation_frame, 
                             text="(Når aktivert, viser engelsk betydning så du vet hva du skal lytte etter)",
                             font=('Arial', 12), 
                             fg=self.colors['dark_gray'], bg='white')
        help_label.pack(anchor='w', pady=(10, 0))
        
        # Game mode section
        mode_frame = tk.Frame(main_frame, bg='white')
        mode_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(mode_frame, text="Spillmodus:", 
                font=('Arial', 14, 'bold'), 
                fg=self.colors['dark_gray'], bg='white').pack(anchor='w', pady=(0, 10))
        
        # Game mode radio buttons
        mode_buttons_frame = tk.Frame(mode_frame, bg='white')
        mode_buttons_frame.pack(fill=tk.X)
        
        def on_mode_change():
            print(f"Game mode changed to: {self.game_mode_var.get()}")
            update_mode_styles()
        
        def update_mode_styles():
            current = self.game_mode_var.get()
            
            # Reset all buttons to default style
            for btn in [practice_radio, action_radio]:
                btn.config(bg='white', fg=self.colors['dark_gray'], relief='flat')
            
            # Highlight the selected button
            if current == "practice":
                practice_radio.config(bg=self.colors['light_green'], fg='white', relief='raised')
            elif current == "action":
                action_radio.config(bg=self.colors['red'], fg='white', relief='raised')
        
        practice_radio = tk.Radiobutton(
            mode_buttons_frame,
            text="Øvelse (Normal)",
            variable=self.game_mode_var,
            value="practice",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg=self.colors['dark_gray'],
            selectcolor=self.colors['green'],
            activebackground=self.colors['light_green'],
            activeforeground='white',
            padx=20,
            pady=8,
            relief='flat',
            bd=2,
            command=on_mode_change
        )
        practice_radio.pack(side=tk.LEFT, padx=10)
        
        action_radio = tk.Radiobutton(
            mode_buttons_frame,
            text="Aksjon (Intensivt)",
            variable=self.game_mode_var,
            value="action",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg=self.colors['dark_gray'],
            selectcolor=self.colors['red'],
            activebackground=self.colors['red'],
            activeforeground='white',
            padx=20,
            pady=8,
            relief='flat',
            bd=2,
            command=on_mode_change
        )
        action_radio.pack(side=tk.LEFT, padx=10)
        
        # Set initial styling
        settings_window.after(100, update_mode_styles)
        
        # Action mode description
        action_desc = tk.Label(mode_frame, 
                              text="Aksjon-modus: Start med lette ord, gå til middels, deretter vanskelig.\nTid overføres mellom ord. Spillet slutter når tiden er ute!",
                              font=('Arial', 12), 
                              fg=self.colors['dark_gray'], bg='white',
                              justify='left')
        action_desc.pack(anchor='w', pady=(10, 0))
        
        # Word counts section
        counts_frame = tk.Frame(main_frame, bg='white')
        counts_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(counts_frame, text="Tilgjengelige Ord:", 
                font=('Arial', 14, 'bold'), 
                fg=self.colors['dark_gray'], bg='white').pack(anchor='w', pady=(0, 8))
        
        word_counts_text = f"• Lett: {len(self.difficulty_levels.get('easy', []))} ord\n• Middels: {len(self.difficulty_levels.get('medium', []))} ord\n• Vanskelig: {len(self.difficulty_levels.get('hard', []))} ord"
        word_counts_label = tk.Label(counts_frame, text=word_counts_text,
                                   font=('Arial', 12), 
                                   fg=self.colors['dark_gray'], bg='white',
                                   justify='left')
        word_counts_label.pack(anchor='w')
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(fill=tk.X, pady=(20, 15))
        
        # Save button
        save_button = tk.Button(button_frame, text="💾 Lagre", 
                               font=('Arial', 12, 'bold'),
                               bg=self.colors['green'], fg='white',
                               relief='flat', bd=0,
                               padx=20, pady=8,
                               command=lambda: self.save_settings(settings_window))
        save_button.pack(side=tk.LEFT, padx=(0, 15))
        
        # Cancel button
        cancel_button = tk.Button(button_frame, text="❌ Avbryt", 
                                 font=('Arial', 12, 'bold'),
                                 bg=self.colors['light_gray'], fg=self.colors['dark_gray'],
                                 relief='flat', bd=0,
                                 padx=20, pady=8,
                                 command=settings_window.destroy)
        cancel_button.pack(side=tk.LEFT)
    
    def save_settings(self, settings_window):
        """Save settings and close window"""
        # Settings are automatically saved to the variables
        settings_window.destroy()
        
        # Update settings indicator
        mode_map = {"practice": "Øvelse", "action": "Aksjon"}
        mode = mode_map.get(self.game_mode_var.get(), "Øvelse")
        difficulty_map = {"easy": "Lett", "medium": "Middels", "hard": "Vanskelig"}
        difficulty = difficulty_map.get(self.difficulty_var.get(), "Lett")
        words = self.words_per_session_var.get()
        translation = "Oversettelse PÅ" if self.show_translation_var.get() else "Oversettelse AV"
        if hasattr(self, 'settings_info_label') and self.settings_info_label.winfo_exists():
            self.settings_info_label.config(text=f"Nåværende: {mode} • {difficulty} • {words} ord • {translation}")
        
        # Show confirmation
        messagebox.showinfo("Innstillinger Lagret", "Dine innstillinger er lagret!")
    
    def on_translation_toggle(self):
        """Called when translation checkbox is toggled"""
        self.update_translation_indicator()
        print(f"Translation setting changed to: {self.show_translation_var.get()}")
    
    def update_translation_indicator(self):
        """Update the visual indicator for translation setting"""
        if hasattr(self, 'translation_indicator'):
            if self.show_translation_var.get():
                self.translation_indicator.config(text="✅", fg=self.colors['green'])
            else:
                self.translation_indicator.config(text="❌", fg=self.colors['red'])
    
    def refresh_chapter_dropdown(self, settings_window):
        """Refresh the chapter dropdown with available chapters"""
        try:
            # Try to get chapters from chapter-based system
            if hasattr(self, 'chapter_manager') and self.chapter_manager:
                chapters = self.chapter_manager.get_available_chapters()
            else:
                # Fallback to basic chapters
                chapters = [
                    {
                        "name": "Kapital En",
                        "folder": "capital_one", 
                        "unlocked": True,
                        "words_count": len(self.words_data),
                        "description": "Grunnleggende norske ord"
                    }
                ]
            
            # Prepare dropdown values with visual clues
            dropdown_values = []
            self.chapter_mapping = {}
            
            for chapter in chapters:
                if chapter['unlocked']:
                    # Unlocked chapter - green checkmark and green text
                    visual_text = f"✅ {chapter['name']} ({chapter.get('words_count', 0)} ord)"
                else:
                    # Locked chapter - lock icon and grey text
                    required_score = chapter.get('required_score', 70)
                    visual_text = f"🔒 {chapter['name']} (Trenger {required_score}%)"
                
                dropdown_values.append(visual_text)
                self.chapter_mapping[visual_text] = chapter
            
            # Set dropdown values
            self.chapter_dropdown['values'] = dropdown_values
            
            # Select first unlocked chapter by default
            unlocked_chapters = [v for v in dropdown_values if v.startswith("✅")]
            if unlocked_chapters:
                self.chapter_dropdown.set(unlocked_chapters[0])
                self.on_chapter_dropdown_selected()
            
            # Bind selection event
            self.chapter_dropdown.bind('<<ComboboxSelected>>', self.on_chapter_dropdown_selected)
            
        except Exception as e:
            print(f"Error refreshing chapter dropdown: {e}")
            # Fallback to basic chapter
            self.chapter_dropdown['values'] = ["✅ Kapital En (83 ord)"]
            self.chapter_dropdown.set("✅ Kapital En (83 ord)")
    
    def on_chapter_dropdown_selected(self, event=None):
        """Handle chapter dropdown selection"""
        selected_text = self.chapter_var.get()
        
        if not selected_text:
            return
        
        # Get selected chapter
        selected_chapter = self.chapter_mapping.get(selected_text)
        if not selected_chapter:
            return
        
        # Update chapter info display with better colors
        if hasattr(self, 'chapter_info_label'):
            if selected_chapter['unlocked']:
                info_text = f"📝 {selected_chapter.get('description', 'Norsk ord og fraser')} • {selected_chapter.get('words_count', 0)} ord tilgjengelig"
                info_color = self.colors['green']  # Green for active chapters
            else:
                required_score = selected_chapter.get('required_score', 70)
                info_text = f"🔒 Låst • Trenger {required_score}% score i forrige kapittel for å låse opp"
                info_color = '#888888'  # Grey for locked chapters
            
            self.chapter_info_label.config(text=info_text, fg=info_color)
        
        # Update current chapter setting
        self.current_chapter = selected_chapter['name']
        self.current_chapter_folder = selected_chapter['folder']
        
        print(f"Selected chapter: {selected_chapter['name']} (unlocked: {selected_chapter['unlocked']})")
    
    def unlock_next_chapter(self, score):
        """Unlock next chapter if score is sufficient"""
        if hasattr(self, 'chapter_manager') and self.chapter_manager:
            try:
                # Get current chapter
                current_chapter = getattr(self, 'current_chapter_folder', 'capital_one')
                
                # Unlock next chapter
                self.chapter_manager.unlock_next_chapter(current_chapter, score)
                
                # Check if any new chapters were unlocked
                available_chapters = self.chapter_manager.get_available_chapters()
                newly_unlocked = [c for c in available_chapters if c['unlocked'] and c['folder'] != current_chapter]
                
                if newly_unlocked and score >= 70:
                    # Show unlock notification
                    unlocked_chapter = newly_unlocked[0]
                    messagebox.showinfo(
                        "🎉 Nytt Kapittel Låst Opp!",
                        f"Gratulerer! Du har låst opp:\n\n"
                        f"📚 {unlocked_chapter['name']}\n"
                        f"📝 {unlocked_chapter.get('words_count', 0)} nye ord\n\n"
                        f"Du kan nå velge dette kapittelet i innstillinger!"
                    )
                    
            except Exception as e:
                print(f"Error unlocking next chapter: {e}")
    
    def update_circular_progress(self, percentage):
        """Update the circular progress bar based on time remaining percentage"""
        if not hasattr(self, 'progress_canvas') or not self.progress_canvas.winfo_exists():
            return
        
        # Clear the canvas
        self.progress_canvas.delete("all")
        
        # Canvas dimensions
        canvas_width = 60
        canvas_height = 60
        center_x = canvas_width // 2
        center_y = canvas_height // 2
        radius = 22
        
        # Determine color based on percentage
        if percentage > 50:
            color = self.colors['green']
        elif percentage > 25:
            color = self.colors['orange']
        else:
            color = self.colors['red']
        
        # Draw background circle (empty)
        self.progress_canvas.create_oval(
            center_x - radius, center_y - radius,
            center_x + radius, center_y + radius,
            outline=self.colors['light_gray'], width=3, fill='white'
        )
        
        # Draw progress arc (filled portion)
        if percentage > 0:
            # Calculate the extent of the arc (0 to 360 degrees)
            extent = (percentage / 100) * 360
            
            # Draw the progress arc
            self.progress_canvas.create_arc(
                center_x - radius, center_y - radius,
                center_x + radius, center_y + radius,
                start=90, extent=-extent,  # Start from top, go counter-clockwise
                outline=color, width=3, style='arc'
            )
        
        # Add percentage text in the center
        self.progress_canvas.create_text(
            center_x, center_y,
            text=f"{int(percentage)}%",
            font=('Arial', 10, 'bold'),
            fill=color
        )
    
    def update_hearts_display(self):
        """Update the hearts display based on current hearts"""
        if not hasattr(self, 'hearts_label') or not self.hearts_label.winfo_exists():
            return
        
        # Create hearts string based on current hearts
        hearts_text = "❤️" * self.current_hearts + "🤍" * (self.max_hearts - self.current_hearts)
        self.hearts_label.config(text=hearts_text)
        
        # Update hint button state
        if hasattr(self, 'hint_button') and self.hint_button.winfo_exists():
            if self.current_hearts > 0:
                self.hint_button.config(text=f"💡 Hint (1 ❤️)", state='normal')
            else:
                self.hint_button.config(text="💡 Hint (Ingen ❤️)", state='disabled')
    
    def use_hint(self):
        """Use a hint to reveal the answer (costs 1 heart)"""
        if self.current_hearts <= 0 or not self.game_running or self.answer_submitted:
            return
        
        # Check if we're in action mode
        game_mode = getattr(self, 'game_mode_var', tk.StringVar(value="practice")).get()
        if game_mode != "action":
            return
        
        # Use one heart
        self.current_hearts -= 1
        self.update_hearts_display()
        
        # Reveal the answer
        if hasattr(self, 'input_var'):
            self.input_var.set(self.current_word)
        
        # Show feedback
        if hasattr(self, 'result_text') and self.result_text.winfo_exists():
            self.result_text.config(state='normal')
            self.result_text.delete(1.0, tk.END)
            
            translation = self.get_translation(self.current_word)
            hint_message = f"💡 Hint brukt! (-1 ❤️)\n\n🎯 Riktig svar: '{self.current_word}'\n📖 Betydning: '{translation}'\n\n⏰ Du har fortsatt tid til å sende inn svaret!"
            
            self.result_text.insert(tk.END, hint_message)
            self.result_text.tag_add("hint", "1.0", "end")
            self.result_text.tag_config("hint", foreground=self.colors['orange'])
            self.result_text.config(state='disabled')
        
        # Play hint sound (optional)
        self.play_feedback_sound(True)
    
    def update_display_state(self):
        """Update the UI based on game state"""
        # Only update if UI elements exist
        if hasattr(self, 'input_entry') and self.input_entry.winfo_exists():
            if self.game_running:
                self.input_entry.config(state='normal')
                if hasattr(self, 'check_button') and self.check_button.winfo_exists():
                    self.check_button.config(text="Sjekk", command=self.submit_answer)
                if hasattr(self, 'start_button') and self.start_button.winfo_exists():
                    self.start_button.config(text="Start Leksjon", command=self.start_game)
            else:
                self.input_entry.config(state='disabled')
                if hasattr(self, 'check_button') and self.check_button.winfo_exists():
                    self.check_button.config(text="Start Leksjon", command=self.start_game)
                if hasattr(self, 'start_button') and self.start_button.winfo_exists():
                    self.start_button.config(text="Start Leksjon", command=self.start_game)
    
    def start_game(self):
        """Start the dictation game"""
        # Get session settings
        try:
            words_per_session_var = getattr(self, 'words_per_session_var', tk.StringVar(value="10"))
            self.words_per_session = int(words_per_session_var.get())
        except:
            self.words_per_session = 10
        
        # Get game mode
        game_mode = getattr(self, 'game_mode_var', tk.StringVar(value="practice")).get()
        
        if game_mode == "action":
            # Action mode: progressive difficulty with time carryover
            self.setup_action_mode()
        else:
            # Practice mode: normal behavior
            self.setup_practice_mode()
    
    def setup_practice_mode(self):
        """Setup practice mode (original behavior)"""
        # Hide hint button for practice mode
        if hasattr(self, 'hint_button') and self.hint_button.winfo_exists():
            self.hint_button.pack_forget()
        
        # Prepare session words
        difficulty = getattr(self, 'difficulty_var', tk.StringVar(value="easy")).get()
        available_words = self.difficulty_levels.get(difficulty, [])
        
        if not available_words:
            error_msg = f"No words available for '{difficulty}' difficulty!\n\nAvailable difficulties:\n"
            for diff, words in self.difficulty_levels.items():
                error_msg += f"- {diff}: {len(words)} words\n"
            messagebox.showerror("No Words", error_msg)
            return
        
        # Load review words and prioritize them
        review_words = self.load_review_words()
        review_words_in_difficulty = [word for word in review_words if word in available_words]
        
        # Select words for session, prioritizing review words
        if len(review_words_in_difficulty) >= self.words_per_session:
            # Use only review words
            self.session_words = random.sample(review_words_in_difficulty, self.words_per_session)
        elif len(review_words_in_difficulty) > 0:
            # Mix review words with new words
            remaining_slots = self.words_per_session - len(review_words_in_difficulty)
            other_words = [word for word in available_words if word not in review_words]
            
            if len(other_words) >= remaining_slots:
                additional_words = random.sample(other_words, remaining_slots)
                self.session_words = review_words_in_difficulty + additional_words
                random.shuffle(self.session_words)  # Mix the order
            else:
                self.session_words = review_words_in_difficulty + other_words
                random.shuffle(self.session_words)
        else:
            # No review words, use regular selection
            if len(available_words) < self.words_per_session:
                self.session_words = available_words.copy()
            else:
                self.session_words = random.sample(available_words, self.words_per_session)
        
        # Reset game state
        self.game_running = True
        self.answer_submitted = False
        self.score = 0
        self.total_words = 0
        self.correct_words = 0
        self.correct_answers = []
        self.incorrect_answers = []
        self.attempted_words = set()
        
        # Update game stats
        self.game_stats["total_sessions"] += 1
        
        # Update UI
        self.update_display_state()
        if hasattr(self, 'input_var'):
            self.input_var.set("")
        if hasattr(self, 'result_text') and self.result_text.winfo_exists():
            self.result_text.config(state='normal')
            self.result_text.delete(1.0, tk.END)
            self.result_text.config(state='disabled')
        
        self.next_word()
    
    def setup_action_mode(self):
        """Setup action mode with progressive difficulty and time carryover"""
        # Reset action mode state
        self.current_time_bank = 0
        self.current_difficulty_level = 'easy'
        
        # Reset hearts for action mode
        self.current_hearts = self.max_hearts
        self.update_hearts_display()
        
        # Show hint button for action mode
        if hasattr(self, 'hint_button') and self.hint_button.winfo_exists():
            self.hint_button.pack(pady=(0, 10))
        
        # Initialize progress bar to show full time for first word
        self.update_circular_progress(100)
        
        # Get all words from all difficulties
        all_easy_words = self.difficulty_levels.get('easy', [])
        all_medium_words = self.difficulty_levels.get('medium', [])
        all_hard_words = self.difficulty_levels.get('hard', [])
        
        if not all_easy_words and not all_medium_words and not all_hard_words:
            messagebox.showerror("No Words", "No words available in any difficulty level!")
            return
        
        # Create progressive word list: easy -> medium -> hard
        self.session_words = []
        self.session_words.extend(all_easy_words)
        self.session_words.extend(all_medium_words)
        self.session_words.extend(all_hard_words)
        
        # Shuffle within each difficulty group to maintain progression
        easy_count = len(all_easy_words)
        medium_count = len(all_medium_words)
        
        if easy_count > 0:
            self.session_words[:easy_count] = random.sample(all_easy_words, easy_count)
        if medium_count > 0:
            self.session_words[easy_count:easy_count + medium_count] = random.sample(all_medium_words, medium_count)
        if len(all_hard_words) > 0:
            self.session_words[easy_count + medium_count:] = random.sample(all_hard_words, len(all_hard_words))
        
        # Reset game state
        self.game_running = True
        self.answer_submitted = False
        self.score = 0
        self.total_words = 0
        self.correct_words = 0
        self.correct_answers = []
        self.incorrect_answers = []
        self.attempted_words = set()
        
        # Update game stats
        self.game_stats["total_sessions"] += 1
        
        # Update UI
        self.update_display_state()
        if hasattr(self, 'input_var'):
            self.input_var.set("")
        if hasattr(self, 'result_text') and self.result_text.winfo_exists():
            self.result_text.config(state='normal')
            self.result_text.delete(1.0, tk.END)
            self.result_text.config(state='disabled')
        
        self.next_word()
    
    def stop_game(self):
        """Stop the game"""
        self.game_running = False
        self.answer_submitted = True
        
        if self.audio_thread and self.audio_thread.is_alive():
            self.audio_thread.join(timeout=1)
        
        if self.timer_thread and self.timer_thread.is_alive():
            self.timer_thread.join(timeout=1)
        
        if self.reveal_thread and self.reveal_thread.is_alive():
            self.reveal_thread.join(timeout=1)
        
        if self.feedback_thread and self.feedback_thread.is_alive():
            self.feedback_thread.join(timeout=1)
        
        self.update_display_state()
    
    def next_word(self):
        """Load the next word for dictation"""
        if not self.game_running:
            return
        
        # Check if session is complete
        if self.total_words >= len(self.session_words):
            self.end_session()
            return
        
        # Reset answer submission flag
        self.answer_submitted = False
        
        # Get next word from session
        self.current_word = self.session_words[self.total_words]
        self.current_audio_file = self.words_data[self.current_word]['audio_file']
        
        # Update difficulty level for action mode
        game_mode = getattr(self, 'game_mode_var', tk.StringVar(value="practice")).get()
        if game_mode == "action":
            self.update_difficulty_level()
            # Update progress bar to show time bank percentage
            if self.current_time_bank > 0:
                base_time = self.action_mode_times[self.current_difficulty_level]
                total_time = self.current_time_bank + base_time
                percentage = (self.current_time_bank / total_time) * 100
                self.update_circular_progress(percentage)
            else:
                self.update_circular_progress(100)  # Full time for new word
        
        # Setup dictation mode
        self.setup_dictation_mode()
    
    def update_difficulty_level(self):
        """Update the current difficulty level based on word position in action mode"""
        # Count words in each difficulty
        easy_count = len(self.difficulty_levels.get('easy', []))
        medium_count = len(self.difficulty_levels.get('medium', []))
        
        if self.total_words < easy_count:
            self.current_difficulty_level = 'easy'
        elif self.total_words < easy_count + medium_count:
            self.current_difficulty_level = 'medium'
        else:
            self.current_difficulty_level = 'hard'
    
    def setup_dictation_mode(self):
        """Setup dictation mode gameplay"""
        # Stop any existing audio first
        self.stop_audio()
        
        # Only try to access input_entry if it exists
        if hasattr(self, 'input_entry') and self.input_entry.winfo_exists():
            self.input_var.set("")
            self.input_entry.focus()
        
        # Show the word and its translation immediately
        self.show_word_translation()
        
        # Start audio playback
        self.play_audio()
        
        # Start timer
        self.start_timer()
    
    
    def show_word_translation(self):
        """Show the current word and optionally its English translation"""
        if not self.current_word:
            return
        
        # Only update if result_text exists
        if not (hasattr(self, 'result_text') and self.result_text.winfo_exists()):
            return
        
        # Check if translation should be shown
        show_translation = getattr(self, 'show_translation_var', tk.BooleanVar(value=False)).get()
        game_mode = getattr(self, 'game_mode_var', tk.StringVar(value="practice")).get()
        
        # Display word and translation
        self.result_text.config(state='normal')
        self.result_text.delete(1.0, tk.END)
        
        if game_mode == "action":
            # Action mode: show difficulty level and time bank
            difficulty_map = {"easy": "Lett", "medium": "Middels", "hard": "Vanskelig"}
            difficulty_text = difficulty_map.get(self.current_difficulty_level, "Lett")
            time_bank_text = f"⏰ Tid igjen: {self.current_time_bank}s"
            
            if show_translation:
                translation = self.get_translation(self.current_word)
                display_text = f"🎯 Vanskelighetsgrad: {difficulty_text}\n{time_bank_text}\n\n📖 Betydning: '{translation}'\n\n🎧 Lyt og skriv det norske ordet!"
            else:
                display_text = f"🎯 Vanskelighetsgrad: {difficulty_text}\n{time_bank_text}\n\n🎧 Lyt til lyden og skriv det du hører!"
        else:
            # Practice mode: normal behavior
            if show_translation:
                # Get translation - show only the English meaning, not the Norwegian word
                translation = self.get_translation(self.current_word)
                # Show only the English translation (the meaning you're listening for)
                display_text = f"📖 Betydning: '{translation}'\n\n🎧 Lyt og skriv det norske ordet for denne betydningen!"
            else:
                # Show only instruction
                display_text = f"🎧 Lyt til lyden og skriv det du hører!\n\n💡 Tips: Du kan aktivere betydningsvisning i innstillinger for å se hva ordet betyr."
        
        self.result_text.insert(tk.END, display_text)
        self.result_text.tag_add("word_info", "1.0", "end")
        self.result_text.tag_config("word_info", foreground=self.colors['blue'])
        self.result_text.config(state='disabled')
    
    def stop_audio(self):
        """Stop any currently playing audio"""
        self.answer_submitted = True  # This will stop the audio loop
        if hasattr(self, 'audio_thread') and self.audio_thread and self.audio_thread.is_alive():
            self.audio_thread.join(timeout=0.5)  # Wait for audio thread to finish
        self.answer_submitted = False  # Reset for new word
    
    def play_audio(self):
        """Play the audio file in a separate thread"""
        def audio_worker():
            audio_path = os.path.join(self.audio_directory, self.current_audio_file)
            if os.path.exists(audio_path):
                try:
                    # Load and play audio
                    audio = AudioSegment.from_mp3(audio_path)
                    
                    # Keep playing until time runs out or answer is submitted
                    while self.game_running and not self.answer_submitted:
                        play(audio)
                        
                        # Wait before next repeat, but check if we should stop
                        if self.game_running and not self.answer_submitted:
                            time.sleep(self.repeat_interval)
                        else:
                            break
                            
                except Exception as e:
                    print(f"Error playing audio: {e}")
        
        self.audio_thread = threading.Thread(target=audio_worker)
        self.audio_thread.daemon = True
        self.audio_thread.start()
    
    def play_current_audio(self):
        """Play the current audio file once (manual play button)"""
        if not self.current_audio_file:
            return
            
        def audio_worker():
            audio_path = os.path.join(self.audio_directory, self.current_audio_file)
            if os.path.exists(audio_path):
                try:
                    audio = AudioSegment.from_mp3(audio_path)
                    play(audio)
                except Exception as e:
                    print(f"Error playing audio: {e}")
        
        # Play in a separate thread to avoid blocking UI
        audio_thread = threading.Thread(target=audio_worker)
        audio_thread.daemon = True
        audio_thread.start()
    
    def play_feedback_sound(self, correct):
        """Play audio feedback for correct or incorrect answer"""
        def worker():
            sound_file = "correct.mp3" if correct else "incorrect.mp3"
            sound_path = os.path.join(self.audio_directory, sound_file)
            if os.path.exists(sound_path):
                try:
                    audio = AudioSegment.from_mp3(sound_path)
                    play(audio)
                except Exception as e:
                    print(f"Error playing feedback sound: {e}")
        
        self.feedback_thread = threading.Thread(target=worker)
        self.feedback_thread.daemon = True
        self.feedback_thread.start()
    
    def start_timer(self):
        """Start the countdown timer"""
        def timer_worker():
            # Get time based on game mode
            game_mode = getattr(self, 'game_mode_var', tk.StringVar(value="practice")).get()
            
            if game_mode == "action":
                # Action mode: use time bank + difficulty time
                base_time = self.action_mode_times[self.current_difficulty_level]
                total_time = self.current_time_bank + base_time
                remaining_time = total_time
            else:
                # Practice mode: use fixed duration
                total_time = self.game_duration
                remaining_time = total_time
            
            while remaining_time > 0 and self.game_running and not self.answer_submitted:
                # Only update timer if the label exists
                if hasattr(self, 'timer_label') and self.timer_label.winfo_exists():
                    self.root.after(0, lambda t=remaining_time: self.timer_label.config(text=f"{t}s"))
                
                # Update circular progress bar for action mode
                if game_mode == "action":
                    percentage = (remaining_time / total_time) * 100
                    self.root.after(0, lambda p=percentage: self.update_circular_progress(p))
                
                time.sleep(1)
                remaining_time -= 1
            
            if self.game_running and not self.answer_submitted:
                # Time's up - handle based on game mode
                if game_mode == "action":
                    self.root.after(0, lambda: self.update_circular_progress(0))  # Show 0% when time's up
                    self.root.after(0, self.handle_action_timeout)
                else:
                    self.root.after(0, self.handle_timeout)
        
        # Stop any existing timer thread
        if self.timer_thread and self.timer_thread.is_alive():
            self.timer_thread.join(timeout=0.1)
        
        self.timer_thread = threading.Thread(target=timer_worker)
        self.timer_thread.daemon = True
        self.timer_thread.start()
    
    def handle_timeout(self):
        """Handle when time runs out"""
        if not self.game_running or self.answer_submitted:
            return
        
        self.answer_submitted = True
        self.total_words += 1
        
        # Store incorrect answer with translation
        translation = self.get_translation(self.current_word)
        self.incorrect_answers.append({
            'word': self.current_word,
            'translation': translation,
            'user_answer': "Tiden utløp"
        })
        
        # Update stats
        difficulty = getattr(self, 'difficulty_var', tk.StringVar(value="easy")).get()
        self.update_stats(difficulty, False)
        
        # Log word for review
        self.log_word_for_review(self.current_word, False)
        
        # Play feedback sound
        self.play_feedback_sound(False)
        
        # Show result
        if hasattr(self, 'result_text') and self.result_text.winfo_exists():
            self.result_text.config(state='normal')
            self.result_text.delete(1.0, tk.END)
            
            timeout_message = f"⏰ Tiden er ute!\n\n🎯 Ord: '{self.current_word}'\n📖 Oversettelse: '{translation}'\n\n💡 Prøv å lytte mer nøye neste gang!"
            
            self.result_text.insert(tk.END, timeout_message)
            self.result_text.tag_add("timeout", "1.0", "end")
            self.result_text.tag_config("timeout", foreground=self.colors['red'])
            self.result_text.config(state='disabled')
        
        # Wait a moment then load next word
        self.root.after(3000, self.next_word)
    
    def handle_action_timeout(self):
        """Handle when time runs out in action mode - game over"""
        if not self.game_running or self.answer_submitted:
            return
        
        self.answer_submitted = True
        self.game_running = False  # Game over in action mode
        
        # Store incorrect answer
        translation = self.get_translation(self.current_word)
        self.incorrect_answers.append({
            'word': self.current_word,
            'translation': translation,
            'user_answer': "Tiden utløp"
        })
        
        # Update stats
        self.update_stats(self.current_difficulty_level, False)
        
        # Log word for review
        self.log_word_for_review(self.current_word, False)
        
        # Play feedback sound
        self.play_feedback_sound(False)
        
        # Show game over message
        if hasattr(self, 'result_text') and self.result_text.winfo_exists():
            self.result_text.config(state='normal')
            self.result_text.delete(1.0, tk.END)
            
            game_over_message = f"💥 SPILL OVER!\n\n⏰ Tiden er ute!\n\n🎯 Du nådde ord {self.total_words + 1} av {len(self.session_words)}\n📊 Vanskelighetsgrad: {self.current_difficulty_level.title()}\n\n💪 Prøv igjen for å komme lenger!"
            
            self.result_text.insert(tk.END, game_over_message)
            self.result_text.tag_add("game_over", "1.0", "end")
            self.result_text.tag_config("game_over", foreground=self.colors['red'])
            self.result_text.config(state='disabled')
        
        # End session after showing game over
        self.root.after(5000, self.end_session)
    
    def submit_answer(self, event=None):
        """Submit the player's answer"""
        if not self.game_running or self.answer_submitted:
            return
        
        player_answer = self.input_var.get().strip()
        correct_answer = self.current_word
        
        # Check if this is the first attempt for this word
        is_first_attempt = correct_answer not in self.attempted_words
        self.attempted_words.add(correct_answer)
        
        # Get game mode
        game_mode = getattr(self, 'game_mode_var', tk.StringVar(value="practice")).get()
        
        # Check if answer is correct (case-insensitive)
        if player_answer.lower() == correct_answer.lower():
            # Correct answer - stop timer and show result
            self.answer_submitted = True
            if hasattr(self, 'timer_label') and self.timer_label.winfo_exists():
                self.timer_label.config(text="0s")
            
            self.total_words += 1
            self.correct_words += 1
            
            # Score only on first attempt
            if is_first_attempt:
                self.score += 10
            
            # Store correct answer with translation
            translation = self.get_translation(correct_answer)
            self.correct_answers.append({
                'word': correct_answer,
                'translation': translation,
                'user_answer': player_answer
            })
            
            # Update stats
            if game_mode == "action":
                self.update_stats(self.current_difficulty_level, True)
            else:
                difficulty = getattr(self, 'difficulty_var', tk.StringVar(value="easy")).get()
                self.update_stats(difficulty, True)
            
            # Play feedback sound
            self.play_feedback_sound(True)
            
            # Log word for review
            self.log_word_for_review(correct_answer, True)
            
            # Handle time carryover for action mode
            if game_mode == "action":
                # Calculate remaining time and add to time bank
                base_time = self.action_mode_times[self.current_difficulty_level]
                total_time = self.current_time_bank + base_time
                # Estimate remaining time (this is approximate since we don't have exact timer state)
                # In a real implementation, you'd want to track the exact remaining time
                estimated_used_time = min(3, total_time)  # Assume 1-3 seconds used
                self.current_time_bank = max(0, total_time - estimated_used_time)
                
                # Update progress bar to show new time bank
                if self.current_time_bank > 0:
                    # Calculate percentage based on next word's total time
                    next_base_time = self.action_mode_times[self.current_difficulty_level]
                    next_total_time = self.current_time_bank + next_base_time
                    percentage = (self.current_time_bank / next_total_time) * 100
                    self.update_circular_progress(percentage)
            
            if hasattr(self, 'result_text') and self.result_text.winfo_exists():
                self.result_text.config(state='normal')
                self.result_text.delete(1.0, tk.END)
                
                if game_mode == "action":
                    result_message = f"🎉 Riktig!\n\n🎯 Ord: '{correct_answer}'\n📖 Oversettelse: '{translation}'\n⏰ Tid igjen: {self.current_time_bank}s"
                else:
                    if is_first_attempt:
                        result_message = f"🎉 Perfekt! Du fikk det riktig!\n\n🎯 Ord: '{correct_answer}'\n📖 Oversettelse: '{translation}'\n\n✨ +10 XP tjent!"
                    else:
                        result_message = f"🎉 Riktig! Bra gjort!\n\n🎯 Ord: '{correct_answer}'\n📖 Oversettelse: '{translation}'"
                
                self.result_text.insert(tk.END, result_message)
                self.result_text.tag_add("correct", "1.0", "end")
                self.result_text.tag_config("correct", foreground=self.colors['green'])
                self.result_text.config(state='disabled')
            
            # Wait a moment then load next word
            self.root.after(3000, self.next_word)
        else:
            # Wrong answer - handle based on game mode
            self.play_feedback_sound(False)
            self.log_word_for_review(correct_answer, False)
            
            if game_mode == "action":
                # Action mode: no correction, just continue with audio
                # The audio will keep repeating until correct answer or timeout
                pass
            else:
                # Practice mode: show correction
                self.reveal_correct_answer(correct_answer, player_answer)
    
    def reveal_correct_answer(self, correct_answer, user_answer=None):
        """Reveal the correct answer letter by letter"""
        def reveal_worker():
            revealed = ""
            for i, letter in enumerate(correct_answer):
                revealed += letter
                if hasattr(self, 'result_text') and self.result_text.winfo_exists():
                    self.root.after(0, lambda: self.result_text.config(state='normal'))
                    self.root.after(0, lambda: self.result_text.delete(1.0, tk.END))
                    self.root.after(0, lambda: self.result_text.insert(tk.END, f"❌ Incorrect. Correct answer: '{revealed}'"))
                    self.root.after(0, lambda: self.result_text.tag_add("incorrect", "1.0", "end"))
                    self.root.after(0, lambda: self.result_text.tag_config("incorrect", foreground=self.colors['red']))
                    self.root.after(0, lambda: self.result_text.config(state='disabled'))
                time.sleep(0.3)
                if not self.game_running:
                    break
            
            # Store incorrect answer after revealing
            translation = self.get_translation(correct_answer)
            self.incorrect_answers.append({
                'word': correct_answer,
                'translation': translation,
                'user_answer': user_answer or "Ingen svar"
            })
        
        self.reveal_thread = threading.Thread(target=reveal_worker)
        self.reveal_thread.daemon = True
        self.reveal_thread.start()
    
    def log_word_for_review(self, word, correct):
        """Log a word for review with spaced repetition interval"""
        try:
            if os.path.exists(self.review_words_file):
                with open(self.review_words_file, 'r', encoding='utf-8') as f:
                    review_words = json.load(f)
            else:
                review_words = {}
            
            if word in review_words:
                interval = review_words[word]["interval"]
                if correct:
                    interval = max(1, interval * 2)  # Double if correct
                else:
                    interval = 1  # Reset if wrong
            else:
                interval = 1
            
            next_review = datetime.now() + timedelta(days=interval)
            review_words[word] = {
                "next_review": next_review.isoformat(),
                "interval": interval
            }
            
            with open(self.review_words_file, 'w', encoding='utf-8') as f:
                json.dump(review_words, f, indent=2)
        except Exception as e:
            print(f"Error logging word for review: {e}")
    
    def load_review_words(self):
        """Load words that need review with spaced repetition"""
        review_words = {}
        try:
            if os.path.exists(self.review_words_file):
                with open(self.review_words_file, 'r', encoding='utf-8') as f:
                    review_words = json.load(f)
        except Exception as e:
            print(f"Error loading review words: {e}")
        
        # Filter due words
        now = datetime.now()
        due_words = [word for word, data in review_words.items() 
                     if datetime.fromisoformat(data["next_review"]) <= now]
        return due_words
    
    def end_session(self):
        """End the current session and show results"""
        # Stop all threads
        self.game_running = False
        self.answer_submitted = True
        
        # Wait for threads to finish
        if self.audio_thread and self.audio_thread.is_alive():
            self.audio_thread.join(timeout=1)
        if self.timer_thread and self.timer_thread.is_alive():
            self.timer_thread.join(timeout=1)
        if self.reveal_thread and self.reveal_thread.is_alive():
            self.reveal_thread.join(timeout=1)
        if self.feedback_thread and self.feedback_thread.is_alive():
            self.feedback_thread.join(timeout=1)
        
        # Calculate final statistics
        total_words = len(self.session_words)
        correct_words = len(self.correct_answers)
        incorrect_words = len(self.incorrect_answers)
        accuracy = (correct_words / total_words * 100) if total_words > 0 else 0
        
        # Update streak
        self.update_streak()
        
        # Unlock next chapter if score is sufficient
        self.unlock_next_chapter(accuracy)
        
        # Add to accuracy history
        self.game_stats["accuracy_history"].append(accuracy)
        self.game_stats["session_history"].append({
            "date": datetime.now().isoformat(),
            "total_words": total_words,
            "correct_words": correct_words,
            "accuracy": accuracy,
            "difficulty": getattr(self, 'difficulty_var', tk.StringVar(value="easy")).get()
        })
        
        # Save updated stats
        self.save_game_stats()
        
        # Show comprehensive results screen
        self.show_results_screen(total_words, correct_words, incorrect_words, accuracy)
    
    def show_results_screen(self, total_words, correct_words, incorrect_words, accuracy):
        """Show a comprehensive results screen that takes over the entire window"""
        # Clear the main content area - check if content_frame exists
        if hasattr(self, 'content_frame') and self.content_frame.winfo_exists():
            for widget in self.content_frame.winfo_children():
                widget.destroy()
        else:
            # If content_frame doesn't exist, we need to recreate the UI structure
            self.setup_gui()
            return
        
        # Create main results container (no scrolling needed)
        results_frame = tk.Frame(self.content_frame, bg='white')
        results_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Title
        title_label = tk.Label(results_frame, text="🎉 Leksjon Fullført!", 
                              font=('Arial', 18, 'bold'), 
                              fg=self.colors['green'], bg='white')
        title_label.pack(pady=(0, 15))
        
        # Overall stats section
        stats_frame = tk.Frame(results_frame, bg='white', relief='solid', bd=2)
        stats_frame.pack(fill=tk.X, pady=(0, 15), padx=10)
        
        tk.Label(stats_frame, text="📊 Samlet Resultat", 
                font=('Arial', 14, 'bold'), 
                fg=self.colors['dark_gray'], bg='white').pack(pady=8)
        
        stats_text = f"""• Totalt Ord: {total_words}
• Riktige: {correct_words}
• Feil: {incorrect_words}
• XP Tjent: {self.score}
• Nøyaktighet: {accuracy:.1f}%
• Streak: {self.game_stats['current_streak']} dager"""
        
        tk.Label(stats_frame, text=stats_text,
                font=('Arial', 11), 
                fg=self.colors['dark_gray'], bg='white',
                justify='left').pack(pady=(0, 8))
        
        # Performance message
        if accuracy > 90:
            performance_msg = "✅ Utmerket arbeid! Du er på rett vei!"
            performance_color = self.colors['green']
        elif accuracy > 70:
            performance_msg = "👍 Bra jobbet! Fortsett slik!"
            performance_color = self.colors['blue']
        else:
            performance_msg = "💪 Fortsett å øve! Du blir bedre!"
            performance_color = self.colors['orange']
        
        tk.Label(stats_frame, text=performance_msg,
                font=('Arial', 11, 'bold'), 
                fg=performance_color, bg='white').pack(pady=(0, 8))
        
        # Create a frame for correct and incorrect answers side by side
        answers_frame = tk.Frame(results_frame, bg='white')
        answers_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Correct answers section (left side)
        if self.correct_answers:
            correct_frame = tk.Frame(answers_frame, bg='white', relief='solid', bd=2)
            correct_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 5))
            
            tk.Label(correct_frame, text="✅ Riktige Svar", 
                    font=('Arial', 12, 'bold'), 
                    fg=self.colors['green'], bg='white').pack(pady=6)
            
            # Create scrollable text widget for correct answers
            correct_text = tk.Text(correct_frame, height=8, 
                                  font=('Arial', 10), 
                                  wrap=tk.WORD,
                                  bg='white', relief='flat',
                                  state='disabled')
            correct_text.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))
            
            # Populate correct answers
            correct_text.config(state='normal')
            for word_data in self.correct_answers:
                correct_text.insert(tk.END, f"• {word_data['word']} - {word_data['translation']}\n")
            correct_text.config(state='disabled')
        
        # Incorrect answers section (right side)
        if self.incorrect_answers:
            incorrect_frame = tk.Frame(answers_frame, bg='white', relief='solid', bd=2)
            incorrect_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 10))
            
            tk.Label(incorrect_frame, text="❌ Ord som Trenger Øvelse", 
                    font=('Arial', 12, 'bold'), 
                    fg=self.colors['red'], bg='white').pack(pady=6)
            
            # Create scrollable text widget for incorrect answers
            incorrect_text = tk.Text(incorrect_frame, height=8, 
                                    font=('Arial', 10), 
                                    wrap=tk.WORD,
                                    bg='white', relief='flat',
                                    state='disabled')
            incorrect_text.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))
            
            # Populate incorrect answers
            incorrect_text.config(state='normal')
            for word_data in self.incorrect_answers:
                incorrect_text.insert(tk.END, f"Riktig: {word_data['word']} - {word_data['translation']}\n")
                if word_data.get('user_answer'):
                    incorrect_text.insert(tk.END, f"Ditt svar: {word_data['user_answer']}\n")
                incorrect_text.insert(tk.END, "\n")
            incorrect_text.config(state='disabled')
        
        # Action buttons
        button_frame = tk.Frame(results_frame, bg='white')
        button_frame.pack(fill=tk.X, pady=10)
        
        # Restart button
        restart_button = tk.Button(button_frame, text="🔄 Start Ny Leksjon", 
                                  font=('Arial', 12, 'bold'),
                                  bg=self.colors['green'], fg='white',
                                  relief='flat', bd=0,
                                  padx=20, pady=8,
                                  command=self.restart_session)
        restart_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Review words button (if there are incorrect answers)
        if self.incorrect_answers:
            review_button = tk.Button(button_frame, text="📚 Øv på Feil Ord", 
                                     font=('Arial', 12, 'bold'),
                                     bg=self.colors['orange'], fg='white',
                                     relief='flat', bd=0,
                                     padx=20, pady=8,
                                     command=self.review_incorrect_words)
            review_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Back to main menu button
        menu_button = tk.Button(button_frame, text="🏠 Tilbake til Hovedmeny", 
                               font=('Arial', 12, 'bold'),
                               bg=self.colors['light_gray'], fg=self.colors['dark_gray'],
                               relief='flat', bd=0,
                               padx=20, pady=8,
                               command=self.return_to_main_menu)
        menu_button.pack(side=tk.LEFT)
    
    def restart_session(self):
        """Restart the current session with same settings"""
        # Stop any running game processes
        self.stop_game()
        
        # Reset game state
        self.current_word = ""
        self.current_audio_file = ""
        self.player_input = ""
        self.session_words = []
        self.correct_answers = []
        self.incorrect_answers = []
        self.score = 0
        self.total_words = 0
        self.correct_words = 0
        self.attempted_words = set()
        self.game_running = False
        self.answer_submitted = False
        self.audio_thread = None
        self.timer_thread = None
        self.reveal_thread = None
        self.feedback_thread = None
        
        # Reset hearts
        self.current_hearts = self.max_hearts
        self.update_hearts_display()
        
        # Recreate the main game interface on existing root
        self.setup_gui()
        
        # Update settings indicator to reflect current settings
        mode_map = {"practice": "Øvelse", "action": "Aksjon"}
        mode = mode_map.get(self.game_mode_var.get(), "Øvelse")
        difficulty_map = {"easy": "Lett", "medium": "Middels", "hard": "Vanskelig"}
        difficulty = difficulty_map.get(self.difficulty_var.get(), "Lett")
        words = self.words_per_session_var.get()
        translation = "Oversettelse PÅ" if self.show_translation_var.get() else "Oversettelse AV"
        if hasattr(self, 'settings_info_label') and self.settings_info_label.winfo_exists():
            self.settings_info_label.config(text=f"Nåværende: {mode} • {difficulty} • {words} ord • {translation}")
        
        # Start new session
        self.start_game()
    
    def review_incorrect_words(self):
        """Start a review session with only the words that were answered incorrectly"""
        # Create a new session with only incorrect words
        review_words = [word_data['word'] for word_data in self.incorrect_answers]
        
        if not review_words:
            messagebox.showinfo("Ingen Feil", "Du hadde ingen feil i denne leksjonen!")
            return
        
        # Reset game state
        self.session_words = review_words
        self.correct_answers = []
        self.incorrect_answers = []
        self.score = 0
        self.attempted_words = set()
        
        # Recreate the main game interface
        self.setup_gui()
        
        # Start review session
        self.start_game()
    
    def return_to_main_menu(self):
        """Return to the main menu interface"""
        # Reset game state
        self.session_words = []
        self.correct_answers = []
        self.incorrect_answers = []
        self.score = 0
        self.attempted_words = set()
        
        # Recreate the main menu
        self.setup_gui()
    
    def run(self):
        """Run the game"""
        self.root.mainloop()
        
        

def main():
    """Main function to run the dictation game"""
    try:
        game = DuolingoStyleDictationGame()
        game.run()
    except Exception as e:
        print(f"Error running game: {e}")

if __name__ == "__main__":
    main()