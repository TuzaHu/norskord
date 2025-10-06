#!/usr/bin/env python3
"""
Duolingo-Style Dictation Game Engine
Modular version of ma.py with all the original features
"""

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
    """Main game engine - modular version of DuolingoStyleDictationGame"""
    
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
    
    def categorize_difficulty(self):
        """Categorize words by difficulty based on length and complexity"""
        difficulties = {
            'easy': [],
            'medium': [],
            'hard': []
        }
        
        for word, data in self.words_data.items():
            difficulty = data.get('difficulty', 'medium')
            if difficulty in difficulties:
                difficulties[difficulty].append(word)
        
        return difficulties
    
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
        with open("game_stats.json", 'w', encoding='utf-8') as f:
            json.dump(self.game_stats, f, ensure_ascii=False, indent=2)
    
    def setup_gui(self):
        """Setup the main GUI"""
        self.root = tk.Tk()
        self.root.title("🇳🇴 Norskord - Norwegian Language Learning")
        self.root.geometry("900x700")
        self.root.configure(bg='white')
        self.root.resizable(True, True)
        
        # Color scheme
        self.colors = {
            'primary': '#2E8B57',
            'secondary': '#4682B4', 
            'accent': '#FF6347',
            'success': '#27AE60',
            'warning': '#F39C12',
            'error': '#E74C3C',
            'info': '#3498DB',
            'light_green': '#90EE90',
            'orange': '#FFA500',
            'red': '#FF6B6B',
            'blue': '#4A90E2',
            'green': '#2ECC71',
            'dark_gray': '#2C3E50',
            'light_gray': '#ECF0F1'
        }
        
        # Initialize GUI variables
        self.difficulty_var = tk.StringVar(value="easy")
        self.show_translation_var = tk.StringVar(value=False)
        self.chapter_var = tk.StringVar(value="Kapital En")
        
        # Create main interface
        self.create_main_interface()
    
    def create_main_interface(self):
        """Create the main game interface"""
        # Main frame
        main_frame = tk.Frame(self.root, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, text="🇳🇴 Norskord", 
                              font=('Arial', 24, 'bold'), 
                              fg=self.colors['primary'], bg='white')
        title_label.pack(pady=(0, 10))
        
        subtitle_label = tk.Label(main_frame, text="Norwegian Language Learning Game", 
                                 font=('Arial', 14), 
                                 fg=self.colors['dark_gray'], bg='white')
        subtitle_label.pack(pady=(0, 30))
        
        # Menu buttons
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(pady=20)
        
        # Start Game button
        start_button = tk.Button(button_frame, text="🎮 Start Game", 
                               font=('Arial', 14, 'bold'),
                               bg=self.colors['primary'], fg='white',
                               relief='flat', bd=0, height=2, width=20,
                               command=self.start_game)
        start_button.pack(pady=5)
        
        # Settings button
        settings_button = tk.Button(button_frame, text="⚙️ Settings", 
                                  font=('Arial', 14, 'bold'),
                                  bg=self.colors['blue'], fg='white',
                                  relief='flat', bd=0, height=2, width=20,
                                  command=self.open_settings)
        settings_button.pack(pady=5)
        
        # Statistics button
        stats_button = tk.Button(button_frame, text="📊 Statistics", 
                               font=('Arial', 14, 'bold'),
                               bg=self.colors['green'], fg='white',
                               relief='flat', bd=0, height=2, width=20,
                               command=self.show_statistics)
        stats_button.pack(pady=5)
        
        # Exit button
        exit_button = tk.Button(button_frame, text="❌ Exit", 
                              font=('Arial', 14, 'bold'),
                              bg=self.colors['error'], fg='white',
                              relief='flat', bd=0, height=2, width=20,
                              command=self.root.quit)
        exit_button.pack(pady=5)
        
        # Status bar
        self.status_frame = tk.Frame(main_frame, bg=self.colors['light_gray'], 
                                   relief='sunken', bd=1)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(20, 0))
        
        self.status_label = tk.Label(self.status_frame, 
                                   text="Ready to learn Norwegian! 🇳🇴", 
                                   font=('Arial', 10), 
                                   fg=self.colors['dark_gray'], 
                                   bg=self.colors['light_gray'])
        self.status_label.pack(pady=5)
    
    def start_game(self):
        """Start a new game session"""
        # Select words for session
        self.session_words = self.select_words_for_session()
        
        if not self.session_words:
            messagebox.showerror("No Words Available", 
                               "No words available for the selected difficulty level.")
            return
        
        # Initialize session
        self.correct_answers = []
        self.incorrect_answers = []
        self.attempted_words = set()
        self.current_word_index = 0
        
        # Start the game interface
        self.create_game_interface()
    
    def select_words_for_session(self):
        """Select words for the current session"""
        difficulty_words = self.difficulty_levels.get(self.difficulty_var.get(), [])
        
        if not difficulty_words:
            return []
        
        # Filter out already attempted words
        available_words = [w for w in difficulty_words if w not in self.attempted_words]
        
        # Select random words
        selected_count = min(self.words_per_session, len(available_words))
        return random.sample(available_words, selected_count)
    
    def create_game_interface(self):
        """Create the game interface"""
        # Clear main interface
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Game frame
        game_frame = tk.Frame(self.root, bg='white')
        game_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header with progress
        header_frame = tk.Frame(game_frame, bg='white')
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        progress_label = tk.Label(header_frame, 
                                text=f"Word {self.current_word_index + 1} of {len(self.session_words)}", 
                                font=('Arial', 16, 'bold'), 
                                fg=self.colors['primary'], bg='white')
        progress_label.pack()
        
        # Progress bar
        self.progress_canvas = tk.Canvas(header_frame, height=20, bg='white', highlightthickness=0)
        self.progress_canvas.pack(fill=tk.X, pady=(10, 0))
        
        # Current word display
        word_frame = tk.Frame(game_frame, bg='white')
        word_frame.pack(fill=tk.BOTH, expand=True)
        
        self.word_label = tk.Label(word_frame, text="", 
                                 font=('Arial', 28, 'bold'), 
                                 fg=self.colors['primary'], bg='white',
                                 wraplength=800, justify='center')
        self.word_label.pack(expand=True)
        
        # Audio button
        audio_button = tk.Button(word_frame, text="🔊 Play Audio", 
                               font=('Arial', 12, 'bold'),
                               bg=self.colors['blue'], fg='white',
                               relief='flat', bd=0, height=2, width=15,
                               command=self.play_current_audio)
        audio_button.pack(pady=20)
        
        # Input area
        input_frame = tk.Frame(game_frame, bg='white')
        input_frame.pack(fill=tk.X, pady=20)
        
        input_label = tk.Label(input_frame, text="Enter English translation:", 
                             font=('Arial', 14, 'bold'), 
                             fg=self.colors['dark_gray'], bg='white')
        input_label.pack(anchor='w', pady=(0, 10))
        
        self.answer_entry = tk.Entry(input_frame, font=('Arial', 16), 
                                   width=50, relief='solid', bd=2)
        self.answer_entry.pack(fill=tk.X, pady=(0, 10))
        self.answer_entry.bind('<Return>', lambda e: self.submit_answer())
        
        # Action buttons
        button_frame = tk.Frame(game_frame, bg='white')
        button_frame.pack(fill=tk.X, pady=20)
        
        submit_button = tk.Button(button_frame, text="Submit Answer", 
                                font=('Arial', 12, 'bold'),
                                bg=self.colors['success'], fg='white',
                                relief='flat', bd=0, height=2, width=15,
                                command=self.submit_answer)
        submit_button.pack(side=tk.LEFT, padx=(0, 10))
        
        skip_button = tk.Button(button_frame, text="Skip", 
                              font=('Arial', 12, 'bold'),
                              bg=self.colors['warning'], fg='white',
                              relief='flat', bd=0, height=2, width=15,
                              command=self.skip_word)
        skip_button.pack(side=tk.LEFT, padx=(0, 10))
        
        quit_button = tk.Button(button_frame, text="Quit Game", 
                              font=('Arial', 12, 'bold'),
                              bg=self.colors['error'], fg='white',
                              relief='flat', bd=0, height=2, width=15,
                              command=self.quit_game)
        quit_button.pack(side=tk.LEFT)
        
        # Start the current word
        self.start_current_word()
    
    def start_current_word(self):
        """Start the current word"""
        if self.current_word_index >= len(self.session_words):
            self.end_session()
            return
        
        self.current_word = self.session_words[self.current_word_index]
        self.word_label.config(text=self.current_word)
        self.answer_entry.delete(0, tk.END)
        self.answer_entry.focus()
        
        # Update progress bar
        self.update_progress_bar()
        
        # Start audio playback
        self.play_current_audio()
        
        # Start timer if in action mode
        if hasattr(self, 'game_mode_var') and self.game_mode_var.get() == "action":
            self.start_timer()
    
    def play_current_audio(self):
        """Play audio for current word"""
        try:
            audio_file = os.path.join(self.audio_directory, f"{self.current_word}.mp3")
            if os.path.exists(audio_file):
                pygame.mixer.music.load(audio_file)
                pygame.mixer.music.play()
            else:
                print(f"Audio file not found: {audio_file}")
        except Exception as e:
            print(f"Error playing audio: {e}")
    
    def submit_answer(self):
        """Submit user's answer"""
        user_answer = self.answer_entry.get().strip()
        
        if not user_answer:
            messagebox.showwarning("Empty Answer", "Please enter a translation.")
            return
        
        # Check answer
        is_correct = self.check_answer(user_answer)
        
        if is_correct:
            self.correct_answers.append(self.current_word)
            messagebox.showinfo("Correct! ✅", "Well done!")
        else:
            self.incorrect_answers.append(self.current_word)
            messagebox.showwarning("Incorrect ❌", 
                                 f"Sorry, that's not correct.\nCorrect answer: {self.current_word}")
        
        self.next_word()
    
    def check_answer(self, user_answer):
        """Check if user's answer is correct"""
        # Get translation for current word
        translation = self.get_word_translation(self.current_word)
        
        # Simple check - could be improved
        return user_answer.lower().strip() == translation.lower().strip()
    
    def get_word_translation(self, word):
        """Get translation for a word"""
        word_data = self.words_data.get(word, {})
        translation = word_data.get('translation')
        
        if translation:
            return translation
        
        # Fallback to translation service
        return self.translation_service.get_translation(word)
    
    def next_word(self):
        """Move to next word"""
        self.current_word_index += 1
        self.start_current_word()
    
    def skip_word(self):
        """Skip current word"""
        self.incorrect_answers.append(self.current_word)
        self.next_word()
    
    def quit_game(self):
        """Quit current game"""
        result = messagebox.askyesno("Quit Game", "Are you sure you want to quit?")
        if result:
            self.end_session()
    
    def end_session(self):
        """End the current session"""
        # Calculate results
        total_words = len(self.correct_answers) + len(self.incorrect_answers)
        accuracy = (len(self.correct_answers) / total_words * 100) if total_words > 0 else 0
        
        # Show results
        self.show_results(total_words, len(self.correct_answers), len(self.incorrect_answers), accuracy)
    
    def show_results(self, total_words, correct_words, incorrect_words, accuracy):
        """Show session results"""
        # Clear game interface
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Results frame
        results_frame = tk.Frame(self.root, bg='white')
        results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(results_frame, text="🎉 Session Complete!", 
                              font=('Arial', 24, 'bold'), 
                              fg=self.colors['primary'], bg='white')
        title_label.pack(pady=(0, 30))
        
        # Results
        results_text = f"""
📊 Session Results:

Total Words: {total_words}
Correct: {correct_words} ✅
Incorrect: {incorrect_words} ❌
Accuracy: {accuracy:.1f}% 🎯
        """
        
        results_label = tk.Label(results_frame, text=results_text.strip(), 
                               font=('Arial', 14), 
                               fg=self.colors['dark_gray'], bg='white',
                               justify='left')
        results_label.pack(pady=20)
        
        # Action buttons
        button_frame = tk.Frame(results_frame, bg='white')
        button_frame.pack(pady=30)
        
        play_again_button = tk.Button(button_frame, text="🔄 Play Again", 
                                    font=('Arial', 14, 'bold'),
                                    bg=self.colors['primary'], fg='white',
                                    relief='flat', bd=0, height=2, width=15,
                                    command=self.start_game)
        play_again_button.pack(side=tk.LEFT, padx=10)
        
        main_menu_button = tk.Button(button_frame, text="🏠 Main Menu", 
                                   font=('Arial', 14, 'bold'),
                                   bg=self.colors['blue'], fg='white',
                                   relief='flat', bd=0, height=2, width=15,
                                   command=self.create_main_interface)
        main_menu_button.pack(side=tk.LEFT, padx=10)
    
    def open_settings(self):
        """Open settings window with chapter dropdown"""
        # Create settings window
        settings_window = tk.Toplevel(self.root)
        settings_window.title("⚙️ Spill Innstillinger")
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
                              fg=self.colors['primary'], bg='white')
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
        
        # Continue with other settings...
        self.create_other_settings(main_frame)
        
        # Save button
        save_button = tk.Button(main_frame, text="💾 Save Settings", 
                              font=('Arial', 14, 'bold'),
                              bg=self.colors['success'], fg='white',
                              relief='flat', bd=0, height=2, width=20,
                              command=lambda: self.save_settings(settings_window))
        save_button.pack(pady=30)
    
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
                info_color = self.colors['primary']  # Green for active chapters
            else:
                required_score = selected_chapter.get('required_score', 70)
                info_text = f"🔒 Låst • Trenger {required_score}% score i forrige kapittel for å låse opp"
                info_color = '#888888'  # Grey for locked chapters
            
            self.chapter_info_label.config(text=info_text, fg=info_color)
        
        # Update current chapter setting
        self.current_chapter = selected_chapter['name']
        self.current_chapter_folder = selected_chapter['folder']
        
        print(f"Selected chapter: {selected_chapter['name']} (unlocked: {selected_chapter['unlocked']})")
    
    def create_other_settings(self, main_frame):
        """Create other settings sections"""
        # Difficulty section
        difficulty_frame = tk.Frame(main_frame, bg='white')
        difficulty_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(difficulty_frame, text="Velg Vanskelighetsgrad:", 
                font=('Arial', 14, 'bold'), 
                fg=self.colors['dark_gray'], bg='white').pack(anchor='w', pady=(0, 10))
        
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
            selectcolor=self.colors['primary'],
            activebackground=self.colors['light_green'],
            activeforeground='white',
            relief='flat',
            bd=0,
            command=on_difficulty_change
        )
        easy_radio.pack(side=tk.LEFT, padx=(0, 10))
        
        medium_radio = tk.Radiobutton(
            difficulty_buttons_frame,
            text="Medium",
            variable=self.difficulty_var,
            value="medium",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg=self.colors['dark_gray'],
            selectcolor=self.colors['orange'],
            activebackground=self.colors['orange'],
            activeforeground='white',
            relief='flat',
            bd=0,
            command=on_difficulty_change
        )
        medium_radio.pack(side=tk.LEFT, padx=(0, 10))
        
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
            relief='flat',
            bd=0,
            command=on_difficulty_change
        )
        hard_radio.pack(side=tk.LEFT)
        
        # Set initial styling
        main_frame.after(100, update_button_styles)
        
        # Words per session section
        words_frame = tk.Frame(main_frame, bg='white')
        words_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(words_frame, text="Ord per Økt:", 
                font=('Arial', 14, 'bold'), 
                fg=self.colors['dark_gray'], bg='white').pack(anchor='w', pady=(0, 10))
        
        self.words_per_session_var = tk.IntVar(value=self.words_per_session)
        words_spinbox = tk.Spinbox(
            words_frame,
            from_=5,
            to=50,
            textvariable=self.words_per_session_var,
            font=('Arial', 12),
            width=10
        )
        words_spinbox.pack(anchor='w')
        
        # Show translation option
        translation_frame = tk.Frame(main_frame, bg='white')
        translation_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(translation_frame, text="Læringsvalg:", 
                font=('Arial', 14, 'bold'), 
                fg=self.colors['dark_gray'], bg='white').pack(anchor='w', pady=(0, 10))
        
        translation_check_frame = tk.Frame(translation_frame, bg='white')
        translation_check_frame.pack(fill=tk.X)
        
        self.translation_checkbox = tk.Checkbutton(
            translation_check_frame,
            text="Vis oversettelser under spillet",
            variable=self.show_translation_var,
            font=('Arial', 12),
            fg=self.colors['dark_gray'],
            bg='white',
            command=self.on_translation_toggle
        )
        self.translation_checkbox.pack(side=tk.LEFT)
        
        # Translation indicator
        self.translation_indicator = tk.Label(
            translation_check_frame,
            text="❌",
            font=('Arial', 16),
            fg=self.colors['error'],
            bg='white'
        )
        self.translation_indicator.pack(side=tk.LEFT, padx=(10, 0))
        
        self.update_translation_indicator()
        
        # Help text for translation setting
        help_label = tk.Label(translation_frame, 
                             text="Hjelp: Aktiver for å se engelske oversettelser mens du spiller", 
                             font=('Arial', 10, 'italic'), 
                             fg=self.colors['dark_gray'], bg='white')
        help_label.pack(anchor='w', pady=(10, 0))
        
        # Game mode section
        mode_frame = tk.Frame(main_frame, bg='white')
        mode_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(mode_frame, text="Spillmodus:", 
                font=('Arial', 14, 'bold'), 
                fg=self.colors['dark_gray'], bg='white').pack(anchor='w', pady=(0, 10))
        
        self.game_mode_var = tk.StringVar(value="practice")
        
        practice_radio = tk.Radiobutton(
            mode_frame,
            text="Øve (Practice) - Læringsmodus",
            variable=self.game_mode_var,
            value="practice",
            font=('Arial', 12),
            fg=self.colors['dark_gray'],
            bg='white'
        )
        practice_radio.pack(anchor='w', pady=2)
        
        action_radio = tk.Radiobutton(
            mode_frame,
            text="Handling (Action) - Tidsbasert utfordring",
            variable=self.game_mode_var,
            value="action",
            font=('Arial', 12),
            fg=self.colors['dark_gray'],
            bg='white'
        )
        action_radio.pack(anchor='w', pady=2)
    
    def on_translation_toggle(self):
        """Called when translation checkbox is toggled"""
        self.update_translation_indicator()
        print(f"Translation setting changed to: {self.show_translation_var.get()}")
    
    def update_translation_indicator(self):
        """Update the visual indicator for translation setting"""
        if hasattr(self, 'translation_indicator'):
            if self.show_translation_var.get():
                self.translation_indicator.config(text="✅", fg=self.colors['primary'])
            else:
                self.translation_indicator.config(text="❌", fg=self.colors['error'])
    
    def save_settings(self, settings_window):
        """Save settings and close window"""
        # Update settings
        self.words_per_session = self.words_per_session_var.get()
        
        # Close settings window
        settings_window.grab_release()
        settings_window.destroy()
        
        # Update status
        if hasattr(self, 'status_label'):
            self.status_label.config(text="Settings saved! ⚙️")
    
    def show_statistics(self):
        """Show statistics window"""
        stats_window = tk.Toplevel(self.root)
        stats_window.title("📊 Game Statistics")
        stats_window.geometry("500x400")
        stats_window.configure(bg='white')
        stats_window.resizable(False, False)
        
        # Center window
        stats_window.update_idletasks()
        x = (stats_window.winfo_screenwidth() // 2) - (500 // 2)
        y = (stats_window.winfo_screenheight() // 2) - (400 // 2)
        stats_window.geometry(f"500x400+{x}+{y}")
        
        # Make it modal
        stats_window.transient(self.root)
        stats_window.grab_set()
        
        # Statistics content
        main_frame = tk.Frame(stats_window, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, text="📊 Game Statistics", 
                              font=('Arial', 18, 'bold'), 
                              fg=self.colors['primary'], bg='white')
        title_label.pack(pady=(0, 20))
        
        # Statistics display
        stats_text = f"""
📚 Total Words Learned: {self.game_stats.get('total_words_learned', 0)}
🎯 Overall Accuracy: {self.game_stats.get('accuracy_percentage', 0):.1f}%
🔥 Current Streak: {self.game_stats.get('current_streak', 0)}
🏆 Best Streak: {self.game_stats.get('best_streak', 0)}

📈 Recent Sessions: {len(self.game_stats.get('session_history', []))}
        """
        
        stats_label = tk.Label(main_frame, text=stats_text.strip(), 
                              font=('Arial', 12), 
                              fg=self.colors['dark_gray'], bg='white',
                              justify='left')
        stats_label.pack(pady=20)
        
        # Close button
        close_button = tk.Button(main_frame, text="Close", 
                               font=('Arial', 12, 'bold'),
                               bg=self.colors['blue'], fg='white',
                               relief='flat', bd=0, height=2, width=15,
                               command=stats_window.destroy)
        close_button.pack(pady=20)
    
    def update_progress_bar(self):
        """Update the progress bar"""
        if not hasattr(self, 'progress_canvas'):
            return
        
        # Clear canvas
        self.progress_canvas.delete("all")
        
        # Calculate progress
        progress = (self.current_word_index + 1) / len(self.session_words)
        bar_width = self.progress_canvas.winfo_width() - 4
        fill_width = int(bar_width * progress)
        
        # Draw background
        self.progress_canvas.create_rectangle(2, 2, bar_width + 2, 18, 
                                            fill=self.colors['light_gray'], outline="")
        
        # Draw progress
        if fill_width > 0:
            self.progress_canvas.create_rectangle(2, 2, fill_width + 2, 18, 
                                                fill=self.colors['primary'], outline="")
    
    def run(self):
        """Run the application"""
        self.root.mainloop()
