import pygame
import random
import time
import os
from pydub import AudioSegment
from pydub.playback import play
import threading
import tkinter as tk
from tkinter import messagebox
from translation_service import TranslationService

class DictationGame:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        # Game settings
        self.audio_directory = "audio"
        self.merged_log_file = "merged_log.txt"
        self.game_duration = 20  # seconds per word
        self.repeat_interval = 3  # seconds between audio repeats
        
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
        self.answer_submitted = False  # Track if answer was submitted early
        self.audio_thread = None
        self.timer_thread = None
        
        # Session management
        self.session_words = []  # Words for current session
        self.correct_answers = []  # List of correctly answered words
        self.incorrect_answers = []  # List of incorrectly answered words
        self.words_per_session = 10  # Default words per session
        self.attempted_words = set()  # Track words that have been attempted
        self.review_words_file = "words_to_review.txt"  # File to log words for review
        
        # Load words dynamically
        self.words_data = self.load_words_data()
        self.difficulty_levels = self.categorize_difficulty()
        
        # GUI setup
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
                            'translation': None  # Will be fetched on demand
                        }
        except FileNotFoundError:
            print(f"Error: {self.merged_log_file} not found")
            return {}
            
        return words_data
    
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
            
            # Simple difficulty categorization
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
        """Setup the game GUI"""
        self.root = tk.Tk()
        self.root.title("Norwegian Dictation Game")
        self.root.geometry("900x700")
        self.root.configure(bg='#2c3e50')
        
        # Title
        title_label = tk.Label(
            self.root,
            text="Norwegian Dictation Game",
            font=("Arial", 28, "bold"),
            bg='#2c3e50',
            fg='white'
        )
        title_label.pack(pady=20)
        
        # Difficulty and session settings
        settings_frame = tk.Frame(self.root, bg='#2c3e50')
        settings_frame.pack(pady=15)
        
        # Difficulty selection
        difficulty_frame = tk.Frame(settings_frame, bg='#2c3e50')
        difficulty_frame.pack()
        
        tk.Label(
            difficulty_frame,
            text="Select Difficulty:",
            font=("Arial", 16, "bold"),
            bg='#2c3e50',
            fg='white'
        ).pack()
        
        self.difficulty_var = tk.StringVar(value="easy")
        for diff in ["easy", "medium", "hard"]:
            tk.Radiobutton(
                difficulty_frame,
                text=diff.title(),
                variable=self.difficulty_var,
                value=diff,
                font=("Arial", 14),
                bg='#2c3e50',
                fg='white',
                selectcolor='#34495e'
            ).pack(side=tk.LEFT, padx=15)
        
        # Words per session
        session_frame = tk.Frame(settings_frame, bg='#2c3e50')
        session_frame.pack(pady=10)
        
        tk.Label(
            session_frame,
            text="Words per Session:",
            font=("Arial", 14, "bold"),
            bg='#2c3e50',
            fg='white'
        ).pack()
        
        self.words_per_session_var = tk.StringVar(value="10")
        session_spinbox = tk.Spinbox(
            session_frame,
            from_=5,
            to=50,
            textvariable=self.words_per_session_var,
            font=("Arial", 12),
            width=10
        )
        session_spinbox.pack()
        
        # Game info
        self.info_label = tk.Label(
            self.root,
            text="Click 'Start Game' to begin!",
            font=("Arial", 14),
            bg='#2c3e50',
            fg='white'
        )
        self.info_label.pack(pady=15)
        
        # Timer
        self.timer_label = tk.Label(
            self.root,
            text="Time: 20s",
            font=("Arial", 18, "bold"),
            bg='#2c3e50',
            fg='#e74c3c'
        )
        self.timer_label.pack(pady=10)
        
        # Progress and Score
        progress_frame = tk.Frame(self.root, bg='#2c3e50')
        progress_frame.pack(pady=10)
        
        self.progress_label = tk.Label(
            progress_frame,
            text="Progress: 0/0",
            font=("Arial", 14),
            bg='#2c3e50',
            fg='#3498db'
        )
        self.progress_label.pack()
        
        self.score_label = tk.Label(
            progress_frame,
            text="Score: 0/0 (0.0%)",
            font=("Arial", 16),
            bg='#2c3e50',
            fg='#27ae60'
        )
        self.score_label.pack()
        
        # Input field
        input_frame = tk.Frame(self.root, bg='#2c3e50')
        input_frame.pack(pady=20)
        
        tk.Label(
            input_frame,
            text="Type your answer:",
            font=("Arial", 14),
            bg='#2c3e50',
            fg='white'
        ).pack()
        
        self.input_var = tk.StringVar()
        self.input_entry = tk.Entry(
            input_frame,
            textvariable=self.input_var,
            font=("Arial", 18),
            width=50,
            state='disabled'
        )
        self.input_entry.pack(pady=10)
        
        # Result display
        result_frame = tk.Frame(self.root, bg='#2c3e50')
        result_frame.pack(pady=15, fill=tk.BOTH, expand=True)
        
        # Create a scrollable text widget for better results display
        self.result_text = tk.Text(
            result_frame,
            height=12,
            width=80,
            font=("Arial", 12),
            bg='#34495e',
            fg='white',
            wrap=tk.WORD,
            state='disabled'
        )
        
        # Add scrollbar
        scrollbar = tk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons
        button_frame = tk.Frame(self.root, bg='#2c3e50')
        button_frame.pack(pady=20)
        
        self.start_button = tk.Button(
            button_frame,
            text="Start Game",
            command=self.start_game,
            font=("Arial", 14, "bold"),
            bg='#27ae60',
            fg='white',
            padx=25,
            pady=12
        )
        self.start_button.pack(side=tk.LEFT, padx=15)
        
        self.stop_button = tk.Button(
            button_frame,
            text="Stop Game",
            command=self.stop_game,
            font=("Arial", 14, "bold"),
            bg='#e74c3c',
            fg='white',
            padx=25,
            pady=12,
            state='disabled'
        )
        self.stop_button.pack(side=tk.LEFT, padx=15)
        
        # Bind Enter key to submit answer
        self.input_entry.bind('<Return>', self.submit_answer)
        
    def start_game(self):
        """Start the dictation game"""
        # Get session settings
        try:
            self.words_per_session = int(self.words_per_session_var.get())
        except ValueError:
            self.words_per_session = 10
        
        # Prepare session words
        difficulty = self.difficulty_var.get()
        available_words = self.difficulty_levels.get(difficulty, [])
        
        if not available_words:
            self.info_label.config(text="No words available for selected difficulty!")
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
        
        # Reset GUI
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.input_entry.config(state='normal')
        self.progress_label.config(text=f"Progress: 0/{len(self.session_words)}")
        self.score_label.config(text="Score: 0 points | Accuracy: 0.0%")
        self.timer_label.config(text="Time: 20s")
        self.result_text.config(state='normal')
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state='disabled')
        
        self.info_label.config(text=f"Game started! {len(self.session_words)} words in this session.")
        self.next_word()
    
    def stop_game(self):
        """Stop the game"""
        self.game_running = False
        
        if self.audio_thread and self.audio_thread.is_alive():
            self.audio_thread.join(timeout=1)
        
        if self.timer_thread and self.timer_thread.is_alive():
            self.timer_thread.join(timeout=1)
        
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.input_entry.config(state='disabled')
        
        accuracy = (self.correct_words / self.total_words * 100) if self.total_words > 0 else 0
        self.info_label.config(text=f"Game stopped! Final score: {self.correct_words}/{self.total_words} ({accuracy:.1f}%)")
        self.timer_label.config(text="Time: 0s")
        self.result_label.config(text="")
    
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
        
        # Update progress
        self.progress_label.config(text=f"Progress: {self.total_words + 1}/{len(self.session_words)}")
        
        self.info_label.config(text=f"Listen to the word... (Word {self.total_words + 1} of {len(self.session_words)})")
        self.input_var.set("")
        self.input_entry.focus()
        
        # Stop any existing audio threads
        if self.audio_thread and self.audio_thread.is_alive():
            self.audio_thread.join(timeout=0.1)
        
        # Start audio playback
        self.play_audio()
        
        # Start timer
        self.start_timer()
    
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
    
    def start_timer(self):
        """Start the countdown timer"""
        def timer_worker():
            remaining_time = self.game_duration
            while remaining_time > 0 and self.game_running and not self.answer_submitted:
                self.timer_label.config(text=f"Time: {remaining_time}s")
                time.sleep(1)
                remaining_time -= 1
            
            if self.game_running and not self.answer_submitted:
                # Time's up - auto-submit with wrong answer
                self.handle_timeout()
        
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
        self.incorrect_answers.append(self.current_word)
        
        # Log word for review
        self.log_word_for_review(self.current_word)
        
        # Update score display
        accuracy = (self.correct_words / self.total_words * 100) if self.total_words > 0 else 0
        self.score_label.config(text=f"Score: {self.score} points | Accuracy: {accuracy:.1f}%")
        
        # Wait a moment then load next word
        self.root.after(3000, self.next_word)
    
    def submit_answer(self, event=None):
        """Submit the player's answer"""
        if not self.game_running or self.answer_submitted:
            return
        
        player_answer = self.input_var.get().strip()
        correct_answer = self.current_word
        
        # Check if this is the first attempt for this word
        is_first_attempt = correct_answer not in self.attempted_words
        self.attempted_words.add(correct_answer)
        
        # Check if answer is correct (case-insensitive)
        if player_answer.lower() == correct_answer.lower():
            # Correct answer - stop timer and show result
            self.answer_submitted = True
            self.timer_label.config(text="Time: 0s")
            
            self.total_words += 1
            self.correct_words += 1
            
            # Score only on first attempt
            if is_first_attempt:
                self.score += 10
                points_earned = 10
            else:
                points_earned = 0
            
            self.correct_answers.append(correct_answer)
            
            # Get translation dynamically
            translation = self.get_translation(correct_answer)
            self.result_text.config(state='normal')
            self.result_text.delete(1.0, tk.END)
            
            if is_first_attempt:
                result_message = f"✅ Correct! '{correct_answer}' = '{translation}' (+10 points)"
            else:
                result_message = f"✅ Correct! '{correct_answer}' = '{translation}' (no points - already attempted)"
            
            self.result_text.insert(tk.END, result_message)
            self.result_text.tag_add("correct", "1.0", "end")
            self.result_text.tag_config("correct", foreground='#27ae60')
            self.result_text.config(state='disabled')
            
            # Update score display
            accuracy = (self.correct_words / self.total_words * 100) if self.total_words > 0 else 0
            self.score_label.config(text=f"Score: {self.score} points | Accuracy: {accuracy:.1f}%")
            
            # Wait a moment then load next word
            self.root.after(3000, self.next_word)
        else:
            # Wrong answer - continue timer, show partial reveal
            self.reveal_correct_answer(correct_answer)
            
            # Don't update score yet, let timer continue
            # Timer will auto-submit when time runs out
    
    def reveal_correct_answer(self, correct_answer):
        """Reveal the correct answer letter by letter"""
        def reveal_worker():
            revealed = ""
            for i, letter in enumerate(correct_answer):
                revealed += letter
                self.result_text.config(state='normal')
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, f"❌ Incorrect. Correct answer: '{revealed}'")
                self.result_text.tag_add("incorrect", "1.0", "end")
                self.result_text.tag_config("incorrect", foreground='#e74c3c')
                self.result_text.config(state='disabled')
                time.sleep(0.3)
                if not self.game_running:
                    break
        
        reveal_thread = threading.Thread(target=reveal_worker)
        reveal_thread.daemon = True
        reveal_thread.start()
    
    def log_word_for_review(self, word):
        """Log a word for future review"""
        try:
            with open(self.review_words_file, 'a', encoding='utf-8') as f:
                f.write(f"{word}\n")
        except Exception as e:
            print(f"Error logging word for review: {e}")
    
    def load_review_words(self):
        """Load words that need review"""
        review_words = set()
        try:
            if os.path.exists(self.review_words_file):
                with open(self.review_words_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        word = line.strip()
                        if word:
                            review_words.add(word)
        except Exception as e:
            print(f"Error loading review words: {e}")
        return review_words
    
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
        
        # Calculate final statistics
        total_words = len(self.session_words)
        correct_words = len(self.correct_answers)
        incorrect_words = len(self.incorrect_answers)
        accuracy = (correct_words / total_words * 100) if total_words > 0 else 0
        
        # Create results message with better formatting
        results_text = f"""🎯 SESSION COMPLETE! 🎯

📊 Final Results:
• Total Words: {total_words}
• Correct: {correct_words}
• Incorrect: {incorrect_words}
• Final Score: {self.score} points
• Accuracy: {accuracy:.1f}%

✅ Words you got right:"""
        
        if self.correct_answers:
            for i, word in enumerate(self.correct_answers, 1):
                results_text += f"\n  {i}. {word}"
        else:
            results_text += "\n  None"
        
        results_text += "\n\n📚 Words you should review:"
        
        if self.incorrect_answers:
            for i, word in enumerate(self.incorrect_answers, 1):
                results_text += f"\n  {i}. {word}"
        else:
            results_text += "\n  None"
        
        results_text += "\n\nClick 'Start Game' to play again!"
        
        # Update GUI
        self.info_label.config(text="Session Complete!")
        self.timer_label.config(text="Time: 0s")
        self.result_text.config(state='normal')
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, results_text)
        self.result_text.tag_add("results", "1.0", "end")
        self.result_text.tag_config("results", foreground='#f39c12')
        self.result_text.config(state='disabled')
        self.progress_label.config(text=f"Final Score: {self.score} points")
        self.score_label.config(text=f"Accuracy: {accuracy:.1f}%")
        
        # Re-enable start button
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.input_entry.config(state='disabled')
    
    def run(self):
        """Run the game"""
        self.root.mainloop()

def main():
    """Main function to run the dictation game"""
    try:
        game = DictationGame()
        game.run()
    except Exception as e:
        print(f"Error running game: {e}")

if __name__ == "__main__":
    main() 