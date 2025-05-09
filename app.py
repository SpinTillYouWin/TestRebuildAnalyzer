import gradio as gr
import math
import pandas as pd
import json
from itertools import combinations
import random
from roulette_data import (
    EVEN_MONEY, DOZENS, COLUMNS, STREETS, CORNERS, SIX_LINES, SPLITS,
    NEIGHBORS_EUROPEAN, LEFT_OF_ZERO_EUROPEAN, RIGHT_OF_ZERO_EUROPEAN
)

# New: Initialize betting category mappings for faster lookups
BETTING_MAPPINGS = {}

def initialize_betting_mappings():
    """Initialize a mapping of numbers to their betting categories for efficient lookups."""
    global BETTING_MAPPINGS
    BETTING_MAPPINGS = {i: {"even_money": [], "dozens": [], "columns": [], "streets": [], "corners": [], "six_lines": [], "splits": []} for i in range(37)}
    
    # Convert lists to sets and map numbers to categories
    for name, numbers in EVEN_MONEY.items():
        numbers_set = set(numbers)
        for num in numbers_set:
            BETTING_MAPPINGS[num]["even_money"].append(name)
    
    for name, numbers in DOZENS.items():
        numbers_set = set(numbers)
        for num in numbers_set:
            BETTING_MAPPINGS[num]["dozens"].append(name)
    
    for name, numbers in COLUMNS.items():
        numbers_set = set(numbers)
        for num in numbers_set:
            BETTING_MAPPINGS[num]["columns"].append(name)
    
    for name, numbers in STREETS.items():
        numbers_set = set(numbers)
        for num in numbers_set:
            BETTING_MAPPINGS[num]["streets"].append(name)
    
    for name, numbers in CORNERS.items():
        numbers_set = set(numbers)
        for num in numbers_set:
            BETTING_MAPPINGS[num]["corners"].append(name)
    
    for name, numbers in SIX_LINES.items():
        numbers_set = set(numbers)
        for num in numbers_set:
            BETTING_MAPPINGS[num]["six_lines"].append(name)
    
    for name, numbers in SPLITS.items():
        numbers_set = set(numbers)
        for num in numbers_set:
            BETTING_MAPPINGS[num]["splits"].append(name)

# Line 1: Start of updated update_scores_batch function
def update_scores_batch(spins):
    """Update scores for a batch of spins and return actions for undo."""
    # UNCHANGED: Initialize action log for undo
    action_log = []
    
    # CHANGED: Directly update state dictionaries and build minimal action_log
    for spin in spins:
        spin_value = int(spin)
        action = {"spin": spin_value, "increments": {}}
        
        # Get all betting categories for this number from precomputed mappings
        categories = BETTING_MAPPINGS[spin_value]
        
        # Update even money scores
        for name in categories["even_money"]:
            state.even_money_scores[name] += 1
            action["increments"].setdefault("even_money_scores", {})[name] = 1
        
        # Update dozens scores
        for name in categories["dozens"]:
            state.dozen_scores[name] += 1
            action["increments"].setdefault("dozen_scores", {})[name] = 1
        
        # Update columns scores
        for name in categories["columns"]:
            state.column_scores[name] += 1
            action["increments"].setdefault("column_scores", {})[name] = 1
        
        # Update streets scores
        for name in categories["streets"]:
            state.street_scores[name] += 1
            action["increments"].setdefault("street_scores", {})[name] = 1
        
        # Update corners scores
        for name in categories["corners"]:
            state.corner_scores[name] += 1
            action["increments"].setdefault("corner_scores", {})[name] = 1
        
        # Update six lines scores
        for name in categories["six_lines"]:
            state.six_line_scores[name] += 1
            action["increments"].setdefault("six_line_scores", {})[name] = 1
        
        # Update splits scores
        for name in categories["splits"]:
            state.split_scores[name] += 1
            action["increments"].setdefault("split_scores", {})[name] = 1
        
        # Update straight-up scores
        state.scores[spin_value] += 1
        action["increments"].setdefault("scores", {})[spin_value] = 1
        
        # Update side scores
        if spin_value in current_left_of_zero:
            state.side_scores["Left Side of Zero"] += 1
            action["increments"].setdefault("side_scores", {})["Left Side of Zero"] = 1
        if spin_value in current_right_of_zero:
            state.side_scores["Right Side of Zero"] += 1
            action["increments"].setdefault("side_scores", {})["Right Side of Zero"] = 1
        
        action_log.append(action)
    
    # UNCHANGED: Return the action log for undo functionality
    return action_log

def validate_roulette_data():
    """Validate that all required constants from roulette_data.py are present and correctly formatted."""
    required_dicts = {
        "EVEN_MONEY": EVEN_MONEY,
        "DOZENS": DOZENS,
        "COLUMNS": COLUMNS,
        "STREETS": STREETS,
        "CORNERS": CORNERS,
        "SIX_LINES": SIX_LINES,
        "SPLITS": SPLITS
    }
    required_neighbors = {
        "NEIGHBORS_EUROPEAN": NEIGHBORS_EUROPEAN,
        "LEFT_OF_ZERO_EUROPEAN": LEFT_OF_ZERO_EUROPEAN,
        "RIGHT_OF_ZERO_EUROPEAN": RIGHT_OF_ZERO_EUROPEAN
    }

# Lines after (context, unchanged)
    errors = []

    # Check betting category dictionaries
    for name, data in required_dicts.items():
        if not isinstance(data, dict):
            errors.append(f"{name} must be a dictionary.")
            continue
        for key, value in data.items():
            if not isinstance(key, str) or not isinstance(value, (list, set, tuple)) or not all(isinstance(n, int) for n in value):
                errors.append(f"{name}['{key}'] must map to a list/set/tuple of integers.")

    # Check neighbor data
    for name, data in required_neighbors.items():
        if name == "NEIGHBORS_EUROPEAN":
            if not isinstance(data, dict):
                errors.append(f"{name} must be a dictionary.")
                continue
            for key, value in data.items():
                if not isinstance(key, int) or not isinstance(value, tuple) or len(value) != 2 or not all(isinstance(n, (int, type(None))) for n in value):
                    errors.append(f"{name}['{key}'] must map to a tuple of two integers or None.")
        else:
            if not isinstance(data, (list, set, tuple)) or not all(isinstance(n, int) for n in data):
                errors.append(f"{name} must be a list/set/tuple of integers.")

    return errors if errors else None

# In Part 1, replace the RouletteState class with the following:

class RouletteState:
    def __init__(self):
        self.scores = {n: 0 for n in range(37)}
        self.even_money_scores = {name: 0 for name in EVEN_MONEY.keys()}
        self.dozen_scores = {name: 0 for name in DOZENS.keys()}
        self.column_scores = {name: 0 for name in COLUMNS.keys()}
        self.street_scores = {name: 0 for name in STREETS.keys()}
        self.corner_scores = {name: 0 for name in CORNERS.keys()}
        self.six_line_scores = {name: 0 for name in SIX_LINES.keys()}
        self.split_scores = {name: 0 for name in SPLITS.keys()}
        self.side_scores = {"Left Side of Zero": 0, "Right Side of Zero": 0}
        self.selected_numbers = set()
        self.last_spins = []
        self.spin_history = []
        self.casino_data = {
            "spins_count": 100,
            "hot_numbers": [],  # Store 5 user-specified hot numbers
            "cold_numbers": [],  # Store 5 user-specified cold numbers
            "even_odd": {"Even": 0.0, "Odd": 0.0},
            "red_black": {"Red": 0.0, "Black": 0.0},
            "low_high": {"Low": 0.0, "High": 0.0},
            "dozens": {"1st Dozen": 0.0, "2nd Dozen": 0.0, "3rd Dozen": 0.0},
            "columns": {"1st Column": 0.0, "2nd Column": 0.0, "3rd Column": 0.0}
        }
        self.hot_suggestions = ""  # Store suggested hot numbers
        self.cold_suggestions = ""  # Store suggested cold numbers
        self.use_casino_winners = False
        self.bankroll = 1000
        self.initial_bankroll = 1000
        self.base_unit = 10
        self.stop_loss = -500
        self.stop_win = 200
        self.target_profit = 10
        self.bet_type = "Even Money"
        self.progression = "Martingale"
        self.current_bet = self.base_unit
        self.next_bet = self.base_unit
        self.progression_state = None
        self.message = f"Start with base bet of {self.base_unit} on {self.bet_type} ({self.progression})"
        self.status = "Active"
        self.status_color = "white"
        self.last_dozen_alert_index = -1
        self.alerted_patterns = set()
        self.last_alerted_spins = None
        self.labouchere_sequence = ""

    def reset(self):
        # Preserve use_casino_winners and casino_data before resetting
        use_casino_winners = self.use_casino_winners
        casino_data = self.casino_data.copy()  # Create a deep copy to preserve the data
        self.scores = {n: 0 for n in range(37)}
        self.even_money_scores = {name: 0 for name in EVEN_MONEY.keys()}
        self.dozen_scores = {name: 0 for name in DOZENS.keys()}
        self.column_scores = {name: 0 for name in COLUMNS.keys()}
        self.street_scores = {name: 0 for name in STREETS.keys()}
        self.corner_scores = {name: 0 for name in CORNERS.keys()}
        self.six_line_scores = {name: 0 for name in SIX_LINES.keys()}
        self.split_scores = {name: 0 for name in SPLITS.keys()}
        self.side_scores = {"Left Side of Zero": 0, "Right Side of Zero": 0}
        self.selected_numbers = set(int(s) for s in self.last_spins if s.isdigit())
        self.last_spins = []
        self.spin_history = []
        # Restore use_casino_winners and casino_data
        self.use_casino_winners = use_casino_winners
        self.casino_data = casino_data
        self.reset_progression()

    def calculate_aggregated_scores_for_spins(self, numbers):
        """Calculate Aggregated Scores for a list of numbers (simulated spins)."""
        even_money_scores = {name: 0 for name in EVEN_MONEY.keys()}
        dozen_scores = {name: 0 for name in DOZENS.keys()}
        column_scores = {name: 0 for name in COLUMNS.keys()}

        for number in numbers:
            # Skip 0 for category counts (consistent with scoring logic)
            if number == 0:
                continue

            # Even Money Bets
            for name, numbers_set in EVEN_MONEY.items():
                if number in numbers_set:
                    even_money_scores[name] += 1

            # Dozens
            for name, numbers_set in DOZENS.items():
                if number in numbers_set:
                    dozen_scores[name] += 1

            # Columns
            for name, numbers_set in COLUMNS.items():
                if number in numbers_set:
                    column_scores[name] += 1

        return even_money_scores, dozen_scores, column_scores

    def reset_progression(self):
        self.current_bet = self.base_unit
        self.next_bet = self.base_unit
        self.progression_state = None
        self.is_stopped = False
        self.message = f"Progression reset. Start with base bet of {self.base_unit} on {self.bet_type} ({self.progression})"
        self.status = "Active"
        return self.bankroll, self.current_bet, self.next_bet, self.message, self.status

    def update_bankroll(self, won):
        payout = {"Even Money": 1, "Dozens": 2, "Columns": 2, "Straight Bets": 35}[self.bet_type]
        if won:
            self.bankroll += self.current_bet * payout
        else:
            self.bankroll -= self.current_bet
        profit = self.bankroll - self.initial_bankroll
        if profit <= self.stop_loss:
            self.is_stopped = True
            self.status = f"Stopped: Hit Stop Loss of {self.stop_loss}"
            self.status_color = "red"  # Red for stop loss
        elif profit >= self.stop_win:
            self.is_stopped = True
            self.status = f"Stopped: Hit Stop Win of {self.stop_win}"
            self.status_color = "green"  # Green for stop win
        else:
            self.status_color = "white"  # Neutral when active

    def update_progression(self, won):
        if self.is_stopped:
            return self.bankroll, self.current_bet, self.next_bet, self.message, self.status, self.status_color
        self.update_bankroll(won)
        if self.bankroll < self.current_bet:
            self.is_stopped = True
            self.status = "Stopped: Insufficient bankroll"
            self.status_color = "red"  # Red for insufficient bankroll
            self.message = "Cannot continue: Bankroll too low."
            return self.bankroll, self.current_bet, self.next_bet, self.message, self.status, self.status_color
    
        if self.progression == "Martingale":
            self.current_bet = self.next_bet
            self.next_bet = self.base_unit if won else self.current_bet * 2
            self.message = f"{'Win' if won else 'Loss'}! Next bet: {self.next_bet}"
        elif self.progression == "Fibonacci":
            fib = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
            if self.progression_state is None:
                self.progression_state = 0
            self.current_bet = self.next_bet
            if won:
                self.progression_state = max(0, self.progression_state - 2)
                self.next_bet = fib[self.progression_state] * self.base_unit
                self.message = f"Win! Move back to {self.next_bet}"
            else:
                self.progression_state = min(len(fib) - 1, self.progression_state + 1)
                self.next_bet = fib[self.progression_state] * self.base_unit
                self.message = f"Loss! Next Fibonacci bet: {self.next_bet}"
        elif self.progression == "Triple Martingale":
            self.current_bet = self.next_bet
            self.next_bet = self.base_unit if won else self.current_bet * 3
            self.message = f"{'Win' if won else 'Loss'}! Next bet: {self.next_bet}"       
        elif self.progression == "Oscar’s Grind":            
            self.current_bet = self.next_bet
            profit = self.bankroll - self.initial_bankroll
            if won and profit > 0:
                self.next_bet = self.base_unit
                self.message = f"Win! Profit achieved, reset to {self.next_bet}"
            elif won:
                self.next_bet = self.current_bet + self.base_unit
                self.message = f"Win! Increase to {self.next_bet}"
            else:
                self.next_bet = self.current_bet
                self.message = f"Loss! Keep bet at {self.next_bet}"
        elif self.progression == "Labouchere":
            # Initialize the sequence if not set
            if self.progression_state is None:
                try:
                    # Try to use the user-provided sequence if available
                    if self.labouchere_sequence and self.labouchere_sequence.strip():
                        sequence = [int(x.strip()) for x in self.labouchere_sequence.split(",")]
                        # Validate sequence: ensure all numbers are positive integers
                        if not sequence or not all(isinstance(x, int) and x > 0 for x in sequence):
                            # Auto-generate sequence based on target_profit if invalid
                            sequence = [1] * self.target_profit  # e.g., target_profit=10 -> [1,1,1,1,1,1,1,1,1,1]
                    else:
                        # Auto-generate sequence based on target_profit
                        sequence = [1] * self.target_profit  # e.g., target_profit=10 -> [1,1,1,1,1,1,1,1,1,1]
                except (ValueError, AttributeError):
                    # Auto-generate sequence based on target_profit if parsing fails
                    sequence = [1] * self.target_profit
                self.progression_state = sequence

            self.current_bet = self.next_bet

            try:
                # Handle empty sequence
                if not self.progression_state:
                    self.progression_state = [1] * self.target_profit  # Reset sequence based on target_profit
                    self.next_bet = self.base_unit
                    self.message = f"Sequence cleared! Reset to {self.next_bet}"
                # Handle sequence with one number
                elif len(self.progression_state) == 1:
                    self.next_bet = self.progression_state[0] * self.base_unit
                    if won:
                        self.progression_state = []
                        self.message = f"Win! Sequence completed, next bet: {self.next_bet}"
                    else:
                        self.message = f"Loss! Next bet: {self.next_bet}"
                # Handle sequence with two or more numbers
                else:
                    if won:
                        # Remove first and last numbers
                        self.progression_state = self.progression_state[1:-1] if len(self.progression_state) > 2 else []
                        # Calculate next bet, default to base_unit if sequence is empty
                        self.next_bet = (self.progression_state[0] + self.progression_state[-1]) * self.base_unit if self.progression_state else self.base_unit
                        self.message = f"Win! Sequence: {self.progression_state}, next bet: {self.next_bet}"
                    else:
                        # Add the lost bet to the end (ensure it's a positive integer)
                        lost_bet = max(1, self.current_bet // self.base_unit)  # Ensure positive
                        self.progression_state.append(lost_bet)
                        # Calculate next bet
                        self.next_bet = (self.progression_state[0] + self.progression_state[-1]) * self.base_unit
                        self.message = f"Loss! Sequence: {self.progression_state}, next bet: {self.next_bet}"
            except Exception as e:
                # Fallback in case of any error
                self.progression_state = [1] * self.target_profit
                self.next_bet = self.base_unit
                self.message = f"Error in Labouchere progression: {str(e)}. Resetting sequence to {self.progression_state}, next bet: {self.next_bet}"
        elif self.progression == "Ladder":
            self.current_bet = self.next_bet
            if won:
                self.next_bet = self.current_bet + self.base_unit
                self.message = f"Win! Increase to {self.next_bet}"
            else:
                self.next_bet = self.base_unit
                self.message = f"Loss! Reset to {self.next_bet}"
        elif self.progression == "D’Alembert":
            self.current_bet = self.next_bet
            if won:
                self.next_bet = max(self.base_unit, self.current_bet - self.base_unit)
                self.message = f"Win! Decrease to {self.next_bet}"
            else:
                self.next_bet = self.current_bet + self.base_unit
                self.message = f"Loss! Increase to {self.next_bet}"
        elif self.progression == "Double After a Win":
            self.current_bet = self.next_bet
            if won:
                self.next_bet = self.current_bet * 2
                self.message = f"Win! Double to {self.next_bet}"
            else:
                self.next_bet = self.base_unit
                self.message = f"Loss! Reset to {self.next_bet}"
        elif self.progression == "+1 Win / -1 Loss":
            self.current_bet = self.next_bet
            if won:
                self.next_bet = self.current_bet + self.base_unit
                self.message = f"Win! Increase to {self.next_bet}"
            else:
                self.next_bet = max(self.base_unit, self.current_bet - self.base_unit)
                self.message = f"Loss! Decrease to {self.next_bet}"
        elif self.progression == "+2 Win / -1 Loss":
            self.current_bet = self.next_bet
            if won:
                self.next_bet = self.current_bet + (self.base_unit * 2)
                self.message = f"Win! Increase by 2 units to {self.next_bet}"
            else:
                self.next_bet = max(self.base_unit, self.current_bet - self.base_unit)
                self.message = f"Loss! Decrease to {self.next_bet}"
        
        # Check stop conditions
        profit = self.bankroll - self.initial_bankroll
        if profit <= self.stop_loss:
            self.is_stopped = True
            self.status = "Stopped: Stop Loss Reached"
            self.status_color = "red"  # Red for stop loss
            self.message = f"Stop Loss reached at {profit}. Current bankroll: {self.bankroll}"
        elif profit >= self.stop_win:
            self.is_stopped = True
            self.status = "Stopped: Stop Win Reached"
            self.status_color = "green"  # Green for stop win
            self.message = f"Stop Win reached at {profit}. Current bankroll: {self.bankroll}"
        
        return self.bankroll, self.current_bet, self.next_bet, self.message, self.status, self.status_color
        
        

# Lines before (context, unchanged)
state = RouletteState()
state.last_spins = []
state.scores = {i: 0 for i in range(37)}
state.casino_data = {"hot_numbers": [], "cold_numbers": []}

# Validate roulette data at startup
data_errors = validate_roulette_data()
if data_errors:
    raise RuntimeError("Roulette data validation failed:\n" + "\n".join(data_errors))

# New: Initialize betting mappings
initialize_betting_mappings()

# Lines after (context, unchanged)
current_table_type = "European"
current_neighbors = NEIGHBORS_EUROPEAN
current_left_of_zero = LEFT_OF_ZERO_EUROPEAN
current_right_of_zero = RIGHT_OF_ZERO_EUROPEAN

# Global scores dictionaries
scores = {n: 0 for n in range(37)}
even_money_scores = {name: 0 for name in EVEN_MONEY.keys()}
dozen_scores = {name: 0 for name in DOZENS.keys()}
column_scores = {name: 0 for name in COLUMNS.keys()}
street_scores = {name: 0 for name in STREETS.keys()}
corner_scores = {name: 0 for name in CORNERS.keys()}
six_line_scores = {name: 0 for name in SIX_LINES.keys()}
split_scores = {name: 0 for name in SPLITS.keys()}
side_scores = {"Left Side of Zero": 0, "Right Side of Zero": 0}
selected_numbers = set()

last_spins = []

colors = {
    "0": "green",
    "1": "red", "3": "red", "5": "red", "7": "red", "9": "red", "12": "red",
    "14": "red", "16": "red", "18": "red", "19": "red", "21": "red", "23": "red",
    "25": "red", "27": "red", "30": "red", "32": "red", "34": "red", "36": "red",
    "2": "black", "4": "black", "6": "black", "8": "black", "10": "black", "11": "black",
    "13": "black", "15": "black", "17": "black", "20": "black", "22": "black", "24": "black",
    "26": "black", "28": "black", "29": "black", "31": "black", "33": "black", "35": "black"
}


# Lines before (context)
def format_spins_as_html(spins, num_to_show, show_trends=True):
    """Format the spins as HTML with color-coded display, animations, and pattern badges."""
    if not spins:
        return "<h4>Last Spins</h4><p>No spins yet.</p>"
    
    # Split the spins string into a list and reverse to get the most recent first
    spin_list = spins.split(", ") if spins else []
    spin_list = spin_list[-int(num_to_show):] if spin_list else []  # Take the last N spins
    
    if not spin_list:
        return "<h4>Last Spins</h4><p>No spins yet.</p>"
    
    # Define colors for each number (matching the European Roulette Table)
    colors = {
        "0": "green",
        "1": "red", "3": "red", "5": "red", "7": "red", "9": "red", "12": "red", "14": "red", "16": "red", "18": "red",
        "19": "red", "21": "red", "23": "red", "25": "red", "27": "red", "30": "red", "32": "red", "34": "red", "36": "red",
        "2": "black", "4": "black", "6": "black", "8": "black", "10": "black", "11": "black", "13": "black", "15": "black", "17": "black",
        "20": "black", "22": "black", "24": "black", "26": "black", "28": "black", "29": "black", "31": "black", "33": "black", "35": "black"
    }
    
    # Pattern detection for consecutive colors, dozens, columns, even/odd, and high/low (only if show_trends is True)
    patterns_by_index = {}  # Dictionary to store all patterns starting at each index
    if show_trends:
        for i in range(len(spin_list) - 2):
            if i >= len(spin_list):
                break
            # Check for consecutive colors
            if colors.get(spin_list[i], "") == colors.get(spin_list[i+1], "") == colors.get(spin_list[i+2], ""):
                color_name = colors.get(spin_list[i], '').capitalize()
                if color_name:  # Ensure color_name is not empty
                    if i not in patterns_by_index:
                        patterns_by_index[i] = []
                    patterns_by_index[i].append(f"3 {color_name}s in a Row")
            # Check for consecutive dozens
            dozen_hits = [next((name for name, nums in DOZENS.items() if int(spin) in nums), None) for spin in spin_list[i:i+3]]
            if None not in dozen_hits and len(set(dozen_hits)) == 1:
                if i not in patterns_by_index:
                    patterns_by_index[i] = []
                patterns_by_index[i].append(f"{dozen_hits[0]} Streak")
            # Check for consecutive columns
            column_hits = [next((name for name, nums in COLUMNS.items() if int(spin) in nums), None) for spin in spin_list[i:i+3]]
            if None not in column_hits and len(set(column_hits)) == 1:
                if i not in patterns_by_index:
                    patterns_by_index[i] = []
                patterns_by_index[i].append(f"{column_hits[0]} Streak")
            # Check for consecutive even/odd
            even_odd_hits = [next((name for name, nums in EVEN_MONEY.items() if name in ["Even", "Odd"] and int(spin) in nums), None) for spin in spin_list[i:i+3]]
            if None not in even_odd_hits and len(set(even_odd_hits)) == 1:
                if i not in patterns_by_index:
                    patterns_by_index[i] = []
                patterns_by_index[i].append(f"3 {even_odd_hits[0]}s in a Row")
            # Check for consecutive high/low
            high_low_hits = [next((name for name, nums in EVEN_MONEY.items() if name in ["High", "Low"] and int(spin) in nums), None) for spin in spin_list[i:i+3]]
            if None not in high_low_hits and len(set(high_low_hits)) == 1:
                if i not in patterns_by_index:
                    patterns_by_index[i] = []
                patterns_by_index[i].append(f"3 {high_low_hits[0]}s in a Row")
    
    # Format each spin as a colored span
    html_spins = []
    for i, spin in enumerate(spin_list):
        color = colors.get(spin.strip(), "black")  # Default to black if not found
        # Apply flip, flash, and new-spin classes to the newest spin (last in the list)
        if i == len(spin_list) - 1:
            class_attr = f'fade-in flip flash new-spin spin-{color} {color}'
        else:
            class_attr = f'fade-in {color}'
        # Add all pattern badges for this spin if show_trends is True
        pattern_badges = ""
        if show_trends and i in patterns_by_index:
            for pattern_text in patterns_by_index[i]:
                pattern_badges += f'<span class="pattern-badge" title="{pattern_text}" style="background-color: #ffd700; color: #333; padding: 2px 5px; border-radius: 3px; font-size: 10px; margin-left: 5px;">{pattern_text}</span>'
        html_spins.append(f'<span class="{class_attr}" style="background-color: {color}; color: white; padding: 2px 5px; margin: 2px; border-radius: 3px; display: inline-block;">{spin}{pattern_badges}</span>')
    
    # Wrap the spins in a div with flexbox to enable wrapping, and add a title
    html_output = f'<h4 style="margin-bottom: 5px;">Last Spins</h4><div style="display: flex; flex-wrap: wrap; gap: 5px;">{"".join(html_spins)}</div>'
    
    # Add JavaScript to remove fade-in, flash, flip, and new-spin classes after animations
    html_output += '''
    <script>
        document.querySelectorAll('.fade-in').forEach(element => {
            setTimeout(() => {
                element.classList.remove('fade-in');
            }, 500);
        });
        document.querySelectorAll('.flash').forEach(element => {
            setTimeout(() => {
                element.classList.remove('flash');
            }, 300);
        });
        document.querySelectorAll('.flip').forEach(element => {
            setTimeout(() => {
                element.classList.remove('flip');
            }, 500);
        });
        document.querySelectorAll('.new-spin').forEach(element => {
            setTimeout(() => {
                element.classList.remove('new-spin');
            }, 1000);
        });
    </script>
    '''
    
    return html_output


def render_sides_of_zero_display():
    left_hits = state.side_scores["Left Side of Zero"]
    zero_hits = state.scores[0]
    right_hits = state.side_scores["Right Side of Zero"]
    
    # Calculate the maximum hit count for scaling
    max_hits = max(left_hits, zero_hits, right_hits, 1)  # Avoid division by zero
    
    # Calculate progress percentages (0 to 100)
    left_progress = (left_hits / max_hits) * 100 if max_hits > 0 else 0
    zero_progress = (zero_hits / max_hits) * 100 if max_hits > 0 else 0
    right_progress = (right_hits / max_hits) * 100 if max_hits > 0 else 0
    
    # Define the order of numbers for the European roulette wheel
    original_order = [5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26, 0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10]
    left_side = original_order[:18]  # 5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26
    zero = [0]
    right_side = original_order[19:]  # 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10
    wheel_order = left_side + zero + right_side  # Used for wheel SVG, now 5, ..., 26, 0, 32, ..., 10
    
    # Define betting sections
    jeu_0 = [12, 35, 3, 26, 0, 32, 15]
    voisins_du_zero = [22, 18, 29, 7, 28, 12, 35, 3, 26, 0, 32, 15, 19, 4, 21, 2, 25]
    orphelins = [17, 34, 6, 1, 20, 14, 31, 9]
    tiers_du_cylindre = [27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33]
    
    # Calculate hit counts for each betting section
    jeu_0_hits = sum(state.scores.get(num, 0) for num in jeu_0)
    voisins_du_zero_hits = sum(state.scores.get(num, 0) for num in voisins_du_zero)
    orphelins_hits = sum(state.scores.get(num, 0) for num in orphelins)
    tiers_du_cylindre_hits = sum(state.scores.get(num, 0) for num in tiers_du_cylindre)
    
    # Determine the winning section for Left/Right Side
    winning_section = "Left Side" if left_hits > right_hits else "Right Side" if right_hits > left_hits else None
    
    # Get the latest spin for bounce effect and wheel rotation
    latest_spin = int(state.last_spins[-1]) if state.last_spins else None
    latest_spin_angle = 0
    has_latest_spin = latest_spin is not None
    if latest_spin is not None:
        index = original_order.index(latest_spin) if latest_spin in original_order else 0
        latest_spin_angle = (index * (360 / 37)) + 90  # Adjust for zero at bottom
    
    # Prepare numbers with hit counts
    wheel_numbers = [(num, state.scores.get(num, 0)) for num in wheel_order]
    
    # Calculate maximum hits for scaling highlights
    max_segment_hits = max(state.scores.values(), default=1)
    
    # Hot & Cold Numbers Display with Ties Handling and Cap
    hot_cold_html = '<div class="hot-cold-numbers" style="margin-top: 10px; padding: 8px; background-color: #f9f9f9; border: 1px solid #d3d3d3; border-radius: 5px; display: flex; flex-wrap: wrap; gap: 5px; justify-content: center;">'
    if state.last_spins and len(state.last_spins) >= 1:
        # Use state.scores for consistency with Strongest Numbers Tables
        hit_counts = {n: state.scores.get(n, 0) for n in range(37)}
        
        # Hot numbers: Sort by score descending, number ascending
        sorted_hot = sorted(hit_counts.items(), key=lambda x: (-x[1], x[0]))
        # Take top 5, but include all tied numbers at the 5th position, capped at 28
        hot_numbers = []
        if len(sorted_hot) >= 5:
            fifth_score = sorted_hot[4][1]  # Score of the 5th number
            for num, score in sorted_hot:
                if len(hot_numbers) < 5 or score == fifth_score:
                    if score > 0:  # Only include numbers with hits
                        hot_numbers.append((num, score))
                else:
                    break
        else:
            hot_numbers = [(num, score) for num, score in sorted_hot if score > 0]
        hot_numbers = hot_numbers[:28]  # Cap at 28 to keep display compact
        
        # Cold numbers: Sort by score ascending, number ascending
        sorted_cold = sorted(hit_counts.items(), key=lambda x: (x[1], x[0]))
        # Take top 5, but include all tied numbers at the 5th position, capped at 15
        cold_numbers = []
        if len(sorted_cold) >= 5:
            fifth_score = sorted_cold[4][1]  # Score of the 5th number
            for num, score in sorted_cold:
                if len(cold_numbers) < 5 or score == fifth_score:
                    cold_numbers.append((num, score))
                else:
                    break
        else:
            cold_numbers = [(num, score) for num, score in sorted_cold]
        cold_numbers = cold_numbers[:15]  # Cap at 15 to prevent overflow
        
        # Hot numbers display
        hot_cold_html += '<div style="flex: 1; min-width: 150px;">'
        hot_cold_html += '<span style="display: block; font-weight: bold; font-size: 14px; background: linear-gradient(to right, #ff0000, #ff4500); color: white; padding: 2px 8px; border-radius: 3px; margin-bottom: 5px;">🔥 Hot</span>'
        hot_display = []
        for num, hits in hot_numbers:
            hot_display.append(
                f'<span class="number-badge hot-badge" style="display: inline-flex; align-items: center; justify-content: center; width: 22px; height: 22px; background-color: #ff4444; color: white; border-radius: 50%; font-size: 10px; font-weight: bold; margin: 0 1px; position: relative; box-shadow: 0 2px 4px rgba(0,0,0,0.3); transition: transform 0.2s ease;">{num}<span class="hit-badge" style="position: absolute; top: -6px; right: -6px; background-color: #ff0000; color: white; border-radius: 50%; width: 16px; height: 16px; line-height: 16px; font-size: 8px; text-align: center;">{hits}</span></span>'
            )
        hot_cold_html += "".join(hot_display) if hot_display else '<span style="color: #666;">None</span>'
        hot_cold_html += '</div>'
        
        # Cold numbers display
        hot_cold_html += '<div style="flex: 1; min-width: 150px;">'
        hot_cold_html += '<span style="display: block; font-weight: bold; font-size: 14px; background: linear-gradient(to right, #1e90ff, #87cefa); color: white; padding: 2px 8px; border-radius: 3px; margin-bottom: 5px;">🧊 Cold</span>'
        cold_display = []
        for num, hits in cold_numbers:
            cold_display.append(
                f'<span class="number-badge cold-badge" style="display: inline-flex; align-items: center; justify-content: center; width: 22px; height: 22px; background-color: #87cefa; color: white; border-radius: 50%; font-size: 10px; font-weight: bold; margin: 0 1px; position: relative; box-shadow: 0 2px 4px rgba(0,0,0,0.3); transition: transform 0.2s ease;">{num}<span class="hit-badge" style="position: absolute; top: -6px; right: -6px; background-color: #4682b4; color: white; border-radius: 50%; width: 16px; height: 16px; line-height: 16px; font-size: 8px; text-align: center;">{hits}</span></span>'
            )
        hot_cold_html += "".join(cold_display) if cold_display else '<span style="color: #666;">None</span>'
        hot_cold_html += '</div>'
    else:
        hot_cold_html += '<p style="color: #666; font-size: 12px;">No spins yet to analyze.</p>'
    hot_cold_html += '</div>'
    
    # Generate HTML for the number list
    def generate_number_list(numbers):
        if not numbers:
            return '<div class="number-list">No numbers</div>'
        
        number_html = []
        # Use left_side as is for display
        display_left_side = left_side  # Already 5, 24, 16, ..., 26
        display_wheel_order = display_left_side + zero + right_side  # 5, ..., 26, 0, 32, ..., 10
        display_numbers = [(num, state.scores.get(num, 0)) for num in display_wheel_order]
        
        for num, hits in display_numbers:
            color = colors.get(str(num), "black")
            badge = f'<span class="hit-badge">{hits}</span>' if hits > 0 else ''
            class_name = "number-item" + (" zero-number" if num == 0 else "") + (" bounce" if num == latest_spin else "")
            number_html.append(
                f'<span class="{class_name}" style="background-color: {color}; color: white;" data-hits="{hits}" data-number="{num}">{num}{badge}</span>'
            )
        
        return f'<div class="number-list">{"".join(number_html)}</div>'
    
    number_list = generate_number_list(wheel_numbers)
    
    # Generate SVG for the roulette wheel
    wheel_svg = '<div class="roulette-wheel-container">'
    wheel_svg += '<svg id="roulette-wheel" width="340" height="340" viewBox="0 0 340 340" style="transform: rotate(90deg);">'  # Size unchanged
    
    # Add background arcs for Left Side and Right Side
    left_start_angle = 0
    left_end_angle = 180
    left_start_rad = left_start_angle * (3.14159 / 180)
    left_end_rad = left_end_angle * (3.14159 / 180)
    left_x1 = 170 + 145 * math.cos(left_start_rad)
    left_y1 = 170 + 145 * math.sin(left_start_rad)
    left_x2 = 170 + 145 * math.cos(left_end_rad)
    left_y2 = 170 + 145 * math.sin(left_end_rad)
    left_path_d = f"M 170,170 L {left_x1},{left_y1} A 145,145 0 0,1 {left_x2},{left_y2} L 170,170 Z"
    left_fill = "rgba(106, 27, 154, 0.5)" if winning_section == "Left Side" else "rgba(128, 128, 128, 0.3)"
    left_stroke = "#4A148C" if winning_section == "Left Side" else "#808080"
    wheel_svg += f'<path d="{left_path_d}" fill="{left_fill}" stroke="{left_stroke}" stroke-width="3"/>'
    
    right_start_angle = 180
    right_end_angle = 360
    right_start_rad = right_start_angle * (3.14159 / 180)
    right_end_rad = right_end_angle * (3.14159 / 180)
    right_x1 = 170 + 145 * math.cos(right_start_rad)
    right_y1 = 170 + 145 * math.sin(right_start_rad)
    right_x2 = 170 + 145 * math.cos(right_end_rad)
    right_y2 = 170 + 145 * math.sin(right_end_rad)
    right_path_d = f"M 170,170 L {right_x1},{left_y1} A 145,145 0 0,1 {right_x2},{right_y2} L 170,170 Z"
    right_fill = "rgba(244, 81, 30, 0.5)" if winning_section == "Right Side" else "rgba(128, 128, 128, 0.3)"
    right_stroke = "#D84315" if winning_section == "Right Side" else "#808080"
    wheel_svg += f'<path d="{right_path_d}" fill="{right_fill}" stroke="{right_stroke}" stroke-width="3"/>'
    
    # Add the wheel background
    wheel_svg += '<circle cx="170" cy="170" r="135" fill="#2e7d32"/>'
    
    # Draw the wheel segments
    angle_per_number = 360 / 37
    for i, num in enumerate(original_order):
        angle = i * angle_per_number
        color = colors.get(str(num), "black")
        hits = state.scores.get(num, 0)
        stroke_width = 2 + (hits / max_segment_hits * 3) if max_segment_hits > 0 else 2
        opacity = 0.5 + (hits / max_segment_hits * 0.5) if max_segment_hits > 0 else 0.5
        stroke_color = "#FF00FF" if hits > 0 else "#FFF"
        is_winning_segment = (winning_section == "Left Side" and num in left_side) or (winning_section == "Right Side" and num in right_side)
        class_name = "wheel-segment" + (" pulse" if hits > 0 else "") + (" winning-segment" if is_winning_segment else "")
        rad = angle * (3.14159 / 180)
        next_rad = (angle + angle_per_number) * (3.14159 / 180)
        x1 = 170 + 135 * math.cos(rad)
        y1 = 170 + 135 * math.sin(rad)
        x2 = 170 + 135 * math.cos(next_rad)
        y2 = 170 + 135 * math.sin(next_rad)
        x3 = 170 + 105 * math.cos(next_rad)
        y3 = 170 + 105 * math.sin(next_rad)
        x4 = 170 + 105 * math.cos(rad)
        y4 = 170 + 105 * math.sin(rad)
        path_d = f"M 170,170 L {x1},{y1} A 135,135 0 0,1 {x2},{y2} L {x3},{y3} A 105,105 0 0,0 {x4},{y4} Z"
        wheel_svg += f'<path class="{class_name}" data-number="{num}" data-hits="{hits}" d="{path_d}" fill="{color}" stroke="{stroke_color}" stroke-width="{stroke_width}" fill-opacity="{opacity}" style="cursor: pointer;"/>'
        text_angle = angle + (angle_per_number / 2)
        text_rad = text_angle * (3.14159 / 180)
        text_x = 170 + 120 * math.cos(text_rad)
        text_y = 170 + 120 * math.sin(text_rad)
        wheel_svg += f'<text x="{text_x}" y="{text_y}" font-size="8" fill="white" text-anchor="middle" transform="rotate({text_angle + 90} {text_x},{text_y})">{num}</text>'
        hit_text_x = 170 + 90 * math.cos(text_rad)
        hit_text_y = 170 + 90 * math.sin(text_rad)
        wheel_svg += f'<text x="{hit_text_x}" y="{hit_text_y}" font-size="6" fill="#FFD700" text-anchor="middle" transform="rotate({text_angle + 90} {hit_text_x},{hit_text_y})">{hits if hits > 0 else ""}</text>'
    
    # Add labels for Left Side and Right Side
    left_label_angle = 90
    left_label_rad = left_label_angle * (3.14159 / 180)
    left_label_x = 170 + 155 * math.cos(left_label_rad)
    left_label_y = 170 + 155 * math.sin(left_label_rad)
    wheel_svg += f'<rect x="{left_label_x - 25}" y="{left_label_y - 8}" width="50" height="16" fill="#FFF" stroke="#6A1B9A" stroke-width="1" rx="3"/>'
    wheel_svg += f'<text x="{left_label_x}" y="{left_label_y}" font-size="10" fill="#6A1B9A" text-anchor="middle" dy="3">Left: {left_hits}</text>'
    
    right_label_angle = 270
    right_label_rad = right_label_angle * (3.14159 / 180)
    right_label_x = 170 + 155 * math.cos(right_label_rad)
    right_label_y = 170 + 155 * math.sin(right_label_rad)
    wheel_svg += f'<rect x="{right_label_x - 25}" y="{right_label_y - 8}" width="50" height="16" fill="#FFF" stroke="#F4511E" stroke-width="1" rx="3"/>'
    wheel_svg += f'<text x="{right_label_x}" y="{right_label_y}" font-size="10" fill="#F4511E" text-anchor="middle" dy="3">Right: {right_hits}</text>'
    
    wheel_svg += '<circle cx="170" cy="170" r="15" fill="#FFD700"/>'  # Gold center
    wheel_svg += '</svg>'
    wheel_svg += f'<div id="wheel-pointer" style="position: absolute; top: -10px; left: 168.5px; width: 3px; height: 170px; background-color: #00695C; transform-origin: bottom center;"></div>'
    wheel_svg += f'<div id="spinning-ball" style="position: absolute; width: 12px; height: 12px; background-color: #fff; border-radius: 50%; transform-origin: center center;"></div>'
    wheel_svg += f'<div id="wheel-fallback" style="display: none;">Latest Spin: {latest_spin if latest_spin is not None else "None"}</div>'
    wheel_svg += '</div>'
    
    # Add static betting sections display below the wheel with enhanced effects
    betting_sections_html = '<div class="betting-sections-container">'
    sections = [
        ("jeu_0", "Jeu 0", jeu_0, "#228B22", jeu_0_hits),
        ("voisins_du_zero", "Voisins du Zero", voisins_du_zero, "#008080", voisins_du_zero_hits),
        ("orphelins", "Orphelins", orphelins, "#800080", orphelins_hits),
        ("tiers_du_cylindre", "Tiers du Cylindre", tiers_du_cylindre, "#FFA500", tiers_du_cylindre_hits)
    ]
    
    for section_id, section_name, numbers, color, hits in sections:
        # Generate the numbers list with colors and enhanced effects for numbers with hits
        numbers_html = []
        for num in numbers:
            num_color = colors.get(str(num), "black")
            hit_count = state.scores.get(num, 0)
            is_hot = hit_count > 0
            class_name = "section-number" + (" hot-number" if is_hot else "")
            badge = f'<span class="number-hit-badge">{hit_count}</span>' if is_hot else ''
            numbers_html.append(f'<span class="{class_name}" style="background-color: {num_color}; color: white;" data-hits="{hit_count}" data-number="{num}">{num}{badge}</span>')
        numbers_display = "".join(numbers_html)
        
        # Create a static section instead of an accordion
        badge = f'<span class="hit-badge betting-section-hits">{hits}</span>' if hits > 0 else ''
        betting_sections_html += f'''
        <div class="betting-section">
            <div class="betting-section-header" style="background-color: {color};">
                {section_name}{badge}
            </div>
            <div class="betting-section-numbers">{numbers_display}</div>
        </div>
        '''
    
    betting_sections_html += '</div>'
    
    # Convert Python boolean to JavaScript lowercase boolean
    js_has_latest_spin = "true" if has_latest_spin else "false"
    
    # HTML output with JavaScript to handle animations and interactivity
    return f"""
    <style>
        .circular-progress {{
            position: relative;
            width: 80px;
            height: 80px;
            background: conic-gradient(#d3d3d3 0% 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            transition: all 0.5s ease;
        }}
        .circular-progress::before {{
            content: '';
            position: absolute;
            width: 60px;
            height: 60px;
            background: #e0e0e0;
            border-radius: 50%;
            z-index: 1;
        }}
        .circular-progress span {{
            position: relative;
            z-index: 2;
            font-size: 12px;
            font-weight: bold;
            color: #333;
            text-align: center;
        }}
        #left-progress {{
            background: conic-gradient(#6a1b9a {left_progress}% , #d3d3d3 {left_progress}% 100%);
        }}
        #zero-progress {{
            background: conic-gradient(#00695c {zero_progress}% , #d3d3d3 {zero_progress}% 100%);
        }}
        #right-progress {{
            background: conic-gradient(#f4511e {right_progress}% , #d3d3d3 {right_progress}% 100%);
        }}
        .circular-progress:hover {{
            transform: scale(1.05);
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        }}
        .number-list {{
            display: flex;
            flex-wrap: nowrap;
            gap: 3px;
            justify-content: center;
            margin-top: 10px;
            overflow-x: auto;
            width: 100%;
            padding: 5px 0;
        }}
        .number-item {{
            width: 20px;
            height: 20px;
            line-height: 20px;
            text-align: center;
            font-size: 10px;
            border-radius: 50%;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            position: relative;
            flex-shrink: 0;
        }}
        .number-item.zero-number {{
            width: 60px;
            height: 60px;
            line-height: 60px;
            font-size: 30px;
        }}
        .hit-badge {{
            position: absolute;
            top: -4px;
            right: -4px;
            background: #ffffff;
            color: #000000;
            border: 1px solid #000000;
            font-size: 8px;
            width: 12px;
            height: 12px;
            line-height: 12px;
            border-radius: 50%;
            z-index: 2;
        }}
        .number-item.zero-number .hit-badge {{
            top: -6px;
            right: -6px;
            width: 20px;
            height: 20px;
            line-height: 20px;
            font-size: 10px;
        }}
        .number-badge:hover {{
            transform: scale(1.15);
            box-shadow: 0 0 10px rgba(255, 255, 255, 0.7);
        }}
        .hot-badge {{
            animation: hot-glow 1.5s infinite ease-in-out, flame-effect 2s infinite ease-in-out;
        }}
        @keyframes hot-glow {{
            0% {{ box-shadow: 0 0 5px #ff0000; }}
            50% {{ box-shadow: 0 0 15px #ff4500; }}
            100% {{ box-shadow: 0 0 5px #ff0000; }}
        }}
        @keyframes flame-effect {{
            0% {{ background-color: #ff4444; }}
            50% {{ background-color: #ff6347; }}
            100% {{ background-color: #ff4444; }}
        }}
        .cold-badge {{
            animation: cold-glow 1.5s infinite ease-in-out, snowflake-effect 2s infinite ease-in-out;
        }}
        @keyframes cold-glow {{
            0% {{ box-shadow: 0 0 5px #1e90ff; }}
            50% {{ box-shadow: 0 0 15px #87cefa; }}
            100% {{ box-shadow: 0 0 5px #1e90ff; }}
        }}
        @keyframes snowflake-effect {{
            0% {{ background-color: #87cefa; }}
            50% {{ background-color: #add8e6; }}
            100% {{ background-color: #87cefa; }}
        }}
        .tooltip {{
            position: absolute;
            background: #000;
            color: white;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 14px;
            font-weight: bold;
            z-index: 10;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.2s ease;
            white-space: pre-wrap;
            border: 1px solid #FF00FF;
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }}
        .tracker-column {{
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 5px;
        }}
        .tracker-container {{
            display: flex;
            flex-direction: row;
            justify-content: space-around;
            gap: 15px;
            width: 100%;
            max-width: 600px;
            margin: 0 auto;
            font-family: Arial, sans-serif;
        }}
        .roulette-wheel-container {{
            position: relative;
            width: 340px;
            height: 340px;
            margin: 20px auto;
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        .wheel-segment:hover {{
            filter: brightness(1.2);
        }}
        .pulse {{
            animation: pulse 1.5s infinite ease-in-out;
        }}
        @keyframes pulse {{
            0% {{ stroke-opacity: 1; }}
            50% {{ stroke-opacity: 0.5; }}
            100% {{ stroke-opacity: 1; }}
        }}
        .winning-segment {{
            filter: drop-shadow(0 0 5px rgba(255, 255, 255, 0.8));
        }}
        #wheel-pointer {{
            z-index: 3;
        }}
        @media (max-width: 600px) {{
            .tracker-container {{
                flex-direction: column;
                align-items: center;
            }}
            .number-list {{
                flex-wrap: nowrap;
                overflow-x: auto;
            }}
            .number-item {{
                width: 16px;
                height: 16px;
                line-height: 16px;
                font-size: 8px;
            }}
            .number-item.zero-number {{
                width: 64px;
                height: 64px;
                line-height: 64px;
                font-size: 32px;
            }}
            .hit-badge {{
                width: 10px;
                height: 10px;
                line-height: 10px;
                font-size: 6px;
                top: -3px;
                right: -3px;
            }}
            .number-item.zero-number .hit-badge {{
                width: 20px;
                height: 20px;
                line-height: 20px;
                font-size: 10px;
                top: -6px;
                right: -6px;
            }}
            .roulette-wheel-container {{
                width: 290px;
                height: 290px;
            }}
            #roulette-wheel {{
                width: 290px;
                height: 290px;
            }}
            #wheel-pointer {{
                top: -24px;
                left: 143.5px;
                width: 3px;
                height: 150px;
                background-color: #00695C;
            }}
            #spinning-ball {{
                width: 10px;
                height: 10px;
            }}
        }}
        /* Updated styles for static betting sections with enhanced effects */
        .betting-sections-container {{
            display: flex;
            flex-direction: column;
            gap: 10px;
            margin-top: 20px;
            padding: 10px;
        }}
        .betting-section {{
            background-color: #fff;
            border: 1px solid #d3d3d3;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: box-shadow 0.2s ease;
        }}
        .betting-section:hover {{
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }}
        .betting-section-header {{
            color: white;
            padding: 8px 12px;
            border-radius: 5px 5px 0 0; /* Adjusted for static section */
            font-weight: bold;
            font-size: 14px;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .betting-section-numbers {{
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
            padding: 10px;
            justify-content: center;
            background-color: #f9f9f9;
            border-top: 1px solid #d3d3d3;
            border-radius: 0 0 5px 5px;
        }}
        .section-number {{
            padding: 0;
            margin: 2px;
            border-radius: 50%;
            width: 28px;
            height: 28px;
            line-height: 28px;
            text-align: center;
            font-size: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        .section-number:not(.hot-number) {{
            margin-left: 4px;
            margin-right: 4px;
        }}
        .hot-number {{
            width: 34px;
            height: 34px;
            line-height: 34px;
            font-size: 16px;
            border: 2px solid #FF00FF;
            box-shadow: 0 0 8px #FF00FF;
            text-shadow: 0 0 5px #FF00FF;
            animation: glow 1.5s infinite ease-in-out, border-flash 1.5s infinite ease-in-out, bounce 0.4s ease-in-out;
        }}
        @keyframes glow {{
            0% {{ box-shadow: 0 0 8px #FF00FF; text-shadow: 0 0 5px #FF00FF; }}
            50% {{ box-shadow: 0 0 12px #FF00FF; text-shadow: 0 0 8px #FF00FF; }}
            100% {{ box-shadow: 0 0 8px #FF00FF; text-shadow: 0 0 5px #FF00FF; }}
        }}
        @keyframes border-flash {{
            0% {{ border-color: #FF00FF; }}
            50% {{ border-color: #FFFFFF; }}
            100% {{ border-color: #FF00FF; }}
        }}
        @keyframes bounce {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.2); }}
        }}
        /* Dynamic color pulse for red numbers */
        .hot-number[style*="background-color: red"] {{
            animation: glow 1.5s infinite ease-in-out, border-flash 1.5s infinite ease-in-out, bounce 0.4s ease-in-out, red-pulse 1.5s infinite ease-in-out;
        }}
        @keyframes red-pulse {{
            0% {{ background-color: red; }}
            50% {{ background-color: #ff3333; }}
            100% {{ background-color: red; }}
        }}
        /* Dynamic color pulse for black numbers */
        .hot-number[style*="background-color: black"] {{
            animation: glow 1.5s infinite ease-in-out, border-flash 1.5s infinite ease-in-out, bounce 0.4s ease-in-out, black-pulse 1.5s infinite ease-in-out;
        }}
        @keyframes black-pulse {{
            0% {{ background-color: black; }}
            50% {{ background-color: #333333; }}
            100% {{ background-color: black; }}
        }}
        /* Dynamic color pulse for green numbers */
        .hot-number[style*="background-color: green"] {{
            animation: glow 1.5s infinite ease-in-out, border-flash 1.5s infinite ease-in-out, bounce 0.4s ease-in-out, green-pulse 1.5s infinite ease-in-out;
        }}
        @keyframes green-pulse {{
            0% {{ background-color: green; }}
            50% {{ background-color: #33cc33; }}
            100% {{ background-color: green; }}
        }}
        .number-hit-badge {{
            position: absolute;
            top: -8px;
            right: -8px;
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #ff4444;
            font-size: 8px;
            width: 16px;
            height: 16px;
            line-height: 16px;
            border-radius: 50%;
            z-index: 3;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .betting-section-hits {{
            background-color: #ff4444;
            color: white;
            border: none;
            font-size: 10px;
            width: 20px;
            height: 20px;
            line-height: 20px;
            border-radius: 50%;
            z-index: 3;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
    </style>
    <div style="background-color: #f5c6cb; border: 2px solid #d3d3d3; border-radius: 5px; padding: 10px;">
        <h4 style="text-align: center; margin: 0 0 10px 0; font-family: Arial, sans-serif;">Dealer’s Spin Tracker (Can you spot Bias???) 🔍</h4>
        <div class="tracker-container">
            <div class="tracker-column">
                <div class="circular-progress" id="left-progress">
                    <span>{left_hits}</span>
                </div>
                <span style="display: block; font-weight: bold; font-size: 10px; background-color: #6a1b9a; color: white; padding: 2px 5px; border-radius: 3px;">Left Side</span>
            </div>
            <div class="tracker-column">
                <div class="circular-progress" id="zero-progress">
                    <span>{zero_hits}</span>
                </div>
                <span style="display: block; font-weight: bold; font-size: 10px; background-color: #00695c; color: white; padding: 2px 5px; border-radius: 3px;">Zero</span>
            </div>
            <div class="tracker-column">
                <div class="circular-progress" id="right-progress">
                    <span>{right_hits}</span>
                </div>
                <span style="display: block; font-weight: bold; font-size: 10px; background-color: #f4511e; color: white; padding: 2px 5px; border-radius: 3px;">Right Side</span>
            </div>
        </div>
        {hot_cold_html}
        {number_list}
        {wheel_svg}
        {betting_sections_html}
    </div>
    <script>
        function updateCircularProgress(id, progress) {{
            const element = document.getElementById(id);
            if (!element) {{
                console.error('Element not found: ' + id);
                return;
            }}
            const colors = {{
                'left-progress': '#6a1b9a',
                'zero-progress': '#00695c',
                'right-progress': '#f4511e'
            }};
            const color = colors[id] || '#d3d3d3';
            element.style.background = "conic-gradient(" + color + " " + progress + "%, #d3d3d3 " + progress + "% 100%)";
            element.querySelector('span').textContent = element.querySelector('span').textContent;
        }}
        updateCircularProgress('left-progress', {left_progress});
        updateCircularProgress('zero-progress', {zero_progress});
        updateCircularProgress('right-progress', {right_progress});

        // Tooltip functionality for numbers
        document.querySelectorAll('.number-item').forEach(element => {{
            element.addEventListener('mouseover', (e) => {{
                const hits = element.getAttribute('data-hits');
                const num = element.getAttribute('data-number');
                const tooltipText = "Number " + num + ": " + hits + " hits";
                
                const tooltip = document.createElement('div');
                tooltip.className = 'tooltip';
                tooltip.textContent = tooltipText;
                
                document.body.appendChild(tooltip);
                
                const rect = element.getBoundingClientRect();
                const tooltipRect = tooltip.getBoundingClientRect();
                tooltip.style.left = (rect.left + window.scrollX + (rect.width / 2) - (tooltipRect.width / 2)) + 'px';
                tooltip.style.top = (rect.top + window.scrollY - tooltipRect.height - 5) + 'px';
                tooltip.style.opacity = '1';
            }});
            
            element.addEventListener('mouseout', () => {{
                const tooltip = document.querySelector('.tooltip');
                if (tooltip) {{
                    tooltip.remove();
                }}
            }});
        }});

        // Tooltip functionality for wheel segments
        document.querySelectorAll('.wheel-segment').forEach(segment => {{
            segment.addEventListener('click', (e) => {{
                const hits = segment.getAttribute('data-hits');
                const num = segment.getAttribute('data-number');
                const neighbors = {json.dumps(dict(current_neighbors))};
                const leftNeighbor = neighbors[num] ? neighbors[num][0] : 'None';
                const rightNeighbor = neighbors[num] ? neighbors[num][1] : 'None';
                const tooltipText = "Number " + num + ": " + hits + " hits\\nLeft Neighbor: " + leftNeighbor + "\\nRight Neighbor: " + rightNeighbor;
                
                // Remove any existing tooltips
                const existingTooltip = document.querySelector('.tooltip');
                if (existingTooltip) existingTooltip.remove();
                
                const tooltip = document.createElement('div');
                tooltip.className = 'tooltip';
                tooltip.textContent = tooltipText;
                
                document.body.appendChild(tooltip);
                
                const rect = segment.getBoundingClientRect();
                const tooltipRect = tooltip.getBoundingClientRect();
                tooltip.style.left = (rect.left + window.scrollX + (rect.width / 2) - (tooltipRect.width / 2)) + 'px';
                tooltip.style.top = (rect.top + window.scrollY - tooltipRect.height - 5) + 'px';
                tooltip.style.opacity = '1';
                
                // Remove tooltip after 3 seconds or on click
                setTimeout(() => {{
                    tooltip.remove();
                }}, 3000);
                segment.addEventListener('click', () => {{
                    tooltip.remove();
                }}, {{ once: true }});
            }});
            
            segment.addEventListener('mouseout', () => {{
                const tooltip = document.querySelector('.tooltip');
                if (tooltip) {{
                    tooltip.style.opacity = '0';
                }}
            }});
        }});

        // Remove bounce class after animation
        document.querySelectorAll('.bounce').forEach(element => {{
            setTimeout(() => {{
                element.classList.remove('bounce');
            }}, 400);
        }});

        // JavaScript animation function
        function animateElement(element, startAngle, endAngle, duration, isBall = false) {{
            console.log("animateElement called for element: " + element.id + ", startAngle: " + startAngle + ", endAngle: " + endAngle + ", duration: " + duration + ", isBall: " + isBall);
            const startTime = performance.now();
            const radius = isBall ? 135 : 0;
            
            function step(currentTime) {{
                const elapsed = currentTime - startTime;
                const progress = Math.min(elapsed / duration, 1);
                const easeOut = 1 - Math.pow(1 - progress, 3);
                const currentAngle = startAngle + (endAngle - startAngle) * easeOut;
                
                if (isBall) {{
                    element.style.transform = "rotate(" + currentAngle + "deg) translateX(" + radius + "px)";
                }} else {{
                    element.style.transform = "rotate(" + currentAngle + "deg)";
                }}
                console.log("Animation step - element: " + element.id + ", progress: " + progress.toFixed(2) + ", currentAngle: " + currentAngle.toFixed(2));
                
                if (progress < 1) {{
                    requestAnimationFrame(step);
                }} else {{
                    console.log("Animation completed for element: " + element.id);
                }}
            }}
            
            requestAnimationFrame(step);
        }}

        // Trigger wheel and ball spin animations with JavaScript
        setTimeout(() => {{
            console.log('Attempting to trigger animations...');
            const wheel = document.getElementById('roulette-wheel');
            const ball = document.getElementById('spinning-ball');
            const hasSpin = {js_has_latest_spin};
            console.log('Wheel element:', wheel);
            console.log('Ball element:', ball);
            console.log('Has latest spin:', hasSpin);
            console.log('Latest spin angle:', {latest_spin_angle});
            
            if (wheel && ball && hasSpin) {{
                console.log('Starting animations for wheel and ball using JavaScript...');
                
                // Force visibility toggle to ensure rendering
                wheel.style.visibility = 'hidden';
                ball.style.visibility = 'hidden';
                setTimeout(() => {{
                    wheel.style.visibility = 'visible';
                    ball.style.visibility = 'visible';
                    console.log('Visibility toggled to visible for wheel and ball');
                    
                    // Directly use JavaScript animation
                    animateElement(wheel, 90, {latest_spin_angle}, 2000);
                    animateElement(ball, 0, {-latest_spin_angle}, 2000, true);
                    console.log('JavaScript animations triggered for wheel and ball');
                    
                    // Finalize position after animation
                    setTimeout(() => {{
                        console.log('Finalizing animation positions...');
                        wheel.style.transform = "rotate(" + {latest_spin_angle} + "deg)";
                        ball.style.transform = "rotate(" + {-latest_spin_angle} + "deg) translateX(135px)";
                        console.log('Animation positions finalized');
                    }}, 2000);
                }}, 10);
            }} else {{
                console.warn('Animation not triggered: Elements or latest spin missing');
                if (!wheel) console.warn('Wheel element not found');
                if (!ball) console.warn('Ball element not found');
                if (!hasSpin) console.warn('No latest spin to animate');
            }}
        }}, 2000);

        // Add tooltips to section numbers
        document.querySelectorAll('.section-number').forEach(element => {{
            element.addEventListener('mouseover', (e) => {{
                const hits = element.getAttribute('data-hits');
                const num = element.getAttribute('data-number');
                const tooltipText = "Number " + num + ": " + hits + " hits";
                
                const tooltip = document.createElement('div');
                tooltip.className = 'tooltip';
                tooltip.textContent = tooltipText;
                
                document.body.appendChild(tooltip);
                
                const rect = element.getBoundingClientRect();
                const tooltipRect = tooltip.getBoundingClientRect();
                tooltip.style.left = (rect.left + window.scrollX + (rect.width / 2) - (tooltipRect.width / 2)) + 'px';
                tooltip.style.top = (rect.top + window.scrollY - tooltipRect.height - 5) + 'px';
                tooltip.style.opacity = '1';
            }});
            
            element.addEventListener('mouseout', () => {{
                const tooltip = document.querySelector('.tooltip');
                if (tooltip) {{
                    tooltip.remove();
                }}
            }});
        }});
    </script>
    """

# Line 1: Start of updated validate_spins_input function
def validate_spins_input(spins_input):
    """Validate manually entered spins and update state."""
    import gradio as gr
    import time
    start_time = time.time()  # CHANGED: Added for performance logging
    
    # CHANGED: Enhanced logging with input details
    print(f"validate_spins_input: Processing spins_input='{spins_input}'")
    
    # UNCHANGED: Handle empty input
    if not spins_input or not spins_input.strip():
        print("validate_spins_input: No spins input provided.")
        return "", "<h4>Last Spins</h4><p>No spins entered.</p>"

    # CHANGED: Split and clean spins, enforce max limit
    raw_spins = [s.strip() for s in spins_input.split(",") if s.strip()]
    if len(raw_spins) > 1000:
        error_msg = f"Too many spins ({len(raw_spins)}). Maximum allowed is 1000."
        gr.Warning(error_msg)
        print(f"validate_spins_input: Error - {error_msg}")
        return "", f"<h4>Last Spins</h4><p>{error_msg}</p>"

    # CHANGED: Batch validate spins
    valid_spins = []
    errors = []
    invalid_inputs = []
    
    for spin in raw_spins:
        try:
            num = int(spin)
            if not (0 <= num <= 36):
                errors.append(f"'{spin}' is out of range (must be 0-36)")
                invalid_inputs.append(spin)
            else:
                valid_spins.append(str(num))
        except ValueError:
            errors.append(f"'{spin}' is not a valid integer")
            invalid_inputs.append(spin)

    # CHANGED: Improved error handling and messaging
    if not valid_spins:
        error_msg = "No valid spins found:\n- " + "\n- ".join(errors) + "\nUse comma-separated integers between 0 and 36 (e.g., 5, 12, 0)."
        gr.Warning(error_msg)
        print(f"validate_spins_input: Errors - {error_msg}")
        return "", f"<h4>Last Spins</h4><p>{error_msg}</p>"

    # UNCHANGED: Update state and scores
    state.last_spins = valid_spins
    state.selected_numbers = set(int(s) for s in valid_spins)
    action_log = update_scores_batch(valid_spins)
    for i, spin in enumerate(valid_spins):
        state.spin_history.append(action_log[i])
        # UNCHANGED: Limit spin history to 100 spins
        if len(state.spin_history) > 100:
            state.spin_history.pop(0)

    # UNCHANGED: Generate output
    spins_display_value = ", ".join(valid_spins)
    formatted_html = format_spins_as_html(spins_display_value, 36)  # Default to showing all spins
    
    # CHANGED: Detailed success logging
    print(f"validate_spins_input: Processed {len(valid_spins)} valid spins, spins_display_value='{spins_display_value}', time={time.time() - start_time:.3f}s")
    if invalid_inputs:
        print(f"validate_spins_input: Ignored invalid inputs: {', '.join(invalid_inputs)}")
    
    # CHANGED: Include invalid inputs in warning if present
    if errors:
        warning_msg = f"Processed {len(valid_spins)} valid spins. Invalid inputs ignored:\n- " + "\n- ".join(errors) + "\nUse integers 0-36."
        gr.Warning(warning_msg)
        print(f"validate_spins_input: Warning - {warning_msg}")
    
    return spins_display_value, formatted_html

# Line 1: Start of updated add_spin function
def add_spin(number, current_spins, num_to_show):
    import gradio as gr
    import time
    start_time = time.time()  # CHANGED: Added for performance logging
    
    # CHANGED: Enhanced logging with input details
    print(f"add_spin: Processing number='{number}', current_spins='{current_spins}', num_to_show={num_to_show}")
    
    # CHANGED: Split and deduplicate spins
    numbers = [n.strip() for n in number.split(",") if n.strip()]
    unique_numbers = list(dict.fromkeys(numbers))  # Preserve order, remove duplicates
    if not unique_numbers:
        gr.Warning("No valid input provided. Please enter numbers between 0 and 36.")
        print("add_spin: No valid numbers provided.")
        return current_spins, current_spins, "<h4>Last Spins</h4><p>Error: No valid numbers provided.</p>", update_spin_counter(), render_sides_of_zero_display()
    
    # CHANGED: Reuse validate_spins_input for validation
    spins_input = ", ".join(unique_numbers)
    spins_display_value, formatted_html = validate_spins_input(spins_input)
    
    # CHANGED: Check if validation failed
    if not spins_display_value:
        print(f"add_spin: Validation failed, returning error HTML: {formatted_html}")
        return current_spins, current_spins, formatted_html, update_spin_counter(), render_sides_of_zero_display()
    
    # CHANGED: Efficiently update current spins
    current_spins_list = current_spins.split(", ") if current_spins and current_spins.strip() else []
    if current_spins_list == [""]:
        current_spins_list = []
    
    # CHANGED: Append new spins only if not already processed by validate_spins_input
    new_spins = current_spins_list + unique_numbers
    new_spins_str = ", ".join(new_spins)
    
    # CHANGED: Log duplicates if any
    if len(unique_numbers) < len(numbers):
        duplicates = [n for n in numbers if numbers.count(n) > 1]
        print(f"add_spin: Removed duplicates: {', '.join(set(duplicates))}")
    
    # CHANGED: Log success
    print(f"add_spin: Added {len(unique_numbers)} spins, new_spins_str='{new_spins_str}', time={time.time() - start_time:.3f}s")
    
    # UNCHANGED: Return updated outputs
    return new_spins_str, new_spins_str, formatted_html, update_spin_counter(), render_sides_of_zero_display()

# Line 3: Start of next function (unchanged)
def clear_spins():
    state.selected_numbers.clear()
    state.last_spins = []
    state.spin_history = []  # Clear spin history as well
    state.side_scores = {"Left Side of Zero": 0, "Right Side of Zero": 0}  # Reset side scores
    state.scores = {n: 0 for n in range(37)}  # Reset straight-up scores
    return "", "", "Spins cleared successfully!", "<h4>Last Spins</h4><p>No spins yet.</p>", update_spin_counter(), render_sides_of_zero_display()

# Lines after (context, unchanged)
# Function to save the session
# In Part 1, replace save_session and load_session with:

def save_session():
    session_data = {
        "spins": state.last_spins,
        "spin_history": state.spin_history,
        "scores": state.scores,
        "even_money_scores": state.even_money_scores,
        "dozen_scores": state.dozen_scores,
        "column_scores": state.column_scores,
        "street_scores": state.street_scores,
        "corner_scores": state.corner_scores,
        "six_line_scores": state.six_line_scores,
        "split_scores": state.split_scores,
        "side_scores": state.side_scores,
        "casino_data": state.casino_data,  # Includes hot_numbers and cold_numbers as lists
        "use_casino_winners": state.use_casino_winners
    }
    with open("session.json", "w") as f:
        json.dump(session_data, f)
    return "session.json"

def load_session(file, strategy_name, neighbours_count, strong_numbers_count, *checkbox_args):
    try:
        if file is None:
            return ("", "", "Please upload a session file to load.", "", "", "", "", "", "", "", "", "", "", "", create_dynamic_table(strategy_name, neighbours_count, strong_numbers_count), "")

        with open(file.name, "r") as f:
            session_data = json.load(f)

        # Load state data
        state.last_spins = session_data.get("spins", [])
        state.spin_history = session_data.get("spin_history", [])
        state.scores = session_data.get("scores", {n: 0 for n in range(37)})
        state.even_money_scores = session_data.get("even_money_scores", {name: 0 for name in EVEN_MONEY.keys()})
        state.dozen_scores = session_data.get("dozen_scores", {name: 0 for name in DOZENS.keys()})
        state.column_scores = session_data.get("column_scores", {name: 0 for name in COLUMNS.keys()})
        state.street_scores = session_data.get("street_scores", {name: 0 for name in STREETS.keys()})
        state.corner_scores = session_data.get("corner_scores", {name: 0 for name in CORNERS.keys()})
        state.six_line_scores = session_data.get("six_line_scores", {name: 0 for name in SIX_LINES.keys()})
        state.split_scores = session_data.get("split_scores", {name: 0 for name in SPLITS.keys()})
        state.side_scores = session_data.get("side_scores", {"Left Side of Zero": 0, "Right Side of Zero": 0})
        state.casino_data = session_data.get("casino_data", {
            "spins_count": 100,
            "hot_numbers": [],  # Load as list
            "cold_numbers": [],  # Load as list
            "even_odd": {"Even": 0.0, "Odd": 0.0},
            "red_black": {"Red": 0.0, "Black": 0.0},
            "low_high": {"Low": 0.0, "High": 0.0},
            "dozens": {"1st Dozen": 0.0, "2nd Dozen": 0.0, "3rd Dozen": 0.0},
            "columns": {"1st Column": 0.0, "2nd Column": 0.0, "3rd Column": 0.0}
        })
        state.use_casino_winners = session_data.get("use_casino_winners", False)

        new_spins = ", ".join(state.last_spins)
        spin_analysis_output = f"Session loaded successfully with {len(state.last_spins)} spins."
        even_money_output = "\n".join([f"{name}: {score}" for name, score in state.even_money_scores.items()])
        dozens_output = "\n".join([f"{name}: {score}" for name, score in state.dozen_scores.items()])
        columns_output = "\n".join([f"{name}: {score}" for name, score in state.column_scores.items()])
        streets_output = "\n".join([f"{name}: {score}" for name, score in state.street_scores.items()])
        corners_output = "\n".join([f"{name}: {score}" for name, score in state.corner_scores.items()])
        six_lines_output = "\n".join([f"{name}: {score}" for name, score in state.six_line_scores.items()])
        splits_output = "\n".join([f"{name}: {score}" for name, score in state.split_scores.items()])
        sides_output = "\n".join([f"{name}: {score}" for name, score in state.side_scores.items()])
        straight_up_df = pd.DataFrame(list(state.scores.items()), columns=["Number", "Score"]).sort_values(by="Score", ascending=False)
        straight_up_html = straight_up_df.to_html(index=False, classes="scrollable-table")
        top_18_df = straight_up_df[straight_up_df["Score"] > 0].head(18)
        top_18_html = top_18_df.to_html(index=False, classes="scrollable-table")
        strongest_numbers_output = ", ".join([str(n) for n, s in straight_up_df.head(3).iterrows() if s["Score"] > 0]) or "No numbers have hit yet."

        return (
            new_spins,
            new_spins,
            spin_analysis_output,
            even_money_output,
            dozens_output,
            columns_output,
            streets_output,
            corners_output,
            six_lines_output,
            splits_output,
            sides_output,
            straight_up_html,
            top_18_html,
            strongest_numbers_output,
            create_dynamic_table(strategy_name, neighbours_count, strong_numbers_count),
            show_strategy_recommendations(strategy_name, neighbours_count, strong_numbers_count)
        )
    except Exception as e:
        print(f"load_session: Error loading session: {str(e)}")
        return ("", "", f"Error loading session: {str(e)}", "", "", "", "", "", "", "", "", "", "", "", create_dynamic_table(strategy_name, neighbours_count, strong_numbers_count), "")

# Function to calculate statistical insights
def statistical_insights():
    if not state.last_spins:
        return "No spins to analyze yet—click some numbers first!"
    total_spins = len(state.last_spins)
    number_freq = {num: state.scores[num] for num in state.scores if state.scores[num] > 0}
    top_numbers = sorted(number_freq.items(), key=lambda x: x[1], reverse=True)[:5]
    output = [f"Total Spins: {total_spins}"]
    output.append("Top 5 Numbers by Hits:")
    for num, hits in top_numbers:
        output.append(f"Number {num}: {hits} hits")
    return "\n".join(output)

# Function to create HTML table (used in analyze_spins)
def create_html_table(df, title):
    if df.empty:
        return f"<h3>{title}</h3><p>No data to display.</p>"
    html = f"<h3>{title}</h3>"
    html += '<table border="1" style="border-collapse: collapse; text-align: center;">'
    html += "<tr>" + "".join(f"<th>{col}</th>" for col in df.columns) + "</tr>"
    for _, row in df.iterrows():
        html += "<tr>" + "".join(f"<td>{val}</td>" for val in row) + "</tr>"
    html += "</table>"
    return html

def create_strongest_numbers_with_neighbours_table():
    straight_up_df = pd.DataFrame(list(state.scores.items()), columns=["Number", "Score"])
    straight_up_df = straight_up_df[straight_up_df["Score"] > 0].sort_values(by="Score", ascending=False)

    if straight_up_df.empty:
        return "<h3>Strongest Numbers with Neighbours</h3><p>No numbers have hit yet.</p>"

    # Create the HTML table
    table_html = '<table border="1" style="border-collapse: collapse; text-align: center; font-family: Arial, sans-serif;">'
    table_html += "<tr><th>Hit</th><th>Left N.</th><th>Right N.</th><th>Score</th></tr>"  # Table header
    for _, row in straight_up_df.iterrows():
        num = str(row["Number"])
        left, right = current_neighbors.get(row["Number"], ("", ""))
        left = str(left) if left is not None else ""
        right = str(right) if right is not None else ""
        score = row["Score"]
        table_html += f"<tr><td>{num}</td><td>{left}</td><td>{right}</td><td>{score}</td></tr>"
    table_html += "</table>"

    return f"<h3>Strongest Numbers with Neighbours</h3>{table_html}"
def highlight_even_money(strategy_name, sorted_sections, top_color, middle_color, lower_color):
    """Highlight even money bets for relevant strategies."""
    if sorted_sections is None:
        return None, None, None, {}
    trending, second, third = None, None, None
    number_highlights = {}
    if strategy_name in ["Best Even Money Bets", "Best Even Money Bets + Top Pick 18 Numbers", 
                         "Best Dozens + Best Even Money Bets + Top Pick 18 Numbers", 
                         "Best Columns + Best Even Money Bets + Top Pick 18 Numbers"]:
        even_money_hits = [item for item in sorted_sections["even_money"] if item[1] > 0]
        if even_money_hits:
            trending = even_money_hits[0][0]
            second = even_money_hits[1][0] if len(even_money_hits) > 1 else None
            third = even_money_hits[2][0] if len(even_money_hits) > 2 else None
    elif strategy_name == "Hot Bet Strategy":
        trending = sorted_sections["even_money"][0][0] if sorted_sections["even_money"] else None
        second = sorted_sections["even_money"][1][0] if len(sorted_sections["even_money"]) > 1 else None
    elif strategy_name == "Cold Bet Strategy":
        sorted_even_money = sorted(state.even_money_scores.items(), key=lambda x: x[1])
        trending = sorted_even_money[0][0] if sorted_even_money else None
        second = sorted_even_money[1][0] if len(sorted_even_money) > 1 else None
    elif strategy_name in ["3-8-6 Rising Martingale", "Fibonacci To Fortune"]:
        # For Fibonacci To Fortune, highlight only the top even money bet
        trending = sorted_sections["even_money"][0][0] if sorted_sections["even_money"] else None
    return trending, second, third, number_highlights

def highlight_dozens(strategy_name, sorted_sections, top_color, middle_color, lower_color):
    """Highlight dozens for relevant strategies."""
    if sorted_sections is None:
        return None, None, {}
    trending, second = None, None
    number_highlights = {}
    if strategy_name in ["Best Dozens", "Best Dozens + Top Pick 18 Numbers", 
                         "Best Dozens + Best Even Money Bets + Top Pick 18 Numbers", 
                         "Best Dozens + Best Streets"]:
        dozens_hits = [item for item in sorted_sections["dozens"] if item[1] > 0]
        if dozens_hits:
            trending = dozens_hits[0][0]
            second = dozens_hits[1][0] if len(dozens_hits) > 1 else None
    elif strategy_name == "Hot Bet Strategy":
        trending = sorted_sections["dozens"][0][0] if sorted_sections["dozens"] else None
        second = sorted_sections["dozens"][1][0] if len(sorted_sections["dozens"]) > 1 else None
    elif strategy_name == "Cold Bet Strategy":
        sorted_dozens = sorted(state.dozen_scores.items(), key=lambda x: x[1])
        trending = sorted_dozens[0][0] if sorted_dozens else None
        second = sorted_dozens[1][0] if len(sorted_dozens) > 1 else None
    elif strategy_name in ["Fibonacci Strategy", "Fibonacci To Fortune"]:
        # For Fibonacci To Fortune, always highlight the top two dozens
        trending = sorted_sections["dozens"][0][0] if sorted_sections["dozens"] else None
        second = sorted_sections["dozens"][1][0] if len(sorted_sections["dozens"]) > 1 else None
    elif strategy_name == "1 Dozen +1 Column Strategy":
        trending = sorted_sections["dozens"][0][0] if sorted_sections["dozens"] and sorted_sections["dozens"][0][1] > 0 else None
    elif strategy_name == "Romanowksy Missing Dozen":
        trending = sorted_sections["dozens"][0][0] if sorted_sections["dozens"] and sorted_sections["dozens"][0][1] > 0 else None
        second = sorted_sections["dozens"][1][0] if len(sorted_sections["dozens"]) > 1 and sorted_sections["dozens"][1][1] > 0 else None
        weakest_dozen = min(state.dozen_scores.items(), key=lambda x: x[1], default=("1st Dozen", 0))[0]
        straight_up_df = pd.DataFrame(list(state.scores.items()), columns=["Number", "Score"])
        straight_up_df = straight_up_df[straight_up_df["Score"] > 0].sort_values(by="Score", ascending=False)
        weak_numbers = [row["Number"] for _, row in straight_up_df.iterrows() if row["Number"] in DOZENS[weakest_dozen]][:8]
        for num in weak_numbers:
            number_highlights[str(num)] = top_color
    return trending, second, number_highlights

def highlight_columns(strategy_name, sorted_sections, top_color, middle_color, lower_color):
    """Highlight columns for relevant strategies."""
    if sorted_sections is None:
        return None, None, {}
    trending, second = None, None
    number_highlights = {}
    if strategy_name in ["Best Columns", "Best Columns + Top Pick 18 Numbers", 
                         "Best Columns + Best Even Money Bets + Top Pick 18 Numbers", 
                         "Best Columns + Best Streets"]:
        columns_hits = [item for item in sorted_sections["columns"] if item[1] > 0]
        if columns_hits:
            trending = columns_hits[0][0]
            second = columns_hits[1][0] if len(columns_hits) > 1 else None
    elif strategy_name == "Hot Bet Strategy":
        trending = sorted_sections["columns"][0][0] if sorted_sections["columns"] else None
        second = sorted_sections["columns"][1][0] if len(sorted_sections["columns"]) > 1 else None
    elif strategy_name == "Cold Bet Strategy":
        sorted_columns = sorted(state.column_scores.items(), key=lambda x: x[1])
        trending = sorted_columns[0][0] if sorted_columns else None
        second = sorted_columns[1][0] if len(sorted_columns) > 1 else None
    elif strategy_name in ["Fibonacci Strategy", "Fibonacci To Fortune"]:
        # For Fibonacci To Fortune, always highlight the top two columns
        trending = sorted_sections["columns"][0][0] if sorted_sections["columns"] else None
        second = sorted_sections["columns"][1][0] if len(sorted_sections["columns"]) > 1 else None
    elif strategy_name == "1 Dozen +1 Column Strategy":
        trending = sorted_sections["columns"][0][0] if sorted_sections["columns"] and sorted_sections["columns"][0][1] > 0 else None
    return trending, second, number_highlights

def highlight_numbers(strategy_name, sorted_sections, top_color, middle_color, lower_color):
    """Highlight straight-up numbers for relevant strategies."""
    if sorted_sections is None:
        return {}
    number_highlights = {}
    straight_up_df = pd.DataFrame(list(state.scores.items()), columns=["Number", "Score"])
    straight_up_df = straight_up_df[straight_up_df["Score"] > 0].sort_values(by="Score", ascending=False)
    
    if strategy_name in ["Top Pick 18 Numbers without Neighbours", 
                         "Best Even Money Bets + Top Pick 18 Numbers", 
                         "Best Dozens + Top Pick 18 Numbers", 
                         "Best Columns + Top Pick 18 Numbers", 
                         "Best Dozens + Best Even Money Bets + Top Pick 18 Numbers", 
                         "Best Columns + Best Even Money Bets + Top Pick 18 Numbers"]:
        if len(straight_up_df) >= 18:
            top_18_numbers = straight_up_df["Number"].head(18).tolist()
            for i, num in enumerate(top_18_numbers):
                color = top_color if i < 6 else (middle_color if i < 12 else lower_color)
                number_highlights[str(num)] = color
    elif strategy_name == "Top Numbers with Neighbours (Tiered)":
        num_to_take = min(8, len(straight_up_df))
        top_numbers = set(straight_up_df["Number"].head(num_to_take).tolist())
        number_groups = []
        for num in top_numbers:
            left, right = current_neighbors.get(num, (None, None))
            group = [num]
            if left is not None:
                group.append(left)
            if right is not None:
                group.append(right)
            number_groups.append((state.scores[num], group))
        number_groups.sort(key=lambda x: x[0], reverse=True)
        ordered_numbers = []
        for _, group in number_groups:
            ordered_numbers.extend(group)
        ordered_numbers = ordered_numbers[:24]
        for i, num in enumerate(ordered_numbers):
            color = top_color if i < 8 else (middle_color if i < 16 else lower_color)
            number_highlights[str(num)] = color
    return number_highlights

def highlight_other_bets(strategy_name, sorted_sections, top_color, middle_color, lower_color):
    """Highlight streets, corners, splits, and double streets for relevant strategies."""
    if sorted_sections is None:
        return {}
    number_highlights = {}
    
    if strategy_name == "Hot Bet Strategy":
        for i, (street_name, _) in enumerate(sorted_sections["streets"][:9]):
            numbers = STREETS[street_name]
            color = top_color if i < 3 else (middle_color if 3 <= i < 6 else lower_color)
            for num in numbers:
                number_highlights[str(num)] = color
        for i, (corner_name, _) in enumerate(sorted_sections["corners"][:9]):
            numbers = CORNERS[corner_name]
            color = top_color if i < 3 else (middle_color if 3 <= i < 6 else lower_color)
            for num in numbers:
                number_highlights[str(num)] = color
        for i, (split_name, _) in enumerate(sorted_sections["splits"][:9]):
            numbers = SPLITS[split_name]
            color = top_color if i < 3 else (middle_color if 3 <= i < 6 else lower_color)
            for num in numbers:
                number_highlights[str(num)] = color
    elif strategy_name == "Cold Bet Strategy":
        sorted_streets = sorted(state.street_scores.items(), key=lambda x: x[1])
        sorted_corners = sorted(state.corner_scores.items(), key=lambda x: x[1])
        sorted_splits = sorted(state.split_scores.items(), key=lambda x: x[1])
        for i, (street_name, _) in enumerate(sorted_streets[:9]):
            numbers = STREETS[street_name]
            color = top_color if i < 3 else (middle_color if 3 <= i < 6 else lower_color)
            for num in numbers:
                number_highlights[str(num)] = color
        for i, (corner_name, _) in enumerate(sorted_corners[:9]):
            numbers = CORNERS[corner_name]
            color = top_color if i < 3 else (middle_color if 3 <= i < 6 else lower_color)
            for num in numbers:
                number_highlights[str(num)] = color
        for i, (split_name, _) in enumerate(sorted_splits[:9]):
            numbers = SPLITS[split_name]
            color = top_color if i < 3 else (middle_color if 3 <= i < 6 else lower_color)
            for num in numbers:
                number_highlights[str(num)] = color
    elif strategy_name == "Best Streets":
        for i, (street_name, _) in enumerate(sorted_sections["streets"][:9]):
            numbers = STREETS[street_name]
            color = top_color if i < 3 else (middle_color if 3 <= i < 6 else lower_color)
            for num in numbers:
                number_highlights[str(num)] = color
    elif strategy_name in ["Best Dozens + Best Streets", "Best Columns + Best Streets"]:
        for i, (street_name, _) in enumerate(sorted_sections["streets"][:9]):
            numbers = STREETS[street_name]
            color = top_color if i < 3 else (middle_color if 3 <= i < 6 else lower_color)
            for num in numbers:
                number_highlights[str(num)] = color
    elif strategy_name == "Best Double Streets":
        for i, (six_line_name, _) in enumerate(sorted_sections["six_lines"][:9]):
            numbers = SIX_LINES[six_line_name]
            color = top_color if i < 3 else (middle_color if 3 <= i < 6 else lower_color)
            for num in numbers:
                number_highlights[str(num)] = color
    elif strategy_name == "Best Corners":
        for i, (corner_name, _) in enumerate(sorted_sections["corners"][:9]):
            numbers = CORNERS[corner_name]
            color = top_color if i < 3 else (middle_color if 3 <= i < 6 else lower_color)
            for num in numbers:
                number_highlights[str(num)] = color
    elif strategy_name == "Best Splits":
        for i, (split_name, _) in enumerate(sorted_sections["splits"][:9]):
            numbers = SPLITS[split_name]
            color = top_color if i < 3 else (middle_color if 3 <= i < 6 else lower_color)
            for num in numbers:
                number_highlights[str(num)] = color
    elif strategy_name == "Non-Overlapping Double Street Strategy":
        non_overlapping_sets = [
            ["1ST D.STREET – 1, 4", "3RD D.STREET – 7, 10", "5TH D.STREET – 13, 16", "7TH D.STREET – 19, 22", "9TH D.STREET – 25, 28"],
            ["2ND D.STREET – 4, 7", "4TH D.STREET – 10, 13", "6TH D.STREET – 16, 19", "8TH D.STREET – 22, 25", "10TH D.STREET – 28, 31"]
        ]
        set_scores = []
        for idx, non_overlapping_set in enumerate(non_overlapping_sets):
            total_score = sum(state.six_line_scores.get(name, 0) for name in non_overlapping_set)
            set_scores.append((idx, total_score, non_overlapping_set))
        best_set = max(set_scores, key=lambda x: x[1], default=(0, 0, non_overlapping_sets[0]))
        sorted_best_set = sorted(best_set[2], key=lambda name: state.six_line_scores.get(name, 0), reverse=True)[:9]
        for i, double_street_name in enumerate(sorted_best_set):
            numbers = SIX_LINES[double_street_name]
            color = top_color if i < 3 else (middle_color if 3 <= i < 6 else lower_color)
            for num in numbers:
                number_highlights[str(num)] = color
    elif strategy_name == "Non-Overlapping Corner Strategy":
        sorted_corners = sorted(state.corner_scores.items(), key=lambda x: x[1], reverse=True)
        selected_corners = []
        selected_numbers = set()
        for corner_name, _ in sorted_corners:
            if len(selected_corners) >= 9:
                break
            corner_numbers = set(CORNERS[corner_name])
            if not corner_numbers & selected_numbers:
                selected_corners.append(corner_name)
                selected_numbers.update(corner_numbers)
        for i, corner_name in enumerate(selected_corners):
            numbers = CORNERS[corner_name]
            color = top_color if i < 3 else (middle_color if 3 <= i < 6 else lower_color)
            for num in numbers:
                number_highlights[str(num)] = color
    elif strategy_name == "3-8-6 Rising Martingale":
        top_streets = sorted_sections["streets"][:8]
        for i, (street_name, _) in enumerate(top_streets):
            numbers = STREETS[street_name]
            color = top_color if i < 3 else (middle_color if 3 <= i < 6 else lower_color)
            for num in numbers:
                number_highlights[str(num)] = color
    elif strategy_name == "Fibonacci To Fortune":
        # Highlight the best double street in the weakest dozen, excluding numbers from the top two dozens
        sorted_dozens = sorted(state.dozen_scores.items(), key=lambda x: x[1], reverse=True)
        weakest_dozen = min(state.dozen_scores.items(), key=lambda x: x[1], default=("1st Dozen", 0))[0]
        top_two_dozens = [item[0] for item in sorted_dozens[:2]]
        top_two_dozen_numbers = set()
        for dozen_name in top_two_dozens:
            top_two_dozen_numbers.update(DOZENS[dozen_name])
        double_streets_in_weakest = [
            (name, state.six_line_scores.get(name, 0))
            for name, numbers in SIX_LINES.items()
            if set(numbers).issubset(DOZENS[weakest_dozen]) and not set(numbers).intersection(top_two_dozen_numbers)
        ]
        if double_streets_in_weakest:
            top_double_street = max(double_streets_in_weakest, key=lambda x: x[1])[0]
            for num in SIX_LINES[top_double_street]:
                number_highlights[str(num)] = top_color
    return number_highlights

def highlight_neighbors(strategy_name, sorted_sections, neighbours_count, strong_numbers_count, top_color, middle_color):
    """Highlight neighbors for the Neighbours of Strong Number strategy."""
    if sorted_sections is None:
        return {}
    number_highlights = {}
    if strategy_name == "Neighbours of Strong Number":
        sorted_numbers = sorted(state.scores.items(), key=lambda x: (-x[1], x[0]))
        numbers_hits = [item for item in sorted_numbers if item[1] > 0]
        if numbers_hits:
            strong_numbers_count = min(strong_numbers_count, len(numbers_hits))
            top_numbers = set(item[0] for item in numbers_hits[:strong_numbers_count])
            neighbors_set = set()
            for strong_number in top_numbers:
                current_number = strong_number
                for _ in range(neighbours_count):
                    left, _ = current_neighbors.get(current_number, (None, None))
                    if left is not None:
                        neighbors_set.add(left)
                        current_number = left
                    else:
                        break
                current_number = strong_number
                for _ in range(neighbours_count):
                    _, right = current_neighbors.get(current_number, (None, None))
                    if right is not None:
                        neighbors_set.add(right)
                        current_number = right
                    else:
                        break
            neighbors_set = neighbors_set - top_numbers
            for num in top_numbers:
                number_highlights[str(num)] = top_color
            for num in neighbors_set:
                number_highlights[str(num)] = middle_color
    return number_highlights
# Function to create the dynamic roulette table with highlighted trending sections
def calculate_trending_sections():
    """Calculate trending sections based on current scores."""
    if not any(state.scores.values()) and not any(state.even_money_scores.values()):
        return None  # Indicates no data to process

    return {
        "even_money": sorted(state.even_money_scores.items(), key=lambda x: x[1], reverse=True),
        "dozens": sorted(state.dozen_scores.items(), key=lambda x: x[1], reverse=True),
        "columns": sorted(state.column_scores.items(), key=lambda x: x[1], reverse=True),
        "streets": sorted(state.street_scores.items(), key=lambda x: x[1], reverse=True),
        "six_lines": sorted(state.six_line_scores.items(), key=lambda x: x[1], reverse=True),
        "corners": sorted(state.corner_scores.items(), key=lambda x: x[1], reverse=True),
        "splits": sorted(state.split_scores.items(), key=lambda x: x[1], reverse=True)
    }

# Line 1: Start of apply_strategy_highlights function (updated)
# Line 1: Start of apply_strategy_highlights function (updated)
# Line 1: Start of apply_strategy_highlights function (updated with neighbor highlights)
def apply_strategy_highlights(strategy_name, neighbours_count, strong_numbers_count, sorted_sections, top_color=None, middle_color=None, lower_color=None, suggestions=None):
    """Apply highlights based on the selected strategy with custom colors, passing suggestions for outside bets."""
    if sorted_sections is None:
        return None, None, None, None, None, None, None, {}, "white", "white", "white", None

    # Set default colors unless overridden
    if strategy_name == "Cold Bet Strategy":
        top_color = "#D3D3D3"  # Light Gray (Cold Top)
        middle_color = "#DDA0DD"  # Plum (Cold Middle)
        lower_color = "#E0FFFF"  # Light Cyan (Cold Lower)
    else:
        top_color = top_color if top_color else "rgba(255, 255, 0, 0.5)"  # Yellow
        middle_color = middle_color if middle_color else "rgba(0, 255, 255, 0.5)"  # Cyan
        lower_color = lower_color if lower_color else "rgba(0, 255, 0, 0.5)"  # Green

    # Initialize highlight variables
    trending_even_money, second_even_money, third_even_money = None, None, None
    trending_dozen, second_dozen = None, None
    trending_column, second_column = None, None
    number_highlights = {}

    # Apply highlights based on strategy
    if strategy_name and strategy_name in STRATEGIES:
        strategy_info = STRATEGIES[strategy_name]
        if strategy_name == "Neighbours of Strong Number":
            result = strategy_info["function"](neighbours_count, strong_numbers_count)
            # Handle the tuple return value
            if isinstance(result, tuple) and len(result) == 2:
                recommendations, strategy_suggestions = result
                suggestions = suggestions if suggestions is not None else strategy_suggestions
            else:
                # Fallback in case the function doesn't return the expected tuple
                recommendations = result
                suggestions = None
        else:
            # Other strategies return a single string
            recommendations = strategy_info["function"]()
            suggestions = None
        
        # Delegate to helper functions
        em_trending, em_second, em_third, em_highlights = highlight_even_money(strategy_name, sorted_sections, top_color, middle_color, lower_color)
        dz_trending, dz_second, dz_highlights = highlight_dozens(strategy_name, sorted_sections, top_color, middle_color, lower_color)
        col_trending, col_second, col_highlights = highlight_columns(strategy_name, sorted_sections, top_color, middle_color, lower_color)
        num_highlights = highlight_numbers(strategy_name, sorted_sections, top_color, middle_color, lower_color)
        neighbor_highlights = highlight_neighbors(strategy_name, sorted_sections, neighbours_count, strong_numbers_count, top_color, middle_color)
        other_highlights = highlight_other_bets(strategy_name, sorted_sections, top_color, middle_color, lower_color)

        # Combine highlights
        trending_even_money = em_trending
        second_even_money = em_second
        third_even_money = em_third
        trending_dozen = dz_trending
        second_dozen = dz_second
        trending_column = col_trending
        second_column = col_second
        number_highlights.update(em_highlights)
        number_highlights.update(dz_highlights)
        number_highlights.update(col_highlights)
        number_highlights.update(num_highlights)
        number_highlights.update(neighbor_highlights)
        number_highlights.update(other_highlights)

    # Dozen Tracker Logic (When No Strategy is Selected)
    if strategy_name == "None":
        recent_spins = state.last_spins[-neighbours_count:] if len(state.last_spins) >= neighbours_count else state.last_spins
        dozen_counts = {"1st Dozen": 0, "2nd Dozen": 0, "3rd Dozen": 0}
        for spin in recent_spins:
            spin_value = int(spin)
            if spin_value != 0:
                for name, numbers in DOZENS.items():
                    if spin_value in numbers:
                        dozen_counts[name] += 1
                        break
        sorted_dozens = sorted(dozen_counts.items(), key=lambda x: x[1], reverse=True)
        if sorted_dozens[0][1] > 0:
            trending_dozen = sorted_dozens[0][0]
        if sorted_dozens[1][1] > 0:
            second_dozen = sorted_dozens[1][0]

    return trending_even_money, second_even_money, third_even_money, trending_dozen, second_dozen, trending_column, second_column, number_highlights, top_color, middle_color, lower_color, suggestions

# Line 1: Start of render_dynamic_table_html function (updated)
def render_dynamic_table_html(trending_even_money, second_even_money, third_even_money, trending_dozen, second_dozen, trending_column, second_column, number_highlights, top_color, middle_color, lower_color, suggestions=None, hot_numbers=None, scores=None):
    """Generate HTML for the dynamic roulette table with improved visual clarity, using suggestions for highlighting outside bets."""
    if all(v is None for v in [trending_even_money, second_even_money, third_even_money, trending_dozen, second_dozen, trending_column, second_column]) and not number_highlights and not suggestions:
        return "<p>Please analyze some spins first to see highlights on the dynamic table.</p>"

    # Define casino winners if highlighting is enabled, only for non-zero data
    casino_winners = {"hot_numbers": set(), "cold_numbers": set(), "even_money": set(), "dozens": set(), "columns": set()}
    if state.use_casino_winners:
        casino_winners["hot_numbers"] = set(state.casino_data["hot_numbers"].keys())
        casino_winners["cold_numbers"] = set(state.casino_data["cold_numbers"].keys())
        if any(state.casino_data["even_odd"].values()):
            casino_winners["even_money"].add(max(state.casino_data["even_odd"], key=state.casino_data["even_odd"].get))
        if any(state.casino_data["red_black"].values()):
            casino_winners["even_money"].add(max(state.casino_data["red_black"], key=state.casino_data["red_black"].get))
        if any(state.casino_data["low_high"].values()):
            casino_winners["even_money"].add(max(state.casino_data["low_high"], key=state.casino_data["low_high"].get))
        if any(state.casino_data["dozens"].values()):
            casino_winners["dozens"] = {max(state.casino_data["dozens"], key=state.casino_data["dozens"].get)}
        if any(state.casino_data["columns"].values()):
            casino_winners["columns"] = {max(state.casino_data["columns"], key=state.casino_data["columns"].get)}
        print(f"Casino Winners Set: Hot={casino_winners['hot_numbers']}, Cold={casino_winners['cold_numbers']}, Even Money={casino_winners['even_money']}, Dozens={casino_winners['dozens']}, Columns={casino_winners['columns']}")

    # Initialize highlights for outside bets using suggestions (for Neighbours of Strong Number strategy)
    suggestion_highlights = {}
    if suggestions:
        # Parse suggestions to extract recommendations
        best_even_money = None
        best_bet = None
        play_two_first = None
        play_two_second = None

        for key, value in suggestions.items():
            if key == "best_even_money" and "(Tied with" not in value:
                # Extract the even money bet (e.g., "Even: 5" -> "Even")
                best_even_money = value.split(":")[0].strip()
            elif key == "best_bet" and "(Tied with" not in value:
                # Extract the best bet (e.g., "2nd Column: 6" -> "2nd Column")
                best_bet = value.split(":")[0].strip()
            elif key == "play_two" and "(Tied with" not in value:
                # Extract the two options (e.g., "Play Two Columns: 2nd Column (6) and 1st Column (2)")
                parts = value.split(":", 1)[1].split(" and ")
                play_two_first = parts[0].split("(")[0].strip()  # e.g., "2nd Column"
                play_two_second = parts[1].split("(")[0].strip()  # e.g., "1st Column"

        # Apply highlights based on suggestions (yellow for top tier, green for second in Play Two)
        if best_even_money:
            suggestion_highlights[best_even_money] = top_color  # Yellow for Best Even Money Bet
        if best_bet:
            suggestion_highlights[best_bet] = top_color  # Yellow for Best Bet
        if play_two_first and play_two_second:
            # Ensure the first option in Play Two matches the Best Bet (if present) and gets yellow
            if best_bet and play_two_first == best_bet:
                suggestion_highlights[play_two_first] = top_color  # Already set to yellow
            else:
                suggestion_highlights[play_two_first] = top_color  # Yellow if not already set
            suggestion_highlights[play_two_second] = lower_color  # Green for second option

    table_layout = [
        ["", "3", "6", "9", "12", "15", "18", "21", "24", "27", "30", "33", "36"],
        ["0", "2", "5", "8", "11", "14", "17", "20", "23", "26", "29", "32", "35"],
        ["", "1", "4", "7", "10", "13", "16", "19", "22", "25", "28", "31", "34"]
    ]

    html = '<table class="large-table dynamic-roulette-table" border="1" style="border-collapse: collapse; text-align: center; font-size: 14px; font-family: Arial, sans-serif; border-color: black; table-layout: fixed; width: 100%; max-width: 600px;">'
    html += '<colgroup>'
    html += '<col style="width: 40px;">'
    for _ in range(12):
        html += '<col style="width: 40px;">'
    html += '<col style="width: 80px;">'
    html += '</colgroup>'

    # Ensure hot_numbers is a set for consistent comparison
    hot_numbers = set(hot_numbers) if hot_numbers else set()
    # Debug scores to verify hit counts
    scores = scores if scores is not None else {}
    print(f"render_dynamic_table_html: Hot numbers={hot_numbers}, Scores={dict(scores)}")

    for row_idx, row in enumerate(table_layout):
        html += "<tr>"
        for num in row:
            if num == "":
                html += '<td style="height: 40px; border-color: black; box-sizing: border-box;"></td>'
            else:
                base_color = colors.get(num, "black")
                highlight_color = number_highlights.get(num, base_color)
                if num in casino_winners["hot_numbers"]:
                    border_style = "3px solid #FFD700"  # Gold, solid for consistent glow
                elif num in casino_winners["cold_numbers"]:
                    border_style = "3px solid #C0C0C0"  # Silver, solid for consistent glow
                else:
                    border_style = "3px solid black"
                text_style = "color: white; font-weight: bold; text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);"
                cell_class = "hot-number has-tooltip" if num in hot_numbers else "has-tooltip"
                hit_count = scores.get(num, scores.get(int(num), 0) if num.isdigit() else 0)
                tooltip = f"Hit {hit_count} times"
                html += f'<td style="height: 40px; background-color: {highlight_color}; {text_style} border: {border_style}; padding: 0; vertical-align: middle; box-sizing: border-box; text-align: center;" class="{cell_class}" data-tooltip="{tooltip}">{num}</td>'
        if row_idx == 0:
            bg_color = suggestion_highlights.get("3rd Column", top_color if trending_column == "3rd Column" else (middle_color if second_column == "3rd Column" else "white"))
            border_style = "3px dashed #FFD700" if "3rd Column" in casino_winners["columns"] else "1px solid black"
            tier_class = "top-tier" if bg_color == top_color else "middle-tier" if bg_color == middle_color else "lower-tier" if bg_color == lower_color else ""
            # Compute column score and progress bar
            col_score = state.column_scores.get("3rd Column", 0)
            max_col_score = max(state.column_scores.values(), default=1) or 1  # Avoid division by zero
            fill_percentage = (col_score / max_col_score) * 100
            html += f'<td style="background-color: {bg_color}; border: {border_style}; padding: 0; font-size: 10px; vertical-align: middle; box-sizing: border-box; height: 40px; text-align: center;" class="{tier_class}"><span>3rd Column</span><div class="progress-bar"><div class="progress-fill {tier_class}" style="width: {fill_percentage}%;"></div></div></td>'
        elif row_idx == 1:
            bg_color = suggestion_highlights.get("2nd Column", top_color if trending_column == "2nd Column" else (middle_color if second_column == "2nd Column" else "white"))
            border_style = "3px dashed #FFD700" if "2nd Column" in casino_winners["columns"] else "1px solid black"
            tier_class = "top-tier" if bg_color == top_color else "middle-tier" if bg_color == middle_color else "lower-tier" if bg_color == lower_color else ""
            col_score = state.column_scores.get("2nd Column", 0)
            max_col_score = max(state.column_scores.values(), default=1) or 1
            fill_percentage = (col_score / max_col_score) * 100
            html += f'<td style="background-color: {bg_color}; border: {border_style}; padding: 0; font-size: 10px; vertical-align: middle; box-sizing: border-box; height: 40px; text-align: center;" class="{tier_class}"><span>2nd Column</span><div class="progress-bar"><div class="progress-fill {tier_class}" style="width: {fill_percentage}%;"></div></div></td>'
        elif row_idx == 2:
            bg_color = suggestion_highlights.get("1st Column", top_color if trending_column == "1st Column" else (middle_color if second_column == "1st Column" else "white"))
            border_style = "3px dashed #FFD700" if "1st Column" in casino_winners["columns"] else "1px solid black"
            tier_class = "top-tier" if bg_color == top_color else "middle-tier" if bg_color == middle_color else "lower-tier" if bg_color == lower_color else ""
            col_score = state.column_scores.get("1st Column", 0)
            max_col_score = max(state.column_scores.values(), default=1) or 1
            fill_percentage = (col_score / max_col_score) * 100
            html += f'<td style="background-color: {bg_color}; border: {border_style}; padding: 0; font-size: 10px; vertical-align: middle; box-sizing: border-box; height: 40px; text-align: center;" class="{tier_class}"><span>1st Column</span><div class="progress-bar"><div class="progress-fill {tier_class}" style="width: {fill_percentage}%;"></div></div></td>'
        html += "</tr>"

    html += "<tr>"
    html += '<td style="height: 40px; border-color: black; box-sizing: border-box;"></td>'
    bg_color = suggestion_highlights.get("Low", top_color if trending_even_money == "Low" else (middle_color if second_even_money == "Low" else (lower_color if third_even_money == "Low" else "white")))
    border_style = "3px dashed #FFD700" if "Low" in casino_winners["even_money"] else "1px solid black"
    tier_class = "top-tier" if bg_color == top_color else "middle-tier" if bg_color == middle_color else "lower-tier" if bg_color == lower_color else ""
    low_score = state.even_money_scores.get("Low", 0)
    max_even_money_score = max(state.even_money_scores.values(), default=1) or 1
    fill_percentage = (low_score / max_even_money_score) * 100
    html += f'<td colspan="6" style="background-color: {bg_color}; color: black; border: {border_style}; padding: 0; font-size: 10px; vertical-align: middle; box-sizing: border-box; height: 40px; text-align: center;" class="{tier_class}"><span>Low (1 to 18)</span><div class="progress-bar"><div class="progress-fill {tier_class}" style="width: {fill_percentage}%;"></div></div></td>'
    bg_color = suggestion_highlights.get("High", top_color if trending_even_money == "High" else (middle_color if second_even_money == "High" else (lower_color if third_even_money == "High" else "white")))
    border_style = "3px dashed #FFD700" if "High" in casino_winners["even_money"] else "1px solid black"
    tier_class = "top-tier" if bg_color == top_color else "middle-tier" if bg_color == middle_color else "lower-tier" if bg_color == lower_color else ""
    high_score = state.even_money_scores.get("High", 0)
    fill_percentage = (high_score / max_even_money_score) * 100
    html += f'<td colspan="6" style="background-color: {bg_color}; color: black; border: {border_style}; padding: 0; font-size: 10px; vertical-align: middle; box-sizing: border-box; height: 40px; text-align: center;" class="{tier_class}"><span>High (19 to 36)</span><div class="progress-bar"><div class="progress-fill {tier_class}" style="width: {fill_percentage}%;"></div></div></td>'
    html += '<td style="border-color: black; box-sizing: border-box;"></td>'
    html += "</tr>"

    html += "<tr>"
    html += '<td style="height: 40px; border-color: black; box-sizing: border-box;"></td>'
    bg_color = suggestion_highlights.get("1st Dozen", top_color if trending_dozen == "1st Dozen" else (middle_color if second_dozen == "1st Dozen" else "white"))
    border_style = "3px dashed #FFD700" if "1st Dozen" in casino_winners["dozens"] else "1px solid black"
    tier_class = "top-tier" if bg_color == top_color else "middle-tier" if bg_color == middle_color else "lower-tier" if bg_color == lower_color else ""
    dozen_score = state.dozen_scores.get("1st Dozen", 0)
    max_dozen_score = max(state.dozen_scores.values(), default=1) or 1
    fill_percentage = (dozen_score / max_dozen_score) * 100
    html += f'<td colspan="4" style="background-color: {bg_color}; color: black; border: {border_style}; padding: 0; font-size: 10px; vertical-align: middle; box-sizing: border-box; height: 40px; text-align: center;" class="{tier_class}"><span>1st Dozen</span><div class="progress-bar"><div class="progress-fill {tier_class}" style="width: {fill_percentage}%;"></div></div></td>'
    bg_color = suggestion_highlights.get("2nd Dozen", top_color if trending_dozen == "2nd Dozen" else (middle_color if second_dozen == "2nd Dozen" else "white"))
    border_style = "3px dashed #FFD700" if "2nd Dozen" in casino_winners["dozens"] else "1px solid black"
    tier_class = "top-tier" if bg_color == top_color else "middle-tier" if bg_color == middle_color else "lower-tier" if bg_color == lower_color else ""
    dozen_score = state.dozen_scores.get("2nd Dozen", 0)
    fill_percentage = (dozen_score / max_dozen_score) * 100
    html += f'<td colspan="4" style="background-color: {bg_color}; color: black; border: {border_style}; padding: 0; font-size: 10px; vertical-align: middle; box-sizing: border-box; height: 40px; text-align: center;" class="{tier_class}"><span>2nd Dozen</span><div class="progress-bar"><div class="progress-fill {tier_class}" style="width: {fill_percentage}%;"></div></div></td>'
    bg_color = suggestion_highlights.get("3rd Dozen", top_color if trending_dozen == "3rd Dozen" else (middle_color if second_dozen == "3rd Dozen" else "white"))
    border_style = "3px dashed #FFD700" if "3rd Dozen" in casino_winners["dozens"] else "1px solid black"
    tier_class = "top-tier" if bg_color == top_color else "middle-tier" if bg_color == middle_color else "lower-tier" if bg_color == lower_color else ""
    dozen_score = state.dozen_scores.get("3rd Dozen", 0)
    fill_percentage = (dozen_score / max_dozen_score) * 100
    html += f'<td colspan="4" style="background-color: {bg_color}; color: black; border: {border_style}; padding: 0; font-size: 10px; vertical-align: middle; box-sizing: border-box; height: 40px; text-align: center;" class="{tier_class}"><span>3rd Dozen</span><div class="progress-bar"><div class="progress-fill {tier_class}" style="width: {fill_percentage}%;"></div></div></td>'
    html += '<td style="border-color: black; box-sizing: border-box;"></td>'
    html += "</tr>"

    html += "<tr>"
    html += '<td style="height: 40px; border-color: black; box-sizing: border-box;"></td>'
    html += f'<td colspan="4" style="border-color: black; box-sizing: border-box;"></td>'
    bg_color = suggestion_highlights.get("Odd", top_color if trending_even_money == "Odd" else (middle_color if second_even_money == "Odd" else (lower_color if third_even_money == "Odd" else "white")))
    border_style = "3px dashed #FFD700" if "Odd" in casino_winners["even_money"] else "1px solid black"
    tier_class = "top-tier" if bg_color == top_color else "middle-tier" if bg_color == middle_color else "lower-tier" if bg_color == lower_color else ""
    odd_score = state.even_money_scores.get("Odd", 0)
    max_even_money_score = max(state.even_money_scores.values(), default=1) or 1
    fill_percentage = (odd_score / max_even_money_score) * 100
    html += f'<td style="background-color: {bg_color}; color: black; border: {border_style}; padding: 0; font-size: 10px; vertical-align: middle; box-sizing: border-box; height: 40px; text-align: center;" class="{tier_class}"><span>ODD</span><div class="progress-bar"><div class="progress-fill {tier_class}" style="width: {fill_percentage}%;"></div></div></td>'
    bg_color = suggestion_highlights.get("Red", top_color if trending_even_money == "Red" else (middle_color if second_even_money == "Red" else (lower_color if third_even_money == "Red" else "white")))
    border_style = "3px dashed #FFD700" if "Red" in casino_winners["even_money"] else "1px solid black"
    tier_class = "top-tier" if bg_color == top_color else "middle-tier" if bg_color == middle_color else "lower-tier" if bg_color == lower_color else ""
    red_score = state.even_money_scores.get("Red", 0)
    fill_percentage = (red_score / max_even_money_score) * 100
    html += f'<td style="background-color: {bg_color}; color: black; border: {border_style}; padding: 0; font-size: 10px; vertical-align: middle; box-sizing: border-box; height: 40px; text-align: center;" class="{tier_class}"><span>RED</span><div class="progress-bar"><div class="progress-fill {tier_class}" style="width: {fill_percentage}%;"></div></div></td>'
    bg_color = suggestion_highlights.get("Black", top_color if trending_even_money == "Black" else (middle_color if second_even_money == "Black" else (lower_color if third_even_money == "Black" else "white")))
    border_style = "3px dashed #FFD700" if "Black" in casino_winners["even_money"] else "1px solid black"
    tier_class = "top-tier" if bg_color == top_color else "middle-tier" if bg_color == middle_color else "lower-tier" if bg_color == lower_color else ""
    black_score = state.even_money_scores.get("Black", 0)
    fill_percentage = (black_score / max_even_money_score) * 100
    html += f'<td style="background-color: {bg_color}; color: black; border: {border_style}; padding: 0; font-size: 10px; vertical-align: middle; box-sizing: border-box; height: 40px; text-align: center;" class="{tier_class}"><span>BLACK</span><div class="progress-bar"><div class="progress-fill {tier_class}" style="width: {fill_percentage}%;"></div></div></td>'
    bg_color = suggestion_highlights.get("Even", top_color if trending_even_money == "Even" else (middle_color if second_even_money == "Even" else (lower_color if third_even_money == "Even" else "white")))
    border_style = "3px dashed #FFD700" if "Even" in casino_winners["even_money"] else "1px solid black"
    tier_class = "top-tier" if bg_color == top_color else "middle-tier" if bg_color == middle_color else "lower-tier" if bg_color == lower_color else ""
    even_score = state.even_money_scores.get("Even", 0)
    fill_percentage = (even_score / max_even_money_score) * 100
    html += f'<td style="background-color: {bg_color}; color: black; border: {border_style}; padding: 0; font-size: 10px; vertical-align: middle; box-sizing: border-box; height: 40px; text-align: center;" class="{tier_class}"><span>EVEN</span><div class="progress-bar"><div class="progress-fill {tier_class}" style="width: {fill_percentage}%;"></div></div></td>'
    html += f'<td colspan="4" style="border-color: black; box-sizing: border-box;"></td>'
    html += '<td style="border-color: black; box-sizing: border-box;"></td>'
    html += "</tr>"

    html += "</table>"
    return html

def update_casino_data(spins_count, even_percent, odd_percent, red_percent, black_percent, low_percent, high_percent, dozen1_percent, dozen2_percent, dozen3_percent, col1_percent, col2_percent, col3_percent, use_winners):
    """Parse casino data inputs, update state, and generate HTML output."""
    try:
        state.casino_data["spins_count"] = int(spins_count)
        state.use_casino_winners = use_winners

        # Remove Hot/Cold Numbers parsing
        state.casino_data["hot_numbers"] = {}
        state.casino_data["cold_numbers"] = {}

        # Parse percentages from dropdowns
        def parse_percent(value, category, key):
            try:
                return float(value) if value != "00" else 0.0
            except ValueError:
                raise ValueError(f"Invalid {category} percentage for {key}: {value}")

        # Even/Odd
        even_val = parse_percent(even_percent, "Even vs Odd", "Even")
        odd_val = parse_percent(odd_percent, "Even vs Odd", "Odd")
        state.casino_data["even_odd"] = {"Even": even_val, "Odd": odd_val}
        has_even_odd = even_val > 0 or odd_val > 0

        # Red/Black
        red_val = parse_percent(red_percent, "Red vs Black", "Red")
        black_val = parse_percent(black_percent, "Red vs Black", "Black")
        state.casino_data["red_black"] = {"Red": red_val, "Black": black_val}
        has_red_black = red_val > 0 or black_val > 0

        # Low/High
        low_val = parse_percent(low_percent, "Low vs High", "Low")
        high_val = parse_percent(high_percent, "Low vs High", "High")
        state.casino_data["low_high"] = {"Low": low_val, "High": high_val}
        has_low_high = low_val > 0 or high_val > 0

        # Dozens
        d1_val = parse_percent(dozen1_percent, "Dozens", "1st Dozen")
        d2_val = parse_percent(dozen2_percent, "Dozens", "2nd Dozen")
        d3_val = parse_percent(dozen3_percent, "Dozens", "3rd Dozen")
        state.casino_data["dozens"] = {"1st Dozen": d1_val, "2nd Dozen": d2_val, "3rd Dozen": d3_val}
        has_dozens = d1_val > 0 or d2_val > 0 or d3_val > 0

        # Columns
        c1_val = parse_percent(col1_percent, "Columns", "1st Column")
        c2_val = parse_percent(col2_percent, "Columns", "2nd Column")
        c3_val = parse_percent(col3_percent, "Columns", "3rd Column")
        state.casino_data["columns"] = {"1st Column": c1_val, "2nd Column": c2_val, "3rd Column": c3_val}
        has_columns = c1_val > 0 or c2_val > 0 or c3_val > 0

        # Check for empty data when highlighting is enabled
        if use_winners and not any([has_even_odd, has_red_black, has_low_high, has_dozens, has_columns]):
            gr.Warning("Highlight Casino Winners is enabled, but no casino data is provided. Enter percentages to see highlights.")
            return "<p>Warning: No casino data provided for highlighting. Please enter percentages for Even/Odd, Red/Black, Low/High, Dozens, or Columns.</p>"

        # Generate HTML Output
        output = f"<h4>Casino Data Insights (Last {spins_count} Spins):</h4>"
        for key, name, has_data in [
            ("even_odd", "Even vs Odd", has_even_odd),
            ("red_black", "Red vs Black", has_red_black),
            ("low_high", "Low vs High", has_low_high)
        ]:
            if has_data:
                winner = max(state.casino_data[key], key=state.casino_data[key].get)
                output += f"<p>{name}: " + " vs ".join(
                    f"<b>{v:.1f}%</b>" if k == winner else f"{v:.1f}%" for k, v in state.casino_data[key].items()
                ) + f" (Winner: {winner})</p>"
            else:
                output += f"<p>{name}: Not set</p>"
        for key, name, has_data in [
            ("dozens", "Dozens", has_dozens),
            ("columns", "Columns", has_columns)
        ]:
            if has_data:
                winner = max(state.casino_data[key], key=state.casino_data[key].get)
                output += f"<p>{name}: " + " vs ".join(
                    f"<b>{v:.1f}%</b>" if k == winner else f"{v:.1f}%" for k, v in state.casino_data[key].items()
                ) + f" (Winner: {winner})</p>"
            else:
                output += f"<p>{name}: Not set</p>"
        print(f"Generated HTML Output: {output}")
        return output
    except ValueError as e:
        return f"<p>Error: {str(e)}</p>"
    except Exception as e:
        return f"<p>Unexpected error parsing casino data: {str(e)}</p>"
        
def reset_casino_data():
    """Reset casino data to defaults and clear UI inputs."""
    state.casino_data = {
        "spins_count": 100,
        "hot_numbers": {},
        "cold_numbers": {},
        "even_odd": {"Even": 0.0, "Odd": 0.0},
        "red_black": {"Red": 0.0, "Black": 0.0},
        "low_high": {"Low": 0.0, "High": 0.0},
        "dozens": {"1st Dozen": 0.0, "2nd Dozen": 0.0, "3rd Dozen": 0.0},
        "columns": {"1st Column": 0.0, "2nd Column": 0.0, "3rd Column": 0.0}
    }
    state.use_casino_winners = False
    return (
        "100",  # spins_count_dropdown
        "",     # hot_numbers_input
        "",     # cold_numbers_input
        "",     # even_odd_input
        "",     # red_black_input
        "",     # low_high_input
        "",     # dozens_input
        "",     # columns_input
        False,  # use_winners_checkbox
        "<p>Casino data reset to defaults.</p>"  # casino_data_output
    )

# Line 1: Start of create_dynamic_table function (updated)
def create_dynamic_table(strategy_name=None, neighbours_count=2, strong_numbers_count=1, dozen_tracker_spins=5, top_color=None, middle_color=None, lower_color=None):
    try:
        print(f"create_dynamic_table called with strategy: {strategy_name}, neighbours_count: {neighbours_count}, strong_numbers_count: {strong_numbers_count}, dozen_tracker_spins: {dozen_tracker_spins}, top_color: {top_color}, middle_color: {middle_color}, lower_color: {lower_color}")
        print(f"Using casino winners: {state.use_casino_winners}, Hot Numbers: {state.casino_data['hot_numbers']}, Cold Numbers: {state.casino_data['cold_numbers']}")
        
        print("create_dynamic_table: Calculating trending sections")
        sorted_sections = calculate_trending_sections()
        print(f"create_dynamic_table: sorted_sections={sorted_sections}")
        
        # If no spins yet, initialize with default even money focus
        if sorted_sections is None and strategy_name == "Best Even Money Bets":
            print("create_dynamic_table: No spins yet, using default even money focus")
            trending_even_money = "Red"  # Default to "Red" as an example
            second_even_money = "Black"
            third_even_money = "Even"
            trending_dozen = None
            second_dozen = None
            trending_column = None
            second_column = None
            number_highlights = {}
            top_color = top_color if top_color else "rgba(255, 255, 0, 0.5)"
            middle_color = middle_color if middle_color else "rgba(0, 255, 255, 0.5)"
            lower_color = lower_color if lower_color else "rgba(0, 255, 0, 0.5)"
            suggestions = None
            hot_numbers = []  # No hot numbers without spins
        else:
            print("create_dynamic_table: Applying strategy highlights")
            trending_even_money, second_even_money, third_even_money, trending_dozen, second_dozen, trending_column, second_column, number_highlights, top_color, middle_color, lower_color, suggestions = apply_strategy_highlights(strategy_name, int(dozen_tracker_spins) if strategy_name == "None" else neighbours_count, strong_numbers_count, sorted_sections, top_color, middle_color, lower_color)
            print(f"create_dynamic_table: Strategy highlights applied - trending_even_money={trending_even_money}, second_even_money={second_even_money}, third_even_money={third_even_money}, trending_dozen={trending_dozen}, second_dozen={second_dozen}, trending_column={trending_column}, second_column={second_column}, number_highlights={number_highlights}")
            
            # Determine hot numbers (top 5 with hits)
            sorted_scores = sorted(state.scores.items(), key=lambda x: x[1], reverse=True)
            hot_numbers = [str(num) for num, score in sorted_scores[:5] if score > 0]
            print(f"create_dynamic_table: Hot numbers={hot_numbers}, Scores={dict(state.scores)}")
        
        # If still no highlights and no sorted_sections, provide a default message
        if sorted_sections is None and not any([trending_even_money, second_even_money, third_even_money, trending_dozen, second_dozen, trending_column, second_column, number_highlights]):
            print("create_dynamic_table: No spins and no highlights, returning default message")
            return "<p>No spins yet. Select a strategy to see default highlights.</p>"
        
        print("create_dynamic_table: Rendering dynamic table HTML")
        html = render_dynamic_table_html(trending_even_money, second_even_money, third_even_money, trending_dozen, second_dozen, trending_column, second_column, number_highlights, top_color, middle_color, lower_color, suggestions, hot_numbers, scores=state.scores)
        print("create_dynamic_table: Table generated successfully")
        return html
    
    except Exception as e:
        print(f"create_dynamic_table: Error: {str(e)}")
        raise  # Re-raise for debugging
    
# Function to get strongest numbers with neighbors
def get_strongest_numbers_with_neighbors(num_count):
    num_count = int(num_count)
    straight_up_df = pd.DataFrame(list(state.scores.items()), columns=["Number", "Score"])
    straight_up_df = straight_up_df[straight_up_df["Score"] > 0].sort_values(by="Score", ascending=False)

    if straight_up_df.empty:
        return "No numbers have hit yet."

    num_to_take = max(1, num_count // 3)
    top_numbers = straight_up_df["Number"].head(num_to_take).tolist()

    if not top_numbers:
        return "No strong numbers available to display."

    all_numbers = set()
    for num in top_numbers:
        neighbors = current_neighbors.get(num, (None, None))
        left, right = neighbors
        all_numbers.add(num)
        if left is not None:
            all_numbers.add(left)
        if right is not None:
            all_numbers.add(right)

    sorted_numbers = sorted(list(all_numbers))
    return f"Strongest {len(sorted_numbers)} Numbers (Sorted Lowest to Highest): {', '.join(map(str, sorted_numbers))}"

# Function to analyze spins
def analyze_spins(spins_input, strategy_name, neighbours_count, *checkbox_args):
    """Analyze the spins and return formatted results for all sections, always resetting scores."""
    try:
        print(f"analyze_spins: Starting with spins_input='{spins_input}', strategy_name='{strategy_name}', neighbours_count={neighbours_count}, checkbox_args={checkbox_args}")
        
        # Handle empty spins case
        if not spins_input or not spins_input.strip():
            print("analyze_spins: No spins input provided.")
            state.reset()  # Always reset scores
            print("analyze_spins: Scores reset due to empty spins.")
            return ("Please enter at least one number (e.g., 5, 12, 0).", "", "", "", "", "", "", "", "", "", "", "", "", "", render_sides_of_zero_display())

        raw_spins = [spin.strip() for spin in spins_input.split(",") if spin.strip()]
        spins = []
        errors = []

        for spin in raw_spins:
            try:
                num = int(spin)
                if not (0 <= num <= 36):
                    errors.append(f"Error: '{spin}' is out of range. Use numbers between 0 and 36.")
                    continue
                spins.append(str(num))
            except ValueError:
                errors.append(f"Error: '{spin}' is not a valid number. Use whole numbers (e.g., 5, 12, 0).")
                continue

        if errors:
            error_msg = "\n".join(errors)
            print(f"analyze_spins: Errors found - {error_msg}")
            return (error_msg, "", "", "", "", "", "", "", "", "", "", "", "", "", render_sides_of_zero_display())

        if not spins:
            print("analyze_spins: No valid spins found.")
            state.reset()  # Always reset scores
            print("analyze_spins: Scores reset due to no valid spins.")
            return ("No valid numbers found. Please enter numbers like '5, 12, 0'.", "", "", "", "", "", "", "", "", "", "", "", "", "", render_sides_of_zero_display())

        # Always reset scores
        state.reset()
        print("analyze_spins: Scores reset.")

        # Batch update scores for all spins
        print("analyze_spins: Updating scores batch")
        action_log = update_scores_batch(spins)
        print(f"analyze_spins: action_log={action_log}")

        # Update state.last_spins and spin_history
        state.last_spins = spins  # Replace last_spins with current spins
        state.spin_history = action_log  # Replace spin_history with current action_log
        # Limit spin history to 100 spins
        if len(state.spin_history) > 100:
            state.spin_history = state.spin_history[-100:]
        print(f"analyze_spins: Updated state.last_spins={state.last_spins}, spin_history length={len(state.spin_history)}")

        # Generate spin analysis output
        print("analyze_spins: Generating spin analysis output")
        spin_results = []
        state.selected_numbers.clear()  # Clear before rebuilding
        for idx, spin in enumerate(spins):
            spin_value = int(spin)
            hit_sections = []
            action = action_log[idx]

            # Reconstruct hit sections from increments
            for name, increment in action["increments"].get("even_money_scores", {}).items():
                if increment > 0:
                    hit_sections.append(name)
            for name, increment in action["increments"].get("dozen_scores", {}).items():
                if increment > 0:
                    hit_sections.append(name)
            for name, increment in action["increments"].get("column_scores", {}).items():
                if increment > 0:
                    hit_sections.append(name)
            for name, increment in action["increments"].get("street_scores", {}).items():
                if increment > 0:
                    hit_sections.append(name)
            for name, increment in action["increments"].get("corner_scores", {}).items():
                if increment > 0:
                    hit_sections.append(name)
            for name, increment in action["increments"].get("six_line_scores", {}).items():
                if increment > 0:
                    hit_sections.append(name)
            for name, increment in action["increments"].get("split_scores", {}).items():
                if increment > 0:
                    hit_sections.append(name)
            if spin_value in action["increments"].get("scores", {}):
                hit_sections.append(f"Straight Up {spin}")
            for name, increment in action["increments"].get("side_scores", {}).items():
                if increment > 0:
                    hit_sections.append(name)

            # Add neighbor information
            if spin_value in current_neighbors:
                left, right = current_neighbors[spin_value]
                hit_sections.append(f"Left Neighbor: {left}")
                hit_sections.append(f"Right Neighbor: {right}")

            spin_results.append(f"Spin {spin} hits: {', '.join(hit_sections)}\nTotal sections hit: {len(hit_sections)}")
        state.selected_numbers = set(int(s) for s in state.last_spins if s.isdigit())  # Sync with last_spins

        spin_analysis_output = "\n".join(spin_results)
        print(f"analyze_spins: spin_analysis_output='{spin_analysis_output}'")
        even_money_output = "Even Money Bets:\n" + "\n".join(f"{name}: {score}" for name, score in state.even_money_scores.items())
        print(f"analyze_spins: even_money_output='{even_money_output}'")
        dozens_output = "Dozens:\n" + "\n".join(f"{name}: {score}" for name, score in state.dozen_scores.items())
        print(f"analyze_spins: dozens_output='{dozens_output}'")
        columns_output = "Columns:\n" + "\n".join(f"{name}: {score}" for name, score in state.column_scores.items())
        print(f"analyze_spins: columns_output='{columns_output}'")
        streets_output = "Streets:\n" + "\n".join(f"{name}: {score}" for name, score in state.street_scores.items() if score > 0)
        print(f"analyze_spins: streets_output='{streets_output}'")
        corners_output = "Corners:\n" + "\n".join(f"{name}: {score}" for name, score in state.corner_scores.items() if score > 0)
        print(f"analyze_spins: corners_output='{corners_output}'")
        six_lines_output = "Double Streets:\n" + "\n".join(f"{name}: {score}" for name, score in state.six_line_scores.items() if score > 0)
        print(f"analyze_spins: six_lines_output='{six_lines_output}'")
        splits_output = "Splits:\n" if any(score > 0 for score in state.split_scores.values()) else "Splits: No hits yet.\n"
        splits_output += "\n".join(f"{name}: {score}" for name, score in state.split_scores.items() if score > 0)
        print(f"analyze_spins: splits_output='{splits_output}'")
        sides_output = "Sides of Zero:\n" + "\n".join(f"{name}: {score}" for name, score in state.side_scores.items())
        print(f"analyze_spins: sides_output='{sides_output}'")

        print("analyze_spins: Creating straight_up_df")
        straight_up_df = pd.DataFrame(list(state.scores.items()), columns=["Number", "Score"])
        straight_up_df = straight_up_df[straight_up_df["Score"] > 0].sort_values(by="Score", ascending=False)
        straight_up_df["Left Neighbor"] = straight_up_df["Number"].apply(lambda x: current_neighbors[x][0] if x in current_neighbors else "")
        straight_up_df["Right Neighbor"] = straight_up_df["Number"].apply(lambda x: current_neighbors[x][1] if x in current_neighbors else "")
        straight_up_html = create_html_table(straight_up_df[["Number", "Left Neighbor", "Right Neighbor", "Score"]], "Strongest Numbers")
        print(f"analyze_spins: straight_up_html generated")

        print("analyze_spins: Creating top_18_df")
        top_18_df = straight_up_df.head(18).sort_values(by="Number", ascending=True)
        numbers = top_18_df["Number"].tolist()
        if len(numbers) < 18:
            numbers.extend([""] * (18 - len(numbers)))
        grid_data = [numbers[i::3] for i in range(3)]
        top_18_html = "<h3>Top 18 Strongest Numbers (Sorted Lowest to Highest)</h3>"
        top_18_html += '<table border="1" style="border-collapse: collapse; text-align: center;">'
        for row in grid_data:
            top_18_html += "<tr>"
            for num in row:
                top_18_html += f'<td style="padding: 5px; width: 40px;">{num}</td>'
            top_18_html += "</tr>"
        top_18_html += "</table>"
        print(f"analyze_spins: top_18_html generated")

        print("analyze_spins: Getting strongest numbers")
        strongest_numbers_output = get_strongest_numbers_with_neighbors(3)
        print(f"analyze_spins: strongest_numbers_output='{strongest_numbers_output}'")

        print("analyze_spins: Generating dynamic_table_html")
        dynamic_table_html = create_dynamic_table(strategy_name, neighbours_count)
        print(f"analyze_spins: dynamic_table_html generated")

        print("analyze_spins: Generating strategy_output")
        strategy_output = show_strategy_recommendations(strategy_name, neighbours_count, *checkbox_args)
        print(f"analyze_spins: Strategy output = {strategy_output}")

        print("analyze_spins: Returning results")
        return (spin_analysis_output, even_money_output, dozens_output, columns_output,
                streets_output, corners_output, six_lines_output, splits_output, sides_output,
                straight_up_html, top_18_html, strongest_numbers_output, dynamic_table_html, strategy_output, render_sides_of_zero_display())
    except Exception as e:
        print(f"analyze_spins: Unexpected error: {str(e)}")
        raise  # Re-raise for debugging

# Function to reset scores (no longer needed, but kept for compatibility)
def reset_scores():
    state.reset()
    return "Scores reset!"

def undo_last_spin(current_spins_display, undo_count, strategy_name, neighbours_count, strong_numbers_count, *checkbox_args):
    if not state.spin_history:
        return ("No spins to undo.", "", "", "", "", "", "", "", "", "", "", current_spins_display, current_spins_display, "", create_dynamic_table(strategy_name, neighbours_count, strong_numbers_count), "", create_color_code_table(), update_spin_counter(), render_sides_of_zero_display())

    try:
        undo_count = int(undo_count)
        if undo_count <= 0:
            return ("Please select a positive number of spins to undo.", "", "", "", "", "", "", "", "", "", "", current_spins_display, current_spins_display, "", create_dynamic_table(strategy_name, neighbours_count, strong_numbers_count), "", create_color_code_table(), update_spin_counter(), render_sides_of_zero_display())
        undo_count = min(undo_count, len(state.spin_history))  # Don't exceed history length

        # Undo the specified number of spins
        undone_spins = []
        for _ in range(undo_count):
            if not state.spin_history:
                break
            action = state.spin_history.pop()
            spin_value = action["spin"]
            undone_spins.append(str(spin_value))

            # Decrement scores based on recorded increments
            for category, increments in action["increments"].items():
                score_dict = getattr(state, category)
                for key, value in increments.items():
                    score_dict[key] -= value
                    if score_dict[key] < 0:  # Prevent negative scores
                        score_dict[key] = 0

            state.last_spins.pop()  # Remove from last_spins too

        spins_input = ", ".join(state.last_spins) if state.last_spins else ""
        spin_analysis_output = f"Undo successful: Removed {undo_count} spin(s) - {', '.join(undone_spins)}"

        even_money_output = "Even Money Bets:\n" + "\n".join(f"{name}: {score}" for name, score in state.even_money_scores.items())
        dozens_output = "Dozens:\n" + "\n".join(f"{name}: {score}" for name, score in state.dozen_scores.items())
        columns_output = "Columns:\n" + "\n".join(f"{name}: {score}" for name, score in state.column_scores.items())
        streets_output = "Streets:\n" + "\n".join(f"{name}: {score}" for name, score in state.street_scores.items() if score > 0)
        corners_output = "Corners:\n" + "\n".join(f"{name}: {score}" for name, score in state.corner_scores.items() if score > 0)
        six_lines_output = "Double Streets:\n" + "\n".join(f"{name}: {score}" for name, score in state.six_line_scores.items() if score > 0)
        splits_output = "Splits:\n" + "\n".join(f"{name}: {score}" for name, score in state.split_scores.items() if score > 0)
        sides_output = "Sides of Zero:\n" + "\n".join(f"{name}: {score}" for name, score in state.side_scores.items())

        straight_up_df = pd.DataFrame(list(state.scores.items()), columns=["Number", "Score"])
        straight_up_df = straight_up_df[straight_up_df["Score"] > 0].sort_values(by="Score", ascending=False)
        straight_up_df["Left Neighbor"] = straight_up_df["Number"].apply(lambda x: current_neighbors[x][0] if x in current_neighbors else "")
        straight_up_df["Right Neighbor"] = straight_up_df["Number"].apply(lambda x: current_neighbors[x][1] if x in current_neighbors else "")
        straight_up_html = create_html_table(straight_up_df[["Number", "Left Neighbor", "Right Neighbor", "Score"]], "Strongest Numbers")

        top_18_df = straight_up_df.head(18).sort_values(by="Number", ascending=True)
        numbers = top_18_df["Number"].tolist()
        if len(numbers) < 18:
            numbers.extend([""] * (18 - len(numbers)))
        grid_data = [numbers[i::3] for i in range(3)]
        top_18_html = "<h3>Top 18 Strongest Numbers (Sorted Lowest to Highest)</h3>"
        top_18_html += '<table border="1" style="border-collapse: collapse; text-align: center;">'
        for row in grid_data:
            top_18_html += "<tr>"
            for num in row:
                top_18_html += f'<td style="padding: 5px; width: 40px;">{num}</td>'
            top_18_html += "</tr>"
        top_18_html += "</table>"

        strongest_numbers_output = get_strongest_numbers_with_neighbors(3)
        dynamic_table_html = create_dynamic_table(strategy_name, neighbours_count, strong_numbers_count)

        print(f"undo_last_spin: Generating strategy recommendations for {strategy_name}")
        strategy_output = show_strategy_recommendations(strategy_name, neighbours_count, strong_numbers_count, *checkbox_args)

        return (spin_analysis_output, even_money_output, dozens_output, columns_output,
            streets_output, corners_output, six_lines_output, splits_output, sides_output,
            straight_up_html, top_18_html, strongest_numbers_output, spins_input, spins_input,
            dynamic_table_html, strategy_output, create_color_code_table(), update_spin_counter(), render_sides_of_zero_display())
    except ValueError:
        return ("Error: Invalid undo count. Please use a positive number.", "", "", "", "", "", "", "", "", "", "", current_spins_display, current_spins_display, "", create_dynamic_table(strategy_name, neighbours_count, strong_numbers_count), "", create_color_code_table(), update_spin_counter(), render_sides_of_zero_display())
    except Exception as e:
        print(f"undo_last_spin: Unexpected error: {str(e)}")
        return (f"Unexpected error during undo: {str(e)}", "", "", "", "", "", "", "", "", "", "", current_spins_display, current_spins_display, "", create_dynamic_table(strategy_name, neighbours_count, strong_numbers_count), "", create_color_code_table(), update_spin_counter(), render_sides_of_zero_display())

def clear_all():
    state.selected_numbers.clear()
    state.last_spins = []
    state.reset()
    return "", "", "All spins and scores cleared successfully!", "<h4>Last Spins</h4><p>No spins yet.</p>", "", "", "", "", "", "", "", "", "", "", "", update_spin_counter(), render_sides_of_zero_display()

def reset_strategy_dropdowns():
    default_category = "Even Money Strategies"
    default_strategy = "Best Even Money Bets"
    strategy_choices = strategy_categories[default_category]
    return default_category, default_strategy, strategy_choices

def generate_random_spins(num_spins, current_spins_display, last_spin_count):
    try:
        num_spins = int(num_spins)
        if num_spins <= 0:
            return current_spins_display, current_spins_display, "Please select a number of spins greater than 0.", update_spin_counter(), render_sides_of_zero_display()

        new_spins = [str(random.randint(0, 36)) for _ in range(num_spins)]
        # Update scores for the new spins
        update_scores_batch(new_spins)

        if current_spins_display and current_spins_display.strip():
            current_spins = current_spins_display.split(", ")
            updated_spins = current_spins + new_spins
        else:
            updated_spins = new_spins

        # Update state.last_spins
        state.last_spins = updated_spins  # Replace the list entirely
        spins_text = ", ".join(updated_spins)
        print(f"generate_random_spins: Setting spins_textbox to '{spins_text}'")
        return spins_text, spins_text, f"Generated {num_spins} random spins: {', '.join(new_spins)}", update_spin_counter(), render_sides_of_zero_display()
    except ValueError:
        print("generate_random_spins: Invalid number of spins entered.")
        return current_spins_display, current_spins_display, "Please enter a valid number of spins.", update_spin_counter(), render_sides_of_zero_display()
    except Exception as e:
        print(f"generate_random_spins: Unexpected error: {str(e)}")
        return current_spins_display, current_spins_display, f"Error generating spins: {str(e)}", update_spin_counter(), render_sides_of_zero_display()

# Strategy functions
def best_even_money_bets():
    recommendations = []
    sorted_even_money = sorted(state.even_money_scores.items(), key=lambda x: x[1], reverse=True)
    even_money_hits = [item for item in sorted_even_money if item[1] > 0]
    
    if not even_money_hits:
        recommendations.append("Best Even Money Bets: No hits yet.")
        return "\n".join(recommendations)

    # Collect the top 3 bets, including ties
    top_bets = []
    scores_seen = set()
    for name, score in sorted_even_money:
        if len(top_bets) < 3 or score in scores_seen:
            top_bets.append((name, score))
            scores_seen.add(score)
        else:
            break

    # Display the top 3 bets
    recommendations.append("Best Even Money Bets (Top 3):")
    for i, (name, score) in enumerate(top_bets[:3], 1):
        recommendations.append(f"{i}. {name}: {score}")

    # Check for ties among the top 3 positions
    if len(top_bets) > 1:
        # Check for ties at the 1st position
        first_score = top_bets[0][1]
        tied_first = [name for name, score in top_bets if score == first_score]
        if len(tied_first) > 1:
            recommendations.append(f"Note: Tie for 1st place among {', '.join(tied_first)} with score {first_score}")

        # Check for ties at the 2nd position
        if len(top_bets) > 1:
            second_score = top_bets[1][1]
            tied_second = [name for name, score in top_bets if score == second_score]
            if len(tied_second) > 1:
                recommendations.append(f"Note: Tie for 2nd place among {', '.join(tied_second)} with score {second_score}")

        # Check for ties at the 3rd position
        if len(top_bets) > 2:
            third_score = top_bets[2][1]
            tied_third = [name for name, score in top_bets if score == third_score]
            if len(tied_third) > 1:
                recommendations.append(f"Note: Tie for 3rd place among {', '.join(tied_third)} with score {third_score}")

    return "\n".join(recommendations)

def hot_bet_strategy():
    recommendations = []
    sorted_even_money = sorted(state.even_money_scores.items(), key=lambda x: x[1], reverse=True)
    even_money_hits = [item for item in sorted_even_money if item[1] > 0]
    if even_money_hits:
        recommendations.append("Even Money (Top 2):")
        for i, (name, score) in enumerate(even_money_hits[:2], 1):
            recommendations.append(f"{i}. {name}: {score}")
    else:
        recommendations.append("Even Money: No hits yet.")

    sorted_dozens = sorted(state.dozen_scores.items(), key=lambda x: x[1], reverse=True)
    dozens_hits = [item for item in sorted_dozens if item[1] > 0]
    if dozens_hits:
        recommendations.append("\nDozens (Top 2):")
        for i, (name, score) in enumerate(dozens_hits[:2], 1):
            recommendations.append(f"{i}. {name}: {score}")
    else:
        recommendations.append("\nDozens: No hits yet.")

    sorted_columns = sorted(state.column_scores.items(), key=lambda x: x[1], reverse=True)
    columns_hits = [item for item in sorted_columns if item[1] > 0]
    if columns_hits:
        recommendations.append("\nColumns (Top 2):")
        for i, (name, score) in enumerate(columns_hits[:2], 1):
            recommendations.append(f"{i}. {name}: {score}")
    else:
        recommendations.append("\nColumns: No hits yet.")

    sorted_streets = sorted(state.street_scores.items(), key=lambda x: x[1], reverse=True)
    streets_hits = [item for item in sorted_streets if item[1] > 0]
    if streets_hits:
        recommendations.append("\nStreets (Ranked):")
        for i, (name, score) in enumerate(streets_hits, 1):
            recommendations.append(f"{i}. {name}: {score}")
    else:
        recommendations.append("\nStreets: No hits yet.")

    sorted_corners = sorted(state.corner_scores.items(), key=lambda x: x[1], reverse=True)
    corners_hits = [item for item in sorted_corners if item[1] > 0]
    if corners_hits:
        recommendations.append("\nCorners (Ranked):")
        for i, (name, score) in enumerate(corners_hits, 1):
            recommendations.append(f"{i}. {name}: {score}")
    else:
        recommendations.append("\nCorners: No hits yet.")

    sorted_six_lines = sorted(state.six_line_scores.items(), key=lambda x: x[1], reverse=True)
    six_lines_hits = [item for item in sorted_six_lines if item[1] > 0]
    if six_lines_hits:
        recommendations.append("\nDouble Streets (Ranked):")
        for i, (name, score) in enumerate(six_lines_hits, 1):
            recommendations.append(f"{i}. {name}: {score}")
    else:
        recommendations.append("\nDouble Streets: No hits yet.")

    sorted_splits = sorted(state.split_scores.items(), key=lambda x: x[1], reverse=True)
    splits_hits = [item for item in sorted_splits if item[1] > 0]
    if splits_hits:
        recommendations.append("\nSplits (Ranked):")
        for i, (name, score) in enumerate(splits_hits, 1):
            recommendations.append(f"{i}. {name}: {score}")
    else:
        recommendations.append("\nSplits: No hits yet.")

    sorted_sides = sorted(state.side_scores.items(), key=lambda x: x[1], reverse=True)
    sides_hits = [item for item in sorted_sides if item[1] > 0]
    if sides_hits:
        recommendations.append("\nSides of Zero:")
        recommendations.append(f"1. {sides_hits[0][0]}: {sides_hits[0][1]}")
    else:
        recommendations.append("\nSides of Zero: No hits yet.")

    sorted_numbers = sorted(state.scores.items(), key=lambda x: x[1], reverse=True)
    numbers_hits = [item for item in sorted_numbers if item[1] > 0]
    if numbers_hits:
        number_best = numbers_hits[0]
        left_neighbor, right_neighbor = current_neighbors[number_best[0]]
        recommendations.append(f"\nStrongest Number: {number_best[0]} (Score: {number_best[1]}) with neighbors {left_neighbor} and {right_neighbor}")
    else:
        recommendations.append("\nStrongest Number: No hits yet.")

    return "\n".join(recommendations)

# Function for Cold Bet Strategy
def cold_bet_strategy():
    recommendations = []
    sorted_even_money = sorted(state.even_money_scores.items(), key=lambda x: x[1])
    even_money_non_hits = [item for item in sorted_even_money if item[1] == 0]
    even_money_hits = [item for item in sorted_even_money if item[1] > 0]
    if even_money_non_hits:
        recommendations.append("Even Money (Not Hit):")
        recommendationsече.append(", ".join(item[0] for item in even_money_non_hits))
    if even_money_hits:
        recommendations.append("\nEven Money (Lowest Scores):")
        for i, (name, score) in enumerate(even_money_hits[:2], 1):
            recommendations.append(f"{i}. {name}: {score}")

    sorted_dozens = sorted(state.dozen_scores.items(), key=lambda x: x[1])
    dozens_non_hits = [item for item in sorted_dozens if item[1] == 0]
    dozens_hits = [item for item in sorted_dozens if item[1] > 0]
    if dozens_non_hits:
        recommendations.append("\nDozens (Not Hit):")
        recommendations.append(", ".join(item[0] for item in dozens_non_hits))
    if dozens_hits:
        recommendations.append("\nDozens (Lowest Scores):")
        for i, (name, score) in enumerate(dozens_hits[:2], 1):
            recommendations.append(f"{i}. {name}: {score}")

    sorted_columns = sorted(state.column_scores.items(), key=lambda x: x[1])
    columns_non_hits = [item for item in sorted_columns if item[1] == 0]
    columns_hits = [item for item in sorted_columns if item[1] > 0]
    if columns_non_hits:
        recommendations.append("\nColumns (Not Hit):")
        recommendations.append(", ".join(item[0] for item in columns_non_hits))
    if columns_hits:
        recommendations.append("\nColumns (Lowest Scores):")
        for i, (name, score) in enumerate(columns_hits[:2], 1):
            recommendations.append(f"{i}. {name}: {score}")

    sorted_streets = sorted(state.street_scores.items(), key=lambda x: x[1])
    streets_non_hits = [item for item in sorted_streets if item[1] == 0]
    streets_hits = [item for item in sorted_streets if item[1] > 0]
    if streets_non_hits:
        recommendations.append("\nStreets (Not Hit):")
        recommendations.append(", ".join(item[0] for item in streets_non_hits))
    if streets_hits:
        recommendations.append("\nStreets (Lowest Scores):")
        for i, (name, score) in enumerate(streets_hits[:3], 1):
            recommendations.append(f"{i}. {name}: {score}")

    sorted_corners = sorted(state.corner_scores.items(), key=lambda x: x[1])
    corners_non_hits = [item for item in sorted_corners if item[1] == 0]
    corners_hits = [item for item in sorted_corners if item[1] > 0]
    if corners_non_hits:
        recommendations.append("\nCorners (Not Hit):")
        recommendations.append(", ".join(item[0] for item in corners_non_hits))
    if corners_hits:
        recommendations.append("\nCorners (Lowest Scores):")
        for i, (name, score) in enumerate(corners_hits[:3], 1):
            recommendations.append(f"{i}. {name}: {score}")

    sorted_six_lines = sorted(state.six_line_scores.items(), key=lambda x: x[1])
    six_lines_non_hits = [item for item in sorted_six_lines if item[1] == 0]
    six_lines_hits = [item for item in sorted_six_lines if item[1] > 0]
    if six_lines_non_hits:
        recommendations.append("\nDouble Streets (Not Hit):")
        recommendations.append(", ".join(item[0] for item in six_lines_non_hits))
    if six_lines_hits:
        recommendations.append("\nDouble Streets (Lowest Scores):")
        for i, (name, score) in enumerate(six_lines_hits[:3], 1):
            recommendations.append(f"{i}. {name}: {score}")

    sorted_splits = sorted(state.split_scores.items(), key=lambda x: x[1])
    splits_non_hits = [item for item in sorted_splits if item[1] == 0]
    splits_hits = [item for item in sorted_splits if item[1] > 0]
    if splits_non_hits:
        recommendations.append("\nSplits (Not Hit):")
        recommendations.append(", ".join(item[0] for item in splits_non_hits))
    if splits_hits:
        recommendations.append("\nSplits (Lowest Scores):")
        for i, (name, score) in enumerate(splits_hits[:3], 1):
            recommendations.append(f"{i}. {name}: {score}")

    sorted_sides = sorted(state.side_scores.items(), key=lambda x: x[1])
    sides_non_hits = [item for item in sorted_sides if item[1] == 0]
    sides_hits = [item for item in sorted_sides if item[1] > 0]
    if sides_non_hits:
        recommendations.append("\nSides of Zero (Not Hit):")
        recommendations.append(", ".join(item[0] for item in sides_non_hits))
    if sides_hits:
        recommendations.append("\nSides of Zero (Lowest Score):")
        recommendations.append(f"1. {sides_hits[0][0]}: {sides_hits[0][1]}")

    sorted_numbers = sorted(state.scores.items(), key=lambda x: x[1])
    numbers_non_hits = [item for item in sorted_numbers if item[1] == 0]
    numbers_hits = [item for item in sorted_numbers if item[1] > 0]
    if numbers_non_hits:
        recommendations.append("\nNumbers (Not Hit):")
        recommendations.append(", ".join(str(item[0]) for item in numbers_non_hits))
    if numbers_hits:
        number_worst = numbers_hits[0]
        left_neighbor, right_neighbor = current_neighbors[number_worst[0]]
        recommendations.append(f"\nColdest Number: {number_worst[0]} (Score: {number_worst[1]}) with neighbors {left_neighbor} and {right_neighbor}")

    return "\n".join(recommendations)

def best_dozens():
    recommendations = []
    sorted_dozens = sorted(state.dozen_scores.items(), key=lambda x: x[1], reverse=True)
    dozens_hits = [item for item in sorted_dozens if item[1] > 0]
    if dozens_hits:
        recommendations.append("Best Dozens (Top 2):")
        for i, (name, score) in enumerate(dozens_hits[:2], 1):
            recommendations.append(f"{i}. {name}: {score}")
    else:
        recommendations.append("Best Dozens: No hits yet.")
    return "\n".join(recommendations)

def best_columns():
    recommendations = []
    sorted_columns = sorted(state.column_scores.items(), key=lambda x: x[1], reverse=True)
    columns_hits = [item for item in sorted_columns if item[1] > 0]
    if columns_hits:
        recommendations.append("Best Columns (Top 2):")
        for i, (name, score) in enumerate(columns_hits[:2], 1):
            recommendations.append(f"{i}. {name}: {score}")
    else:
        recommendations.append("Best Columns: No hits yet.")
    return "\n".join(recommendations)

def fibonacci_strategy():
    recommendations = []
    sorted_dozens = sorted(state.dozen_scores.items(), key=lambda x: x[1], reverse=True)
    dozens_hits = [item for item in sorted_dozens if item[1] > 0]
    sorted_columns = sorted(state.column_scores.items(), key=lambda x: x[1], reverse=True)
    columns_hits = [item for item in sorted_columns if item[1] > 0]

    if not dozens_hits and not columns_hits:
        recommendations.append("Fibonacci Strategy: No hits in Dozens or Columns yet.")
        return "\n".join(recommendations)

    best_dozen_score = dozens_hits[0][1] if dozens_hits else 0
    best_column_score = columns_hits[0][1] if columns_hits else 0

    if best_dozen_score > best_column_score:
        # Dozens wins: show top two dozens
        recommendations.append("Best Category: Dozens")
        top_dozens = []
        scores_seen = set()
        for name, score in sorted_dozens:
            if len(top_dozens) < 2 or score in scores_seen:
                top_dozens.append((name, score))
                scores_seen.add(score)
            else:
                break
        for i, (name, score) in enumerate(top_dozens[:2], 1):
            recommendations.append(f"Best Dozen {i}: {name} (Score: {score})")
        # Check for ties among the top two
        if len(top_dozens) > 1 and top_dozens[0][1] == top_dozens[1][1]:
            tied_dozens = [name for name, score in top_dozens if score == top_dozens[0][1]]
            recommendations.append(f"Note: Tie for 1st place among {', '.join(tied_dozens)} with score {top_dozens[0][1]}")
    elif best_column_score > best_dozen_score:
        # Columns wins: show top two columns
        recommendations.append("Best Category: Columns")
        top_columns = []
        scores_seen = set()
        for name, score in sorted_columns:
            if len(top_columns) < 2 or score in scores_seen:
                top_columns.append((name, score))
                scores_seen.add(score)
            else:
                break
        for i, (name, score) in enumerate(top_columns[:2], 1):
            recommendations.append(f"Best Column {i}: {name} (Score: {score})")
        # Check for ties among the top two
        if len(top_columns) > 1 and top_columns[0][1] == top_columns[1][1]:
            tied_columns = [name for name, score in top_columns if score == top_columns[0][1]]
            recommendations.append(f"Note: Tie for 1st place among {', '.join(tied_columns)} with score {top_columns[0][1]}")
    else:
        # Tie between Dozens and Columns: show both top options
        recommendations.append(f"Best Category (Tied): Dozens and Columns (Score: {best_dozen_score})")
        if dozens_hits:
            top_dozens = []
            scores_seen = set()
            for name, score in sorted_dozens:
                if len(top_dozens) < 2 or score in scores_seen:
                    top_dozens.append((name, score))
                    scores_seen.add(score)
                else:
                    break
            for i, (name, score) in enumerate(top_dozens[:2], 1):
                recommendations.append(f"Best Dozen {i}: {name} (Score: {score})")
            if len(top_dozens) > 1 and top_dozens[0][1] == top_dozens[1][1]:
                tied_dozens = [name for name, score in top_dozens if score == top_dozens[0][1]]
                recommendations.append(f"Note: Tie for 1st place among {', '.join(tied_dozens)} with score {top_dozens[0][1]}")
        if columns_hits:
            top_columns = []
            scores_seen = set()
            for name, score in sorted_columns:
                if len(top_columns) < 2 or score in scores_seen:
                    top_columns.append((name, score))
                    scores_seen.add(score)
                else:
                    break
            for i, (name, score) in enumerate(top_columns[:2], 1):
                recommendations.append(f"Best Column {i}: {name} (Score: {score})")
            if len(top_columns) > 1 and top_columns[0][1] == top_columns[1][1]:
                tied_columns = [name for name, score in top_columns if score == top_columns[0][1]]
                recommendations.append(f"Note: Tie for 1st place among {', '.join(tied_columns)} with score {top_columns[0][1]}")

    return "\n".join(recommendations)

def best_streets():
    recommendations = []
    sorted_streets = sorted(state.street_scores.items(), key=lambda x: x[1], reverse=True)
    streets_hits = [item for item in sorted_streets if item[1] > 0]

    if not streets_hits:
        recommendations.append("Best Streets: No hits yet.")
        return "\n".join(recommendations)

    recommendations.append("Top 3 Streets:")
    for i, (name, score) in enumerate(streets_hits[:3], 1):
        recommendations.append(f"{i}. {name}: {score}")

    recommendations.append("\nTop 6 Streets:")
    for i, (name, score) in enumerate(streets_hits[:6], 1):
        recommendations.append(f"{i}. {name}: {score}")

    return "\n".join(recommendations)

def best_double_streets():
    recommendations = []
    sorted_six_lines = sorted(state.six_line_scores.items(), key=lambda x: x[1], reverse=True)
    six_lines_hits = [item for item in sorted_six_lines if item[1] > 0]

    if not six_lines_hits:
        recommendations.append("Best Double Streets: No hits yet.")
        return "\n".join(recommendations)

    recommendations.append("Double Streets (Ranked):")
    for i, (name, score) in enumerate(six_lines_hits, 1):
        recommendations.append(f"{i}. {name}: {score}")

    return "\n".join(recommendations)

def best_corners():
    recommendations = []
    sorted_corners = sorted(state.corner_scores.items(), key=lambda x: x[1], reverse=True)
    corners_hits = [item for item in sorted_corners if item[1] > 0]

    if not corners_hits:
        recommendations.append("Best Corners: No hits yet.")
        return "\n".join(recommendations)

    recommendations.append("Corners (Ranked):")
    for i, (name, score) in enumerate(corners_hits, 1):
        recommendations.append(f"{i}. {name}: {score}")

    return "\n".join(recommendations)

def best_splits():
    recommendations = []
    sorted_splits = sorted(state.split_scores.items(), key=lambda x: x[1], reverse=True)
    splits_hits = [item for item in sorted_splits if item[1] > 0]

    if not splits_hits:
        recommendations.append("Best Splits: No hits yet.")
        return "\n".join(recommendations)

    recommendations.append("Splits (Ranked):")
    for i, (name, score) in enumerate(splits_hits, 1):
        recommendations.append(f"{i}. {name}: {score}")

    return "\n".join(recommendations)

def best_dozens_and_streets():
    recommendations = []
    sorted_dozens = sorted(state.dozen_scores.items(), key=lambda x: x[1], reverse=True)
    dozens_hits = [item for item in sorted_dozens if item[1] > 0]
    if dozens_hits:
        recommendations.append("Best Dozens (Top 2):")
        for i, (name, score) in enumerate(dozens_hits[:2], 1):
            recommendations.append(f"{i}. {name}: {score}")
    else:
        recommendations.append("Best Dozens: No hits yet.")

    sorted_streets = sorted(state.street_scores.items(), key=lambda x: x[1], reverse=True)
    streets_hits = [item for item in sorted_streets if item[1] > 0]
    if streets_hits:
        recommendations.append("\nTop 3 Streets (Yellow):")
        for i, (name, score) in enumerate(streets_hits[:3], 1):
            recommendations.append(f"{i}. {name}: {score}")
        recommendations.append("\nMiddle 3 Streets (Cyan):")
        for i, (name, score) in enumerate(streets_hits[3:6], 1):
            recommendations.append(f"{i}. {name}: {score}")
        recommendations.append("\nBottom 3 Streets (Green):")
        for i, (name, score) in enumerate(streets_hits[6:9], 1):
            recommendations.append(f"{i}. {name}: {score}")
    else:
        recommendations.append("\nBest Streets: No hits yet.")

    return "\n".join(recommendations)

def best_columns_and_streets():
    recommendations = []
    sorted_columns = sorted(state.column_scores.items(), key=lambda x: x[1], reverse=True)
    columns_hits = [item for item in sorted_columns if item[1] > 0]
    if columns_hits:
        recommendations.append("Best Columns (Top 2):")
        for i, (name, score) in enumerate(columns_hits[:2], 1):
            recommendations.append(f"{i}. {name}: {score}")
    else:
        recommendations.append("Best Columns: No hits yet.")

    sorted_streets = sorted(state.street_scores.items(), key=lambda x: x[1], reverse=True)
    streets_hits = [item for item in sorted_streets if item[1] > 0]
    if streets_hits:
        recommendations.append("\nTop 3 Streets (Yellow):")
        for i, (name, score) in enumerate(streets_hits[:3], 1):
            recommendations.append(f"{i}. {name}: {score}")
        recommendations.append("\nMiddle 3 Streets (Cyan):")
        for i, (name, score) in enumerate(streets_hits[3:6], 1):
            recommendations.append(f"{i}. {name}: {score}")
        recommendations.append("\nBottom 3 Streets (Green):")
        for i, (name, score) in enumerate(streets_hits[6:9], 1):
            recommendations.append(f"{i}. {name}: {score}")
    else:
        recommendations.append("\nBest Streets: No hits yet.")

    return "\n".join(recommendations)

def non_overlapping_double_street_strategy():
    non_overlapping_sets = [
        ["1ST D.STREET – 1, 4", "3RD D.STREET – 7, 10", "5TH D.STREET – 13, 16", "7TH D.STREET – 19, 22", "9TH D.STREET – 25, 28"],
        ["2ND D.STREET – 4, 7", "4TH D.STREET – 10, 13", "6TH D.STREET – 16, 19", "8TH D.STREET – 22, 25", "10TH D.STREET – 28, 31"]
    ]

    set_scores = []
    for idx, non_overlapping_set in enumerate(non_overlapping_sets):
        total_score = sum(state.six_line_scores[name] for name in non_overlapping_set)
        set_scores.append((idx, total_score, non_overlapping_set))

    best_set = max(set_scores, key=lambda x: x[1])
    best_set_idx, best_set_score, best_set_streets = best_set

    sorted_streets = sorted(best_set_streets, key=lambda name: state.six_line_scores[name], reverse=True)

    recommendations = []
    recommendations.append(f"Non-Overlapping Double Streets Strategy (Set {best_set_idx + 1} with Total Score: {best_set_score})")
    recommendations.append("Hottest Non-Overlapping Double Streets (Sorted by Hotness):")
    for i, name in enumerate(sorted_streets, 1):
        score = state.six_line_scores[name]
        recommendations.append(f"{i}. {name}: {score}")

    return "\n".join(recommendations)

def non_overlapping_corner_strategy():
    non_overlapping_sets = [
        ["1ST CORNER – 1, 2, 4, 5", "5TH CORNER – 7, 8, 10, 11", "9TH CORNER – 13, 14, 16, 17", "13TH CORNER – 19, 20, 22, 23", "17TH CORNER – 25, 26, 28, 29", "21ST CORNER – 31, 32, 34, 35"],
        ["2ND CORNER – 2, 3, 5, 6", "6TH CORNER – 8, 9, 11, 12", "10TH CORNER – 14, 15, 17, 18", "14TH CORNER – 20, 21, 23, 24", "18TH CORNER – 26, 27, 29, 30", "22ND CORNER – 32, 33, 35, 36"]
    ]

    set_scores = []
    for idx, non_overlapping_set in enumerate(non_overlapping_sets):
        total_score = sum(state.corner_scores[name] for name in non_overlapping_set)
        set_scores.append((idx, total_score, non_overlapping_set))

    best_set = max(set_scores, key=lambda x: x[1])
    best_set_idx, best_set_score, best_set_corners = best_set

    sorted_corners = sorted(best_set_corners, key=lambda name: state.corner_scores[name], reverse=True)

    recommendations = []
    recommendations.append(f"Non-Overlapping Corner Strategy (Set {best_set_idx + 1} with Total Score: {best_set_score})")
    recommendations.append("Hottest Non-Overlapping Corners (Sorted by Hotness):")
    for i, name in enumerate(sorted_corners, 1):
        score = state.corner_scores[name]
        recommendations.append(f"{i}. {name}: {score}")

    return "\n".join(recommendations)

def romanowksy_missing_dozen_strategy():
    recommendations = []
    sorted_dozens = sorted(state.dozen_scores.items(), key=lambda x: x[1], reverse=True)
    dozens_hits = [item for item in sorted_dozens if item[1] > 0]
    dozens_no_hits = [item for item in sorted_dozens if item[1] == 0]

    if not dozens_hits and not dozens_no_hits:
        recommendations.append("Romanowksy Missing Dozen Strategy: No spins recorded yet.")
        return "\n".join(recommendations)

    if len(dozens_hits) < 2:
        recommendations.append("Romanowksy Missing Dozen Strategy: Not enough dozens have hit yet.")
        if dozens_hits:
            recommendations.append(f"Hottest Dozen: {dozens_hits[0][0]} (Score: {dozens_hits[0][1]})")
        return "\n".join(recommendations)

    top_dozens = []
    scores_seen = set()
    for name, score in sorted_dozens:
        if len(top_dozens) < 2 or score in scores_seen:
            top_dozens.append((name, score))
            scores_seen.add(score)
        else:
            break

    recommendations.append("Hottest Dozens (Top 2):")
    for i, (name, score) in enumerate(top_dozens[:2], 1):
        recommendations.append(f"{i}. {name}: {score}")
    if len(top_dozens) > 2 and top_dozens[1][1] == top_dozens[2][1]:
        tied_dozens = [name for name, score in top_dozens if score == top_dozens[1][1]]
        recommendations.append(f"Note: Tie detected among {', '.join(tied_dozens)} with score {top_dozens[1][1]}")

    weakest_dozen = sorted_dozens[-1]
    weakest_dozen_name, weakest_dozen_score = weakest_dozen
    recommendations.append(f"\nWeakest Dozen: {weakest_dozen_name} (Score: {weakest_dozen_score})")

    weakest_dozen_numbers = set(DOZENS[weakest_dozen_name])
    straight_up_df = pd.DataFrame(list(state.scores.items()), columns=["Number", "Score"])
    straight_up_df = straight_up_df[straight_up_df["Score"] > 0].sort_values(by="Score", ascending=False)

    if straight_up_df.empty:
        recommendations.append("No strong numbers have hit yet in any dozen.")
        return "\n".join(recommendations)

    strong_numbers_in_weakest = []
    neighbors_in_weakest = []
    for _, row in straight_up_df.iterrows():
        number = row["Number"]
        score = row["Score"]
        if number in weakest_dozen_numbers:
            strong_numbers_in_weakest.append((number, score))
        else:
            if number in current_neighbors:
                left, right = current_neighbors[number]
                if left in weakest_dozen_numbers:
                    neighbors_in_weakest.append((left, number, score))
                if right in weakest_dozen_numbers:
                    neighbors_in_weakest.append((right, number, score))

    if strong_numbers_in_weakest:
        recommendations.append("\nStrongest Numbers in Weakest Dozen:")
        for number, score in strong_numbers_in_weakest:
            recommendations.append(f"Number {number} (Score: {score})")
    else:
        recommendations.append("\nNo strong numbers directly in the Weakest Dozen.")

    if neighbors_in_weakest:
        recommendations.append("\nNeighbors of Strong Numbers in Weakest Dozen:")
        for neighbor, strong_number, score in neighbors_in_weakest:
            recommendations.append(f"Number {neighbor} (Neighbor of {strong_number}, Score: {score})")
    else:
        if not strong_numbers_in_weakest:
            recommendations.append("No neighbors of strong numbers in the Weakest Dozen.")

    return "\n".join(recommendations)

def fibonacci_to_fortune_strategy():
    recommendations = []

    # Debug: Print scores to verify state
    print(f"fibonacci_to_fortune_strategy: Dozen scores = {dict(state.dozen_scores)}")
    print(f"fibonacci_to_fortune_strategy: Column scores = {dict(state.column_scores)}")
    print(f"fibonacci_to_fortune_strategy: Even money scores = {dict(state.even_money_scores)}")

    # Part 1: Fibonacci Strategy (Best Category: Dozens or Columns)
    sorted_dozens = sorted(state.dozen_scores.items(), key=lambda x: x[1], reverse=True)
    dozens_hits = [item for item in sorted_dozens if item[1] > 0]
    sorted_columns = sorted(state.column_scores.items(), key=lambda x: x[1], reverse=True)
    columns_hits = [item for item in sorted_columns if item[1] > 0]

    best_dozen_score = dozens_hits[0][1] if dozens_hits else 0
    best_column_score = columns_hits[0][1] if columns_hits else 0

    recommendations.append("Fibonacci Strategy:")
    if not dozens_hits and not columns_hits:
        recommendations.append("No hits in Dozens or Columns yet.")
    elif best_dozen_score > best_column_score:
        recommendations.append(f"Best Category: Dozens (Score: {best_dozen_score})")
        recommendations.append(f"Best Dozen: {dozens_hits[0][0]}")
    elif best_column_score > best_dozen_score:
        recommendations.append(f"Best Category: Columns (Score: {best_column_score})")
        recommendations.append(f"Best Column: {columns_hits[0][0]}")
    else:
        recommendations.append(f"Best Category (Tied): Dozens and Columns (Score: {best_dozen_score})")
        if dozens_hits:
            recommendations.append(f"Best Dozen: {dozens_hits[0][0]}")
        if columns_hits:
            recommendations.append(f"Best Column: {columns_hits[0][0]}")

    # Part 2: Dozens (Top 2)
    recommendations.append("\nDozens (Top 2):")
    print(f"fibonacci_to_fortune_strategy: Sorted dozens = {sorted_dozens}")
    if len(sorted_dozens) >= 2:
        for i, (name, score) in enumerate(sorted_dozens[:2], 1):
            recommendations.append(f"{i}. {name}: {score}")
    elif sorted_dozens:
        name, score = sorted_dozens[0]
        recommendations.append(f"1. {name}: {score}")
        recommendations.append("2. No other dozens available.")
    else:
        recommendations.append("No hits yet.")

    # Part 3: Columns (Top 2)
    recommendations.append("\nColumns (Top 2):")
    print(f"fibonacci_to_fortune_strategy: Sorted columns = {sorted_columns}")
    if len(sorted_columns) >= 2:
        for i, (name, score) in enumerate(sorted_columns[:2], 1):
            recommendations.append(f"{i}. {name}: {score}")
    elif sorted_columns:
        name, score = sorted_columns[0]
        recommendations.append(f"1. {name}: {score}")
        recommendations.append("2. No other columns available.")
    else:
        recommendations.append("No hits yet.")

    # Part 4: Best Even Money Bet
    sorted_even_money = sorted(state.even_money_scores.items(), key=lambda x: x[1], reverse=True)
    print(f"fibonacci_to_fortune_strategy: Sorted even money = {sorted_even_money}")
    even_money_hits = [item for item in sorted_even_money if item[1] > 0]
    recommendations.append("\nEven Money (Top 1):")
    if even_money_hits:
        best_even_money = even_money_hits[0]
        name, score = best_even_money
        recommendations.append(f"1. {name}: {score}")
    else:
        recommendations.append("No hits yet.")

    # Part 5: Best Double Street in Weakest Dozen (Excluding Top Two Dozens)
    weakest_dozen = min(state.dozen_scores.items(), key=lambda x: x[1], default=("1st Dozen", 0))
    weakest_dozen_name, weakest_dozen_score = weakest_dozen
    weakest_dozen_numbers = set(DOZENS[weakest_dozen_name])

    top_two_dozens = [item[0] for item in sorted_dozens[:2]]
    top_two_dozen_numbers = set()
    for dozen_name in top_two_dozens:
        top_two_dozen_numbers.update(DOZENS[dozen_name])

    double_streets_in_weakest = []
    for name, numbers in SIX_LINES.items():
        numbers_set = set(numbers)
        if numbers_set.issubset(weakest_dozen_numbers) and not numbers_set.intersection(top_two_dozen_numbers):
            score = state.six_line_scores.get(name, 0)
            double_streets_in_weakest.append((name, score))

    print(f"fibonacci_to_fortune_strategy: Double streets in weakest dozen ({weakest_dozen_name}) = {double_streets_in_weakest}")
    recommendations.append(f"\nDouble Streets (Top 1 in Weakest Dozen: {weakest_dozen_name}, Score: {weakest_dozen_score}):")
    if double_streets_in_weakest:
        double_streets_sorted = sorted(double_streets_in_weakest, key=lambda x: x[1], reverse=True)
        best_double_street = double_streets_sorted[0]
        name, score = best_double_street
        numbers = ', '.join(map(str, sorted(SIX_LINES[name])))
        recommendations.append(f"1. {name} (Numbers: {numbers}, Score: {score})")
    else:
        recommendations.append("No suitable double street available (all overlap with top two dozens or no hits).")

    return "\n".join(recommendations)
    
def three_eight_six_rising_martingale():
    recommendations = []
    sorted_streets = sorted(state.street_scores.items(), key=lambda x: x[1], reverse=True)
    streets_hits = [item for item in sorted_streets if item[1] > 0]

    if not streets_hits:
        recommendations.append("3-8-6 Rising Martingale: No streets have hit yet.")
        return "\n".join(recommendations)

    recommendations.append("Top 3 Streets (Yellow):")
    for i, (name, score) in enumerate(streets_hits[:3], 1):
        recommendations.append(f"{i}. {name}: {score}")

    recommendations.append("\nMiddle 3 Streets (Cyan):")
    for i, (name, score) in enumerate(streets_hits[3:6], 1):
        recommendations.append(f"{i}. {name}: {score}")

    recommendations.append("\nBottom 2 Streets (Green):")
    for i, (name, score) in enumerate(streets_hits[6:8], 1):
        recommendations.append(f"{i}. {name}: {score}")

    return "\n".join(recommendations)

def one_dozen_one_column_strategy():
    recommendations = []
    sorted_dozens = sorted(state.dozen_scores.items(), key=lambda x: x[1], reverse=True)
    dozens_hits = [item for item in sorted_dozens if item[1] > 0]

    if not dozens_hits:
        recommendations.append("Best Dozen: No dozens have hit yet.")
    else:
        top_score = dozens_hits[0][1]
        top_dozens = [item for item in sorted_dozens if item[1] == top_score]
        if len(top_dozens) == 1:
            recommendations.append(f"Best Dozen: {top_dozens[0][0]}")
        else:
            recommendations.append("Best Dozens (Tied):")
            for name, _ in top_dozens:
                recommendations.append(f"- {name}")

    sorted_columns = sorted(state.column_scores.items(), key=lambda x: x[1], reverse=True)
    columns_hits = [item for item in sorted_columns if item[1] > 0]

    if not columns_hits:
        recommendations.append("Best Column: No columns have hit yet.")
    else:
        top_score = columns_hits[0][1]
        top_columns = [item for item in sorted_columns if item[1] == top_score]
        if len(top_columns) == 1:
            recommendations.append(f"Best Column: {top_columns[0][0]}")
        else:
            recommendations.append("Best Columns (Tied):")
            for name, _ in top_columns:
                recommendations.append(f"- {name}")

    return "\n".join(recommendations)

def top_pick_18_numbers_without_neighbours():
    recommendations = []
    straight_up_df = pd.DataFrame(list(state.scores.items()), columns=["Number", "Score"])
    straight_up_df = straight_up_df[straight_up_df["Score"] > 0].sort_values(by="Score", ascending=False)

    if straight_up_df.empty or len(straight_up_df) < 18:
        recommendations.append("Top Pick 18 Numbers without Neighbours: Not enough numbers have hit yet (need at least 18).")
        return "\n".join(recommendations)

    top_18_df = straight_up_df.head(18)
    top_18_numbers = top_18_df["Number"].tolist()

    top_6 = top_18_numbers[:6]
    next_6 = top_18_numbers[6:12]
    last_6 = top_18_numbers[12:18]

    recommendations.append("Top Pick 18 Numbers without Neighbours:")
    recommendations.append("\nTop 6 Numbers (Yellow):")
    for i, num in enumerate(top_6, 1):
        score = top_18_df[top_18_df["Number"] == num]["Score"].iloc[0]
        recommendations.append(f"{i}. Number {num} (Score: {score})")

    recommendations.append("\nNext 6 Numbers (Blue):")
    for i, num in enumerate(next_6, 1):
        score = top_18_df[top_18_df["Number"] == num]["Score"].iloc[0]
        recommendations.append(f"{i}. Number {num} (Score: {score})")

    recommendations.append("\nLast 6 Numbers (Green):")
    for i, num in enumerate(last_6, 1):
        score = top_18_df[top_18_df["Number"] == num]["Score"].iloc[0]
        recommendations.append(f"{i}. Number {num} (Score: {score})")

    return "\n".join(recommendations)

def best_even_money_and_top_18():
    recommendations = []

    # Best Even Money Bets (Top 3 with tie handling, same as best_even_money_bets)
    sorted_even_money = sorted(state.even_money_scores.items(), key=lambda x: x[1], reverse=True)
    even_money_hits = [item for item in sorted_even_money if item[1] > 0]
    
    if even_money_hits:
        # Collect the top 3 bets, including ties
        top_bets = []
        scores_seen = set()
        for name, score in sorted_even_money:
            if len(top_bets) < 3 or score in scores_seen:
                top_bets.append((name, score))
                scores_seen.add(score)
            else:
                break

        # Display the top 3 bets
        recommendations.append("Best Even Money Bets (Top 3):")
        for i, (name, score) in enumerate(top_bets[:3], 1):
            recommendations.append(f"{i}. {name}: {score}")

        # Check for ties among the top 3 positions
        if len(top_bets) > 1:
            first_score = top_bets[0][1]
            tied_first = [name for name, score in top_bets if score == first_score]
            if len(tied_first) > 1:
                recommendations.append(f"Note: Tie for 1st place among {', '.join(tied_first)} with score {first_score}")

            if len(top_bets) > 1:
                second_score = top_bets[1][1]
                tied_second = [name for name, score in top_bets if score == second_score]
                if len(tied_second) > 1:
                    recommendations.append(f"Note: Tie for 2nd place among {', '.join(tied_second)} with score {second_score}")

            if len(top_bets) > 2:
                third_score = top_bets[2][1]
                tied_third = [name for name, score in top_bets if score == third_score]
                if len(tied_third) > 1:
                    recommendations.append(f"Note: Tie for 3rd place among {', '.join(tied_third)} with score {third_score}")
    else:
        recommendations.append("Best Even Money Bets: No hits yet.")

    # Top Pick 18 Numbers without Neighbours (same as top_pick_18_numbers_without_neighbours)
    recommendations.append("")  # Add a blank line for separation
    straight_up_df = pd.DataFrame(list(state.scores.items()), columns=["Number", "Score"])
    straight_up_df = straight_up_df[straight_up_df["Score"] > 0].sort_values(by="Score", ascending=False)

    if straight_up_df.empty or len(straight_up_df) < 18:
        recommendations.append("Top Pick 18 Numbers without Neighbours: Not enough numbers have hit yet (need at least 18).")
        return "\n".join(recommendations)

    top_18_df = straight_up_df.head(18)
    top_18_numbers = top_18_df["Number"].tolist()

    top_6 = top_18_numbers[:6]
    next_6 = top_18_numbers[6:12]
    last_6 = top_18_numbers[12:18]

    recommendations.append("Top Pick 18 Numbers without Neighbours:")
    recommendations.append("\nTop 6 Numbers (Yellow):")
    for i, num in enumerate(top_6, 1):
        score = top_18_df[top_18_df["Number"] == num]["Score"].iloc[0]
        recommendations.append(f"{i}. Number {num} (Score: {score})")

    recommendations.append("\nNext 6 Numbers (Blue):")
    for i, num in enumerate(next_6, 1):
        score = top_18_df[top_18_df["Number"] == num]["Score"].iloc[0]
        recommendations.append(f"{i}. Number {num} (Score: {score})")

    recommendations.append("\nLast 6 Numbers (Green):")
    for i, num in enumerate(last_6, 1):
        score = top_18_df[top_18_df["Number"] == num]["Score"].iloc[0]
        recommendations.append(f"{i}. Number {num} (Score: {score})")

    return "\n".join(recommendations)

def best_dozens_and_top_18():
    recommendations = []

    # Best Dozens (Top 2 with tie handling, same as best_dozens)
    sorted_dozens = sorted(state.dozen_scores.items(), key=lambda x: x[1], reverse=True)
    dozens_hits = [item for item in sorted_dozens if item[1] > 0]
    if dozens_hits:
        # Collect the top 2 dozens, including ties
        top_dozens = []
        scores_seen = set()
        for name, score in sorted_dozens:
            if len(top_dozens) < 2 or score in scores_seen:
                top_dozens.append((name, score))
                scores_seen.add(score)
            else:
                break

        # Display the top 2 dozens
        recommendations.append("Best Dozens (Top 2):")
        for i, (name, score) in enumerate(top_dozens[:2], 1):
            recommendations.append(f"{i}. {name}: {score}")

        # Check for ties among the top 2 positions
        if len(top_dozens) > 1:
            first_score = top_dozens[0][1]
            tied_first = [name for name, score in top_dozens if score == first_score]
            if len(tied_first) > 1:
                recommendations.append(f"Note: Tie for 1st place among {', '.join(tied_first)} with score {first_score}")

            if len(top_dozens) > 1:
                second_score = top_dozens[1][1]
                tied_second = [name for name, score in top_dozens if score == second_score]
                if len(tied_second) > 1:
                    recommendations.append(f"Note: Tie for 2nd place among {', '.join(tied_second)} with score {second_score}")
    else:
        recommendations.append("Best Dozens: No hits yet.")

    # Top Pick 18 Numbers without Neighbours (same as top_pick_18_numbers_without_neighbours)
    recommendations.append("")  # Add a blank line for separation
    straight_up_df = pd.DataFrame(list(state.scores.items()), columns=["Number", "Score"])
    straight_up_df = straight_up_df[straight_up_df["Score"] > 0].sort_values(by="Score", ascending=False)

    if straight_up_df.empty or len(straight_up_df) < 18:
        recommendations.append("Top Pick 18 Numbers without Neighbours: Not enough numbers have hit yet (need at least 18).")
        return "\n".join(recommendations)

    top_18_df = straight_up_df.head(18)
    top_18_numbers = top_18_df["Number"].tolist()

    top_6 = top_18_numbers[:6]
    next_6 = top_18_numbers[6:12]
    last_6 = top_18_numbers[12:18]

    recommendations.append("Top Pick 18 Numbers without Neighbours:")
    recommendations.append("\nTop 6 Numbers (Yellow):")
    for i, num in enumerate(top_6, 1):
        score = top_18_df[top_18_df["Number"] == num]["Score"].iloc[0]
        recommendations.append(f"{i}. Number {num} (Score: {score})")

    recommendations.append("\nNext 6 Numbers (Blue):")
    for i, num in enumerate(next_6, 1):
        score = top_18_df[top_18_df["Number"] == num]["Score"].iloc[0]
        recommendations.append(f"{i}. Number {num} (Score: {score})")

    recommendations.append("\nLast 6 Numbers (Green):")
    for i, num in enumerate(last_6, 1):
        score = top_18_df[top_18_df["Number"] == num]["Score"].iloc[0]
        recommendations.append(f"{i}. Number {num} (Score: {score})")

    return "\n".join(recommendations)

def best_columns_and_top_18():
    recommendations = []

    # Best Columns (Top 2 with tie handling, same as best_columns)
    sorted_columns = sorted(state.column_scores.items(), key=lambda x: x[1], reverse=True)
    columns_hits = [item for item in sorted_columns if item[1] > 0]
    if columns_hits:
        # Collect the top 2 columns, including ties
        top_columns = []
        scores_seen = set()
        for name, score in sorted_columns:
            if len(top_columns) < 2 or score in scores_seen:
                top_columns.append((name, score))
                scores_seen.add(score)
            else:
                break

        # Display the top 2 columns
        recommendations.append("Best Columns (Top 2):")
        for i, (name, score) in enumerate(top_columns[:2], 1):
            recommendations.append(f"{i}. {name}: {score}")

        # Check for ties among the top 2 positions
        if len(top_columns) > 1:
            first_score = top_columns[0][1]
            tied_first = [name for name, score in top_columns if score == first_score]
            if len(tied_first) > 1:
                recommendations.append(f"Note: Tie for 1st place among {', '.join(tied_first)} with score {first_score}")

            if len(top_columns) > 1:
                second_score = top_columns[1][1]
                tied_second = [name for name, score in top_columns if score == second_score]
                if len(tied_second) > 1:
                    recommendations.append(f"Note: Tie for 2nd place among {', '.join(tied_second)} with score {second_score}")
    else:
        recommendations.append("Best Columns: No hits yet.")

    # Top Pick 18 Numbers without Neighbours (same as top_pick_18_numbers_without_neighbours)
    recommendations.append("")  # Add a blank line for separation
    straight_up_df = pd.DataFrame(list(state.scores.items()), columns=["Number", "Score"])
    straight_up_df = straight_up_df[straight_up_df["Score"] > 0].sort_values(by="Score", ascending=False)

    if straight_up_df.empty or len(straight_up_df) < 18:
        recommendations.append("Top Pick 18 Numbers without Neighbours: Not enough numbers have hit yet (need at least 18).")
        return "\n".join(recommendations)

    top_18_df = straight_up_df.head(18)
    top_18_numbers = top_18_df["Number"].tolist()

    top_6 = top_18_numbers[:6]
    next_6 = top_18_numbers[6:12]
    last_6 = top_18_numbers[12:18]

    recommendations.append("Top Pick 18 Numbers without Neighbours:")
    recommendations.append("\nTop 6 Numbers (Yellow):")
    for i, num in enumerate(top_6, 1):
        score = top_18_df[top_18_df["Number"] == num]["Score"].iloc[0]
        recommendations.append(f"{i}. Number {num} (Score: {score})")

    recommendations.append("\nNext 6 Numbers (Blue):")
    for i, num in enumerate(next_6, 1):
        score = top_18_df[top_18_df["Number"] == num]["Score"].iloc[0]
        recommendations.append(f"{i}. Number {num} (Score: {score})")

    recommendations.append("\nLast 6 Numbers (Green):")
    for i, num in enumerate(last_6, 1):
        score = top_18_df[top_18_df["Number"] == num]["Score"].iloc[0]
        recommendations.append(f"{i}. Number {num} (Score: {score})")

    return "\n".join(recommendations)

def best_dozens_even_money_and_top_18():
    recommendations = []

    # Best Dozens (Top 2 with tie handling, same as best_dozens)
    sorted_dozens = sorted(state.dozen_scores.items(), key=lambda x: x[1], reverse=True)
    dozens_hits = [item for item in sorted_dozens if item[1] > 0]
    if dozens_hits:
        # Collect the top 2 dozens, including ties
        top_dozens = []
        scores_seen = set()
        for name, score in sorted_dozens:
            if len(top_dozens) < 2 or score in scores_seen:
                top_dozens.append((name, score))
                scores_seen.add(score)
            else:
                break

        # Display the top 2 dozens
        recommendations.append("Best Dozens (Top 2):")
        for i, (name, score) in enumerate(top_dozens[:2], 1):
            recommendations.append(f"{i}. {name}: {score}")

        # Check for ties among the top 2 positions
        if len(top_dozens) > 1:
            first_score = top_dozens[0][1]
            tied_first = [name for name, score in top_dozens if score == first_score]
            if len(tied_first) > 1:
                recommendations.append(f"Note: Tie for 1st place among {', '.join(tied_first)} with score {first_score}")

            if len(top_dozens) > 1:
                second_score = top_dozens[1][1]
                tied_second = [name for name, score in top_dozens if score == second_score]
                if len(tied_second) > 1:
                    recommendations.append(f"Note: Tie for 2nd place among {', '.join(tied_second)} with score {second_score}")
    else:
        recommendations.append("Best Dozens: No hits yet.")

    # Best Even Money Bets (Top 3 with tie handling, same as best_even_money_bets)
    recommendations.append("")  # Add a blank line for separation
    sorted_even_money = sorted(state.even_money_scores.items(), key=lambda x: x[1], reverse=True)
    even_money_hits = [item for item in sorted_even_money if item[1] > 0]
    
    if even_money_hits:
        # Collect the top 3 bets, including ties
        top_bets = []
        scores_seen = set()
        for name, score in sorted_even_money:
            if len(top_bets) < 3 or score in scores_seen:
                top_bets.append((name, score))
                scores_seen.add(score)
            else:
                break

        # Display the top 3 bets
        recommendations.append("Best Even Money Bets (Top 3):")
        for i, (name, score) in enumerate(top_bets[:3], 1):
            recommendations.append(f"{i}. {name}: {score}")

        # Check for ties among the top 3 positions
        if len(top_bets) > 1:
            first_score = top_bets[0][1]
            tied_first = [name for name, score in top_bets if score == first_score]
            if len(tied_first) > 1:
                recommendations.append(f"Note: Tie for 1st place among {', '.join(tied_first)} with score {first_score}")

            if len(top_bets) > 1:
                second_score = top_bets[1][1]
                tied_second = [name for name, score in top_bets if score == second_score]
                if len(tied_second) > 1:
                    recommendations.append(f"Note: Tie for 2nd place among {', '.join(tied_second)} with score {second_score}")

            if len(top_bets) > 2:
                third_score = top_bets[2][1]
                tied_third = [name for name, score in top_bets if score == third_score]
                if len(tied_third) > 1:
                    recommendations.append(f"Note: Tie for 3rd place among {', '.join(tied_third)} with score {third_score}")
    else:
        recommendations.append("Best Even Money Bets: No hits yet.")

    # Top Pick 18 Numbers without Neighbours (same as top_pick_18_numbers_without_neighbours)
    recommendations.append("")  # Add a blank line for separation
    straight_up_df = pd.DataFrame(list(state.scores.items()), columns=["Number", "Score"])
    straight_up_df = straight_up_df[straight_up_df["Score"] > 0].sort_values(by="Score", ascending=False)

    if straight_up_df.empty or len(straight_up_df) < 18:
        recommendations.append("Top Pick 18 Numbers without Neighbours: Not enough numbers have hit yet (need at least 18).")
        return "\n".join(recommendations)

    top_18_df = straight_up_df.head(18)
    top_18_numbers = top_18_df["Number"].tolist()

    top_6 = top_18_numbers[:6]
    next_6 = top_18_numbers[6:12]
    last_6 = top_18_numbers[12:18]

    recommendations.append("Top Pick 18 Numbers without Neighbours:")
    recommendations.append("\nTop 6 Numbers (Yellow):")
    for i, num in enumerate(top_6, 1):
        score = top_18_df[top_18_df["Number"] == num]["Score"].iloc[0]
        recommendations.append(f"{i}. Number {num} (Score: {score})")

    recommendations.append("\nNext 6 Numbers (Blue):")
    for i, num in enumerate(next_6, 1):
        score = top_18_df[top_18_df["Number"] == num]["Score"].iloc[0]
        recommendations.append(f"{i}. Number {num} (Score: {score})")

    recommendations.append("\nLast 6 Numbers (Green):")
    for i, num in enumerate(last_6, 1):
        score = top_18_df[top_18_df["Number"] == num]["Score"].iloc[0]
        recommendations.append(f"{i}. Number {num} (Score: {score})")

    return "\n".join(recommendations)

def best_columns_even_money_and_top_18():
    recommendations = []

    # Best Columns (Top 2 with tie handling, same as best_columns)
    sorted_columns = sorted(state.column_scores.items(), key=lambda x: x[1], reverse=True)
    columns_hits = [item for item in sorted_columns if item[1] > 0]
    if columns_hits:
        # Collect the top 2 columns, including ties
        top_columns = []
        scores_seen = set()
        for name, score in sorted_columns:
            if len(top_columns) < 2 or score in scores_seen:
                top_columns.append((name, score))
                scores_seen.add(score)
            else:
                break

        # Display the top 2 columns
        recommendations.append("Best Columns (Top 2):")
        for i, (name, score) in enumerate(top_columns[:2], 1):
            recommendations.append(f"{i}. {name}: {score}")

        # Check for ties among the top 2 positions
        if len(top_columns) > 1:
            first_score = top_columns[0][1]
            tied_first = [name for name, score in top_columns if score == first_score]
            if len(tied_first) > 1:
                recommendations.append(f"Note: Tie for 1st place among {', '.join(tied_first)} with score {first_score}")

            if len(top_columns) > 1:
                second_score = top_columns[1][1]
                tied_second = [name for name, score in top_columns if score == second_score]
                if len(tied_second) > 1:
                    recommendations.append(f"Note: Tie for 2nd place among {', '.join(tied_second)} with score {second_score}")
    else:
        recommendations.append("Best Columns: No hits yet.")

    # Best Even Money Bets (Top 3 with tie handling, same as best_even_money_bets)
    recommendations.append("")  # Add a blank line for separation
    sorted_even_money = sorted(state.even_money_scores.items(), key=lambda x: x[1], reverse=True)
    even_money_hits = [item for item in sorted_even_money if item[1] > 0]
    
    if even_money_hits:
        # Collect the top 3 bets, including ties
        top_bets = []
        scores_seen = set()
        for name, score in sorted_even_money:
            if len(top_bets) < 3 or score in scores_seen:
                top_bets.append((name, score))
                scores_seen.add(score)
            else:
                break

        # Display the top 3 bets
        recommendations.append("Best Even Money Bets (Top 3):")
        for i, (name, score) in enumerate(top_bets[:3], 1):
            recommendations.append(f"{i}. {name}: {score}")

        # Check for ties among the top 3 positions
        if len(top_bets) > 1:
            first_score = top_bets[0][1]
            tied_first = [name for name, score in top_bets if score == first_score]
            if len(tied_first) > 1:
                recommendations.append(f"Note: Tie for 1st place among {', '.join(tied_first)} with score {first_score}")

            if len(top_bets) > 1:
                second_score = top_bets[1][1]
                tied_second = [name for name, score in top_bets if score == second_score]
                if len(tied_second) > 1:
                    recommendations.append(f"Note: Tie for 2nd place among {', '.join(tied_second)} with score {second_score}")

            if len(top_bets) > 2:
                third_score = top_bets[2][1]
                tied_third = [name for name, score in top_bets if score == third_score]
                if len(tied_third) > 1:
                    recommendations.append(f"Note: Tie for 3rd place among {', '.join(tied_third)} with score {third_score}")
    else:
        recommendations.append("Best Even Money Bets: No hits yet.")

    # Top Pick 18 Numbers without Neighbours (same as top_pick_18_numbers_without_neighbours)
    recommendations.append("")  # Add a blank line for separation
    straight_up_df = pd.DataFrame(list(state.scores.items()), columns=["Number", "Score"])
    straight_up_df = straight_up_df[straight_up_df["Score"] > 0].sort_values(by="Score", ascending=False)

    if straight_up_df.empty or len(straight_up_df) < 18:
        recommendations.append("Top Pick 18 Numbers without Neighbours: Not enough numbers have hit yet (need at least 18).")
        return "\n".join(recommendations)

    top_18_df = straight_up_df.head(18)
    top_18_numbers = top_18_df["Number"].tolist()

    top_6 = top_18_numbers[:6]
    next_6 = top_18_numbers[6:12]
    last_6 = top_18_numbers[12:18]

    recommendations.append("Top Pick 18 Numbers without Neighbours:")
    recommendations.append("\nTop 6 Numbers (Yellow):")
    for i, num in enumerate(top_6, 1):
        score = top_18_df[top_18_df["Number"] == num]["Score"].iloc[0]
        recommendations.append(f"{i}. Number {num} (Score: {score})")

    recommendations.append("\nNext 6 Numbers (Blue):")
    for i, num in enumerate(next_6, 1):
        score = top_18_df[top_18_df["Number"] == num]["Score"].iloc[0]
        recommendations.append(f"{i}. Number {num} (Score: {score})")

    recommendations.append("\nLast 6 Numbers (Green):")
    for i, num in enumerate(last_6, 1):
        score = top_18_df[top_18_df["Number"] == num]["Score"].iloc[0]
        recommendations.append(f"{i}. Number {num} (Score: {score})")

    return "\n".join(recommendations)

def create_color_code_table():
    html = '''
    <div style="margin-top: 20px;">
        <h3 style="margin-bottom: 10px; font-family: Arial, sans-serif;">Color Code Key</h3>
        <table border="1" style="border-collapse: collapse; text-align: left; font-size: 14px; font-family: Arial, sans-serif; width: 100%; max-width: 600px; border-color: #333;">
            <thead>
                <tr style="background-color: #f2f2f2;">
                    <th style="padding: 8px; width: 20%;">Color</th>
                    <th style="padding: 8px;">Meaning</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td style="padding: 8px; background-color: rgba(255, 255, 0, 0.5); text-align: center;">Yellow (Top Tier)</td>
                    <td style="padding: 8px;">Indicates the hottest or top-ranked numbers/sections (e.g., top 3 or top 6 in most strategies). For Dozen Tracker, this highlights the most frequent Dozen when no strategy is selected. Can be changed via color pickers.</td>
                </tr>
                <tr>
                    <td style="padding: 8px; background-color: rgba(0, 255, 255, 0.5); text-align: center;">Cyan (Middle Tier)</td>
                    <td style="padding: 8px;">Represents the second tier of trending numbers/sections (e.g., ranks 4-6 or secondary picks). For Dozen Tracker, this highlights the second most frequent Dozen when no strategy is selected. Can be changed via color pickers.</td>
                </tr>
                <tr>
                    <td style="padding: 8px; background-color: rgba(0, 255, 0, 0.5); text-align: center;">Green (Lower Tier)</td>
                    <td style="padding: 8px;">Marks the third tier of strong numbers/sections (e.g., ranks 7-9 or lower priority). Can be changed via color pickers.</td>
                </tr>
                <tr>
                    <td style="padding: 8px; background-color: #D3D3D3; text-align: center;">Light Gray (Cold Top)</td>
                    <td style="padding: 8px;">Used in Cold Bet Strategy for the coldest top-tier sections (least hits). Fixed for this strategy.</td>
                </tr>
                <tr>
                    <td style="padding: 8px; background-color: #DDA0DD; text-align: center;">Plum (Cold Middle)</td>
                    <td style="padding: 8px;">Used in Cold Bet Strategy for middle-tier cold sections. Fixed for this strategy.</td>
                </tr>
                <tr>
                    <td style="padding: 8px; background-color: #E0FFFF; text-align: center;">Light Cyan (Cold Lower)</td>
                    <td style="padding: 8px;">Used in Cold Bet Strategy for lower-tier cold sections. Fixed for this strategy.</td>
                </tr>
                <tr>
                    <td style="padding: 8px; background-color: red; color: white; text-align: center;">Red</td>
                    <td style="padding: 8px;">Default color for red numbers on the roulette table.</td>
                </tr>
                <tr>
                    <td style="padding: 8px; background-color: black; color: white; text-align: center;">Black</td>
                    <td style="padding: 8px;">Default color for black numbers on the roulette table.</td>
                </tr>
                <tr>
                    <td style="padding: 8px; background-color: green; color: white; text-align: center;">Green</td>
                    <td style="padding: 8px;">Default color for zero (0) on the roulette table.</td>
                </tr>
                <tr>
                    <td style="padding: 8px; background-color: #FF6347; color: white; text-align: center;">Tomato Red</td>
                    <td style="padding: 8px;">Used in Dozen Tracker to represent the 1st Dozen.</td>
                </tr>
                <tr>
                    <td style="padding: 8px; background-color: #4682B4; color: white; text-align: center;">Steel Blue</td>
                    <td style="padding: 8px;">Used in Dozen Tracker to represent the 2nd Dozen.</td>
                </tr>
                <tr>
                    <td style="padding: 8px; background-color: #32CD32; color: white; text-align: center;">Lime Green</td>
                    <td style="padding: 8px;">Used in Dozen Tracker to represent the 3rd Dozen.</td>
                </tr>
                <tr>
                    <td style="padding: 8px; background-color: #808080; color: white; text-align: center;">Gray</td>
                    <td style="padding: 8px;">Used in Dozen Tracker to represent spins not in any Dozen (i.e., 0).</td>
                </tr>
            </tbody>
        </table>
    </div>
    '''
    return html
    
def update_spin_counter():
    """Update the spin counter HTML with the total number of spins."""
    total_spins = len(state.last_spins)
    return f'<span class="spin-counter glow" style="font-size: 14px; padding: 4px 8px;">Total Spins: {total_spins}</span>'
    
# Lines before (context, unchanged)
def top_numbers_with_neighbours_tiered():
    recommendations = []
    straight_up_df = pd.DataFrame(list(state.scores.items()), columns=["Number", "Score"])
    straight_up_df = straight_up_df[straight_up_df["Score"] > 0].sort_values(by="Score", ascending=False)

    if straight_up_df.empty:
        return "<p>Top Numbers with Neighbours (Tiered): No numbers have hit yet.</p>"

    # Start with the HTML table for Strongest Numbers
    table_html = '<table border="1" style="border-collapse: collapse; text-align: center; font-family: Arial, sans-serif;">'
    table_html += "<tr><th>Hit</th><th>Left N.</th><th>Right N.</th></tr>"  # Table header
    for _, row in straight_up_df.iterrows():
        num = str(row["Number"])
        left, right = current_neighbors.get(row["Number"], ("", ""))
        left = str(left) if left is not None else ""
        right = str(right) if right is not None else ""
        table_html += f"<tr><td>{num}</td><td>{left}</td><td>{right}</td></tr>"
    table_html += "</table>"

    # Wrap the table in a div with a heading
    recommendations.append("<h3>Strongest Numbers:</h3>")
    recommendations.append(table_html)

    num_to_take = min(8, len(straight_up_df))
    top_numbers = straight_up_df["Number"].head(num_to_take).tolist()

    all_numbers = set()
    number_scores = {}
    for num in top_numbers:
        neighbors = current_neighbors.get(num, (None, None))
        left, right = neighbors
        all_numbers.add(num)
        number_scores[num] = state.scores[num]
        if left is not None:
            all_numbers.add(left)
        if right is not None:
            all_numbers.add(right)

    number_groups = []
    for num in top_numbers:
        left, right = current_neighbors.get(num, (None, None))
        group = [num]
        if left is not None:
            group.append(left)
        if right is not None:
            group.append(right)
        number_groups.append((state.scores[num], group))

    number_groups.sort(key=lambda x: x[0], reverse=True)
    ordered_numbers = []
    for _, group in number_groups:
        ordered_numbers.extend(group)

    ordered_numbers = ordered_numbers[:24]
    top_8 = ordered_numbers[:8]
    next_8 = ordered_numbers[8:16]
    last_8 = ordered_numbers[16:24]

    recommendations.append("<h3>Top Numbers with Neighbours (Tiered):</h3>")
    recommendations.append("<p><strong>Top Tier (Yellow):</strong></p>")
    for i, num in enumerate(top_8, 1):
        score = number_scores.get(num, "Neighbor")
        recommendations.append(f"<p>{i}. Number {num} (Score: {score})</p>")

    recommendations.append("<p><strong>Second Tier (Blue):</strong></p>")
    for i, num in enumerate(next_8, 1):
        score = number_scores.get(num, "Neighbor")
        recommendations.append(f"<p>{i}. Number {num} (Score: {score})</p>")

    recommendations.append("<p><strong>Third Tier (Green):</strong></p>")
    for i, num in enumerate(last_8, 1):
        score = number_scores.get(num, "Neighbor")
        recommendations.append(f"<p>{i}. Number {num} (Score: {score})</p>")

    return "\n".join(recommendations)


# Line 1: Start of neighbours_of_strong_number function (updated)
def neighbours_of_strong_number(neighbours_count, strong_numbers_count):
    """Recommend numbers and their neighbors based on hit frequency, including strategy recommendations with tie information."""
    recommendations = []
    
    # Validate inputs
    try:
        neighbours_count = int(neighbours_count)
        strong_numbers_count = int(strong_numbers_count)
        if neighbours_count < 0 or strong_numbers_count < 0:
            raise ValueError("Neighbours count and strong numbers count must be non-negative.")
        if strong_numbers_count == 0:
            raise ValueError("Strong numbers count must be at least 1.")
    except (ValueError, TypeError) as e:
        return f"Error: Invalid input - {str(e)}. Please use positive integers for neighbours and strong numbers.", {}

    # Check if current_neighbors is valid
    if not isinstance(current_neighbors, dict):
        return "Error: Neighbor data is not properly configured. Contact support.", {}
    for key, value in current_neighbors.items():
        if not isinstance(key, int) or not isinstance(value, tuple) or len(value) != 2:
            return "Error: Neighbor data is malformed. Contact support.", {}

    try:
        print(f"neighbours_of_strong_number: Starting with neighbours_count = {neighbours_count}, strong_numbers_count = {strong_numbers_count}")
        sorted_numbers = sorted(state.scores.items(), key=lambda x: (-x[1], x[0]))
        numbers_hits = [item for item in sorted_numbers if item[1] > 0]
        
        if not numbers_hits:
            recommendations.append("Neighbours of Strong Number: No numbers have hit yet.")
            return "\n".join(recommendations), {}

        # Limit strong_numbers_count to available hits
        strong_numbers_count = min(strong_numbers_count, len(numbers_hits))
        top_numbers = [item[0] for item in numbers_hits[:strong_numbers_count]]
        top_scores = {item[0]: item[1] for item in numbers_hits[:strong_numbers_count]}
        selected_numbers = set(top_numbers)
        neighbors_set = set()

        # Calculate neighbors for each strong number
        for strong_number in top_numbers:
            if strong_number not in current_neighbors:
                recommendations.append(f"Warning: No neighbor data for number {strong_number}. Skipping its neighbors.")
                continue
            current_number = strong_number
            # Left neighbors
            for i in range(neighbours_count):
                left, _ = current_neighbors.get(current_number, (None, None))
                if left is not None:
                    neighbors_set.add(left)
                    current_number = left
                else:
                    break
            # Right neighbors
            current_number = strong_number
            for i in range(neighbours_count):
                _, right = current_neighbors.get(current_number, (None, None))
                if right is not None:
                    neighbors_set.add(right)
                    current_number = right
                else:
                    break

        # Remove overlap (strong numbers take precedence)
        neighbors_set = neighbors_set - selected_numbers
        print(f"neighbours_of_strong_number: Strong numbers = {sorted(list(selected_numbers))}")
        print(f"neighbours_of_strong_number: Neighbors = {sorted(list(neighbors_set))}")

        # Combine all bet numbers (strong numbers + neighbors) for aggregated scoring
        bet_numbers = list(selected_numbers) + list(neighbors_set)

        # Calculate Aggregated Scores for the bet numbers (needed for Suggestions)
        even_money_scores, dozen_scores, column_scores = state.calculate_aggregated_scores_for_spins(bet_numbers)

        # Determine the best even money bet and check for ties
        sorted_even_money = sorted(even_money_scores.items(), key=lambda x: (-x[1], x[0]))
        best_even_money = sorted_even_money[0] if sorted_even_money else ("None", 0)
        best_even_money_name, best_even_money_hits = best_even_money
        # Check for ties in even money bets
        even_money_ties = []
        if sorted_even_money and best_even_money_hits > 0:
            even_money_ties = [f"{name}: {score}" for name, score in sorted_even_money if score == best_even_money_hits and name != best_even_money_name]
        even_money_tie_text = f" (Tied with {', '.join(even_money_ties)})" if even_money_ties else ""

        # Determine the best dozen and best column
        best_dozen = max(dozen_scores.items(), key=lambda x: x[1], default=("None", 0))
        best_dozen_name, best_dozen_hits = best_dozen
        best_column = max(column_scores.items(), key=lambda x: x[1], default=("None", 0))
        best_column_name, best_column_hits = best_column

        # Compare dozens vs. columns for the stronger section and check for ties
        suggestion = ""
        winner_category = ""
        best_bet_tie_text = ""
        if best_dozen_hits > best_column_hits:
            suggestion = f"{best_dozen_name}: {best_dozen_hits}"
            winner_category = "dozen"
            # Check if the best dozen ties with others
            sorted_dozens = sorted(dozen_scores.items(), key=lambda x: (-x[1], x[0]))
            dozen_ties = [f"{name}: {score}" for name, score in sorted_dozens if score == best_dozen_hits and name != best_dozen_name]
            if dozen_ties:
                best_bet_tie_text = f" (Tied with {', '.join(dozen_ties)})"
        elif best_column_hits > best_dozen_hits:
            suggestion = f"{best_column_name}: {best_column_hits}"
            winner_category = "column"
            # Check if the best column ties with others
            sorted_columns = sorted(column_scores.items(), key=lambda x: (-x[1], x[0]))
            column_ties = [f"{name}: {score}" for name, score in sorted_columns if score == best_column_hits and name != best_column_name]
            if column_ties:
                best_bet_tie_text = f" (Tied with {', '.join(column_ties)})"
        else:
            # Check for ties between dozens and columns at the top level
            sorted_dozens = sorted(dozen_scores.items(), key=lambda x: (-x[1], x[0]))
            sorted_columns = sorted(column_scores.items(), key=lambda x: (-x[1], x[0]))
            if len(sorted_dozens) >= 2 and sorted_dozens[0][1] == sorted_dozens[1][1] and sorted_dozens[0][1] > 0:
                # Two dozens tie at the highest hit count
                suggestion = f"{sorted_dozens[0][0]} and {sorted_dozens[1][0]}: {sorted_dozens[0][1]}"
                winner_category = "dozen"
                # Check for additional dozen ties
                dozen_ties = [f"{name}: {score}" for name, score in sorted_dozens[2:] if score == sorted_dozens[0][1]]
                if dozen_ties:
                    best_bet_tie_text = f" (Tied with {', '.join(dozen_ties)})"
            elif len(sorted_columns) >= 2 and sorted_columns[0][1] == sorted_columns[1][1] and sorted_columns[0][1] > 0:
                # Two columns tie at the highest hit count
                suggestion = f"{sorted_columns[0][0]} and {sorted_columns[1][0]}: {sorted_columns[0][1]}"
                winner_category = "column"
                # Check for additional column ties
                column_ties = [f"{name}: {score}" for name, score in sorted_columns[2:] if score == sorted_columns[0][1]]
                if column_ties:
                    best_bet_tie_text = f" (Tied with {', '.join(column_ties)})"
            else:
                # Default to the best dozen (alphabetically if tied), check for ties with columns
                suggestion = f"{best_dozen_name}: {best_dozen_hits}"
                winner_category = "dozen"
                if best_dozen_hits == best_column_hits and best_column_hits > 0:
                    best_bet_tie_text = f" (Tied with {best_column_name}: {best_column_hits})"

        # Determine the top two winners in the winning category (dozens or columns) and check for ties
        two_winners_suggestion = ""
        two_winners_tie_text = ""
        if winner_category == "dozen":
            sorted_dozens = sorted(dozen_scores.items(), key=lambda x: (-x[1], x[0]))
            top_two_dozens = sorted_dozens[:2]  # Take top two dozens
            if top_two_dozens[0][1] > 0:  # Only suggest if there are hits
                two_winners_suggestion = f"Play Two Dozens: {top_two_dozens[0][0]} ({top_two_dozens[0][1]}) and {top_two_dozens[1][0]} ({top_two_dozens[1][1]})"
                # Check if the second dozen ties with others
                if len(sorted_dozens) > 2:
                    second_score = top_two_dozens[1][1]
                    ties = [f"{name}: {score}" for name, score in sorted_dozens[2:] if score == second_score]
                    if ties:
                        two_winners_tie_text = f" (Tied with {', '.join(ties)})"
            else:
                two_winners_suggestion = "Play Two Dozens: Not enough hits to suggest two dozens."
        elif winner_category == "column":
            sorted_columns = sorted(column_scores.items(), key=lambda x: (-x[1], x[0]))
            top_two_columns = sorted_columns[:2]  # Take top two columns
            if top_two_columns[0][1] > 0:  # Only suggest if there are hits
                two_winners_suggestion = f"Play Two Columns: {top_two_columns[0][0]} ({top_two_columns[0][1]}) and {top_two_columns[1][0]} ({top_two_columns[1][1]})"
                # Check if the second column ties with others
                if len(sorted_columns) > 2:
                    second_score = top_two_columns[1][1]
                    ties = [f"{name}: {score}" for name, score in sorted_columns[2:] if score == second_score]
                    if ties:
                        two_winners_tie_text = f" (Tied with {', '.join(ties)})"
            else:
                two_winners_suggestion = "Play Two Columns: Not enough hits to suggest two columns."

        # Create the suggestions dictionary
        suggestions = {
            "best_even_money": f"{best_even_money_name}: {best_even_money_hits}{even_money_tie_text}",
            "best_bet": f"{suggestion}{best_bet_tie_text}",
            "play_two": f"{two_winners_suggestion}{two_winners_tie_text}"
        }

        # Append the Suggestions section first
        recommendations.append("Suggestions:")
        recommendations.append(f"Best Even Money Bet: {best_even_money_name}: {best_even_money_hits}{even_money_tie_text}")
        recommendations.append(f"Best Bet: {suggestion}{best_bet_tie_text}")
        recommendations.append(f"{two_winners_suggestion}{two_winners_tie_text}")

        # Now append the Strongest Numbers and Neighbours section
        recommendations.append(f"\nTop {strong_numbers_count} Strongest Numbers and Their Neighbours:")
        recommendations.append("\nStrongest Numbers (Yellow):")
        for i, num in enumerate(sorted(top_numbers), 1):
            score = top_scores[num]
            recommendations.append(f"{i}. Number {num} (Score: {score})")
        
        if neighbors_set:
            recommendations.append(f"\nNeighbours ({neighbours_count} Left + {neighbours_count} Right, Cyan):")
            for i, num in enumerate(sorted(list(neighbors_set)), 1):
                recommendations.append(f"{i}. Number {num}")
        else:
            recommendations.append(f"\nNeighbours ({neighbours_count} Left + {neighbours_count} Right, Cyan): None")

        return "\n".join(recommendations), suggestions

    except Exception as e:
        print(f"neighbours_of_strong_number: Unexpected error: {str(e)}")
        return f"Error in Neighbours of Strong Number: Unexpected issue - {str(e)}. Please try again or contact support.", {}

# Line 3: Start of dozen_tracker function (unchanged)
def dozen_tracker(num_spins_to_check, consecutive_hits_threshold, alert_enabled, sequence_length, follow_up_spins, sequence_alert_enabled):
    """Track and display the history of Dozen hits for the last N spins, with optional alerts for consecutive hits and sequence matching."""
    recommendations = []
    sequence_recommendations = []
    
    # Validate inputs
    try:
        num_spins_to_check = int(num_spins_to_check)
        consecutive_hits_threshold = int(consecutive_hits_threshold)
        sequence_length = int(sequence_length)
        follow_up_spins = int(follow_up_spins)
        if num_spins_to_check < 1:
            return "Error: Number of spins to check must be at least 1.", "<p>Error: Number of spins to check must be at least 1.</p>", "<p>Error: Number of spins to check must be at least 1.</p>"
        if consecutive_hits_threshold < 1:
            return "Error: Consecutive hits threshold must be at least 1.", "<p>Error: Consecutive hits threshold must be at least 1.</p>", "<p>Error: Consecutive hits threshold must be at least 1.</p>"
        if sequence_length < 1:
            return "Error: Sequence length must be at least 1.", "<p>Error: Sequence length must be at least 1.</p>", "<p>Error: Sequence length must be at least 1.</p>"
        if follow_up_spins < 1:
            return "Error: Follow-up spins must be at least 1.", "<p>Error: Follow-up spins must be at least 1.</p>", "<p>Error: Follow-up spins must be at least 1.</p>"
    except (ValueError, TypeError):
        return "Error: Invalid inputs. Please use positive integers.", "<p>Error: Invalid inputs. Please use positive integers.</p>", "<p>Error: Invalid inputs. Please use positive integers.</p>"

    # Get the last N spins for sequence matching
    recent_spins = state.last_spins[-num_spins_to_check:] if len(state.last_spins) >= num_spins_to_check else state.last_spins
    print(f"dozen_tracker: Tracking {num_spins_to_check} spins for sequence matching, recent_spins length = {len(recent_spins)}")
    
    if not recent_spins:
        return "Dozen Tracker: No spins recorded yet.", "<p>Dozen Tracker: No spins recorded yet.</p>", "<p>Dozen Tracker: No spins recorded yet.</p>"

    # Map each spin to its Dozen for sequence matching
    dozen_pattern = []
    dozen_counts = {"1st Dozen": 0, "2nd Dozen": 0, "3rd Dozen": 0, "Not in Dozen": 0}
    for spin in recent_spins:
        spin_value = int(spin)
        if spin_value == 0:
            dozen_pattern.append("Not in Dozen")
            dozen_counts["Not in Dozen"] += 1
        else:
            found = False
            for name, numbers in DOZENS.items():
                if spin_value in numbers:
                    dozen_pattern.append(name)
                    dozen_counts[name] += 1
                    found = True
                    break
            if not found:
                dozen_pattern.append("Not in Dozen")
                dozen_counts["Not in Dozen"] += 1

    # Map the entire spin history to Dozens for sequence matching
    full_dozen_pattern = []
    for spin in state.last_spins:
        spin_value = int(spin)
        if spin_value == 0:
            full_dozen_pattern.append("Not in Dozen")
        else:
            found = False
            for name, numbers in DOZENS.items():
                if spin_value in numbers:
                    full_dozen_pattern.append(name)
                    found = True
                    break
            if not found:
                full_dozen_pattern.append("Not in Dozen")

    # Detect consecutive Dozen hits in the LAST 3 spins only (if alert is enabled)
    if alert_enabled:
        # Take only the last 3 spins (or fewer if not enough spins)
        last_three_spins = state.last_spins[-3:] if len(state.last_spins) >= 3 else state.last_spins
        print(f"dozen_tracker: Checking last 3 spins for consecutive hits, last_three_spins = {last_three_spins}")
        
        if len(last_three_spins) < 3:
            print("dozen_tracker: Not enough spins to check for consecutive hits (need at least 3).")
            state.last_dozen_alert_index = -1
            state.last_alerted_spins = None
        else:
            # Map the last 3 spins to their Dozens
            last_three_dozens = []
            for spin in last_three_spins:
                spin_value = int(spin)
                if spin_value == 0:
                    last_three_dozens.append("Not in Dozen")
                else:
                    found = False
                    for name, numbers in DOZENS.items():
                        if spin_value in numbers:
                            last_three_dozens.append(name)
                            found = True
                            break
                    if not found:
                        last_three_dozens.append("Not in Dozen")
            
            print(f"dozen_tracker: Last 3 spins dozens = {last_three_dozens}")

            # Check if all 3 spins are in the same Dozen and not "Not in Dozen"
            if (last_three_dozens[0] == last_three_dozens[1] == last_three_dozens[2] and 
                last_three_dozens[0] != "Not in Dozen"):
                current_dozen = last_three_dozens[0]
                # Convert last_three_spins to a tuple for comparison (immutable and hashable)
                current_spins_tuple = tuple(last_three_spins)
                # Check if this set of spins is different from the last alerted set
                if state.last_alerted_spins != current_spins_tuple:
                    # Include the spins in the alert
                    spins_str = ", ".join(map(str, last_three_spins))
                    alert_message = f"Alert: {current_dozen} has hit 3 times consecutively! (Spins: {spins_str})"
                    gr.Warning(alert_message)
                    recommendations.append(alert_message)
                    state.last_dozen_alert_index = len(state.last_spins) - 1  # Update the last alerted index
                    state.last_alerted_spins = current_spins_tuple  # Store the spins that triggered this alert
            else:
                # If the last 3 spins don't form a streak, reset the alert index and spins
                state.last_dozen_alert_index = -1
                state.last_alerted_spins = None

    # Detect sequence matches (only if sequence alert is enabled)
    sequence_matches = []
    sequence_follow_ups = []
    if sequence_alert_enabled and len(full_dozen_pattern) >= sequence_length:
        # Take the last X spins to check for a match
        last_x_spins = full_dozen_pattern[-sequence_length:] if len(full_dozen_pattern) >= sequence_length else full_dozen_pattern
        print(f"dozen_tracker: Checking last {sequence_length} spins for sequence matching, last_x_spins = {last_x_spins}")
        
        if len(last_x_spins) < sequence_length:
            print(f"dozen_tracker: Not enough spins to check for sequence of length {sequence_length}.")
        else:
            # Convert the last X spins to a tuple for comparison
            last_x_pattern = tuple(last_x_spins)
            
            # Collect all sequences of length X within the tracking window (recent_spins)
            sequences = []
            for i in range(len(dozen_pattern) - sequence_length + 1):
                seq = tuple(dozen_pattern[i:i + sequence_length])
                # Only consider sequences that end before the last X spins
                if i + sequence_length <= len(dozen_pattern) - sequence_length:
                    sequences.append((i, seq))
            
            print(f"dozen_tracker: Found {len(sequences)} sequences of length {sequence_length} in the tracking window")

            # Check if the last X spins match any previous sequence
            for start_idx, seq in sequences:
                if seq == last_x_pattern:
                    # Check if we've already alerted for this exact pattern
                    if seq not in state.alerted_patterns:
                        sequence_matches.append((start_idx, seq))
                        # Get the next Y spins after the first occurrence
                        follow_up_start = start_idx + sequence_length
                        follow_up_end = follow_up_start + follow_up_spins
                        if follow_up_end <= len(dozen_pattern):
                            follow_up = dozen_pattern[follow_up_start:follow_up_end]
                            sequence_follow_ups.append((start_idx, seq, follow_up))
                        # Mark this pattern as alerted
                        state.alerted_patterns.add(seq)

            # If a match is found, provide betting recommendations with spin context
            if sequence_matches:
                latest_match = max(sequence_matches, key=lambda x: x[0])  # Latest match by start index
                latest_start_idx, matched_sequence = latest_match
                # Find the follow-up spins for the first occurrence of this sequence
                first_occurrence = min((seq for seq in sequences if seq[1] == matched_sequence), key=lambda x: x[0])[0]
                follow_up_start = first_occurrence + sequence_length
                follow_up_end = follow_up_start + follow_up_spins
                # Adjust indices for the full spin history
                latest_start_idx_full = len(full_dozen_pattern) - sequence_length
                # Get the actual spins that triggered the sequence
                sequence_spins = recent_spins[-sequence_length:]  # Last X spins
                sequence_spins_str = ", ".join(map(str, sequence_spins))
                if follow_up_end <= len(dozen_pattern):
                    follow_up = dozen_pattern[follow_up_start:follow_up_end]
                    alert_message = f"Alert: Sequence {', '.join(matched_sequence)} has repeated at spins {sequence_spins_str}!"
                    gr.Warning(alert_message)
                    sequence_recommendations.append(alert_message)
                    sequence_recommendations.append(f"Previous follow-up spins (next {follow_up_spins}): {', '.join(follow_up)}")
                    sequence_recommendations.append("Betting Recommendations (Bet Against Historical Follow-Ups):")
                    all_dozens = ["1st Dozen", "2nd Dozen", "3rd Dozen"]
                    for idx, dozen in enumerate(follow_up):
                        if dozen == "Not in Dozen":
                            sequence_recommendations.append(f"Spin {idx + 1}: 0 (Not in Dozen) - No bet recommendation.")
                        else:
                            dozens_to_bet = [d for d in all_dozens if d != dozen]
                            sequence_recommendations.append(f"Spin {idx + 1}: Bet against {dozen} - Bet on {', '.join(dozens_to_bet)}")
            else:
                # If no match is found, reset the alerted patterns to allow future matches
                state.alerted_patterns.clear()

    # Text summary for Dozen Tracker
    recommendations.append(f"Dozen Tracker (Last {len(recent_spins)} Spins):")
    recommendations.append("Dozen History: " + ", ".join(dozen_pattern))
    recommendations.append("\nSummary of Dozen Hits:")
    for name, count in dozen_counts.items():
        recommendations.append(f"{name}: {count} hits")

    # HTML representation for Dozen Tracker
    html_output = f'<h4>Dozen Tracker (Last {len(recent_spins)} Spins):</h4>'
    html_output += '<div style="display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 10px;">'
    for dozen in dozen_pattern:
        color = {
            "1st Dozen": "#FF6347",  # Tomato red
            "2nd Dozen": "#4682B4",  # Steel blue
            "3rd Dozen": "#32CD32",  # Lime green
            "Not in Dozen": "#808080"  # Gray for 0
        }.get(dozen, "#808080")
        html_output += f'<span style="background-color: {color}; color: white; padding: 2px 5px; border-radius: 3px; display: inline-block;">{dozen}</span>'
    html_output += '</div>'
    if alert_enabled and "Alert:" in "\n".join(recommendations):
        # Extract the alert message from recommendations
        alert_message = next((line for line in recommendations if line.startswith("Alert:")), "")
        html_output += f'<p style="color: red; font-weight: bold;">{alert_message}</p>'
    html_output += '<h4>Summary of Dozen Hits:</h4>'
    html_output += '<ul style="list-style-type: none; padding-left: 0;">'
    for name, count in dozen_counts.items():
        html_output += f'<li>{name}: {count} hits</li>'
    html_output += '</ul>'

    # HTML representation for Sequence Matching
    sequence_html_output = "<h4>Sequence Matching Results:</h4>"
    if not sequence_alert_enabled:
        sequence_html_output += "<p>Sequence matching is disabled. Enable it to see results.</p>"
    elif len(dozen_pattern) < sequence_length:
        sequence_html_output += f"<p>Not enough spins to match a sequence of length {sequence_length}.</p>"
    elif not sequence_matches:
        sequence_html_output += "<p>No sequence matches found yet.</p>"
    else:
        sequence_html_output += "<ul style='list-style-type: none; padding-left: 0;'>"
        for start_idx, seq in sequence_matches:
            # Adjust the start index for display based on the full spin history
            display_start_idx = len(full_dozen_pattern) - sequence_length
            sequence_html_output += f"<li>Match found at spins {display_start_idx + 1} to {display_start_idx + sequence_length}: {', '.join(seq)}</li>"
        sequence_html_output += "</ul>"
        if sequence_recommendations:
            sequence_html_output += "<h4>Latest Match Details:</h4>"
            sequence_html_output += "<ul style='list-style-type: none; padding-left: 0;'>"
            for rec in sequence_recommendations:
                if "Alert:" in rec:
                    sequence_html_output += f"<li style='color: red; font-weight: bold;'>{rec}</li>"
                else:
                    sequence_html_output += f"<li>{rec}</li>"
            sequence_html_output += "</ul>"

    return "\n".join(recommendations), html_output, sequence_html_output


    # New: Even Money Bet Tracker Function
def even_money_tracker(spins_to_check, consecutive_hits_threshold, alert_enabled, combination_mode, track_red, track_black, track_even, track_odd, track_low, track_high, identical_traits_enabled, consecutive_identical_count):
    """Track even money bets and their combinations for consecutive hits, with optional tracking of consecutive identical trait combinations."""
    # Sanitize inputs with defaults to prevent None or invalid values
    spins_to_check = int(spins_to_check) if spins_to_check and str(spins_to_check).strip().isdigit() else 5
    consecutive_hits_threshold = int(consecutive_hits_threshold) if consecutive_hits_threshold and str(consecutive_hits_threshold).strip().isdigit() else 3
    consecutive_identical_count = int(consecutive_identical_count) if consecutive_identical_count and str(consecutive_identical_count).strip().isdigit() else 2

    # Validate inputs
    if spins_to_check < 1 or consecutive_hits_threshold < 1 or consecutive_identical_count < 1:
        return "Error: Inputs must be at least 1.", "<div class='even-money-tracker-container'><p>Error: Inputs must be at least 1.</p></div>"

    # Get recent spins
    recent_spins = state.last_spins[-spins_to_check:] if len(state.last_spins) >= spins_to_check else state.last_spins
    if not recent_spins:
        return "Even Money Tracker: No spins recorded yet.", "<div class='even-money-tracker-container'><p>Even Money Tracker: No spins recorded yet.</p></div>"

    # Determine which categories to track
    categories_to_track = []
    if track_red:
        categories_to_track.append("Red")
    if track_black:
        categories_to_track.append("Black")
    if track_even:
        categories_to_track.append("Even")
    if track_odd:
        categories_to_track.append("Odd")
    if track_low:
        categories_to_track.append("Low")
    if track_high:
        categories_to_track.append("High")

    # If no categories are explicitly selected, track all categories by default
    if not categories_to_track:
        categories_to_track = ["Red", "Black", "Even", "Odd", "Low", "High"]

    # Map spins to even money categories and track full trait combinations
    pattern = []
    category_counts = {name: 0 for name in EVEN_MONEY.keys()}
    trait_combinations = []  # Store the full trait combination for each spin (e.g., "Red, Odd, Low")
    hit_spins = []  # Track spins for each pattern element (Hit/Miss)
    for spin in recent_spins:
        spin_value = int(spin)
        spin_categories = []
        for name, numbers in EVEN_MONEY.items():
            if spin_value in numbers:
                spin_categories.append(name)
                category_counts[name] += 1

        # Determine if the spin matches the tracked combination
        if combination_mode == "And":
            if all(cat in spin_categories for cat in categories_to_track):
                pattern.append("Hit")
                hit_spins.append(str(spin_value))
            else:
                pattern.append("Miss")
                hit_spins.append(str(spin_value))
        else:  # Or mode
            if any(cat in spin_categories for cat in categories_to_track):
                pattern.append("Hit")
                hit_spins.append(str(spin_value))
            else:
                pattern.append("Miss")
                hit_spins.append(str(spin_value))

        # Build the full trait combination for this spin (Color, Parity, Range)
        color = "Red" if "Red" in spin_categories else ("Black" if "Black" in spin_categories else "None")
        parity = "Even" if "Even" in spin_categories else ("Odd" if "Odd" in spin_categories else "None")
        range_ = "Low" if "Low" in spin_categories else ("High" if "High" in spin_categories else "None")
        trait_combination = f"{color}, {parity}, {range_}"
        trait_combinations.append(trait_combination)

    # Track consecutive hits of the selected combination with spin context
    current_streak = 1 if pattern[0] == "Hit" else 0
    max_streak = current_streak
    max_streak_start = 0
    current_streak_spins = [hit_spins[0]] if pattern[0] == "Hit" else []
    max_streak_spins = current_streak_spins[:]
    for i in range(1, len(pattern)):
        if pattern[i] == "Hit" and pattern[i-1] == "Hit":
            current_streak += 1
            current_streak_spins.append(hit_spins[i])
        else:
            current_streak = 1 if pattern[i] == "Hit" else 0
            current_streak_spins = [hit_spins[i]] if pattern[i] == "Hit" else []
        if current_streak > max_streak:
            max_streak = current_streak
            max_streak_start = i - current_streak + 1
            max_streak_spins = current_streak_spins[:]

    # Track consecutive identical trait combinations with spin context
    identical_recommendations = []
    identical_html_output = ""
    betting_recommendation = None
    if identical_traits_enabled:
        # Detect consecutive identical trait combinations
        identical_streak = 1
        identical_streak_start = 0
        identical_matches = []
        identical_streak_spins = [recent_spins[0]]  # Track spins for identical streaks
        for i in range(1, len(trait_combinations)):
            if trait_combinations[i] == trait_combinations[i-1] and trait_combinations[i] != "None, None, None":
                identical_streak += 1
                identical_streak_spins.append(recent_spins[i])
                if identical_streak == consecutive_identical_count:
                    identical_matches.append((i - consecutive_identical_count + 1, trait_combinations[i], identical_streak_spins[-consecutive_identical_count:]))
                    identical_streak_start = i - consecutive_identical_count + 1
            else:
                identical_streak = 1
                identical_streak_spins = [recent_spins[i]]
        if identical_matches:
            # Process the most recent match
            latest_match_start, matched_traits, matched_spins = identical_matches[-1]
            spins_str = ", ".join(map(str, matched_spins))
            if alert_enabled:
                gr.Warning(f"Alert: Traits '{matched_traits}' appeared {consecutive_identical_count} times consecutively! (Spins: {spins_str})")
            identical_recommendations.append(f"Alert: Traits '{matched_traits}' appeared {consecutive_identical_count} times consecutively! (Spins: {spins_str})")

            # Calculate opposite traits
            traits = [t.strip() for t in matched_traits.split(",")]
            opposite_traits = []
            for trait in traits:
                if trait == "Red":
                    opposite_traits.append("Black")
                elif trait == "Black":
                    opposite_traits.append("Red")
                elif trait == "Even":
                    opposite_traits.append("Odd")
                elif trait == "Odd":
                    opposite_traits.append("Even")
                elif trait == "Low":
                    opposite_traits.append("High")
                elif trait == "High":
                    opposite_traits.append("Low")
                else:
                    opposite_traits.append("None")
            opposite_combination = ", ".join(opposite_traits)
            identical_recommendations.append(f"Opposite Traits: {opposite_combination}")

            # Get the top-tier even money bet (highest score in even_money_scores)
            sorted_even_money = sorted(state.even_money_scores.items(), key=lambda x: x[1], reverse=True)
            even_money_hits = [item for item in sorted_even_money if item[1] > 0]
            if even_money_hits:
                top_tier_bet = even_money_hits[0][0]  # e.g., "Even"
                top_tier_score = even_money_hits[0][1]
                identical_recommendations.append(f"Current Top-Tier Even Money Bet (Yellow): {top_tier_bet} (Score: {top_tier_score})")

                # Correctly compare top-tier bet to the corresponding opposite trait
                opposites_map = {
                    "Red": "Black", "Black": "Red",
                    "Even": "Odd", "Odd": "Even",
                    "Low": "High", "High": "Low"
                }
                # Determine which trait category the top-tier bet belongs to
                trait_index = None
                if top_tier_bet in ["Red", "Black"]:
                    trait_index = 0  # Color
                elif top_tier_bet in ["Even", "Odd"]:
                    trait_index = 1  # Parity
                elif top_tier_bet in ["Low", "High"]:
                    trait_index = 2  # Range

                match_found = False
                if trait_index is not None:
                    corresponding_opposite = opposite_traits[trait_index]
                    # Check if the top-tier bet matches its opposite in the correct category
                    if top_tier_bet == corresponding_opposite:
                        match_found = True

                if match_found:
                    betting_recommendation = f"<span class='betting-recommendation'>Match found! Bet on '{top_tier_bet}' for the next 3 spins.</span>"
                    if alert_enabled:
                        gr.Warning(f"Match found! Bet on '{top_tier_bet}' for the next 3 spins.")
                    identical_recommendations.append(betting_recommendation)
                else:
                    identical_recommendations.append("No match with opposite traits. No betting recommendation.")
            else:
                identical_recommendations.append("No top-tier even money bet available (no hits yet).")

            # Build HTML output for identical traits tracking
            identical_html_output = "<div class='identical-traits-section'>"
            identical_html_output += "<h4>Consecutive Identical Traits Tracking:</h4>"
            identical_html_output += "<ul style='list-style-type: none; padding-left: 0;'>"
            for rec in identical_recommendations:
                if "Alert:" in rec or "Match found!" in rec and "betting-recommendation" not in rec:
                    identical_html_output += f"<li style='color: red; font-weight: bold;'>{rec}</li>"
                else:
                    identical_html_output += f"<li>{rec}</li>"
            identical_html_output += "</ul>"
            identical_html_output += "</div>"

    # Generate text and HTML for the original even money tracking with spin context
    tracked_str = " and ".join(categories_to_track) if combination_mode == "And" else " or ".join(categories_to_track)
    recommendations = []
    html_output = "<div class='even-money-tracker-container'>"
    recommendations.append(f"Even Money Tracker (Last {len(recent_spins)} Spins):")
    recommendations.append(f"Tracking: {tracked_str} ({combination_mode})")
    recommendations.append("History: " + ", ".join(pattern))
    if alert_enabled and max_streak >= consecutive_hits_threshold:
        # Include the spins that triggered the streak
        streak_spins = ", ".join(max_streak_spins[-consecutive_hits_threshold:])
        gr.Warning(f"Alert: {tracked_str} hit {max_streak} times consecutively! (Spins: {streak_spins})")
        recommendations.append(f"\nAlert: {tracked_str} hit {max_streak} times consecutively! (Spins: {streak_spins})")
    recommendations.append("\nSummary of Hits:")
    for name, count in category_counts.items():
        if name in categories_to_track:
            recommendations.append(f"{name}: {count} hits")

    html_output += f'<h4>Even Money Tracker (Last {len(recent_spins)} Spins):</h4>'
    html_output += f'<p>Tracking: {tracked_str} ({combination_mode})</p>'
    html_output += '<div style="display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 10px;">'
    for status, spin in zip(pattern, hit_spins):
        color = "#32CD32" if status == "Hit" else "#FF6347"  # Green for Hit, Red for Miss
        html_output += f'<span style="background-color: {color}; color: white; padding: 2px 5px; border-radius: 3px; display: inline-block;" title="Spin: {spin}">{status}</span>'
    html_output += '</div>'
    if alert_enabled and max_streak >= consecutive_hits_threshold:
        html_output += f'<p style="color: red; font-weight: bold;">Alert: {tracked_str} hit {max_streak} times consecutively! (Spins: {streak_spins})</p>'
    html_output += '<h4>Summary of Hits:</h4>'
    html_output += '<ul style="list-style-type: none; padding-left: 0;">'
    for name, count in category_counts.items():
        if name in categories_to_track:
            html_output += f'<li>{name}: {count} hits</li>'
    html_output += '</ul>'

    # Append the identical traits tracking output (if enabled)
    if identical_traits_enabled and identical_html_output:
        html_output += identical_html_output

    html_output += "</div>"

    return "\n".join(recommendations), html_output

def validate_hot_cold_numbers(numbers_input, type_label):
    """Validate hot or cold numbers input (1 to 10 numbers, 0-36)."""
    import gradio as gr
    if not numbers_input or not numbers_input.strip():
        return None, f"Please enter 1 to 10 {type_label} numbers."

    try:
        numbers = [int(n.strip()) for n in numbers_input.split(",") if n.strip()]
        if len(numbers) < 1 or len(numbers) > 10:
            return None, f"Enter 1 to 10 {type_label} numbers (entered {len(numbers)})."
        if not all(0 <= n <= 36 for n in numbers):
            return None, f"All {type_label} numbers must be between 0 and 36."
        return numbers, None
    except ValueError:
        return None, f"Invalid {type_label} numbers. Use comma-separated integers (e.g., 1, 3, 5, 7, 9)."

# Note: play_specific_numbers and clear_hot_cold_picks remain unchanged, e.g.:
def play_specific_numbers(numbers_input, type_label, current_spins_display, last_spin_count):
    """Add the specified hot or cold numbers as spins."""
    import gradio as gr
    try:
        numbers, error = validate_hot_cold_numbers(numbers_input, type_label)
        if error:
            gr.Warning(error)
            return current_spins_display, current_spins_display, error, update_spin_counter(), render_sides_of_zero_display()

        # Check spin limit
        if len(state.last_spins) + len(numbers) > 1000:
            error_msg = "Cannot add spins: Maximum 1000 spins exceeded."
            gr.Warning(error_msg)
            return current_spins_display, current_spins_display, error_msg, update_spin_counter(), render_sides_of_zero_display()

        new_spins = [str(n) for n in numbers]
        for spin in new_spins:
            add_spin(spin, current_spins_display, last_spin_count)  # Reuse add_spin for consistency

        # Update casino data
        state.casino_data[f"{type_label.lower()}_numbers"] = numbers
        spins_text = ", ".join(state.last_spins)
        success_msg = f"Played {type_label} numbers: {', '.join(new_spins)}"
        print(f"play_specific_numbers: {success_msg}")
        return spins_text, spins_text, success_msg, update_spin_counter(), render_sides_of_zero_display()
    except Exception as e:
        error_msg = f"Error playing {type_label} numbers: {str(e)}"
        print(f"play_specific_numbers: {error_msg}")
        gr.Warning(error_msg)
        return current_spins_display, current_spins_display, error_msg, update_spin_counter(), render_sides_of_zero_display()

def clear_hot_cold_picks(type_label, current_spins_display):
    """Clear hot or cold numbers input."""
    state.casino_data[f"{type_label.lower()}_numbers"] = []
    success_msg = f"Cleared {type_label} Picks successfully"
    print(f"clear_hot_cold_picks: {success_msg}")
    return "", success_msg, update_spin_counter(), render_sides_of_zero_display(), current_spins_display

def calculate_hit_percentages(last_spin_count):
    """Calculate hit percentages for Even Money Bets, Columns, and Dozens."""
    try:
        last_spin_count = int(last_spin_count) if last_spin_count is not None else 36
        last_spin_count = max(1, min(last_spin_count, 36))
        last_spins = state.last_spins[-last_spin_count:] if state.last_spins else []
        if not last_spins:
            return "<p>No spins available for analysis.</p>"

        total_spins = len(last_spins)
        even_money_counts = {"Red": 0, "Black": 0, "Even": 0, "Odd": 0, "Low": 0, "High": 0}
        column_counts = {"1st Column": 0, "2nd Column": 0, "3rd Column": 0}
        dozen_counts = {"1st Dozen": 0, "2nd Dozen": 0, "3rd Dozen": 0}

        for spin in last_spins:
            try:
                num = int(spin)
                for name, numbers in EVEN_MONEY.items():
                    if num in numbers:
                        even_money_counts[name] += 1
                for name, numbers in COLUMNS.items():
                    if num in numbers:
                        column_counts[name] += 1
                for name, numbers in DOZENS.items():
                    if num in numbers:
                        dozen_counts[name] += 1
            except ValueError:
                continue

        max_even_money = max(even_money_counts.values()) if even_money_counts else 0
        max_columns = max(column_counts.values()) if column_counts else 0
        max_dozens = max(dozen_counts.values()) if dozen_counts else 0

        html = '<div class="hit-percentage-overview">'
        html += f'<h4>Hit Percentage Overview (Last {total_spins} Spins):</h4>'
        html += '<div class="percentage-wrapper">'

        # Even Money Bets
        html += '<div class="percentage-group">'
        html += '<h4 style="color: #b71c1c;">Even Money Bets</h4>'
        html += '<div class="percentage-badges">'
        even_money_items = []
        for name, count in even_money_counts.items():
            percentage = (count / total_spins * 100) if total_spins > 0 else 0
            badge_class = "percentage-item even-money winner" if count == max_even_money and max_even_money > 0 else "percentage-item even-money"
            bar_color = "#b71c1c" if name == "Red" else "#000000" if name == "Black" else "#666"
            even_money_items.append(f'<div class="percentage-with-bar" data-category="even-money"><span class="{badge_class}">{name}: {percentage:.1f}%</span><div class="progress-bar"><div class="progress-fill" style="width: {percentage}%; background-color: {bar_color};"></div></div></div>')
        html += "".join(even_money_items)
        html += '</div></div>'

        # Columns
        html += '<div class="percentage-group">'
        html += '<h4 style="color: #1565c0;">Columns</h4>'
        html += '<div class="percentage-badges">'
        column_items = []
        for name, count in column_counts.items():
            percentage = (count / total_spins * 100) if total_spins > 0 else 0
            badge_class = "percentage-item column winner" if count == max_columns and max_columns > 0 else "percentage-item column"
            bar_color = "#1565c0"
            column_items.append(f'<div class="percentage-with-bar" data-category="columns"><span class="{badge_class}">{name.split()[0]}: {percentage:.1f}%</span><div class="progress-bar"><div class="progress-fill" style="width: {percentage}%; background-color: {bar_color};"></div></div></div>')
        html += "".join(column_items)
        html += '</div></div>'

        # Dozens
        html += '<div class="percentage-group">'
        html += '<h4 style="color: #388e3c;">Dozens</h4>'
        html += '<div class="percentage-badges">'
        dozen_items = []
        for name, count in dozen_counts.items():
            percentage = (count / total_spins * 100) if total_spins > 0 else 0
            badge_class = "percentage-item dozen winner" if count == max_dozens and max_dozens > 0 else "percentage-item dozen"
            bar_color = "#388e3c"
            dozen_items.append(f'<div class="percentage-with-bar" data-category="dozens"><span class="{badge_class}">{name.split()[0]}: {percentage:.1f}%</span><div class="progress-bar"><div class="progress-fill" style="width: {percentage}%; background-color: {bar_color};"></div></div></div>')
        html += "".join(dozen_items)
        html += '</div></div>'
        html += '</div></div>'  # Close percentage-wrapper and hit-percentage-overview
        return html
    except Exception as e:
        print(f"calculate_hit_percentages: Error: {str(e)}")
        return "<p>Error calculating hit percentages.</p>"

# Updated function with debug log
DEBUG = True  # Keep debugging enabled

def summarize_spin_traits(last_spin_count):
    """Summarize traits for the last X spins as HTML badges, highlighting winners and hot streaks."""
    try:
        if DEBUG:
            print(f"summarize_spin_traits: last_spin_count = {last_spin_count}")
        
        # Validate and clamp last_spin_count
        last_spin_count = int(last_spin_count) if last_spin_count is not None else 36
        last_spin_count = max(1, min(last_spin_count, 36))
        if DEBUG:
            print(f"summarize_spin_traits: After clamping, last_spin_count = {last_spin_count}")

        # Validate state
        if not hasattr(state, 'last_spins') or not isinstance(state.last_spins, list):
            if DEBUG:
                print(f"summarize_spin_traits: Invalid state.last_spins")
            return "<p>Error: Spin data not initialized.</p>"
        
        last_spins = state.last_spins[-last_spin_count:] if state.last_spins else []
        if DEBUG:
            print(f"summarize_spin_traits: last_spins = {last_spins}")
        if not last_spins:
            return "<p>No spins available for analysis.</p>"

        # Validate bet mappings
        if not all(x in globals() for x in ['EVEN_MONEY', 'COLUMNS', 'DOZENS']):
            missing = [x for x in ['EVEN_MONEY', 'COLUMNS', 'DOZENS'] if x not in globals()]
            if DEBUG:
                print(f"summarize_spin_traits: Missing bet mappings: {missing}")
            return "<p>Error: Bet mappings not defined.</p>"

        # Initialize counters and streaks
        even_money_counts = {"Red": 0, "Black": 0, "Even": 0, "Odd": 0, "Low": 0, "High": 0}
        column_counts = {"1st Column": 0, "2nd Column": 0, "3rd Column": 0}
        dozen_counts = {"1st Dozen": 0, "2nd Dozen": 0, "3rd Dozen": 0}
        number_counts = {}
        even_money_streaks = {key: {"current": 0, "max": 0, "last_hit": False, "spins": []} for key in even_money_counts}
        column_streaks = {key: {"current": 0, "max": 0, "last_hit": False, "spins": []} for key in column_counts}
        dozen_streaks = {key: {"current": 0, "max": 0, "last_hit": False, "spins": []} for key in dozen_counts}
        if DEBUG:
            print(f"summarize_spin_traits: Initialized counters and streaks")

        # Analyze spins
        for idx, spin in enumerate(last_spins):
            if DEBUG:
                print(f"summarize_spin_traits: Processing spin {idx}: {spin}")
            try:
                num = int(spin)
                if DEBUG:
                    print(f"summarize_spin_traits: Converted spin to integer: {num}")
                
                # Reset last_hit flags
                for key in even_money_streaks:
                    even_money_streaks[key]["last_hit"] = False
                for key in column_streaks:
                    column_streaks[key]["last_hit"] = False
                for key in dozen_streaks:
                    dozen_streaks[key]["last_hit"] = False
                if DEBUG:
                    print(f"summarize_spin_traits: Reset last_hit flags for spin {num}")

                # Even Money Bets
                for name, numbers in EVEN_MONEY.items():
                    if num in numbers:
                        even_money_counts[name] += 1
                        even_money_streaks[name]["last_hit"] = True
                        even_money_streaks[name]["current"] += 1
                        even_money_streaks[name]["spins"].append(str(num))
                        if len(even_money_streaks[name]["spins"]) > even_money_streaks[name]["current"]:
                            even_money_streaks[name]["spins"] = even_money_streaks[name]["spins"][-even_money_streaks[name]["current"]:]
                        even_money_streaks[name]["max"] = max(even_money_streaks[name]["max"], even_money_streaks[name]["current"])
                    else:
                        if not even_money_streaks[name]["last_hit"]:
                            even_money_streaks[name]["current"] = 0
                            even_money_streaks[name]["spins"] = []
                if DEBUG:
                    print(f"summarize_spin_traits: Processed Even Money Bets for spin {num}")

                # Columns
                for name, numbers in COLUMNS.items():
                    if num in numbers:
                        column_counts[name] += 1
                        column_streaks[name]["last_hit"] = True
                        column_streaks[name]["current"] += 1
                        column_streaks[name]["spins"].append(str(num))
                        if len(column_streaks[name]["spins"]) > column_streaks[name]["current"]:
                            column_streaks[name]["spins"] = column_streaks[name]["spins"][-column_streaks[name]["current"]:]
                        column_streaks[name]["max"] = max(column_streaks[name]["max"], column_streaks[name]["current"])
                    else:
                        if not column_streaks[name]["last_hit"]:
                            column_streaks[name]["current"] = 0
                            column_streaks[name]["spins"] = []
                if DEBUG:
                    print(f"summarize_spin_traits: Processed Columns for spin {num}")

                # Dozens
                for name, numbers in DOZENS.items():
                    if num in numbers:
                        dozen_counts[name] += 1
                        dozen_streaks[name]["last_hit"] = True
                        dozen_streaks[name]["current"] += 1
                        dozen_streaks[name]["spins"].append(str(num))
                        if len(dozen_streaks[name]["spins"]) > dozen_streaks[name]["current"]:
                            dozen_streaks[name]["spins"] = dozen_streaks[name]["spins"][-dozen_streaks[name]["current"]:]
                        dozen_streaks[name]["max"] = max(dozen_streaks[name]["max"], dozen_streaks[name]["current"])
                    else:
                        if not dozen_streaks[name]["last_hit"]:
                            dozen_streaks[name]["current"] = 0
                            dozen_streaks[name]["spins"] = []
                if DEBUG:
                    print(f"summarize_spin_traits: Processed Dozens for spin {num}")

                number_counts[num] = number_counts.get(num, 0) + 1
                if DEBUG:
                    print(f"summarize_spin_traits: Processed Repeat Numbers for spin {num}")
            except ValueError as ve:
                if DEBUG:
                    print(f"summarize_spin_traits: ValueError converting spin {spin} to integer: {str(ve)}")
                continue

        # Calculate max counts
        if DEBUG:
            print(f"summarize_spin_traits: Calculating max counts")
        max_even_money = max(even_money_counts.values()) if even_money_counts else 0
        max_columns = max(column_counts.values()) if column_counts else 0
        max_dozens = max(dozen_counts.values()) if dozen_counts else 0
        if DEBUG:
            print(f"summarize_spin_traits: Max counts - Even Money: {max_even_money}, Columns: {max_columns}, Dozens: {max_dozens}")

        # Quick Trends
        if DEBUG:
            print(f"summarize_spin_traits: Calculating Quick Trends")
        total_spins = len(last_spins)
        trends = []
        if total_spins > 0:
            all_counts = {**even_money_counts, **column_counts, **dozen_counts}
            dominant = max(all_counts.items(), key=lambda x: x[1], default=("None", 0))
            if dominant[1] > 0:
                percentage = (dominant[1] / total_spins * 100)
                trends.append(f"{dominant[0]} dominates with {percentage:.1f}% hits")
            all_streaks = {**even_money_streaks, **column_streaks, **dozen_streaks}
            longest_streak = max((v["current"] for v in all_streaks.values() if v["current"] > 1), default=0)
            if longest_streak > 1:
                streak_name = next(k for k, v in all_streaks.items() if v["current"] == longest_streak)
                streak_spins = ", ".join(all_streaks[streak_name]["spins"][-longest_streak:])
                trends.append(f"{streak_name} on a {longest_streak}-spin streak (Spins: {streak_spins})")
        if DEBUG:
            print(f"summarize_spin_traits: Quick Trends calculated: {trends}")

        # Build HTML
        if DEBUG:
            print(f"summarize_spin_traits: Building HTML")
        html = '<div class="traits-overview">'
        html += f'<h4>SpinTrend Radar (Last {len(last_spins)} Spins):</h4>'
        html += '<div class="traits-wrapper">'
        html += '<div class="quick-trends">'
        html += '<h4 style="color: #ff9800;">Quick Trends</h4>'
        if trends:
            html += '<ul style="list-style-type: none; padding-left: 0;">'
            for trend in trends:
                html += f'<li style="color: #333; margin: 5px 0;">{trend}</li>'
            html += '</ul>'
        else:
            html += '<p>No significant trends detected yet.</p>'
        html += '</div>'
        if DEBUG:
            print(f"summarize_spin_traits: Quick Trends HTML generated")

        # Even Money Bets
        html += '<div class="badge-group">'
        html += '<h4 style="color: #b71c1c;">Even Money Bets</h4>'
        html += '<div class="percentage-badges">'
        for name, count in even_money_counts.items():
            badge_class = "trait-badge even-money winner" if count == max_even_money and max_even_money > 0 else "trait-badge even-money"
            streak = even_money_streaks[name]["max"]
            streak_title = f"{name} Hot Streak: {streak} consecutive hits" if streak >= 3 else ""
            percentage = (count / total_spins * 100) if total_spins > 0 else 0
            bar_color = "#b71c1c" if name in ["Red", "Even", "Low"] else "#000000" if name in ["Black", "Odd", "High"] else "#666"
            html += f'<div class="percentage-with-bar" data-category="even-money"><span class="{badge_class}" title="{streak_title}">{name}: {count}</span><div class="progress-bar"><div class="progress-fill" style="width: {percentage}%; background-color: {bar_color};"></div></div></div>'
        html += '</div></div>'
        if DEBUG:
            print(f"summarize_spin_traits: Even Money Bets HTML generated")

        # Columns
        html += '<div class="badge-group">'
        html += '<h4 style="color: #1565c0;">Columns</h4>'
        html += '<div class="percentage-badges">'
        for name, count in column_counts.items():
            badge_class = "trait-badge column winner" if count == max_columns and max_columns > 0 else "trait-badge column"
            streak = column_streaks[name]["max"]
            streak_title = f"{name} Hot Streak: {streak} consecutive hits" if streak >= 3 else ""
            percentage = (count / total_spins * 100) if total_spins > 0 else 0
            bar_color = "#1565c0"
            html += f'<div class="percentage-with-bar" data-category="columns"><span class="{badge_class}" title="{streak_title}">{name}: {count}</span><div class="progress-bar"><div class="progress-fill" style="width: {percentage}%; background-color: {bar_color};"></div></div></div>'
        html += '</div></div>'
        if DEBUG:
            print(f"summarize_spin_traits: Columns HTML generated")

        # Dozens
        html += '<div class="badge-group">'
        html += '<h4 style="color: #388e3c;">Dozens</h4>'
        html += '<div class="percentage-badges">'
        for name, count in dozen_counts.items():
            badge_class = "trait-badge dozen winner" if count == max_dozens and max_dozens > 0 else "trait-badge dozen"
            streak = dozen_streaks[name]["max"]
            streak_title = f"{name} Hot Streak: {streak} consecutive hits" if streak >= 3 else ""
            percentage = (count / total_spins * 100) if total_spins > 0 else 0
            bar_color = "#388e3c"
            html += f'<div class="percentage-with-bar" data-category="dozens"><span class="{badge_class}" title="{streak_title}">{name}: {count}</span><div class="progress-bar"><div class="progress-fill" style="width: {percentage}%; background-color: {bar_color};"></div></div></div>'
        html += '</div></div>'
        if DEBUG:
            print(f"summarize_spin_traits: Dozens HTML generated")

        # Repeat Numbers
        html += '<div class="badge-group">'
        html += '<h4 style="color: #7b1fa2;">Repeat Numbers</h4>'
        html += '<div class="percentage-badges">'
        repeats = {num: count for num, count in number_counts.items() if count > 1}
        if repeats:
            for num, count in sorted(repeats.items()):
                html += f'<span class="trait-badge repeat">{num}: {count} hits</span>'
        else:
            html += '<span class="trait-badge repeat">No repeats</span>'
        html += '</div></div>'
        html += '</div></div>'  # Close traits-wrapper and traits-overview
        if DEBUG:
            print(f"summarize_spin_traits: Repeat Numbers HTML generated")

        if DEBUG:
            print(f"summarize_spin_traits: Returning HTML successfully")
        return html

    except Exception as e:
        if DEBUG:
            print(f"summarize_spin_traits: Caught exception: {str(e)}")
        raise  # Re-raise to see the full stack trace in logs
        return "<p>Error analyzing spin traits.</p>"

def cache_analysis(spins, last_spin_count):
    """Cache the results of summarize_spin_traits to avoid redundant calculations."""
    spins_list = state.last_spins if hasattr(state, 'last_spins') else []
    if not spins_list and isinstance(spins, str) and spins.strip():
        spins_list = [s.strip() for s in spins.split(",") if s.strip()]
    
    cache_key = f"{last_spin_count}_{hash(tuple(spins_list))}"
    if cache_key in state.analysis_cache:
        if DEBUG:
            print(f"cache_analysis: Cache hit for key {cache_key}")
        return state.analysis_cache[cache_key]
    
    # Limit cache size
    MAX_CACHE_SIZE = 100
    if len(state.analysis_cache) >= MAX_CACHE_SIZE:
        oldest_key = next(iter(state.analysis_cache))
        del state.analysis_cache[oldest_key]
        if DEBUG:
            print(f"cache_analysis: Removed oldest cache entry {oldest_key}")
    
    # Perform analysis
    result = summarize_spin_traits(last_spin_count)
    state.analysis_cache[cache_key] = result
    if DEBUG:
        print(f"cache_analysis: Cached result for key {cache_key}")
    return result


def select_next_spin_top_pick(last_spin_count):
    try:
        last_spin_count = int(last_spin_count) if last_spin_count is not None else 18
        last_spin_count = max(1, min(last_spin_count, 36))
        last_spins = state.last_spins[-last_spin_count:] if state.last_spins else []
        if not last_spins:
            return "<p>No spins available for analysis.</p>"
        # Log the spins being analyzed
        print(f"Analyzing last {last_spin_count} spins: {last_spins}")
        numbers = set(range(37))
        hit_counts = {n: 0 for n in range(37)}
        last_positions = {n: -1 for n in range(37)}
        for i, spin in enumerate(last_spins):
            try:
                num = int(spin)
                hit_counts[num] += 1
                last_positions[num] = i
            except ValueError:
                continue
        even_money_counts = {"Red": 0, "Black": 0, "Even": 0, "Odd": 0, "Low": 0, "High": 0}
        column_counts = {"1st Column": 0, "2nd Column": 0, "3rd Column": 0}
        dozen_counts = {"1st Dozen": 0, "2nd Dozen": 0, "3rd Dozen": 0}
        for spin in last_spins:
            try:
                num = int(spin)
                for name, nums in EVEN_MONEY.items():
                    if num in nums:
                        even_money_counts[name] += 1
                for name, nums in COLUMNS.items():
                    if num in nums:
                        column_counts[name] += 1
                for name, nums in DOZENS.items():
                    if num in nums:
                        dozen_counts[name] += 1
            except ValueError:
                continue
        # Calculate percentages for all traits
        total_spins = len(last_spins)
        trait_percentages = {}
        # Even Money
        for trait, count in even_money_counts.items():
            trait_percentages[trait] = (count / total_spins) * 100 if total_spins > 0 else 0
        # Dozens
        for trait, count in dozen_counts.items():
            trait_percentages[trait] = (count / total_spins) * 100 if total_spins > 0 else 0
        # Columns
        for trait, count in column_counts.items():
            trait_percentages[trait] = (count / total_spins) * 100 if total_spins > 0 else 0
        # Sort traits by percentage (highest to lowest)
        sorted_traits = sorted(trait_percentages.items(), key=lambda x: (-x[1], x[0]))
        # Determine hottest traits (top non-conflicting traits)
        hottest_traits = []
        seen_categories = set()
        for trait, percentage in sorted_traits:
            # Skip if this trait conflicts with a higher-percentage trait in the same category
            if trait in ["Red", "Black"]:
                if "Red-Black" in seen_categories:
                    continue
                hottest_traits.append(trait)
                seen_categories.add("Red-Black")
            elif trait in ["Even", "Odd"]:
                if "Even-Odd" in seen_categories:
                    continue
                hottest_traits.append(trait)
                seen_categories.add("Even-Odd")
            elif trait in ["Low", "High"]:
                if "Low-High" in seen_categories:
                    continue
                hottest_traits.append(trait)
                seen_categories.add("Low-High")
            elif trait in ["1st Dozen", "2nd Dozen", "3rd Dozen"]:
                if "Dozens" in seen_categories:
                    continue
                hottest_traits.append(trait)
                seen_categories.add("Dozens")
            elif trait in ["1st Column", "2nd Column", "3rd Column"]:
                if "Columns" in seen_categories:
                    continue
                hottest_traits.append(trait)
                seen_categories.add("Columns")
        # Second best traits for tiebreakers
        second_best_traits = []
        seen_categories = set()
        for trait, percentage in sorted_traits:
            if trait in hottest_traits:
                continue
            if trait in ["Red", "Black"]:
                if "Red-Black" in seen_categories:
                    continue
                second_best_traits.append(trait)
                seen_categories.add("Red-Black")
            elif trait in ["Even", "Odd"]:
                if "Even-Odd" in seen_categories:
                    continue
                second_best_traits.append(trait)
                seen_categories.add("Even-Odd")
            elif trait in ["Low", "High"]:
                if "Low-High" in seen_categories:
                    continue
                second_best_traits.append(trait)
                seen_categories.add("Low-High")
            elif trait in ["1st Dozen", "2nd Dozen", "3rd Dozen"]:
                if "Dozens" in seen_categories:
                    continue
                second_best_traits.append(trait)
                seen_categories.add("Dozens")
            elif trait in ["1st Column", "2nd Column", "3rd Column"]:
                if "Columns" in seen_categories:
                    continue
                second_best_traits.append(trait)
                seen_categories.add("Columns")
        left_side = set(LEFT_OF_ZERO_EUROPEAN)
        right_side = set(RIGHT_OF_ZERO_EUROPEAN)
        left_hits = sum(hit_counts[num] for num in left_side)
        right_hits = sum(hit_counts[num] for num in right_side)
        most_hit_side = "Left" if left_hits > right_hits else "Right" if right_hits > left_hits else "Both"
        betting_sections = {
            "Voisins du Zero": [22, 18, 29, 7, 28, 12, 35, 3, 26, 0, 32, 15, 19, 4, 21, 2, 25],
            "Orphelins": [17, 34, 6, 1, 20, 14, 31, 9],
            "Tiers du Cylindre": [27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33]
        }
        section_hits = {name: sum(hit_counts[num] for num in nums) for name, nums in betting_sections.items()}
        section_last_pos = {name: -1 for name in betting_sections}
        for name, nums in betting_sections.items():
            for num in nums:
                if last_positions[num] > section_last_pos[name]:
                    section_last_pos[name] = last_positions[num]
        sorted_sections = sorted(section_hits.items(), key=lambda x: (-x[1], -section_last_pos[x[0]]))
        top_section = sorted_sections[0][0] if sorted_sections else None
        neighbor_boost = {num: 0 for num in range(37)}
        last_five = last_spins[-5:] if len(last_spins) >= 5 else last_spins
        last_five_set = set(last_five)
        for num in range(37):
            if num in NEIGHBORS_EUROPEAN:
                left, right = NEIGHBORS_EUROPEAN[num]
                if left is not None and str(left) in last_five_set:
                    neighbor_boost[num] += 2
                if right is not None and str(right) in last_five_set:
                    neighbor_boost[num] += 2
        # Score numbers based on the number of matching traits in order
        scores = []
        for num in range(37):
            if num not in hit_counts or hit_counts[num] == 0:
                continue  # Only consider numbers that appear in the spins
            # Count matching traits in order
            matching_traits = 0
            for trait in hottest_traits:
                if trait in EVEN_MONEY and num in EVEN_MONEY[trait]:
                    matching_traits += 1
                elif trait in DOZENS and num in DOZENS[trait]:
                    matching_traits += 1
                elif trait in COLUMNS and num in COLUMNS[trait]:
                    matching_traits += 1
            # Secondary score for second best traits
            secondary_matches = 0
            for trait in second_best_traits:
                if trait in EVEN_MONEY and num in EVEN_MONEY[trait]:
                    secondary_matches += 1
                elif trait in DOZENS and num in DOZENS[trait]:
                    secondary_matches += 1
                elif trait in COLUMNS and num in COLUMNS[trait]:
                    secondary_matches += 1
            # Additional scoring factors
            wheel_side_score = 0
            if most_hit_side == "Both" or (most_hit_side == "Left" and num in left_side) or (most_hit_side == "Right" and num in right_side):
                wheel_side_score = 5
            section_score = 10 if top_section and num in betting_sections[top_section] else 0
            recency_score = (last_spin_count - (last_positions[num] + 1)) * 1.0 if last_positions[num] >= 0 else 0
            if last_positions[num] == last_spin_count - 1:
                recency_score = max(recency_score, 10)
            hit_bonus = 5 if hit_counts[num] > 0 else 0
            neighbor_score = neighbor_boost[num]
            tiebreaker_score = 0
            if num == 0:
                pass
            else:
                if num in EVEN_MONEY["Red"]:
                    tiebreaker_score += even_money_counts["Red"]
                elif num in EVEN_MONEY["Black"]:
                    tiebreaker_score += even_money_counts["Black"]
                if num in EVEN_MONEY["Even"]:
                    tiebreaker_score += even_money_counts["Even"]
                elif num in EVEN_MONEY["Odd"]:
                    tiebreaker_score += even_money_counts["Odd"]
                if num in EVEN_MONEY["Low"]:
                    tiebreaker_score += even_money_counts["Low"]
                elif num in EVEN_MONEY["High"]:
                    tiebreaker_score += even_money_counts["High"]
            for name, nums in DOZENS.items():
                if num in nums:
                    tiebreaker_score += dozen_counts[name]
                    break
            for name, nums in COLUMNS.items():
                if num in nums:
                    tiebreaker_score += column_counts[name]
                    break
            total_score = matching_traits * 100 + secondary_matches * 10 + wheel_side_score + section_score + recency_score + hit_bonus + neighbor_score
            scores.append((num, total_score, matching_traits, secondary_matches, wheel_side_score, section_score, recency_score, hit_bonus, neighbor_score, tiebreaker_score))
        # Sort by number of matching traits, then secondary matches, then tiebreaker, then recency
        scores.sort(key=lambda x: (-x[2], -x[3], -x[9], -x[6], -x[0]))
        # Ensure top 10 picks have at least as many matches as the 10th pick
        if len(scores) > 10:
            min_traits = sorted([x[2] for x in scores[:10]], reverse=True)[9]
            top_picks = [x for x in scores if x[2] >= min_traits][:10]
        else:
            top_picks = scores[:10]
        state.current_top_pick = top_picks[0][0]
        top_pick = top_picks[0][0]
        # Calculate confidence based on matching traits
        max_possible_traits = len(hottest_traits)
        top_traits_matched = top_picks[0][2]
        confidence = max(0, min(100, int((top_traits_matched / max_possible_traits) * 100)))
        characteristics = []
        top_pick_int = int(top_pick)
        if top_pick_int == 0:
            characteristics.append("Green")
        elif "Red" in EVEN_MONEY and top_pick_int in EVEN_MONEY["Red"]:
            characteristics.append("Red")
        elif "Black" in EVEN_MONEY and top_pick_int in EVEN_MONEY["Black"]:
            characteristics.append("Black")
        if top_pick_int != 0:
            if "Even" in EVEN_MONEY and top_pick_int in EVEN_MONEY["Even"]:
                characteristics.append("Even")
            elif "Odd" in EVEN_MONEY and top_pick_int in EVEN_MONEY["Odd"]:
                characteristics.append("Odd")
            if "Low" in EVEN_MONEY and top_pick_int in EVEN_MONEY["Low"]:
                characteristics.append("Low")
            elif "High" in EVEN_MONEY and top_pick_int in EVEN_MONEY["High"]:
                characteristics.append("High")
        for name, nums in DOZENS.items():
            if top_pick_int in nums:
                characteristics.append(name)
                break
        for name, nums in COLUMNS.items():
            if top_pick_int in nums:
                characteristics.append(name)
                break
        characteristics_str = ", ".join(characteristics) if characteristics else "No notable characteristics"
        color = colors.get(str(top_pick), "black")
        _, total_score, matching_traits, secondary_matches, wheel_side_score, section_score, recency_score, hit_bonus, neighbor_score, tiebreaker_score = top_picks[0]
        reasons = []
        matched_traits = []
        for trait in hottest_traits:
            if trait in EVEN_MONEY and top_pick in EVEN_MONEY[trait]:
                matched_traits.append(trait)
            elif trait in DOZENS and top_pick in DOZENS[trait]:
                matched_traits.append(trait)
            elif trait in COLUMNS and top_pick in COLUMNS[trait]:
                matched_traits.append(trait)
        if matched_traits:
            reasons.append(f"Matches the hottest traits: {', '.join(matched_traits)}")
        if section_score > 0:
            reasons.append(f"Located in the hottest wheel section: {top_section}")
        if recency_score > 0:
            last_pos = last_positions[top_pick]
            reasons.append(f"Recently appeared in the spin history (position {last_pos})")
        if hit_bonus > 0:
            reasons.append(f"Has appeared in the spin history")
        if wheel_side_score > 0:
            reasons.append(f"On the most hit side of the wheel: {most_hit_side}")
        if neighbor_score > 0:
            neighbors_hit = [str(n) for n in NEIGHBORS_EUROPEAN.get(top_pick, (None, None)) if str(n) in last_five_set]
            reasons.append(f"Has recent neighbors in the last 5 spins: {', '.join(neighbors_hit)}")
        if tiebreaker_score > 0:
            reasons.append(f"Boosted by aggregated trait scores (tiebreaker: {tiebreaker_score})")
        reasons_html = "<ul>" + "".join(f"<li>{reason}</li>" for reason in reasons) + "</ul>" if reasons else "<p>No specific reasons available.</p>"
        last_five_spins = last_spins[-5:] if len(last_spins) >= 5 else last_spins
        last_five_spins_html = ""
        for spin in last_five_spins:
            spin_color = colors.get(str(spin), "black")
            last_five_spins_html += f'<span class="first-spin {spin_color}">{spin}</span>'
        top_5_html = ""
        for i, (num, total_score, matching_traits, secondary_matches, wheel_side_score, section_score, recency_score, hit_bonus, neighbor_score, tiebreaker_score) in enumerate(top_picks[1:10], 1):
            num_color = colors.get(str(num), "black")
            num_characteristics = []
            if num == 0:
                num_characteristics.append("Green")
            elif "Red" in EVEN_MONEY and num in EVEN_MONEY["Red"]:
                num_characteristics.append("Red")
            elif "Black" in EVEN_MONEY and num in EVEN_MONEY["Black"]:
                num_characteristics.append("Black")
            if num != 0:
                if "Even" in EVEN_MONEY and num in EVEN_MONEY["Even"]:
                    num_characteristics.append("Even")
                elif "Odd" in EVEN_MONEY and num in EVEN_MONEY["Odd"]:
                    num_characteristics.append("Odd")
                if "Low" in EVEN_MONEY and num in EVEN_MONEY["Low"]:
                    num_characteristics.append("Low")
                elif "High" in EVEN_MONEY and top_pick_int in EVEN_MONEY["High"]:
                    num_characteristics.append("High")
            for name, nums in DOZENS.items():
                if num in nums:
                    num_characteristics.append(name)
                    break
            for name, nums in COLUMNS.items():
                if num in nums:
                    num_characteristics.append(name)
                    break
            num_characteristics_str = ", ".join(num_characteristics) if num_characteristics else "No notable characteristics"
            num_reasons = []
            num_matched_traits = []
            for trait in hottest_traits:
                if trait in EVEN_MONEY and num in EVEN_MONEY[trait]:
                    num_matched_traits.append(trait)
                elif trait in DOZENS and num in DOZENS[trait]:
                    num_matched_traits.append(trait)
                elif trait in COLUMNS and num in COLUMNS[trait]:
                    num_matched_traits.append(trait)
            if num_matched_traits:
                num_reasons.append(f"Matches: {', '.join(num_matched_traits)}")
            for section_name, nums in betting_sections.items():
                if num in nums:
                    num_reasons.append(f"In {section_name}")
                    break
            if tiebreaker_score > 0:
                num_reasons.append(f"Tiebreaker: {tiebreaker_score}")
            num_reasons_str = ", ".join(num_reasons) if num_reasons else "No notable reasons"
            top_5_html += f'''
            <div class="secondary-pick">
              <span class="secondary-badge {num_color}" data-number="{num}">{num}</span>
              <div class="secondary-info">
                <div class="secondary-characteristics">
                  {''.join(f'<span class="char-badge {char.lower()}">{char}</span>' for char in num_characteristics_str.split(", "))}
                </div>
                <div class="secondary-reasons">{num_reasons_str}</div>
              </div>
            </div>
            '''
        html = f'''
        <div class="first-spins">
          <h5>Last 5 Spins</h5>
          <div class="first-spins-container">{last_five_spins_html}</div>
        </div>
        <div class="top-pick-container">
          <h4>Top Pick for Next Spin</h4>
          <div class="top-pick-wrapper">
            <div class="badge-wrapper">
              <span class="top-pick-badge {color}" data-number="{top_pick}" onclick="copyToClipboard('{top_pick}')">{top_pick}</span>
            </div>
            <div class="top-pick-characteristics">
              {''.join(f'<span class="char-badge {char.lower()}">{char}</span>' for char in characteristics_str.split(", "))}
            </div>
          </div>
          <div class="confidence-bar">
            <div class="confidence-fill" style="width: {confidence}%"></div>
            <span>Confidence: {confidence}%</span>
          </div>
          <p class="top-pick-description">Based on analysis of the last {last_spin_count} spins.</p>
          <div class="accordion">
            <input type="checkbox" id="reasons-toggle" class="accordion-toggle">
            <label for="reasons-toggle" class="accordion-header">Why This Number Was Chosen</label>
            <div class="accordion-content">
              <div class="top-pick-reasons">
                {reasons_html}
              </div>
            </div>
          </div>
          <div class="secondary-picks">
            <h5>Other Top Picks</h5>
            <div class="secondary-picks-container">
              {top_5_html}
            </div>
          </div>
        </div>
        <style>
          @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');
          @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
          }}
          @keyframes confetti {{
            0% {{ transform: translateY(0) rotate(0deg); opacity: 1; }}
            100% {{ transform: translateY(100vh) rotate(720deg); opacity: 0; }}
          }}
          .first-spins {{
            margin-bottom: 10px;
            text-align: center;
          }}
          .first-spins h5 {{
            margin: 0 0 5px 0;
            color: #FFD700;
            font-family: 'Montserrat', sans-serif;
            font-size: 16px;
            text-transform: uppercase;
          }}
          .first-spins-container {{
            display: flex;
            justify-content: center;
            gap: 5px;
          }}
          .first-spin {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 30px;
            height: 30px;
            border-radius: 15px;
            font-size: 18px;
            font-weight: bold;
            color: #ffffff !important;
            border: 1px solid #ffffff;
            box-shadow: 0 0 5px rgba(0, 0, 0, 0.3);
          }}
          .first-spin.red {{ background-color: red; }}
          .first-spin.black {{ background-color: black; }}
          .first-spin.green {{ background-color: green; }}
          .accordion {{
            margin: 10px 0;
            border: 1px solid #FFD700;
            border-radius: 8px;
            background: linear-gradient(135deg, #2E8B57, #FFD700);
            transition: all 0.3s ease;
          }}
          .accordion-toggle {{
            display: none;
          }}
          .accordion-header {{
            padding: 12px;
            font-weight: bold;
            font-size: 18px;
            color: #FFD700;
            cursor: pointer;
            text-transform: uppercase;
            display: flex;
            align-items: center;
            gap: 8px;
            font-family: 'Montserrat', sans-serif;
            position: sticky;
            top: 0;
            z-index: 10;
            background: inherit;
          }}
          .chip-icon {{
            font-size: 20px;
          }}
          .accordion-header:hover {{
            background-color: rgba(255, 255, 255, 0.2);
          }}
          .accordion-content {{
            display: none !important;
            animation: fadeIn 0.5s ease-in-out;
          }}
          .accordion-toggle:checked + .accordion-header + .accordion-content {{
            display: block !important;
          }}
          .top-pick-container {{
            background: linear-gradient(135deg, #2E8B57, #FFD700);
            border: 3px solid #FFD700;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
            margin: 10px 0;
          }}
          .top-pick-container h4 {{
            margin: 0 0 15px 0;
            color: #FFD700;
            font-size: 24px;
            font-weight: bold;
            text-transform: uppercase;
            font-family: 'Montserrat', sans-serif;
          }}
          .top-pick-wrapper {{
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 10px;
          }}
          .badge-wrapper {{
            display: flex;
            align-items: center;
            gap: 10px;
          }}
          .top-pick-badge {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 60px;
            height: 60px;
            border-radius: 30px;
            font-weight: bold;
            font-size: 28px;
            color: #ffffff !important;
            background-color: {color};
            border: 2px solid #ffffff;
            box-shadow: 0 0 12px rgba(0, 0, 0, 0.3);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            cursor: pointer;
            position: relative;
          }}
          .top-pick-badge:hover {{
            transform: rotate(360deg) scale(1.2);
            box-shadow: 0 0 20px rgba(255, 215, 0, 0.8);
          }}
          .top-pick-badge.red {{ background-color: red; }}
          .top-pick-badge.black {{ background-color: black; }}
          .top-pick-badge.green {{ background-color: green; }}
          .top-pick-characteristics {{
            display: flex;
            gap: 5px;
            flex-wrap: wrap;
            justify-content: center;
          }}
          .char-badge {{
            background-color: rgba(255, 213, 0, 0.9);
            color: #FFD700;
            font-weight: bold;
            font-size: 14px;
            padding: 3px 8px;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
          }}
          .char-badge.red {{ background-color: #FF0000; color: #ffffff; }}
          .char-badge.black {{ background-color: #000000; color: #ffffff; }}
          .char-badge.even {{ background-color: #4682B4; color: #ffffff; }}
          .char-badge.odd {{ background-color: #4682B4; color: #ffffff; }}
          .char-badge.low {{ background-color: #32CD32; color: #ffffff; }}
          .char-badge.high {{ background-color: #32CD32; color: #ffffff; }}
          .confidence-bar {{
            margin-top: 10px;
            background-color: #2E8B57;
            border-radius: 5px;
            height: 20px;
            position: relative;
            overflow: hidden;
          }}
          .confidence-fill {{
            height: 100%;
            background-color: #FFD700;
            transition: width 1s ease;
          }}
          .confidence-bar span {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: #2E8B57;
            font-size: 12px;
            font-weight: bold;
          }}
          .top-pick-description {{
            margin-top: 15px;
            font-style: italic;
            color: #3e2723;
            font-size: 14px;
          }}
          .top-pick-reasons {{
            padding: 10px;
            color: #3e2723;
            font-size: 14px;
          }}
          .top-pick-reasons ul {{
            list-style-type: disc;
            padding-left: 20px;
            margin: 0;
          }}
          .top-pick-reasons li {{
            margin-bottom: 5px;
          }}
          .secondary-picks {{
            margin-top: 20px;
            text-align: center;
          }}
          .secondary-picks h5 {{
            margin: 0 0 10px 0;
            color: #FFD700;
            font-family: 'Montserrat', sans-serif;
            font-size: 16px;
            text-transform: uppercase;
          }}
          .secondary-picks-container {{
            display: flex;
            justify-content: center;
            gap: 15px;
            flex-wrap: wrap;
          }}
          .secondary-pick {{
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 5px;
          }}
          .secondary-badge {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 50px;
            height: 50px;
            border-radius: 25px;
            font-weight: bold;
            font-size: 28px;
            color: #ffffff !important;
            border: 2px solid #ffffff;
            box-shadow: 0 0 8px rgba(0, 0, 0, 0.2);
            position: relative;
            transition: transform 0.3s ease;
          }}
          .secondary-badge:hover {{
            transform: rotate(360deg) scale(1.2);
          }}
          .secondary-badge.red {{ background-color: red; }}
          .secondary-badge.black {{ background-color: black; }}
          .secondary-badge.green {{ background-color: green; }}
          .secondary-info {{
            text-align: center;
          }}
          .secondary-characteristics {{
            display: flex;
            gap: 5px;
            flex-wrap: wrap;
            justify-content: center;
          }}
          .secondary-reasons {{
            font-size: 10px;
            color: #3e2723;
            font-style: italic;
          }}
          .celebration {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 1000;
          }}
          .confetti {{
            position: absolute;
            width: 10px;
            height: 10px;
            background-color: #FFD700;
            animation: confetti 2s ease infinite;
          }}
          @media (max-width: 600px) {{
            .top-pick-badge {{
              width: 50px;
              height: 50px;
              font-size: 24px;
            }}
            .first-spin {{
              width: 25px;
              height: 25px;
              font-size: 14px;
            }}
            .secondary-badge {{
              width: 40px;
              height: 40px;
              font-size: 20px;
            }}
            .top-pick-container h4 {{
              font-size: 20px;
            }}
            .accordion-header {{
              font-size: 16px;
            }}
          }}
        </style>
        <script>
          function triggerConfetti() {{
            const celebration = document.querySelector('.celebration');
            for (let i = 0; i < 50; i++) {{
              const confetti = document.createElement('div');
              confetti.className = 'confetti';
              confetti.style.left = Math.random() * 100 + 'vw';
              confetti.style.backgroundColor = ['#FFD700', '#FF0000', '#2E8B57'][Math.floor(Math.random() * 3)];
              confetti.style.animationDelay = Math.random() * 2 + 's';
              celebration.appendChild(confetti);
            }}
          }}
          function copyToClipboard(text) {{
            navigator.clipboard.writeText(text).then(() => {{
              alert('Number ' + text + ' copied to clipboard!');
            }}).catch(err => {{
              console.error('Failed to copy: ', err);
            }});
          }}
        </script>
        '''
        return html
    except Exception as e:
        print(f"select_next_spin_top_pick: Error: {str(e)}")
        return "<p>Error selecting top pick.</p>"

# Lines after (context, unchanged from Part 2)
with gr.Blocks(title="WheelPulse by S.T.Y.W 📈") as demo:
    # 1. Row 1: Header (Moved to the top)
    with gr.Row(elem_id="header-row"):
        gr.Markdown("<h1 style='text-align: center; color: #ff9800;'>WheelPulse by S.T.Y.W 📈</h1>")
        gr.HTML(
            '''
            <div style="display: flex; gap: 10px; justify-content: center; align-items: center;">
                <button id="start-tour-btn" onclick="startTour()" style="width: 150px; height: 40px; padding: 8px 15px; background-color: #ff9800; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 14px; font-weight: bold; line-height: 1; transition: transform 0.2s ease; box-sizing: border-box;">🚀 Take the Tour!</button>
                <a href="https://drive.google.com/file/d/154GfZaiNUfAFB73WEIA617ofdZbRaEIN/view?usp=drive_link" target="_blank" style="width: 150px; height: 40px; padding: 8px 15px; background-color: #dc3545; color: white; text-decoration: none; border-radius: 5px; font-size: 14px; font-weight: bold; line-height: 1; transition: transform 0.2s ease; box-sizing: border-box; display: inline-block; text-align: center;">📖 View Guide</a>
            </div>
            <style>
                #start-tour-btn:hover, a[href*="drive.google.com"]:hover {
                    transform: scale(1.05);
                    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                }
            </style>
            '''
        )

    # Define state and components used across sections
    spins_display = gr.State(value="")
    show_trends_state = gr.State(value=True)  # Default to showing trends
    toggle_trends_label = gr.State(value="Hide Trends")  # Default label when trends are shown
    analysis_cache = gr.State(value={})  # New: Cache for analysis results
    spins_textbox = gr.Textbox(
        label="Selected Spins (Edit manually with commas, e.g., 5, 12, 0)",
        value="",
        interactive=True,
        elem_id="selected-spins"
    )
    spin_counter = gr.HTML(
        label="Total Spins",
        value='<span class="spin-counter" style="font-size: 14px; padding: 4px 8px;">Total Spins: 0</span>',
        elem_classes=["spin-counter"]
    )
    with gr.Accordion("Dealer’s Spin Tracker (Can you spot Bias???) 🕵️", open=False, elem_id="sides-of-zero-accordion"):
        sides_of_zero_display = gr.HTML(
            label="Sides of Zero",
            value=render_sides_of_zero_display(),
            elem_classes=["sides-of-zero-container"]
        )
    last_spin_display = gr.HTML(
        label="Last Spins",
        value='<h4>Last Spins</h4><p>No spins yet.</p>',
        elem_classes=["last-spins-container"]
    )
    last_spin_count = gr.Slider(
        label="",  # Remove the label to be safe
        minimum=1,
        maximum=36,
        step=1,
        value=36,
        interactive=True,
        elem_classes="long-slider"
    )

def suggest_hot_cold_numbers():
    """Suggest top 5 hot and bottom 5 cold numbers based on state.scores."""
    try:
        if not state.scores or not any(state.scores.values()):
            return "", "<p>No spin data available for suggestions.</p>"

        sorted_scores = sorted(state.scores.items(), key=lambda x: x[1], reverse=True)
        hot_numbers = [str(num) for num, score in sorted_scores[:5] if score > 0]
        cold_numbers = [str(num) for num, score in sorted_scores[-5:] if score >= 0]

        if not hot_numbers:
            hot_numbers = ["No hot numbers"]
        if not cold_numbers:
            cold_numbers = ["No cold numbers"]

        return ", ".join(hot_numbers), ", ".join(cold_numbers)
    except Exception as e:
        print(f"suggest_hot_cold_numbers: Error: {str(e)}")
        return "", "<p>Error generating suggestions.</p>"

STRATEGIES = {
    "Hot Bet Strategy": {"function": hot_bet_strategy, "categories": ["even_money", "dozens", "columns", "streets", "corners", "six_lines", "splits", "sides", "numbers"]},
    "Cold Bet Strategy": {"function": cold_bet_strategy, "categories": ["even_money", "dozens", "columns", "streets", "corners", "six_lines", "splits", "sides", "numbers"]},
    "Best Even Money Bets": {"function": best_even_money_bets, "categories": ["even_money"]},
    "Best Even Money Bets + Top Pick 18 Numbers": {"function": best_even_money_and_top_18, "categories": ["even_money", "numbers"]},
    "Best Dozens": {"function": best_dozens, "categories": ["dozens"]},
    "Best Dozens + Top Pick 18 Numbers": {"function": best_dozens_and_top_18, "categories": ["dozens", "numbers"]},
    "Best Columns": {"function": best_columns, "categories": ["columns"]},
    "Best Columns + Top Pick 18 Numbers": {"function": best_columns_and_top_18, "categories": ["columns", "numbers"]},
    "Best Dozens + Best Even Money Bets + Top Pick 18 Numbers": {"function": best_dozens_even_money_and_top_18, "categories": ["dozens", "even_money", "numbers", "trends"]},
    "Best Columns + Best Even Money Bets + Top Pick 18 Numbers": {"function": best_columns_even_money_and_top_18, "categories": ["columns", "even_money", "numbers", "trends"]},
    "Fibonacci Strategy": {"function": fibonacci_strategy, "categories": ["dozens", "columns"]},
    "Best Streets": {"function": best_streets, "categories": ["streets"]},
    "Best Double Streets": {"function": best_double_streets, "categories": ["six_lines"]},
    "Best Corners": {"function": best_corners, "categories": ["corners"]},
    "Best Splits": {"function": best_splits, "categories": ["splits"]},
    "Best Dozens + Best Streets": {"function": best_dozens_and_streets, "categories": ["dozens", "streets"]},
    "Best Columns + Best Streets": {"function": best_columns_and_streets, "categories": ["columns", "streets"]},
    "Non-Overlapping Double Street Strategy": {"function": non_overlapping_double_street_strategy, "categories": ["six_lines"]},
    "Non-Overlapping Corner Strategy": {"function": non_overlapping_corner_strategy, "categories": ["corners"]},
    "Romanowksy Missing Dozen": {"function": romanowksy_missing_dozen_strategy, "categories": ["dozens", "numbers"]},
    "Fibonacci To Fortune": {"function": fibonacci_to_fortune_strategy, "categories": ["even_money", "dozens", "columns", "six_lines"]},
    "3-8-6 Rising Martingale": {"function": three_eight_six_rising_martingale, "categories": ["streets"]},
    "1 Dozen +1 Column Strategy": {"function": one_dozen_one_column_strategy, "categories": ["dozens", "columns"]},
    "Top Pick 18 Numbers without Neighbours": {"function": top_pick_18_numbers_without_neighbours, "categories": ["numbers"]},
    "Top Numbers with Neighbours (Tiered)": {"function": top_numbers_with_neighbours_tiered, "categories": ["numbers"]},
    "Neighbours of Strong Number": {"function": neighbours_of_strong_number, "categories": ["neighbours"]}
}


# Line 1: Start of show_strategy_recommendations function (updated)
# Line 1: Start of show_strategy_recommendations function (updated)
def show_strategy_recommendations(strategy_name, neighbours_count, *args):
    """Generate strategy recommendations based on the selected strategy."""
    try:
        print(f"show_strategy_recommendations: scores = {dict(state.scores)}")
        print(f"show_strategy_recommendations: even_money_scores = {dict(state.even_money_scores)}")
        print(f"show_strategy_recommendations: any_scores = {any(state.scores.values())}, any_even_money = {any(state.even_money_scores.values())}")
        print(f"show_strategy_recommendations: strategy_name = {strategy_name}, neighbours_count = {neighbours_count}, args = {args}")

        if strategy_name == "None":
            return "<p>No strategy selected. Please choose a strategy to see recommendations.</p>"
        
        # If no spins yet, provide a default for "Best Even Money Bets"
        if not any(state.scores.values()) and not any(state.even_money_scores.values()):
            if strategy_name == "Best Even Money Bets":
                return "<p>No spins yet. Default Even Money Bets to consider:<br>1. Red<br>2. Black<br>3. Even</p>"
            return "<p>Please analyze some spins first to generate scores.</p>"

        strategy_info = STRATEGIES[strategy_name]
        strategy_func = strategy_info["function"]

        if strategy_name == "Neighbours of Strong Number":
            try:
                neighbours_count = int(neighbours_count)
                strong_numbers_count = int(args[0]) if args else 1  # Assuming strong_numbers_count is first in args
                print(f"show_strategy_recommendations: Using neighbours_count = {neighbours_count}, strong_numbers_count = {strong_numbers_count}")
            except (ValueError, TypeError) as e:
                print(f"show_strategy_recommendations: Error converting inputs: {str(e)}, defaulting to 2 and 1.")
                neighbours_count = 2
                strong_numbers_count = 1
            result = strategy_func(neighbours_count, strong_numbers_count)
            # Handle the tuple return value for Neighbours of Strong Number
            if isinstance(result, tuple) and len(result) == 2:
                recommendations, _ = result  # We only need the recommendations string for display
            else:
                recommendations = result
        elif strategy_name == "Dozen Tracker":
            # Dozen Tracker expects multiple arguments and returns a tuple
            result = strategy_func(*args)
            if isinstance(result, tuple) and len(result) == 3:
                recommendations, _, _ = result  # Unpack the tuple, we only need the first element
            else:
                recommendations = result
        elif strategy_name == "Top Numbers Strategy":
            # Handle Top Numbers Strategy
            try:
                strong_numbers_count = int(args[0]) if args else 5  # Number of top numbers to show
                print(f"show_strategy_recommendations: Using strong_numbers_count = {strong_numbers_count} for Top Numbers Strategy")
            except (ValueError, TypeError) as e:
                print(f"show_strategy_recommendations: Error converting inputs: {str(e)}, defaulting to 5.")
                strong_numbers_count = 5
            # Call the strategy function to get the top numbers
            top_numbers = strategy_func()  # Assuming this returns a list of (number, score) tuples
            if not top_numbers:
                return "<p>No top numbers available. Please analyze more spins.</p>"
            # Limit to strong_numbers_count and sort by score
            top_numbers = sorted(top_numbers, key=lambda x: x[1], reverse=True)[:strong_numbers_count]
            # Generate neighbors for each number
            html = "<p>Here are the top numbers to consider based on recent spins:</p>"
            html += '<table class="strongest-numbers-table">'
            html += "<tr><th>Number</th><th>Score</th><th>Neighbors</th><th>Number</th><th>Score</th><th>Neighbors</th><th>Number</th><th>Score</th><th>Neighbors</th></tr>"
            # Pad the list with empty entries to make it divisible by 3
            while len(top_numbers) % 3 != 0:
                top_numbers.append(("", ""))
            # Group numbers into sets of 3
            for i in range(0, len(top_numbers), 3):
                group = top_numbers[i:i+3]
                html += "<tr>"
                for number, score in group:
                    if number:
                        neighbors = get_neighbors(number, neighbours_count)
                        html += f"<td>{number}</td><td>{score}</td><td>{', '.join(map(str, neighbors))}</td>"
                    else:
                        html += "<td></td><td></td><td></td>"
                html += "</tr>"
            html += "</table>"
            return html
        else:
            # Other strategies return a single string
            recommendations = strategy_func()

        print(f"show_strategy_recommendations: Raw strategy output for {strategy_name} = '{recommendations}'")

        # If the output is already HTML (e.g., for "Top Numbers with Neighbours (Tiered)"), return it as is
        if strategy_name == "Top Numbers with Neighbours (Tiered)":
            return recommendations
        # Special handling for "Neighbours of Strong Number" to format Suggestions section
        elif strategy_name == "Neighbours of Strong Number":
            lines = recommendations.split("\n")
            html_lines = []
            in_suggestions = False
            for line in lines:
                if line.strip() == "Suggestions:":
                    in_suggestions = True
                    html_lines.append('<p style="margin: 2px 0; font-weight: bold;">Suggestions:</p>')
                elif line.strip() == "" and in_suggestions:
                    in_suggestions = False
                    html_lines.append('<p style="margin: 2px 0;"></p>')
                elif in_suggestions:
                    html_lines.append(f'<p style="margin: 2px 0; padding-left: 10px;">{line}</p>')
                else:
                    html_lines.append(f'<p style="margin: 2px 0;">{line}</p>')
            return '<div style="font-family: Arial, sans-serif; font-size: 14px;">' + "".join(html_lines) + "</div>"
        # Otherwise, convert plain text to HTML with proper line breaks
        else:
            # Split the output into lines, removing any empty lines
            lines = [line for line in recommendations.split("\n") if line.strip()]
            # Wrap each line in <p> tags and join with <br> for proper spacing
            html_lines = [f"<p style='margin: 2px 0;'>{line}</p>" for line in lines]
            return "<div style='font-family: Arial, sans-serif; font-size: 14px;'>" + "".join(html_lines) + "</div>"

    except Exception as e:
        print(f"show_strategy_recommendations: Error: {str(e)}")
        raise  # Re-raise for debugging

# Line 3: Start of clear_outputs function (unchanged)
def clear_outputs():
    return "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""

# Lines after (context, unchanged)
def toggle_checkboxes(strategy_name):
    return (gr.update(visible=strategy_name == "Kitchen Martingale"),
            gr.update(visible=strategy_name == "S.T.Y.W: Victory Vortex"))

def reset_colors():
    """Reset color pickers to default values and update the dynamic table."""
    default_top = "rgba(255, 255, 0, 0.5)"  # Yellow
    default_middle = "rgba(0, 255, 255, 0.5)"  # Cyan
    default_lower = "rgba(0, 255, 0, 0.5)"  # Green
    return default_top, default_middle, default_lower

def clear_last_spins_display():
    """Clear the Last Spins HTML display without affecting spins data."""
    return "<h4>Last Spins</h4><p>Display cleared. Add spins to see them here.</p>", update_spin_counter()

# Build the Gradio interface
with gr.Blocks(title="WheelPulse by S.T.Y.W 📈") as demo:
    # 1. Row 1: Header (Moved to the top)
    with gr.Row(elem_id="header-row"):
        gr.Markdown("<h1 style='text-align: center; color: #ff9800;'>WheelPulse by S.T.Y.W 📈</h1>")
        gr.HTML(
            '''
            <div style="display: flex; gap: 10px; justify-content: center; align-items: center;">
                <button id="start-tour-btn" onclick="startTour()" style="width: 150px; height: 40px; padding: 8px 15px; background-color: #ff9800; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 14px; font-weight: bold; line-height: 1; transition: transform 0.2s ease; box-sizing: border-box;">🚀 Take the Tour!</button>
                <a href="https://drive.google.com/file/d/154GfZaiNUfAFB73WEIA617ofdZbRaEIN/view?usp=drive_link" target="_blank" style="width: 150px; height: 40px; padding: 8px 15px; background-color: #dc3545; color: white; text-decoration: none; border-radius: 5px; font-size: 14px; font-weight: bold; line-height: 1; transition: transform 0.2s ease; box-sizing: border-box; display: inline-block; text-align: center;">📖 View Guide</a>
            </div>
            <style>
                #start-tour-btn:hover, a[href*="drive.google.com"]:hover {
                    transform: scale(1.05);
                    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                }
            </style>
            '''
        )

    # Define state and components used across sections
    # Define state and components used across sections
    spins_display = gr.State(value="")
    show_trends_state = gr.State(value=True)  # Default to showing trends
    toggle_trends_label = gr.State(value="Hide Trends")  # Default label when trends are shown
    analysis_cache = gr.State(value={})  # New: Cache for analysis results
    spins_textbox = gr.Textbox(
        label="Selected Spins (Edit manually with commas, e.g., 5, 12, 0)",
        value="",
        interactive=True,
        elem_id="selected-spins"
    )
    spin_counter = gr.HTML(
        label="Total Spins",
        value='<span class="spin-counter" style="font-size: 14px; padding: 4px 8px;">Total Spins: 0</span>',
        elem_classes=["spin-counter"]
    )
    with gr.Accordion("Dealer’s Spin Tracker (Can you spot Bias???) 🕵️", open=False, elem_id="sides-of-zero-accordion"):
        sides_of_zero_display = gr.HTML(
            label="Sides of Zero",
            value=render_sides_of_zero_display(),
            elem_classes=["sides-of-zero-container"]
        )
    last_spin_display = gr.HTML(
        label="Last Spins",
        value='<h4>Last Spins</h4><p>No spins yet.</p>',
        elem_classes=["last-spins-container"]
    )
    last_spin_count = gr.Slider(
        label="",  # Remove the label to be safe
        minimum=1,
        maximum=36,
        step=1,
        value=36,
        interactive=True,
        elem_classes="long-slider"
    )

    # Start of updated section
    with gr.Accordion("Hit Percentage Overview 📊", open=False, elem_id="hit-percentage-overview"):
        with gr.Row():
            with gr.Column(scale=1):
                hit_percentage_display = gr.HTML(
                    label="Hit Percentages",
                    value=calculate_hit_percentages(36),
                    elem_classes=["hit-percentage-container"]
                )

    with gr.Accordion("SpinTrend Radar 🌀", open=False, elem_id="spin-trend-radar"):
        with gr.Row():
            with gr.Column(scale=1):
                traits_display = gr.HTML(
                    label="Spin Traits",
                    value=summarize_spin_traits(36),
                    elem_classes=["traits-container"]
                )

    # Line 1: Updated Next Spin Top Pick accordion
    with gr.Accordion("Next Spin Top Pick 🎯", open=False, elem_id="next-spin-top-pick"):
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 🎯 Select Your Top Pick")
                gr.Markdown("Adjust the slider to analyze the last X spins and find the top pick for your next spin. Add spins using the roulette table below or enter them manually.")
                top_pick_spin_count = gr.Slider(
                    label="Number of Spins to Analyze",
                    minimum=1,
                    maximum=36,
                    step=1,
                    value=18,
                    interactive=True,
                    elem_classes="long-slider"
                )
                top_pick_display = gr.HTML(
                    label="Top Pick",
                    value=select_next_spin_top_pick(18),
                    elem_classes=["top-pick-container"]
                )
        gr.HTML("""
        <style>
            #next-spin-top-pick {
                background-color: #e3f2fd !important;
                border: 2px solid #2196f3 !important;
                border-radius: 5px !important;
                padding: 10px !important;
            }
            #next-spin-top-pick summary {
                background-color: #2196f3 !important;
                color: white !important;
                padding: 10px !important;
                border-radius: 5px !important;
            }
            .top-pick-container p {
                font-style: italic;
                color: #666;
            }
            .top-pick-container h4 {
                margin: 10px 0;
                color: #333;
            }
        </style>
        """)

    # 2. Row 2: European Roulette Table
    with gr.Group():
        gr.Markdown("### European Roulette Table")
        table_layout = [
            ["", "3", "6", "9", "12", "15", "18", "21", "24", "27", "30", "33", "36"],
            ["0", "2", "5", "8", "11", "14", "17", "20", "23", "26", "29", "32", "35"],
            ["", "1", "4", "7", "10", "13", "16", "19", "22", "25", "28", "31", "34"]
        ]
        with gr.Column(elem_classes="roulette-table"):
            for row in table_layout:
                with gr.Row(elem_classes="table-row"):
                    for num in row:
                        if num == "":
                            gr.Button(value=" ", interactive=False, min_width=40, elem_classes="empty-button")
                        else:
                            color = colors.get(str(num), "black")
                            is_selected = int(num) in state.selected_numbers
                            btn_classes = [f"roulette-button", color]
                            if is_selected:
                                btn_classes.append("selected")
                            btn = gr.Button(
                                value=num,
                                min_width=40,
                                elem_classes=btn_classes
                            )
                            btn.click(
                                fn=add_spin,
                                inputs=[gr.State(value=num), spins_display, last_spin_count],
                                outputs=[spins_display, spins_textbox, last_spin_display, spin_counter, sides_of_zero_display]
                            ).then(
                                fn=format_spins_as_html,
                                inputs=[spins_display, last_spin_count],
                                outputs=[last_spin_display]
                            ).then(
                                fn=summarize_spin_traits,
                                inputs=[last_spin_count],
                                outputs=[traits_display]
                            ).then(
                                fn=calculate_hit_percentages,
                                inputs=[last_spin_count],
                                outputs=[hit_percentage_display]
                            ).then(
                                fn=select_next_spin_top_pick,
                                inputs=[top_pick_spin_count],
                                outputs=[top_pick_display]
                            ).then(
                                fn=lambda: print(f"After add_spin: state.last_spins = {state.last_spins}"),
                                inputs=[],
                                outputs=[]
                            )

    # Row 3 (keep the accordion here)
    # 3. Row 3: Last Spins Display and Show Last Spins Slider
    with gr.Row():
        with gr.Column():
            last_spin_display
            last_spin_count
        
            

    # 4. Row 4: Spin Controls
    with gr.Row():
        with gr.Column(scale=2):
            clear_last_spins_button = gr.Button("Clear Last Spins Display", elem_classes=["action-button"])
        with gr.Column(scale=1):
            undo_button = gr.Button("Undo Spins", elem_classes=["action-button"], elem_id="undo-spins-btn")
        with gr.Column(scale=1):
            generate_spins_button = gr.Button("Generate Random Spins", elem_classes=["action-button"])
        with gr.Column(scale=1):
            toggle_trends_button = gr.Button(
                value="Hide Trends",  # Initial string value
                elem_classes=["action-button"],
                elem_id="toggle-trends-btn"
            )
    
    # 5. Row 5: Selected Spins Textbox and Spin Counter
    with gr.Row(elem_id="selected-spins-row"):
        with gr.Column(scale=4, min_width=600):
            spins_textbox
        with gr.Column(scale=1, min_width=200):
            spin_counter  # Restore side-by-side layout with styling
      

    # Define strategy categories and choices
    strategy_categories = {
        "Trends": ["Cold Bet Strategy", "Hot Bet Strategy", "Best Dozens + Best Even Money Bets + Top Pick 18 Numbers", "Best Columns + Best Even Money Bets + Top Pick 18 Numbers"],
        "Even Money Strategies": ["Best Even Money Bets", "Best Even Money Bets + Top Pick 18 Numbers", "Fibonacci To Fortune"],
        "Dozen Strategies": ["1 Dozen +1 Column Strategy", "Best Dozens", "Best Dozens + Top Pick 18 Numbers", "Best Dozens + Best Even Money Bets + Top Pick 18 Numbers", "Best Dozens + Best Streets", "Fibonacci Strategy", "Romanowksy Missing Dozen"],
        "Column Strategies": ["1 Dozen +1 Column Strategy", "Best Columns", "Best Columns + Top Pick 18 Numbers", "Best Columns + Best Even Money Bets + Top Pick 18 Numbers", "Best Columns + Best Streets"],
        "Street Strategies": ["3-8-6 Rising Martingale", "Best Streets", "Best Columns + Best Streets", "Best Dozens + Best Streets"],
        "Double Street Strategies": ["Best Double Streets", "Non-Overlapping Double Street Strategy"],
        "Corner Strategies": ["Best Corners", "Non-Overlapping Corner Strategy"],
        "Split Strategies": ["Best Splits"],
        "Number Strategies": ["Top Numbers with Neighbours (Tiered)", "Top Pick 18 Numbers without Neighbours"],
        "Neighbours Strategies": ["Neighbours of Strong Number"]
    }
    category_choices = ["None"] + sorted(strategy_categories.keys())

    # Define video categories matching strategy categories
    video_categories = {
        "Trends": [],
        "Even Money Strategies": [
            {
                "title": "S.T.Y.W: Zero Jack 2-2-3 Roulette Strategy",
                "link": "https://youtu.be/I_F9Wys3Ww0"
            },
            {
                "title": "S.T.Y.W: Fibonacci to Fortune (My Top Strategy) - Follow The Winner",
                "link": "https://youtu.be/bwa0FUk6Yps"
            },
            {
                "title": "S.T.Y.W: Triple Entry Max Climax Strategy",
                "link": "https://youtu.be/64aq0GEPww0"
            }
        ],
        "Dozen Strategies": [
            {
                "title": "S.T.Y.W: Dynamic Play: 1 Dozen with 4 Streets or 2 Double Streets?",
                "link": "https://youtu.be/8aMHrvuzBGU"
            },
            {
                "title": "S.T.Y.W: Romanowsky Missing Dozen Strategy",
                "link": "https://youtu.be/YbBtum5WVCk"
            },
            {
                "title": "S.T.Y.W: Victory Vortex (Dozen Domination)",
                "link": "https://youtu.be/aKGA_csI9lY"
            },
            {
                "title": "S.T.Y.W: The Overlap Jackpot (4 Streets + 2 Dozens) Strategy",
                "link": "https://youtu.be/rTqdMQk4_I4"
            },
            {
                "title": "S.T.Y.W: Fibonacci to Fortune (My Top Strategy) - Follow The Winner",
                "link": "https://youtu.be/bwa0FUk6Yps"
            },
            {
                "title": "S.T.Y.W: Double Up: Dozen & Street Strategy",
                "link": "https://youtu.be/Hod5gxusAVE"
            },
            {
                "title": "S.T.Y.W: Triple Entry Max Climax Strategy",
                "link": "https://youtu.be/64aq0GEPww0"
            }
        ],
        "Column Strategies": [
            {
                "title": "S.T.Y.W: Zero Jack 2-2-3 Roulette Strategy",
                "link": "https://youtu.be/I_F9Wys3Ww0"
            },
            {
                "title": "S.T.Y.W: Victory Vortex (Dozen Domination)",
                "link": "https://youtu.be/aKGA_csI9lY"
            },
            {
                "title": "S.T.Y.W: Fibonacci to Fortune (My Top Strategy) - Follow The Winner",
                "link": "https://youtu.be/bwa0FUk6Yps"
            }
        ],
        "Street Strategies": [
            {
                "title": "S.T.Y.W: Dynamic Play: 1 Dozen with 4 Streets or 2 Double Streets?",
                "link": "https://youtu.be/8aMHrvuzBGU"
            },
            {
                "title": "S.T.Y.W: 3-8-6 Rising Martingale",
                "link": "https://youtu.be/-ZcEUOTHMzA"
            },
            {
                "title": "S.T.Y.W: The Overlap Jackpot (4 Streets + 2 Dozens) Strategy",
                "link": "https://youtu.be/rTqdMQk4_I4"
            },
            {
                "title": "S.T.Y.W: Double Up: Dozen & Street Strategy",
                "link": "https://youtu.be/Hod5gxusAVE"
            }
        ],
        "Double Street Strategies": [
            {
                "title": "S.T.Y.W: Dynamic Play: 1 Dozen with 4 Streets or 2 Double Streets?",
                "link": "https://youtu.be/8aMHrvuzBGU"
            },
            {
                "title": "S.T.Y.W: The Classic Five Double Street",
                "link": "https://youtu.be/XX7lSDElwWI"
            }
        ],
        "Corner Strategies": [
            {
                "title": "S.T.Y.W: 4-Corners Strategy (Seq:1,1,2,5,8,17,28,50)",
                "link": "https://youtu.be/zw7eUllTDbg"
            }
        ],
       "Split Strategies": [
            {
                "title": "S.T.Y.W: Triple Entry Max Climax Strategy",
                "link": "https://youtu.be/64aq0GEPww0"
            }
        ],
        "Number Strategies": [
            {
                "title": "The Pulse Wheel Strategy (6 Numbers +1 Neighbours)",
                "link": "https://youtu.be/UBajAwUXWS0"
            },
            {
                "title": "Eighteen Strong Numbers with No Neighbours Strategy",
                "link": "https://youtu.be/8Nmbi8KmY9c"
            }
        ],
        "Neighbours Strategies": [
            {
                "title": "The Pulse Wheel Strategy (6 Numbers +1 Neighbours)",
                "link": "https://youtu.be/UBajAwUXWS0"
            },
            {
                "title": "Triad Spin Strategy: 87.53% (Modified Makarov-Biarritz)",
                "link": "https://youtu.be/ADhCvxNiWVc"
            }
        ]
    }
    
    # 6. Row 6: Analyze Spins, Clear Spins, and Clear All Buttons
    with gr.Row():
        with gr.Column(scale=2):
            analyze_button = gr.Button("Analyze Spins", elem_classes=["action-button", "green-btn"], interactive=True)
        with gr.Column(scale=1):
            clear_spins_button = gr.Button("Clear Spins", elem_classes=["clear-spins-btn", "small-btn"])
        with gr.Column(scale=1):
            clear_all_button = gr.Button("Clear All", elem_classes=["clear-spins-btn", "small-btn"])
    
    # 7. Row 7: Dynamic Roulette Table and Strategy Recommendations
    with gr.Column(scale=3, min_width=1000, elem_classes="dynamic-table-container"):
        gr.Markdown("### Dynamic Roulette Table", elem_id="dynamic-table-heading")
        dynamic_table_output = gr.HTML(
            label="Dynamic Table",
            value=create_dynamic_table(strategy_name="Best Even Money Bets"),
            elem_classes=["scrollable-table", "large-table"]
        )
        gr.Markdown("### Strategy Recommendations")
        # Wrap the entire section in a div with class "strategy-card"
        with gr.Row(elem_classes="strategy-card"):
            with gr.Column(scale=1):  # Use a single column to stack elements vertically
                with gr.Row():
                    category_dropdown = gr.Dropdown(
                        label="Select Category",
                        choices=category_choices,
                        value="Even Money Strategies",
                        allow_custom_value=False,
                        elem_id="select-category"
                    )
                    strategy_dropdown = gr.Dropdown(
                        label="Select Strategy",
                        choices=strategy_categories["Even Money Strategies"],
                        value="Best Even Money Bets",
                        allow_custom_value=False,
                        elem_id="strategy-dropdown"
                    )
                reset_strategy_button = gr.Button("Reset Category & Strategy", elem_classes=["action-button"])
                neighbours_count_slider = gr.Slider(
                    label="Number of Neighbors (Left + Right)",
                    minimum=1,
                    maximum=5,
                    step=1,
                    value=1,
                    interactive=True,
                    visible=False,
                    elem_classes="long-slider"
                )
                strong_numbers_count_slider = gr.Slider(
                    label="Strong Numbers to Highlight (Neighbours Strategy)",
                    minimum=1,
                    maximum=18,
                    step=1,
                    value=1,
                    interactive=True,
                    visible=False,
                    elem_classes="long-slider"
                )
                strategy_output = gr.HTML(
                    label="Strategy Recommendations",
                    value=show_strategy_recommendations("Best Even Money Bets", 2, 1),
                    elem_classes=["strategy-box"]
                )

    # 7.1. Row 7.1: Dozen Tracker
    with gr.Row():
        with gr.Column(scale=3):
            with gr.Accordion("Create Dozen/Even Bet Triggers", open=False, elem_id="dozen-tracker"):
                with gr.Accordion("Dozen Triggers", open=False, elem_id="dozen-triggers"):
                    dozen_tracker_spins_dropdown = gr.Dropdown(
                        label="Number of Spins to Track",
                        choices=["3", "4", "5", "6", "10", "15", "20", "25", "30", "40", "50", "75", "100", "150", "200"],
                        value="5",
                        interactive=True
                    )
                    dozen_tracker_consecutive_hits_dropdown = gr.Dropdown(
                        label="Alert on Consecutive Dozen Hits",
                        choices=["3", "4", "5"],
                        value="3",
                        interactive=True
                    )
                    dozen_tracker_alert_checkbox = gr.Checkbox(
                        label="Enable Consecutive Dozen Hits Alert",
                        value=False,
                        interactive=True
                    )
                    dozen_tracker_sequence_length_dropdown = gr.Dropdown(
                        label="Sequence Length to Match (X)",
                        choices=["3", "4", "5"],
                        value="4",
                        interactive=True
                    )
                    dozen_tracker_follow_up_spins_dropdown = gr.Dropdown(
                        label="Follow-Up Spins to Track (Y)",
                        choices=["3", "4", "5", "6", "7", "8", "9", "10"],
                        value="5",
                        interactive=True
                    )
                    dozen_tracker_sequence_alert_checkbox = gr.Checkbox(
                        label="Enable Sequence Matching Alert",
                        value=False,
                        interactive=True
                    )
                    dozen_tracker_output = gr.HTML(
                        label="Dozen Tracker",
                        value="<p>Select the number of spins to track and analyze spins to see the Dozen history.</p>"
                    )
                    dozen_tracker_sequence_output = gr.HTML(
                        label="Sequence Matching Results",
                        value="<p>Enable sequence matching to see results here.</p>"
                    )
                with gr.Accordion("Even Money", open=False, elem_id="even-money-tracker"):
                    even_money_tracker_spins_dropdown = gr.Dropdown(
                        label="Number of Spins to Track",
                        choices=["1", "2", "3", "4", "5", "6", "10", "15", "20", "25", "30", "40", "50", "75", "100", "150", "200"],
                        value="5",
                        interactive=True
                    )
                    even_money_tracker_consecutive_hits_dropdown = gr.Dropdown(
                        label="Alert on Consecutive Even Money Hits",
                        choices=["1", "2", "3", "4", "5"],
                        value="3",
                        interactive=True
                    )
                    even_money_tracker_combination_mode_dropdown = gr.Dropdown(
                        label="Combination Mode",
                        choices=["And", "Or"],
                        value="And",
                        interactive=True
                    )
                    even_money_tracker_identical_traits_checkbox = gr.Checkbox(
                        label="Track Consecutive Identical Traits",
                        value=False,
                        interactive=True
                    )
                    even_money_tracker_consecutive_identical_dropdown = gr.Dropdown(
                        label="Number of Consecutive Identical Traits",
                        choices=["1", "2", "3", "4", "5"],
                        value="2",
                        interactive=True
                    )
                    with gr.Row():
                        even_money_tracker_red_checkbox = gr.Checkbox(label="Red", value=False, interactive=True)
                        even_money_tracker_black_checkbox = gr.Checkbox(label="Black", value=False, interactive=True)
                        even_money_tracker_even_checkbox = gr.Checkbox(label="Even", value=False, interactive=True)
                        even_money_tracker_odd_checkbox = gr.Checkbox(label="Odd", value=False, interactive=True)
                        even_money_tracker_low_checkbox = gr.Checkbox(label="Low", value=False, interactive=True)
                        even_money_tracker_high_checkbox = gr.Checkbox(label="High", value=False, interactive=True)
                    even_money_tracker_alert_checkbox = gr.Checkbox(
                        label="Enable Even Money Hits Alert",
                        value=False,
                        interactive=True
                    )
                    even_money_tracker_output = gr.HTML(
                        label="Even Money Tracker",
                        value="<p>Select categories to track and analyze spins to see even money bet history.</p>"
                    )
        with gr.Column(scale=2):
            pass  # Empty column to maintain layout balance
    
    # 8. Row 8: Betting Progression Tracker
    with gr.Row():
        with gr.Accordion("Betting Progression Tracker", open=False, elem_classes=["betting-progression"]):
            with gr.Row():
                bankroll_input = gr.Number(label="Bankroll", value=1000)
                base_unit_input = gr.Number(label="Base Unit", value=10)
                stop_loss_input = gr.Number(label="Stop Loss", value=-500)
                stop_win_input = gr.Number(label="Stop Win", value=200)
                target_profit_input = gr.Number(label="Target Profit (Units)", value=10, step=1)
            with gr.Row():
                bet_type_dropdown = gr.Dropdown(
                    label="Bet Type",
                    choices=["Even Money", "Dozens", "Columns", "Straight Bets"],
                    value="Even Money"
                )
                progression_dropdown = gr.Dropdown(
                    label="Progression",
                    choices=["Martingale", "Fibonacci", "Triple Martingale", "Oscar’s Grind", "Labouchere", "Ladder", "D’Alembert", "Double After a Win", "+1 Win / -1 Loss", "+2 Win / -1 Loss"],
                    value="Martingale"
                )
                labouchere_sequence = gr.Textbox(
                    label="Labouchere Sequence (comma-separated)",
                    value="",
                    visible=False
                )
            with gr.Row():
                win_button = gr.Button("Win")
                lose_button = gr.Button("Lose")
                reset_progression_button = gr.Button("Reset Progression")
            with gr.Row():
                bankroll_output = gr.Textbox(label="Current Bankroll", value="1000", interactive=False)
                current_bet_output = gr.Textbox(label="Current Bet", value="10", interactive=False)
                next_bet_output = gr.Textbox(label="Next Bet", value="10", interactive=False)
            with gr.Row():
                message_output = gr.Textbox(label="Message", value="Start with base bet of 10 on Even Money (Martingale)", interactive=False)
                status_output = gr.HTML(label="Status", value='<div style="background-color: white; padding: 5px; border-radius: 3px;">Active</div>') 
         
    # 8.1. Row 8.1: Casino Data Insights
    with gr.Row():
        with gr.Accordion("Casino Data Insights", open=False, elem_classes=["betting-progression"], elem_id="casino-data-insights"):
            spins_count_dropdown = gr.Dropdown(
                label="Past Spins Count",
                choices=["30", "50", "100", "200", "300", "500"],
                value="100",
                interactive=True
            )
            with gr.Row():
                even_percent = gr.Dropdown(
                    label="Even %",
                    choices=[f"{i:02d}" for i in range(100)],
                    value="00",
                    interactive=True
                )
                odd_percent = gr.Dropdown(
                    label="Odd %",
                    choices=[f"{i:02d}" for i in range(100)],
                    value="00",
                    interactive=True
                )
            with gr.Row():
                red_percent = gr.Dropdown(
                    label="Red %",
                    choices=[f"{i:02d}" for i in range(100)],
                    value="00",
                    interactive=True
                )
                black_percent = gr.Dropdown(
                    label="Black %",
                    choices=[f"{i:02d}" for i in range(100)],
                    value="00",
                    interactive=True
                )
            with gr.Row():
                low_percent = gr.Dropdown(
                    label="Low %",
                    choices=[f"{i:02d}" for i in range(100)],
                    value="00",
                    interactive=True
                )
                high_percent = gr.Dropdown(
                    label="High %",
                    choices=[f"{i:02d}" for i in range(100)],
                    value="00",
                    interactive=True
                )
            with gr.Row():
                dozen1_percent = gr.Dropdown(
                    label="1st Dozen %",
                    choices=[f"{i:02d}" for i in range(100)],
                    value="00",
                    interactive=True
                )
                dozen2_percent = gr.Dropdown(
                    label="2nd Dozen %",
                    choices=[f"{i:02d}" for i in range(100)],
                    value="00",
                    interactive=True
                )
                dozen3_percent = gr.Dropdown(
                    label="3rd Dozen %",
                    choices=[f"{i:02d}" for i in range(100)],
                    value="00",
                    interactive=True
                )
            with gr.Row():
                col1_percent = gr.Dropdown(
                    label="1st Column %",
                    choices=[f"{i:02d}" for i in range(100)],
                    value="00",
                    interactive=True
                )
                col2_percent = gr.Dropdown(
                    label="2nd Column %",
                    choices=[f"{i:02d}" for i in range(100)],
                    value="00",
                    interactive=True
                )
                col3_percent = gr.Dropdown(
                    label="3rd Column %",
                    choices=[f"{i:02d}" for i in range(100)],
                    value="00",
                    interactive=True
                )
            use_winners_checkbox = gr.Checkbox(
                label="Highlight Casino Winners",
                value=False,
                interactive=True
            )
            reset_casino_data_button = gr.Button(
                "Reset Casino Data",
                elem_classes=["action-button"]
            )
            casino_data_output = gr.HTML(
                label="Casino Data Insights",
                value="<p>No casino data entered yet.</p>",
                elem_classes=["fade-in"]
            )
            # Hot and Cold Numbers Section
            with gr.Accordion("Hot and Cold Numbers", open=False, elem_id="hot-cold-numbers"):
                with gr.Row():
                    gr.HTML('<span class="hot-icon">🔥</span>')
                    hot_numbers_input = gr.Textbox(
                        label="Hot Numbers (1 to 10 comma-separated numbers, e.g., 1, 3, 5, 7, 9)",
                        value="",
                        interactive=True,
                        placeholder="Enter 1 to 10 hot numbers"
                    )
                hot_suggestions = gr.Textbox(
                    label="Suggested Hot Numbers (based on recent spins)",
                    value="",
                    interactive=False,
                    elem_classes=["suggestion-box"]
                )
                gr.Button("Use Suggested Hot Numbers", elem_classes=["action-button", "suggestion-btn"]).click(
                    fn=lambda: state.hot_suggestions,
                    inputs=[],
                    outputs=[hot_numbers_input]
                )
                with gr.Row():
                    gr.HTML('<span class="cold-icon">❄️</span>')
                    cold_numbers_input = gr.Textbox(
                        label="Cold Numbers (1 to 10 comma-separated numbers, e.g., 2, 4, 6, 8, 10)",
                        value="",
                        interactive=True,
                        placeholder="Enter 1 to 10 cold numbers"
                    )
                cold_suggestions = gr.Textbox(
                    label="Suggested Cold Numbers (based on recent spins)",
                    value="",
                    interactive=False,
                    elem_classes=["suggestion-box"]
                )
                gr.Button("Use Suggested Cold Numbers", elem_classes=["action-button", "suggestion-btn"]).click(
                    fn=lambda: state.cold_suggestions,
                    inputs=[],
                    outputs=[cold_numbers_input]
                )
                with gr.Row():
                    play_hot_button = gr.Button("Play Hot Numbers", elem_classes=["action-button", "play-btn"])
                    play_cold_button = gr.Button("Play Cold Numbers", elem_classes=["action-button", "play-btn"])
                with gr.Row():
                    clear_hot_button = gr.Button("Clear Hot Picks", elem_classes=["action-button", "clear-btn"])
                    clear_cold_button = gr.Button("Clear Cold Picks", elem_classes=["action-button", "clear-btn"])
    
    # 9. Row 9: Color Code Key (Collapsible, with Color Pickers Inside)
    with gr.Accordion("Color Code Key", open=False, elem_id="color-code-key"):
        with gr.Row():
            top_color_picker = gr.ColorPicker(
                label="Top Tier Color",
                value="rgba(255, 255, 0, 0.5)",
                interactive=True,
                elem_id="top-color-picker"
            )
            middle_color_picker = gr.ColorPicker(
                label="Middle Tier Color",
                value="rgba(0, 255, 255, 0.5)",
                interactive=True
            )
            lower_color_picker = gr.ColorPicker(
                label="Lower Tier Color",
                value="rgba(0, 255, 0, 0.5)",
                interactive=True
            )
            reset_colors_button = gr.Button("Reset Colors", elem_classes=["action-button"])
        color_code_output = gr.HTML(label="Color Code Key")


    # 10. Row 10: Analysis Outputs (Collapsible, Renumbered)
    with gr.Accordion("Spin Logic Reactor 🧠", open=False, elem_id="spin-analysis"):
        spin_analysis_output = gr.Textbox(
            label="",
            value="",
            interactive=False,
            lines=5
        )

    with gr.Accordion("Strongest Numbers Tables", open=False, elem_id="strongest-numbers-table"):
        with gr.Row():
            with gr.Column():
                straight_up_html = gr.HTML(label="Strongest Numbers", elem_classes="scrollable-table")
            with gr.Column():
                top_18_html = gr.HTML(label="Top 18 Strongest Numbers (Sorted Lowest to Highest)", elem_classes="scrollable-table")
        with gr.Row():
            strongest_numbers_dropdown = gr.Dropdown(
                label="Select Number of Strongest Numbers",
                choices=["3", "6", "9", "12", "15", "18", "21", "24", "27", "30", "33"],
                value="3",
                allow_custom_value=False,
                interactive=True,
                elem_id="strongest-numbers-dropdown",
                visible=False  # Hide the dropdown
            )
            strongest_numbers_output = gr.Textbox(
                label="Strongest Numbers (Sorted Lowest to Highest)",
                value="",
                lines=2,
                visible=False  # Hide the textbox
            )

    with gr.Accordion("Aggregated Scores", open=False, elem_id="aggregated-scores"):
        with gr.Row():
            with gr.Column():
                with gr.Accordion("Even Money Bets", open=False):
                    even_money_output = gr.Textbox(label="Even Money Bets", lines=10, max_lines=50)
            with gr.Column():
                with gr.Accordion("Dozens", open=False):
                    dozens_output = gr.Textbox(label="Dozens", lines=10, max_lines=50)
        with gr.Row():
            with gr.Column():
                with gr.Accordion("Columns", open=False):
                    columns_output = gr.Textbox(label="Columns", lines=10, max_lines=50)
            with gr.Column():
                with gr.Accordion("Streets", open=False):
                    streets_output = gr.Textbox(label="Streets", lines=10, max_lines=50)
        with gr.Row():
            with gr.Column():
                with gr.Accordion("Corners", open=False):
                    corners_output = gr.Textbox(label="Corners", lines=10, max_lines=50)
            with gr.Column():
                with gr.Accordion("Double Streets", open=False):
                    six_lines_output = gr.Textbox(label="Double Streets", lines=10, max_lines=50)
        with gr.Row():
            with gr.Column():
                with gr.Accordion("Splits", open=False):
                    splits_output = gr.Textbox(label="Splits", lines=10, max_lines=50)
            with gr.Column():
                with gr.Accordion("Sides of Zero", open=False):
                    sides_output = gr.Textbox(label="Sides of Zero", lines=10, max_lines=50)

    # 11. Row 11: Save/Load Session (Collapsible, Renumbered)
    with gr.Accordion("Save/Load Session", open=False, elem_id="save-load-session"):
        with gr.Row():
            save_button = gr.Button("Save Session", elem_id="save-session-btn")
            load_input = gr.File(label="Upload Session")
        save_output = gr.File(label="Download Session")

    # 11. Row 11: Top Strategies with Roulette Spin Analyzer (Moved to be Independent)
    with gr.Row():
        with gr.Column():
            with gr.Accordion("Top Strategies with WheelPulse by S.T.Y.W 📈🎥", open=False, elem_id="top-strategies"):
                gr.Markdown("### Explore Strategies Through Videos")
                video_category_dropdown = gr.Dropdown(
                    label="Select Video Category",
                    choices=sorted(video_categories.keys()),
                    value="Dozen Strategies",
                    allow_custom_value=False,
                    elem_id="video-category-dropdown"
                )
                video_dropdown = gr.Dropdown(
                    label="Select Video",
                    choices=[video["title"] for video in video_categories["Dozen Strategies"]],
                    value=video_categories["Dozen Strategies"][0]["title"] if video_categories["Dozen Strategies"] else None,
                    allow_custom_value=False,
                    elem_id="video-dropdown"
                )
                video_output = gr.HTML(
                    label="Video",
                    value=f'<iframe width="100%" height="315" src="https://www.youtube.com/embed/{video_categories["Dozen Strategies"][0]["link"].split("/")[-1]}" frameborder="0" allowfullscreen></iframe>' if video_categories["Dozen Strategies"] else "<p>Select a category and video to watch.</p>"
                )

    # 12. Row 12: Feedback Section
    with gr.Row():
        with gr.Column():
            with gr.Accordion("Feedback & Suggestions 📝", open=False, elem_id="feedback-section"):
                gr.HTML("""
                <div style="background-color: #f5c6cb; border: 2px solid #d3d3d3; border-radius: 5px; padding: 15px;">
                    <h4 style="text-align: center; margin: 0 0 10px 0; font-family: Arial, sans-serif; color: #333;">
                        Share Your Feedback or Submit a Strategy
                    </h4>
                    <p style="text-align: center; font-family: Arial, sans-serif; color: #555; margin-bottom: 15px;">
                        We’d love to hear your suggestions, edits, or strategies for the Roulette Spin Analyzer!
                    </p>
                    <form id="feedback-form" style="display: flex; flex-direction: column; gap: 10px;">
                        <input type="text" name="name" placeholder="Your Name (Optional)" style="padding: 8px; border: 1px solid #d3d3d3; border-radius: 5px; font-family: Arial, sans-serif;">
                        <input type="email" name="_replyto" placeholder="Your Email (Required)" required style="padding: 8px; border: 1px solid #d3d3d3; border-radius: 5px; font-family: Arial, sans-serif;">
                        <textarea name="feedback" placeholder="Your Feedback or Suggestions" rows="4" style="padding: 8px; border: 1px solid #d3d3d3; border-radius: 5px; font-family: Arial, sans-serif; resize: vertical;"></textarea>
                        <textarea name="strategy" placeholder="Submit Your Strategy (Optional)" rows="4" style="padding: 8px; border: 1px solid #d3d3d3; border-radius: 5px; font-family: Arial, sans-serif; resize: vertical;"></textarea>
                        <button type="submit" style="background-color: #dc3545; color: white; padding: 10px; border: none; border-radius: 5px; font-family: Arial, sans-serif; cursor: pointer; transition: background-color 0.3s ease;">
                            Submit
                        </button>
                    </form>
                    <div id="form-message" style="margin-top: 10px; text-align: center; font-family: Arial, sans-serif;"></div>
                </div>
                <script>
                    document.getElementById("feedback-form").addEventListener("submit", function(event) {
                        event.preventDefault();
                        const form = event.target;
                        const formData = new FormData(form);
                        const messageDiv = document.getElementById("form-message");
                        messageDiv.innerHTML = '<p style="color: #333;">Submitting your feedback...</p>';
                        fetch("https://formspree.io/f/mnnpllqq", {
                            method: "POST",
                            body: formData,
                            headers: {
                                "Accept": "application/json"
                            }
                        })
                        .then(response => {
                            if (response.ok) {
                                messageDiv.innerHTML = '<p style="color: green; font-weight: bold;">Thank you for your feedback!</p>';
                                form.reset();
                            } else {
                                messageDiv.innerHTML = '<p style="color: red;">There was an error submitting your feedback. Please try again later.</p>';
                            }
                        })
                        .catch(error => {
                            console.error("Form submission error:", error);
                            messageDiv.innerHTML = '<p style="color: red;">There was an error submitting your feedback. Please try again later.</p>';
                        });
                    });
                </script>
                """)
    
    # CSS (end of the previous section, for context)
    gr.HTML("""
    <link rel="stylesheet" href="https://unpkg.com/shepherd.js@10.0.1/dist/css/shepherd.css">
    <script src="https://unpkg.com/shepherd.js@10.0.1/dist/js/shepherd.min.js" onerror="loadShepherdFallback()"></script>
    <script>
      function loadShepherdFallback() {
        console.warn('Shepherd.js CDN failed to load. Attempting to load from fallback...');
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/shepherd.js@10.0.1/dist/js/shepherd.min.js';
        script.onerror = () => {
          console.error('Shepherd.js fallback also failed. Tour will be unavailable.');
          alert('Tour unavailable: Shepherd.js failed to load from both sources. Please try again later.');
        };
        document.head.appendChild(script);
    
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = 'https://cdn.jsdelivr.net/npm/shepherd.js@10.0.1/dist/css/shepherd.css';
        document.head.appendChild(link);
      }
    </script>
    <style>
        /* General Layout */
        .gr-row { margin: 0 !important; padding: 5px 0 !important; }
        .gr-column { margin: 0 !important; padding: 5px !important; display: flex !important; flex-direction: column !important; align-items: stretch !important; }
        .gr-box { border-radius: 5px !important; }
        
        /* Style for Dealer’s Spin Tracker accordion */
        #sides-of-zero-accordion {
            background-color: #f5c6cb !important;
            padding: 10px !important;
        }
        #sides-of-zero-accordion > div {
            background-color: #f5c6cb !important;
        }
        #sides-of-zero-accordion summary {
            background-color: #dc3545 !important;
            color: #fff !important;
            padding: 10px !important;
            border-radius: 5px !important;
        }
        
        /* Style for Feedback Section accordion */
        #feedback-section summary {
            background-color: #dc3545 !important;
            color: #fff !important;
            padding: 10px !important;
            border-radius: 5px !important;
        }
        
        /* Hide stray labels in the Sides of Zero section */
        .sides-of-zero-container + label, .last-spins-container + label:not(.long-slider label) {
            display: none !important;
        }
        
        /* Header Styling */
        #header-row {
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            flex-wrap: wrap !important;
            background-color: white !important;
            padding: 10px 0 !important;
            width: 100% !important;
            margin: 0 auto !important;
            margin-bottom: 20px !important;
        }
        
        .header-title { text-align: center !important; font-size: 2.5em !important; margin: 0 !important; color: #333 !important; } 
        
        /* Fix Selected Spins Label Cutoff */
        #selected-spins-row {
            width: 100% !important;
            max-width: none !important;
            overflow: visible !important;
        }
        #selected-spins label {
            white-space: normal !important;
            width: 100% !important;
            height: auto !important;
            overflow: visible !important;
            display: block !important;
            background-color: #87CEEB;
            color: black;
            padding: 10px 5px !important;
            border-radius: 3px;
            line-height: 1.5em !important;
            font-size: 14px !important;
            margin-top: 5px !important;
        }
        #selected-spins {
            width: 100% !important;
            min-width: 800px !important;
        }
        
        /* Roulette Table */
        .roulette-button.green { background-color: green !important; color: white !important; border: 1px solid white !important; text-align: center !important; font-weight: bold !important; }
        .roulette-button.red { background-color: red !important; color: white !important; border: 1px solid white !important; text-align: center !important; font-weight: bold !important; }
        .roulette-button.black { background-color: black !important; color: white !important; border: 1px solid white !important; text-align: center !important; font-weight: bold !important; }
        .roulette-button:hover { opacity: 0.8; }
        .roulette-button.selected { border: 3px solid yellow !important; opacity: 0.9; }
        .roulette-button { margin: 0 !important; padding: 0 !important; width: 40px !important; height: 40px !important; font-size: 14px !important; display: flex !important; align-items: center !important; justify-content: center !important; border: 1px solid white !important; box-sizing: border-box !important; }
        .empty-button { margin: 0 !important; padding: 0 !important; width: 40px !important; height: 40px !important; border: 1px solid white !important; box-sizing: border-box !important; }
        .roulette-table { 
            display: flex !important; 
            flex-direction: column !important; 
            gap: 0 !important; 
            margin: 0 !important; 
            padding: 5px !important; 
            background-color: #2e7d32 !important;
            border: 2px solid #d3d3d3 !important; 
            border-radius: 5px !important; 
            width: 100% !important; 
            max-width: 600px !important; 
            margin: 0 auto !important; 
            overflow-x: auto !important;
            overflow-y: hidden !important;
        }
        .table-row { 
            display: flex !important; 
            gap: 0 !important; 
            margin: 0 !important; 
            padding: 0 !important; 
            flex-wrap: nowrap !important; 
            line-height: 0 !important; 
            min-width: 580px !important;
            white-space: nowrap !important;
        }
        
        /* Responsive adjustments for desktop */
        @media (min-width: 768px) {
            .roulette-table {
                max-width: 800px !important;
            }
            .table-row {
                min-width: 754px !important;
            }
            .roulette-button, .empty-button {
                width: 48px !important;
                height: 48px !important;
                font-size: 16px !important;
            }
        }
        
        /* Buttons */    
        .action-button { min-width: 120px !important; padding: 5px 10px !important; font-size: 14px !important; width: 100% !important; box-sizing: border-box !important; }
        button.green-btn { background-color: #28a745 !important; color: white !important; border: 1px solid #000 !important; padding: 8px 16px !important; transition: transform 0.2s ease, box-shadow 0.2s ease !important; box-sizing: border-box !important; }
        button.green-btn:hover { background-color: #218838 !important; transform: scale(1.05) !important; box-shadow: 0 4px 8px rgba(0,0,0,0.3) !important; }
        
        button.green-btn {
            background-color: #28a745 !important;
            color: white !important;
            border: 1px solid #000 !important;
            padding: 8px 16px !important;
            transition: transform 0.2s ease, box-shadow 0.2s ease !important;
            box-sizing: border-box !important;
        }
        button.green-btn:hover {
            background-color: #218838 !important;
            transform: scale(1.05) !important;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3) !important;
        }
        
        button.clear-spins-btn {
            background-color: #ff4444 !important;
            color: white !important;
            border: 1px solid #000 !important;
            box-sizing: border-box !important;
            display: inline-block !important;
        }
        button.clear-spins-btn:hover {
            background-color: #cc0000 !important;
        }
        button.generate-spins-btn { background-color: #007bff !important; color: white !important; border: 1px solid #000 !important; }
        button.generate-spins-btn:hover { background-color: #0056b3 !important; }
        
        /* NEW CODE: Add glow effect for buttons */
        .action-button, .green-btn, .roulette-button {
            transition: box-shadow 0.3s ease, transform 0.2s ease !important;
        }
        
        .action-button:active, .green-btn:active, .roulette-button:active {
            box-shadow: 0 0 10px 5px rgba(255, 215, 0, 0.7) !important; /* Yellow glow */
            transform: scale(1.05) !important; /* Slight scale for emphasis */
        }
        
        /* Ensure glow works on mobile touch */
        @media (max-width: 600px) {
            .action-button:active, .green-btn:active, .roulette-button:active {
                box-shadow: 0 0 8px 4px rgba(255, 215, 0, 0.7) !important; /* Slightly smaller glow for mobile */
            }
        }
        
        /* Optional: Glow for specific buttons like Analyze Spins */
        .green-btn:active {
            box-shadow: 0 0 10px 5px rgba(40, 167, 69, 0.7) !important; /* Green glow for Analyze button */
        }
        
        /* Ensure columns have appropriate spacing */
        .gr-column { margin: 0 !important; padding: 5px !important; display: flex !important; flex-direction: column !important; align-items: stretch !important; }
        
        /* Compact Components */
        .long-slider { width: 100% !important; margin: 0 !important; padding: 0 !important; }
        .long-slider .gr-box { width: 100% !important; }
        
        /* Target the Accordion and its children */
        .gr-accordion { background-color: #ffffff !important; }
        .gr-accordion * { background-color: #ffffff !important; }
        .gr-accordion .gr-column { background-color: #ffffff !important; }
        .gr-accordion .gr-row { background-color: #ffffff !important; }
        
        /* Section Labels */
        #selected-spins label { background-color: #87CEEB; color: black; padding: 5px; border-radius: 3px; }
        #spin-analysis label { background-color: #90EE90 !important; color: black !important; padding: 5px; border-radius: 3px; }
        #strongest-numbers-table label { background-color: #E6E6FA !important; color: black !important; padding: 5px; border-radius: 3px; }
        #number-of-random-spins label { background-color: #FFDAB9 !important; color: black !important; padding: 5px; border-radius: 3px; }
        #aggregated-scores label { background-color: #FFB6C1 !important; color: black !important; padding: 5px; border-radius: 3px; }
        #select-category label { background-color: #FFFFE0 !important; color: black !important; padding: 5px; border-radius: 3px; }
        
        /* Compact dropdown styling for Select Category and Select Strategy */
        #select-category select, #strategy-dropdown select {
            max-height: 150px !important;
            overflow-y: auto !important;
            scrollbar-width: thin !important;
            font-size: 14px;
            padding: 5px;
            background-color: #f9f9f9;
            border: 1px solid #ccc;
            border-radius: 3px;
        }
        #select-category select::-webkit-scrollbar, #strategy-dropdown select::-webkit-scrollbar {
            width: 6px;
        }
        #select-category select::-webkit-scrollbar-thumb, #strategy-dropdown select::-webkit-scrollbar-thumb {
            background-color: #888;
            border-radius: 3px;
        }
        
        /* Scrollable Tables */
        .scrollable-table {
            max-height: 300px;
            overflow-y: auto;
            display: block;
            width: 100%;
        }
        
        /* Updated styling for the Dynamic Roulette Table */
        .large-table {
            max-height: 800px !important;
            max-width: 1000px !important;
            margin: 0 auto !important;
            display: block !important;
            background: linear-gradient(135deg, #f0f0f0, #e0e0e0) !important;
            border: 2px solid #3b82f6 !important;
            border-radius: 10px !important;
            box-shadow: 0 0 15px rgba(59, 130, 246, 0.5) !important;
            padding: 10px !important;
        }
        /* Dynamic Table Container */
        .dynamic-table-container {
            width: 100% !important;
            max-width: 1200px !important;
            margin: 0 auto !important;
            padding: 20px 10px !important;
            display: flex !important;
            flex-direction: column !important; /* Ensure children stack vertically */
            justify-content: center !important;
            align-items: center !important;
            box-sizing: border-box !important;
        }
        
        /* Ensure all children of the container are centered */
        .dynamic-table-container > * {
            width: 100% !important;
            max-width: 900px !important; /* Match the large-table max-width */
            margin: 0 auto !important;
        }
        
        /* Large Table */
        .large-table {
            max-height: 800px !important;
            max-width: 900px !important;
            width: 100% !important;
            margin: 0 auto !important;
            display: block !important;
            background: linear-gradient(135deg, #f0f0f0, #e0e0e0) !important;
            border: 2px solid #3b82f6 !important;
            border-radius: 12px !important;
            box-shadow: 0 0 20px rgba(59, 130, 246, 0.6) !important;
            padding: 15px !important;
            box-sizing: border-box !important;
            overflow: visible !important;
            text-align: center !important; /* Center table content */
            animation: tableFadeIn 0.5s ease-in-out !important; /* Add load animation */
            /* Add gradient border */
            background-clip: padding-box !important;
            border-image: linear-gradient(45deg, #3b82f6, #1e90ff) 1 !important;
        }
        
        /* Define the load animation */
        @keyframes tableFadeIn {
            0% {
                opacity: 0;
                transform: scale(0.95);
            }
            100% {
                opacity: 1;
                transform: scale(1);
            }
        }
        
        .large-table table {
            width: 100% !important;
            max-width: 100% !important;
            margin: 0 auto !important;
            text-align: center !important;
        }
        
        .large-table th {
            font-weight: bold !important;
            color: #000000 !important;
            text-shadow: 0 0 5px rgba(0, 0, 0, 0.3) !important;
            background: rgba(59, 130, 246, 0.1) !important;
            padding: 10px !important;
        }
        
        .large-table td {
            padding: 8px !important;
            text-align: center !important;
            position: relative !important;
            overflow: visible !important;
        }
        
        /* Glowing Hover Effects for Hot Numbers (specific to Dynamic Roulette Table) */
        .dynamic-roulette-table td.hot-number:hover {
            box-shadow: 0 0 12px 4px #ffd700 !important;
            transform: scale(1.1) !important;
            transition: all 0.3s ease !important;
        }
        
        /* Tooltip Styles for Number Cells */
        .dynamic-roulette-table td.has-tooltip:hover::after {
            content: attr(data-tooltip) !important;
            position: absolute !important;
            background: #333 !important;
            color: #fff !important;
            padding: 5px 10px !important;
            border-radius: 4px !important;
            border: 1px solid #8c6bb1 !important;
            bottom: 100% !important;
            left: 50% !important;
            transform: translateX(-50%) !important;
            white-space: nowrap !important;
            z-index: 10 !important;
            font-size: 12px !important;
            font-family: Arial, sans-serif !important;
            animation: fadeIn 0.3s ease !important;
        }
        
        @keyframes fadeIn {
            0% { opacity: 0; transform: translateX(-50%) translateY(5px); }
            100% { opacity: 1; transform: translateX(-50%) translateY(0); }
        }
        
        /* Bet Tier Icons with Bounce Animation */
        .dynamic-roulette-table td.top-tier::before {
            content: "🔥" !important;
            margin-right: 5px !important;
            display: inline-block !important;
            animation: bounce 0.5s ease-in-out !important;
        }
        
        .dynamic-roulette-table td.middle-tier::before {
            content: "⭐" !important;
            margin-right: 5px !important;
            display: inline-block !important;
            animation: bounce 0.5s ease-in-out !important;
        }
        
        .dynamic-roulette-table td.lower-tier::before {
            content: "🌟" !important;
            margin-right: 5px !important;
            display: inline-block !important;
            animation: bounce 0.5s ease-in-out !important;
        }
        
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-5px); }
        }
        
        /* Progress Bar Styles for Bet Strength */
        .dynamic-roulette-table .progress-bar {
            width: 100% !important;
            height: 5px !important;
            background: #d3d3d3 !important;
            border-radius: 3px !important;
            margin-top: 3px !important;
            position: relative !important;
            display: block !important;
        }
        
        .dynamic-roulette-table .progress-fill.top-tier {
            height: 100% !important;
            background: #ffd700 !important; /* Yellow for top-tier */
            border-radius: 3px !important;
            position: absolute !important;
            top: 0 !important;
            left: 0 !important;
        }
        
        .dynamic-roulette-table .progress-fill.middle-tier {
            height: 100% !important;
            background: #00ffff !important; /* Cyan for middle-tier */
            border-radius: 3px !important;
            position: absolute !important;
            top: 0 !important;
            left: 0 !important;
        }
        
        .dynamic-roulette-table .progress-fill.lower-tier {
            height: 100% !important;
            background: #00ff00 !important; /* Green for lower-tier */
            border-radius: 3px !important;
            position: absolute !important;
            top: 0 !important;
            left: 0 !important;
        }
        
        /* Responsive adjustments */
        @media (max-width: 1200px) {
            .dynamic-table-container {
                max-width: 90vw !important;
                padding: 15px 5px !important;
            }
        
            .dynamic-table-container > * {
                max-width: 95% !important;
            }
        
            .large-table {
                max-width: 95% !important;
                padding: 12px !important;
            }
        }
        
        @media (max-width: 768px) {
            .dynamic-table-container {
                max-width: 100vw !important;
                padding: 10px 5px !important;
            }
        
            .dynamic-table-container > * {
                max-width: 100% !important;
            }
        
            .large-table {
                max-width: 100% !important;
                padding: 10px !important;
            }
        }
        

        .strategy-box {
            max-height: 300px !important;
            overflow-y: auto !important;
            max-width: 1000px !important;
            margin: 0 auto !important;
            background: linear-gradient(135deg, #1e3a8a, #3b82f6) !important;
            border: 2px solid #3b82f6 !important;
            border-radius: 10px !important;
            box-shadow: 0 0 15px rgba(59, 130, 246, 0.5) !important;
            padding: 15px !important;
        }
        
        .strategy-box, .strategy-box p, .strategy-box span, .strategy-box ul, .strategy-box li {
            color: #ffffff !important;
            text-shadow: 0 0 8px rgba(59, 130, 246, 0.7), 0 0 12px rgba(59, 130, 246, 0.5) !important;
        }
        
        .strategy-box .gr-dropdown, .strategy-box .gr-button, .strategy-box .gr-slider {
            background: rgba(59, 130, 246, 0.1) !important;
            border: 1px solid #3b82f6 !important;
            border-radius: 5px !important;
            color: #ffffff !important;
            text-shadow: 0 0 5px rgba(59, 130, 246, 0.5) !important;
        }
        
        .strategy-box .gr-dropdown select {
            background: transparent !important;
            color: #ffffff !important;
            border: none !important;
        }
        
        .strategy-box .gr-button {
            background: #3b82f6 !important;
            color: #ffffff !important;
            border: 1px solid #3b82f6 !important;
            box-shadow: 0 0 5px rgba(59, 130, 246, 0.5) !important;
        }
        
        .strategy-box .gr-button:hover {
            background: #1e90ff !important;
        }
        
        .strongest-numbers-table {
            width: 100% !important;
            max-width: 100% !important;
            background: linear-gradient(135deg, #2a2a72, #4682b4) !important;
            border-collapse: collapse !important;
            border: 1px solid #3b82f6 !important;
            box-shadow: 0 0 10px rgba(59, 130, 246, 0.5) !important;
            margin: 10px 0 !important;
        }
        
        .strongest-numbers-table th, .strongest-numbers-table td {
            padding: 8px 12px !important;
            border: 1px solid #3b82f6 !important;
            text-align: center !important;
            color: #ffffff !important;
            text-shadow: 0 0 5px rgba(59, 130, 246, 0.7) !important;
        }
        
        .strongest-numbers-table th {
            background: rgba(59, 130, 246, 0.2) !important;
            font-weight: bold !important;
        }
        
        .strongest-numbers-table td:nth-child(3), 
        .strongest-numbers-table td:nth-child(6), 
        .strongest-numbers-table td:nth-child(9) {
            white-space: normal !important;
            word-wrap: break-word !important;
            max-width: 150px !important;
        }
        
        /* Last Spins Container */
        .last-spins-container {
            background-color: #f5f5f5 !important;
            border: 1px solid #d3d3d3 !important;
            padding: 10px !important;
            border-radius: 5px !important;
            margin-top: 10px !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
        }
        
        /* Fade-in animation for Last Spins */
        .fade-in {
            animation: fadeIn 0.5s ease-in;
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        /* Pattern Badge for Spin Patterns */
        .pattern-badge {
            background-color: #ffd700 !important;
            color: #333 !important;
            padding: 2px 5px !important;
            border-radius: 3px !important;
            font-size: 10px !important;
            margin-left: 5px !important;
            cursor: pointer !important;
            transition: transform 0.2s ease !important;
        }
        .pattern-badge:hover {
            transform: scale(1.1) !important;
            box-shadow: 0 0 8px #ffd700 !important;
        }
        
        /* Quick Trends Section for SpinTrend Radar */
        .quick-trends {
            background: linear-gradient(135deg, #d8bfd8 0%, #e6e6fa 100%) !important; /* Light lavender gradient */
            padding: 12px !important;
            border-radius: 6px !important;
            margin-bottom: 12px !important;
            border: 1px solid #8c6bb1 !important; /* Purple border matching Hit Percentage Overview */
            box-shadow: 0 0 8px rgba(140, 107, 177, 0.3) !important; /* Subtle purple shadow */
        }
        
        .quick-trends h4 {
            margin: 0 0 8px 0 !important;
            font-size: 16px !important; /* Slightly larger for emphasis */
            color: #ff66cc !important; /* Pink to match Hit Percentage Overview border */
            text-shadow: 0 0 4px rgba(255, 102, 204, 0.5) !important; /* Subtle glow */
            font-weight: bold !important;
        }
        
        .quick-trends ul {
            margin: 0 !important;
            padding-left: 15px !important; /* Slight indent for list items */
        }
        
        .quick-trends ul li {
            color: #3e2723 !important; /* Dark brown for readability */
            font-size: 14px !important;
            margin: 4px 0 !important;
            font-weight: 500 !important; /* Medium weight for clarity */
        }
        
        /* Spin animation for roulette table buttons */
        .roulette-button:active {
            animation: spin 0.5s ease-in-out !important;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* Flash animation for new spins */
        .flash.red {
            animation: flashRed 0.3s ease-in-out;
        }
        .flash.green {
            animation: flashGreen 0.3s ease-in-out;
        }
        .flash.black {
            animation: flashBlack 0.3s ease-in-out;
        }
        @keyframes flashRed {
            0%, 100% { background-color: red; }
            50% { background-color: #ff3333; }
        }
        @keyframes flashRed {
            0%, 100% { background-color: red; }
            50% { background-color: #ff3333; }
        }
        @keyframes flashGreen {
            0%, 100% { background-color: green; }
            50% { background-color: #33cc33; }
        }
        @keyframes flashBlack {
            0%, 100% { background-color: black; }
            50% { background-color: #333333; }
        }
        
        /* Bounce animation for Dealer's Spin Tracker numbers */
        .bounce {
            animation: bounce 0.4s ease-in-out;
        }
        @keyframes bounce {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.2); }
        }
        
        /* New: Flip animation for Last Spins new numbers */
        .flip {
            animation: flip 0.5s ease-in-out;
        }
        @keyframes flip {
            0% { transform: rotateY(0deg); }
            100% { transform: rotateY(360deg); }
        }
        /* New Spin Highlight Effect */
        .new-spin {
            position: relative !important;
            animation: pulse-highlight 1s ease-in-out !important;
        }
        
        @keyframes pulse-highlight {
            0%, 100% { box-shadow: none; }
            50% { box-shadow: 0 0 10px 5px var(--highlight-color); }
        }
        
        /* Color-coded highlights for new spins */
        .new-spin.spin-red {
            --highlight-color: rgba(255, 0, 0, 0.8) !important;
        }
        .new-spin.spin-black {
            --highlight-color: rgba(255, 255, 255, 0.8) !important;
        }
        .new-spin.spin-green {
            --highlight-color: rgba(0, 255, 0, 0.8) !important;
        }
        
        /* Spin Counter Styling */
        .spin-counter {
            font-size: 14px !important;
            font-weight: bold !important;
            color: #ffffff !important;
            background: linear-gradient(135deg, #87CEEB, #5DADE2) !important;
            padding: 4px 8px !important;
            border: 2px solid #3498DB !important;
            border-radius: 6px !important;
            margin-top: 0 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.15) !important;
            transition: transform 0.2s ease, box-shadow 0.2s ease !important;
        }
        .spin-counter:hover {
            transform: scale(1.05) !important;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3) !important;
        }
        .spin-counter.glow {
            animation: counter-glow 0.5s ease-in-out !important;
        }
        
        @keyframes counter-glow {
            0%, 100% { box-shadow: 0 2px 4px rgba(0,0,0,0.15); }
            50% { box-shadow: 0 0 10px 5px rgba(52, 152, 219, 0.8); }
        }
        .sides-of-zero-container {
            background-color: #ffffff !important;
            border: 1px solid #d3d3d3 !important;
            padding: 10px !important;
            border-radius: 5px !important;
            margin: 10px 0 !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
        }
        
        /* Hit Percentage Overview - Revamped for High-Tech Look with Increased Specificity */
        #hit-percentage-overview .hit-percentage-container {
            padding: 20px !important;
            background: linear-gradient(135deg, #6b4e8c 0%, #8c6bb1 100%) !important;
            border-radius: 12px !important;
            border: 3px solid #ff66cc !important;
            box-shadow: 0 0 20px rgba(255, 102, 204, 0.5) !important;
            width: 100% !important;
            max-width: 2000px !important;
            margin-top: 10px !important;
            box-sizing: border-box !important;
            position: relative !important;
            overflow: visible !important;
            animation: dataPulse 3s ease-in-out infinite !important;
            outline: 2px solid yellow !important;
        }
        
        /* Data scanning pulse effect */
        @keyframes dataPulse {
            0%, 100% { box-shadow: 0 0 20px rgba(255, 102, 204, 0.5); }
            50% { box-shadow: 0 0 30px rgba(255, 102, 204, 0.8); }
        }
        
        /* Add a subtle grid overlay for high-tech effect */
        #hit-percentage-overview .hit-percentage-container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: radial-gradient(circle, rgba(255, 102, 204, 0.15) 0%, transparent 70%) !important;
            opacity: 0.4;
            pointer-events: none;
        }
        
        #hit-percentage-overview .hit-percentage-overview {
            display: flex !important;
            flex-wrap: wrap !important;
            gap: 20px !important;
        }
        
        #hit-percentage-overview .percentage-wrapper {
            width: 100% !important;
            max-width: 1600px !important;
            box-sizing: border-box !important;
            padding-top: 15px !important;
        }
        
        #hit-percentage-overview .percentage-group {
            margin: 10px 0 !important;
            padding-top: 15px !important;
            flex: 1 !important;
            min-width: 150px !important;
            overflow: visible !important;
        }
        
        #hit-percentage-overview .percentage-group h4 {
            margin: 5px 0 !important;
            color: #ffccff !important;
            text-shadow: 0 0 5px rgba(255, 102, 204, 0.5) !important;
        }
        
        #hit-percentage-overview .percentage-badges, #hit-percentage-overview .percentage-badges {
            display: flex !important;
            flex-wrap: wrap !important;
            gap: 10px !important;
            align-items: center !important;
            padding: 5px 0 !important;
        }
        
        /* Responsive adjustments for mobile */
        @media (max-width: 600px) {
            #hit-percentage-overview .percentage-badges, #hit-percentage-overview .percentage-badges {
                flex-wrap: wrap !important;
                overflow-x: visible !important;
            }
            #hit-percentage-overview .percentage-item {
                font-size: 10px !important;
                padding: 4px 8px !important;
            }
        }
        
        /* TITLE: Percentage Item Styles - Revamped for High-Tech Effect */
        #hit-percentage-overview .percentage-item {
            background: transparent !important;
            color: #fff !important;
            padding: 6px 14px !important;
            border-radius: 15px !important;
            font-size: 12px !important;
            margin: 5px 3px !important;
            transition: transform 0.2s, box-shadow 0.3s, filter 0.3s !important;
            cursor: pointer !important;
            border: 1px solid transparent !important;
            box-shadow: 0 0 10px rgba(255, 255, 255, 0.3) !important;
            font-weight: bold !important;
            display: inline-block !important;
        }
        
        #hit-percentage-overview .percentage-item:hover {
            transform: scale(1.15) !important;
            filter: brightness(1.4) !important;
        }
        
        #hit-percentage-overview .percentage-item.even-money {
            background: rgba(255, 77, 77, 0.3) !important;
            border-color: #ff4d4d !important;
            box-shadow: 0 0 12px rgba(255, 77, 77, 0.7) !important;
        }
        
        #hit-percentage-overview .percentage-item.column {
            background: rgba(77, 121, 255, 0.3) !important;
            border-color: #4d79ff !important;
            box-shadow: 0 0 12px rgba(77, 121, 255, 0.7) !important;
        }
        
        #hit-percentage-overview .percentage-item.dozen {
            background: rgba(77, 255, 77, 0.3) !important;
            border-color: #4dff4d !important;
            box-shadow: 0 0 12px rgba(77, 255, 77, 0.7) !important;
        }
        
        #hit-percentage-overview .percentage-item.winner {
            font-weight: bold !important;
            color: #fff !important;
            border: 2px solid #ffcc00 !important;
            box-shadow: 0 0 15px #ffcc00 !important;
            background: rgba(255, 204, 0, 0.4) !important;
            transform: scale(1.15) !important;
        }
        
        #hit-percentage-overview .percentage-with-bar {
            display: inline-block !important;
            text-align: center !important;
            margin: 0 3px !important;
            margin-bottom: 8px !important;
        }
        
        /* TITLE: Fix Content Titles for Hit Percentage Overview and SpinTrend Radar */
        .hit-percentage-overview > h4 {
            color: #ff66cc !important;
            text-shadow: 0 0 8px rgba(255, 102, 204, 0.7) !important;
            font-size: 18px !important;
            font-weight: bold !important;
            margin: 0 0 10px 0 !important;
            outline: 2px solid yellow !important;
        }
        
        .traits-overview > h4 {
            color: #00ffcc !important;
            text-shadow: 0 0 8px rgba(0, 255, 204, 0.7) !important;
            font-size: 18px !important;
            font-weight: bold !important;
            margin: 0 0 10px 0 !important;
            outline: 2px solid yellow !important;
        }
        
        /* TITLE: Style Accordion Containers for SpinTrend Radar and Hit Percentage Overview */
        #spin-trend-radar.gr-accordion, #spin-trend-radar.gr-accordion > details {
            background: linear-gradient(135deg, #6b4e8c 0%, #8c6bb1 100%) !important;
            border: 2px solid #00ffcc !important;
            border-radius: 10px !important;
            padding: 10px !important;
            box-shadow: 0 0 10px rgba(0, 255, 204, 0.3) !important;
            outline: 2px solid red !important;
        }
        
        #spin-trend-radar.gr-accordion summary {
            background: rgba(0, 255, 204, 0.15) !important;
            color: #00ffcc !important;
            text-shadow: 0 0 8px rgba(0, 255, 204, 0.7) !important;
            font-size: 18px !important;
            font-weight: bold !important;
            padding: 10px !important;
            border-radius: 8px !important;
        }

        #hit-percentage-overview.gr-accordion, #hit-percentage-overview.gr-accordion > details {
            background: #3a1a5a !important;
            border: 2px solid #ff66cc !important;
            border-radius: 10px !important;
            padding: 10px !important;
            box-shadow: 0 0 10px rgba(255, 102, 204, 0.3) !important;
            outline: 2px solid red !important;
        }
        
        #hit-percentage-overview.gr-accordion summary {
            background: rgba(255, 102, 204, 0.1) !important;
            color: #ff66cc !important;
            text-shadow: 0 0 8px rgba(255, 102, 204, 0.7) !important;
            font-size: 18px !important;
            font-weight: bold !important;
            padding: 10px !important;
            border-radius: 8px !important;
        }
        
        /* TITLE: Progress Bar Styles (UPDATED FOR CHANGE 7) */
        .progress-bar {
            width: 100% !important;
            height: 6px !important;
            min-height: 6px !important;
            background-color: #d3d3d3 !important;
            border-radius: 3px !important;
            margin-top: 6px !important;
            overflow: hidden !important;
            display: block !important;
        }
        .progress-fill {
            height: 100% !important;
            border-radius: 3px !important;
            transition: width 0.3s ease !important;
            display: block !important;
        }
        
        /* TITLE: Traits Container - Revamped for Radar Effect */
        .traits-container {
            padding: 20px !important;
            background: linear-gradient(135deg, #6b4e8c 0%, #8c6bb1 100%) !important; /* Same as Hit Percentage Overview */
            border-radius: 10px !important;
            border: 2px solid #00ffcc !important;
            box-shadow: 0 0 15px rgba(0, 255, 204, 0.3) !important;
            width: 100% !important;
            max-width: 2000px !important;
            margin-top: 10px !important;
            box-sizing: border-box !important;
            position: relative !important;
            overflow: visible !important;
            animation: radarPulse 4s ease-in-out infinite !important;
        }
        
        /* Radar pulsing effect */
        @keyframes radarPulse {
            0%, 100% { box-shadow: 0 0 15px rgba(0, 255, 204, 0.3); }
            50% { box-shadow: 0 0 25px rgba(0, 255, 204, 0.5); }
        }
        
        /* Add a radar-like overlay (optional subtle grid effect) */
        .traits-container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: radial-gradient(circle, rgba(0, 255, 204, 0.1) 0%, transparent 70%) !important;
            opacity: 0.3;
            pointer-events: none;
        }
        
        /* TITLE: Traits Badges Layout */
        .traits-wrapper {
            width: 100% !important;
            max-width: 1600px !important;
            box-sizing: border-box !important;
            display: flex !important;
            flex-wrap: wrap !important;
            gap: 15px !important;
            padding-top: 10px !important;
        }
        .badge-group {
            margin: 10px 0 !important;
            padding-top: 10px !important;
            flex: 1 !important;
            min-width: 150px !important;
            overflow: visible !important;
        }
        .badge-group:nth-child(1) h4 { color: #ff4d4d !important; } /* Even Money Bets - Neon Red */
        .badge-group:nth-child(2) h4 { color: #4d79ff !important; } /* Columns - Neon Blue */
        .badge-group:nth-child(3) h4 { color: #4dff4d !important; } /* Dozens - Neon Green */
        .badge-group:nth-child(4) h4 { color: #cc33ff !important; } /* Repeat Numbers - Neon Purple */
        .percentage-badges {
            display: flex !important;
            flex-wrap: wrap !important;
            gap: 8px !important;
            align-items: center !important;
            padding: 5px 0 !important;
        }
        
        /* TITLE: Trait Badge Styles - Revamped for Radar Effect */
        .trait-badge {
            background: transparent !important;
            color: #fff !important;
            padding: 5px 12px !important;
            border-radius: 15px !important;
            font-size: 12px !important;
            margin: 5px 3px !important;
            transition: transform 0.2s, box-shadow 0.3s, filter 0.3s !important;
            cursor: pointer !important;
            border: 1px solid transparent !important;
            box-shadow: 0 0 8px rgba(255, 255, 255, 0.2) !important;
            font-weight: bold !important;
            display: inline-block !important;
        }
        .trait-badge:hover {
            transform: scale(1.1) !important;
            filter: brightness(1.3) !important;
        }
        .trait-badge.even-money {
            background: rgba(255, 77, 77, 0.2) !important;
            border-color: #ff4d4d !important;
            box-shadow: 0 0 10px rgba(255, 77, 77, 0.5) !important;
        }
        .trait-badge.column {
            background: rgba(77, 121, 255, 0.2) !important;
            border-color: #4d79ff !important;
            box-shadow: 0 0 10px rgba(77, 121, 255, 0.5) !important;
        }
        .trait-badge.dozen {
            background: rgba(77, 255, 77, 0.2) !important;
            border-color: #4dff4d !important;
            box-shadow: 0 0 10px rgba(77, 255, 77, 0.5) !important;
        }
        .trait-badge.repeat {
            background: rgba(204, 51, 255, 0.2) !important;
            border-color: #cc33ff !important;
            box-shadow: 0 0 10px rgba(204, 51, 255, 0.5) !important;
        }
        .trait-badge.winner {
            font-weight: bold !important;
            color: #fff !important;
            border: 2px solid #ffd700 !important;
            box-shadow: 0 0 12px #ffd700 !important;
            background: rgba(255, 215, 0, 0.3) !important;
            transform: scale(1.1) !important;
        }
        
        /* TITLE: Hot Streak Indicator (UPDATED FOR CHANGE 5) */
        .hot-streak {
            display: none !important;
        }
        .hot-streak:hover:after {
            content: attr(title);
            position: absolute;
            background-color: #333 !important;
            color: white !important;
            padding: 6px 10px !important;
            border-radius: 5px !important;
            font-size: 12px !important;
            font-family: Arial, sans-serif !important;
            white-space: nowrap !important;
            z-index: 20 !important;
            top: -35px !important;
            left: 50% !important;
            transform: translateX(-50%) !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.3) !important;
            animation: fadeInTooltip 0.3s ease-in !important;
        }
        @keyframes fadeInTooltip {
            0% { opacity: 0; transform: translateX(-50%) translateY(5px); }
            100% { opacity: 1; transform: translateX(-50%) translateY(0); }
        }
        
        /* Placeholder Section for Hit Percentage and SpinTrend Radar */
        .placeholder-section {
            background-color: #000 !important;
            min-height: 200px !important;
            height: 100% !important;
            width: 100% !important;
            border-radius: 5px !important;
            box-sizing: border-box !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            color: #fff !important;
            font-family: Arial, sans-serif !important;
        }
        
        /* Ensure the columns are truly 50/50 and aligned */
        .hit-percentage-container, .traits-container {
            width: 100% !important;
            max-width: none !important;
            margin: 0 !important;
        }
        
        /* Responsive adjustments */
        @media (max-width: 600px) {
            .placeholder-section {
                min-height: 150px !important;
            }
            .hit-percentage-container, .traits-container {
                padding: 5px !important;
            }
        }
        
        /* TITLE: Suggestion Box */
        .suggestion-box {
            background-color: #f0f8ff !important;
            border: 1px solid #4682b4 !important;
            border-radius: 5px !important;
            padding: 5px !important;
            font-size: 14px !important;
        }
        
        /* TITLE: Spin Animation */
        .play-btn:active {
            animation: spin 0.5s ease-in-out !important;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* TITLE: Fade-In Animation */
        .fade-in {
            animation: fadeIn 0.5s ease-in !important;
        }
    </style>
    """)
    print("CSS Updated")
    
    # Shepherd.js Tour Script
    gr.HTML("""
    <script>
      const tour = new Shepherd.Tour({
        defaultStepOptions: {
          cancelIcon: { enabled: true },
          scrollTo: { behavior: 'smooth', block: 'center' },
          classes: 'shepherd-theme-arrows',
          buttons: [
            { text: 'Back', action: function() { return this.back(); } },
            { text: 'Next', action: function() { return this.next(); } },
            { text: 'Skip', action: function() { return this.cancel(); } }
          ]
        },
        useModalOverlay: true
      });
    
      // Debug function to log step transitions
      function logStep(stepId, nextStepId) {
        return () => {
          console.log(`Moving from ${stepId} to ${nextStepId}`);
          tour.next();
        };
      }
    
      // Force accordion open with direct DOM manipulation and Promise
      function forceAccordionOpen(accordionId) {
        console.log(`Checking accordion: ${accordionId}`);
        return new Promise(resolve => {
          const accordion = document.querySelector(accordionId);
          if (!accordion) {
            console.warn(`Accordion ${accordionId} not found`);
            resolve();
            return;
          }
          const content = accordion.querySelector('.gr-box') || accordion.nextElementSibling;
          if (content && window.getComputedStyle(content).display === 'none') {
            console.log(`Forcing ${accordionId} open`);
            content.style.display = 'block';
            accordion.setAttribute('open', '');
            setTimeout(() => {
              if (window.getComputedStyle(content).display === 'none') {
                console.warn(`Fallback: Forcing visibility for ${accordionId}`);
                content.style.display = 'block';
              }
              resolve();
            }, 500);
          } else {
            console.log(`${accordionId} already open or no content found`);
            resolve();
          }
        });
      }
    
      // Step 1: Header
      tour.addStep({
        id: 'part1',
        title: 'Your Roulette Adventure Begins!',
        text: 'Welcome to the Roulette Spin Analyzer! This tour will guide you through the key features to master your game.<br><iframe width="280" height="158" src="https://www.youtube.com/embed/H7TLQr1HnY0?fs=0" frameborder="0"></iframe>',
        attachTo: { element: '#header-row', on: 'bottom' },
        buttons: [
          { text: 'Next', action: logStep('Part 1', 'Part 2') },
          { text: 'Skip', action: tour.cancel }
        ]
      });
    
      // Step 2: Roulette Table
      tour.addStep({
        id: 'part2',
        title: 'Spin the Wheel, Start the Thrill!',
        text: 'Click numbers on the European Roulette Table to record spins and track your game.<br><iframe width="280" height="158" src="https://www.youtube.com/embed/ja454kZwndo?fs=0" frameborder="0"></iframe>',
        attachTo: { element: '.roulette-table', on: 'right' },
        buttons: [
          { text: 'Back', action: tour.back },
          { text: 'Next', action: logStep('Part 2', 'Part 3') },
          { text: 'Skip', action: tour.cancel }
        ]
      });
    
      // Step 3: Last Spins Display
      tour.addStep({
        id: 'part3',
        title: 'Peek at Your Spin Streak!',
        text: 'View your recent spins here, color-coded for easy tracking.<br><iframe width="280" height="158" src="https://www.youtube.com/embed/a9brOFMy9sA?fs=0" frameborder="0"></iframe>',
        attachTo: { element: '.last-spins-container', on: 'bottom' },
        buttons: [
          { text: 'Back', action: tour.back },
          { text: 'Next', action: logStep('Part 3', 'Part 4') },
          { text: 'Skip', action: tour.cancel }
        ]
      });
    
      // Step 4: Spin Controls
      tour.addStep({
        id: 'part4',
        title: 'Master Your Spin Moves!',
        text: 'Use these buttons to undo spins, generate random spins, or clear the display.<br><iframe width="280" height="158" src="https://www.youtube.com/embed/xG8z1S4HJK4?fs=0" frameborder="0"></iframe>',
        attachTo: { element: '#undo-spins-btn', on: 'bottom' },
        buttons: [
          { text: 'Back', action: tour.back },
          { text: 'Next', action: logStep('Part 4', 'Part 5') },
          { text: 'Skip', action: tour.cancel }
        ]
      });
    
      // Step 5: Selected Spins Textbox
      tour.addStep({
        id: 'part5',
        title: 'Jot Spins, Count Wins!',
        text: 'Manually enter spins here (e.g., 5, 12, 0) to analyze your game.<br><iframe width="280" height="158" src="https://www.youtube.com/embed/2-k1EyKUM8U?fs=0" frameborder="0"></iframe>',
        attachTo: { element: '#selected-spins', on: 'bottom' },
        buttons: [
          { text: 'Back', action: tour.back },
          { text: 'Next', action: logStep('Part 5', 'Part 6') },
          { text: 'Skip', action: tour.cancel }
        ]
      });
    
      // Step 6: Analyze Button
      tour.addStep({
        id: 'part6',
        title: 'Analyze and Reset Like a Pro!',
        text: 'Click "Analyze Spins" to break down your spins and get insights.<br><iframe width="280" height="158" src="https://www.youtube.com/embed/8plHP2RIR3o?fs=0" frameborder="0"></iframe>',
        attachTo: { element: '.green-btn', on: 'bottom' },
        buttons: [
          { text: 'Back', action: tour.back },
          { text: 'Next', action: logStep('Part 6', 'Part 7') },
          { text: 'Skip', action: tour.cancel }
        ]
      });
    
      // Step 7: Dynamic Table
      tour.addStep({
        id: 'part7',
        title: 'Light Up Your Lucky Spots!',
        text: 'The Dynamic Roulette Table highlights trending numbers and bets based on your strategy.<br><iframe width="280" height="158" src="https://www.youtube.com/embed/zT9d06sn07E?fs=0" frameborder="0"></iframe>',
        attachTo: { element: '#dynamic-table-heading', on: 'bottom' },
        buttons: [
          { text: 'Back', action: tour.back },
          { text: 'Next', action: logStep('Part 7', 'Part 8') },
          { text: 'Skip', action: tour.cancel }
        ]
      });
    
      // Step 8: Betting Progression Tracker
      tour.addStep({
        id: 'part8',
        title: 'Bet Smart, Track the Art!',
        text: 'Track your betting progression (e.g., Martingale, Fibonacci) to manage your bankroll.<br><iframe width="280" height="158" src="https://www.youtube.com/embed/jkE-w2MOJ0o?fs=0" frameborder="0"></iframe>',
        attachTo: { element: '.betting-progression', on: 'top' },
        beforeShowPromise: function() {
          return forceAccordionOpen('.betting-progression');
        },
        buttons: [
          { text: 'Back', action: tour.back },
          { text: 'Next', action: logStep('Part 8', 'Part 9') },
          { text: 'Skip', action: tour.cancel }
        ]
      });
    
      // Step 9: Color Code Key
      tour.addStep({
        id: 'part9',
        title: 'Paint Your Winning Hue!',
        text: 'Customize colors for the Dynamic Table to highlight hot and cold bets.<br><iframe width="280" height="158" src="https://www.youtube.com/embed/pUtW2HnWVL8?fs=0" frameborder="0"></iframe>',
        attachTo: { element: '#color-code-key', on: 'top' },
        beforeShowPromise: function() {
          return forceAccordionOpen('#color-code-key');
        },
        buttons: [
          { text: 'Back', action: tour.back },
          { text: 'Next', action: logStep('Part 9', 'Part 10') },
          { text: 'Skip', action: tour.cancel }
        ]
      });
    
      // Step 10: Color Code Key (Continued)
      tour.addStep({
        id: 'part10',
        title: 'Decode the Color Clue!',
        text: 'Understand the color coding to make informed betting decisions.<br><iframe width="280" height="158" src="https://www.youtube.com/embed/PGBEoOOh9Gk?fs=0" frameborder="0"></iframe>',
        attachTo: { element: '#color-code-key', on: 'top' },
        beforeShowPromise: function() {
          return forceAccordionOpen('#color-code-key');
        },
        buttons: [
          { text: 'Back', action: tour.back },
          { text: 'Next', action: logStep('Part 10', 'Part 11') },
          { text: 'Skip', action: tour.cancel }
        ]
      });
    
      // Step 11: Spin Analysis
      tour.addStep({
        id: 'part11',
        title: 'Unleash the Spin Secrets!',
        text: 'Dive into detailed spin analysis to uncover patterns and trends.<br><iframe width="280" height="158" src="https://www.youtube.com/embed/MpcuwWnMdrg?fs=0" frameborder="0"></iframe>',
        attachTo: { element: '#spin-analysis', on: 'top' },
        beforeShowPromise: function() {
          return forceAccordionOpen('#spin-analysis');
        },
        buttons: [
          { text: 'Back', action: tour.back },
          { text: 'Next', action: logStep('Part 11', 'Part 12') },
          { text: 'Skip', action: tour.cancel }
        ]
      });
    
      // Step 12: Save/Load Session
      tour.addStep({
        id: 'part12',
        title: 'Save Your Spin Glory!',
        text: 'Save your session or load a previous one to continue your analysis.<br><iframe width="280" height="158" src="https://www.youtube.com/embed/pHLEa2I0jjE?fs=0" frameborder="0"></iframe>',
        attachTo: { element: '#save-load-session', on: 'top' },
        beforeShowPromise: function() {
          return forceAccordionOpen('#save-load-session');
        },
        buttons: [
          { text: 'Back', action: tour.back },
          { text: 'Next', action: logStep('Part 12', 'Part 13') },
          { text: 'Skip', action: tour.cancel }
        ]
      });
    
      // Step 13: Strategy Selection
      tour.addStep({
        id: 'part13',
        title: 'Pick Your Strategy Groove!',
        text: 'Choose a betting strategy to optimize your game plan.<br><iframe width="280" height="158" src="https://www.youtube.com/embed/iuGEltUVbqc?fs=0" frameborder="0"></iframe>',
        attachTo: { element: '#select-category', on: 'left' },
        buttons: [
          { text: 'Back', action: tour.back },
          { text: 'Next', action: logStep('Part 13', 'Part 14') },
          { text: 'Skip', action: tour.cancel }
        ]
      });
    
      // Step 14: Casino Data Insights
      tour.addStep({
        id: 'part14',
        title: 'Boost Wins with Casino Intel!',
        text: 'Enter casino data to highlight winning trends and make smarter bets.<br><iframe width="280" height="158" src="https://www.youtube.com/embed/FJIczwv9_Ss?fs=0" frameborder="0"></iframe>',
        attachTo: { element: '#casino-data-insights', on: 'bottom' },
        beforeShowPromise: function() {
          return forceAccordionOpen('#casino-data-insights');
        },
        buttons: [
          { text: 'Back', action: tour.back },
          { text: 'Next', action: logStep('Part 14', 'Part 14a') },
          { text: 'Skip', action: tour.cancel }
        ]
      });
    
      // Step 14a: Hot and Cold Numbers
      tour.addStep({
          id: 'part14',
          title: 'Boost Wins with Casino Intel!',
          text: 'Enter casino data to highlight winning trends and make smarter bets.<br><iframe width="280" height="158" src="https://www.youtube.com/embed/FJIczwv9_Ss?fs=0" frameborder="0"></iframe>',
          attachTo: { element: '#casino-data-insights', on: 'bottom' },
          beforeShowPromise: function() {
            console.log('Starting Step 14: Casino Data Insights');
            return forceAccordionOpen('#casino-data-insights');
          },
          buttons: [
            { text: 'Back', action: tour.back },
            { text: 'Finish', action: function() { console.log('Tour completed at Step 14'); tour.complete(); } },
            { text: 'Skip', action: tour.cancel }
          ]
        });
    
      // Step 15: Dealer’s Spin Tracker
      tour.addStep({
        id: 'part15',
        title: 'Spot the Dealer’s Bias!',
        text: 'Uncover potential biases in the Dealer’s Spin Tracker to gain an edge.<br><iframe width="280" height="158" src="https://www.youtube.com/embed/ISoFvrnXbHA?fs=0" frameborder="0"></iframe>',
        attachTo: { element: '#sides-of-zero-accordion', on: 'top' },
        beforeShowPromise: function() {
          return forceAccordionOpen('#sides-of-zero-accordion');
        },
        buttons: [
          { text: 'Back', action: tour.back },
          { text: 'Next', action: logStep('Part 15', 'Part 16a') },
          { text: 'Skip', action: tour.cancel }
        ]
      });
    
      // Step 16a: Create Dozen/Even Bet Triggers - Dozen Triggers
      tour.addStep({
        id: 'part16a',
        title: 'Trigger Dozen Wins!',
        text: 'Set up Dozen Triggers to catch hot streaks and patterns.<br><iframe width="280" height="158" src="https://www.youtube.com/embed/iYfhd8_C1IM?fs=0" frameborder="0"></iframe>',
        attachTo: { element: '#dozen-tracker', on: 'top' },
        beforeShowPromise: function() {
          return forceAccordionOpen('#dozen-tracker');
        },
        buttons: [
          { text: 'Back', action: tour.back },
          { text: 'Next', action: logStep('Part 16a', 'Part 16a1') },
          { text: 'Skip', action: tour.cancel }
        ]
      });
    
      // Step 16a1: Create Dozen/Even Bet Triggers - Dozen Triggers: Alert on Consecutive Dozen Hits
      tour.addStep({
        id: 'part16a1',
        title: 'Catch Dozen Streaks!',
        text: 'Enable alerts for consecutive Dozen hits to spot trends fast.<br><iframe width="280" height="158" src="https://www.youtube.com/embed/e6KAOAoImNQ?fs=0" frameborder="0"></iframe>',
        attachTo: { element: '#dozen-tracker', on: 'top' },
        beforeShowPromise: function() {
          return forceAccordionOpen('#dozen-tracker');
        },
        buttons: [
          { text: 'Back', action: tour.back },
          { text: 'Next', action: logStep('Part 16a1', 'Part 16a2') },
          { text: 'Skip', action: tour.cancel }
        ]
      });
    
      // Step 16a2: Create Dozen/Even Bet Triggers - Dozen Triggers: Sequence Length to Match (X), Follow-Up Spins to Track (Y)
      tour.addStep({
        id: 'part16a2',
        title: 'Match Dozen Sequences!',
        text: 'Track sequences and follow-ups to predict Dozen patterns.<br><iframe width="280" height="158" src="https://www.youtube.com/embed/X4mFSMMc21g?fs=0" frameborder="0"></iframe>',
        attachTo: { element: '#dozen-tracker', on: 'top' },
        beforeShowPromise: function() {
          return forceAccordionOpen('#dozen-tracker');
        },
        buttons: [
          { text: 'Back', action: tour.back },
          { text: 'Next', action: logStep('Part 16a2', 'Part 16b') },
          { text: 'Skip', action: tour.cancel }
        ]
      });
    
      // Step 16b: Create Dozen/Even Bet Triggers - Even Money Bet Triggers
      tour.addStep({
        id: 'part16b',
        title: 'Trigger Even Money Magic!',
        text: 'Set Even Money Triggers to catch winning streaks and traits.<br><iframe width="280" height="158" src="https://www.youtube.com/embed/5z7TjjwpTs0?fs=0" frameborder="0"></iframe>',
        attachTo: { element: '#dozen-tracker', on: 'top' },
        beforeShowPromise: function() {
          return forceAccordionOpen('#dozen-tracker');
        },
        buttons: [
          { text: 'Back', action: tour.back },
          { text: 'Next', action: logStep('Part 16b', 'Part 16b1') },
          { text: 'Skip', action: tour.cancel }
        ]
      });
    
      // Step 16b1: Create Dozen/Even Bet Triggers - Even Money Bet Triggers - Alert on Consecutive Even Money Hits (And/Or)
      tour.addStep({
        id: 'part16b1',
        title: 'Even Money Streaks On!',
        text: 'Get alerts for consecutive Even Money hits with And/Or logic.<br><iframe width="280" height="158" src="https://www.youtube.com/embed/gjQcOdNDGKc?fs=0" frameborder="0"></iframe>',
        attachTo: { element: '#dozen-tracker', on: 'top' },
        beforeShowPromise: function() {
          return forceAccordionOpen('#dozen-tracker');
        },
        buttons: [
          { text: 'Back', action: tour.back },
          { text: 'Next', action: logStep('Part 16b1', 'Part 16b2') },
          { text: 'Skip', action: tour.cancel }
        ]
      });
    
      // Step 16b2: Create Dozen/Even Bet Triggers - Even Money Bet Triggers - Track Consecutive Identical Traits
      tour.addStep({
        id: 'part16b2',
        title: 'Track Even Money Traits!',
        text: 'Spot consecutive identical traits to refine your Even Money bets.<br><iframe width="280" height="158" src="https://www.youtube.com/embed/iRz_y8DeqCU?fs=0" frameborder="0"></iframe>',
        attachTo: { element: '#dozen-tracker', on: 'top' },
        beforeShowPromise: function() {
          return forceAccordionOpen('#dozen-tracker');
        },
        buttons: [
          { text: 'Back', action: tour.back },
          { text: 'Next', action: logStep('Part 16b2', 'Part 17') },
          { text: 'Skip', action: tour.cancel }
        ]
      });
    
      // Step 17: Top Strategies with Roulette Spin Analyzer
      tour.addStep({
        id: 'part17',
        title: 'Learn Top Strategies!',
        text: 'Explore winning strategies with video tutorials to level up your game.<br><iframe width="280" height="158" src="https://www.youtube.com/embed/t_5gvje0SKI?fs=0" frameborder="0"></iframe>',
        attachTo: { element: '#top-strategies', on: 'top' },
        beforeShowPromise: function() {
          return forceAccordionOpen('#top-strategies');
        },
        buttons: [
          { text: 'Back', action: tour.back },
          { text: 'Next', action: logStep('Part 17', 'Part 18') },
          { text: 'Skip', action: tour.cancel }
        ]
      });
    
      // Step 18: Feedback & Suggestions
      tour.addStep({
        id: 'part18',
        title: 'Share Your Winning Ideas!',
        text: 'Submit feedback or suggest new strategies to enhance the app.<br><iframe width="280" height="158" src="https://www.youtube.com/embed/9MgXNg2oDvk?fs=0" frameborder="0"></iframe>',
        attachTo: { element: '#feedback-section', on: 'top' },
        beforeShowPromise: function() {
          return forceAccordionOpen('#feedback-section');
        },
        buttons: [
          { text: 'Back', action: tour.back },
          { text: 'Finish', action: () => { console.log('Tour completed'); tour.complete(); } }
        ]
      });
    
      function startTour() {
        console.log('Tour starting... Attempting to initialize Shepherd.js tour.');
        if (typeof Shepherd === 'undefined') {
          console.error('Shepherd.js is not loaded. Check CDN or network connectivity.');
          alert('Tour unavailable: Shepherd.js failed to load. Please refresh the page or check your internet connection.');
          return;
        }
        setTimeout(() => {
          console.log('Checking DOM elements for tour...');
          const criticalElements = [
            '#header-row',
            '.roulette-table',
            '#selected-spins',
            '#undo-spins-btn',
            '.last-spins-container',
            '.green-btn',
            '#dynamic-table-heading',
            '.betting-progression',
            '#color-code-key',
            '#spin-analysis',
            '#save-load-session',
            '#select-category',
            '#casino-data-insights',
            '#hot-cold-numbers',  // Added for Hot and Cold Numbers
            '#sides-of-zero-accordion',
            '#dozen-tracker',
            '#top-strategies',
            '#feedback-section'
          ];
          const missingElements = criticalElements.filter(el => !document.querySelector(el));
          if (missingElements.length > 0) {
            console.error(`Cannot start tour: Missing elements: ${missingElements.join(', ')}`);
            alert(`Tour unavailable: Missing components (${missingElements.join(', ')}). Please refresh the page or contact support.`);
            return;
          }
          console.log('All critical elements found. Starting tour.');
          try {
            tour.start();
            console.log('Tour started successfully.');
          } catch (error) {
            console.error('Error starting tour:', error);
            alert('Tour failed to start due to an unexpected error. Please check the console for details.');
          }
        }, 2000);
      }
    
      document.addEventListener("DOMContentLoaded", () => {
        console.log("DOM Loaded, #header-row exists:", !!document.querySelector("#header-row"));
        console.log("Shepherd.js available:", typeof Shepherd !== 'undefined');
      });
    </script>
    """)
    
    # Event Handlers
    try:
        spins_textbox.change(
            fn=validate_spins_input,
            inputs=[spins_textbox],
            outputs=[spins_display, last_spin_display]
        ).then(
            fn=lambda spins_display, count, show_trends: format_spins_as_html(spins_display, count, show_trends),
            inputs=[spins_display, last_spin_count, show_trends_state],
            outputs=[last_spin_display]
        ).then(
            fn=analyze_spins,
            inputs=[spins_display, strategy_dropdown, neighbours_count_slider, strong_numbers_count_slider],
            outputs=[
                spin_analysis_output, even_money_output, dozens_output, columns_output,
                streets_output, corners_output, six_lines_output, splits_output,
                sides_output, straight_up_html, top_18_html, strongest_numbers_output,
                dynamic_table_output, strategy_output, sides_of_zero_display
            ]
        ).then(
            fn=update_spin_counter,
            inputs=[],
            outputs=[spin_counter]
        ).then(
            fn=dozen_tracker,
            inputs=[dozen_tracker_spins_dropdown, dozen_tracker_consecutive_hits_dropdown, dozen_tracker_alert_checkbox, dozen_tracker_sequence_length_dropdown, dozen_tracker_follow_up_spins_dropdown, dozen_tracker_sequence_alert_checkbox],
            outputs=[gr.State(), dozen_tracker_output, dozen_tracker_sequence_output]
        ).then(
            fn=even_money_tracker,
            inputs=[
                even_money_tracker_spins_dropdown,
                even_money_tracker_consecutive_hits_dropdown,
                even_money_tracker_alert_checkbox,
                even_money_tracker_combination_mode_dropdown,
                even_money_tracker_red_checkbox,
                even_money_tracker_black_checkbox,
                even_money_tracker_even_checkbox,
                even_money_tracker_odd_checkbox,
                even_money_tracker_low_checkbox,
                even_money_tracker_high_checkbox,
                even_money_tracker_identical_traits_checkbox,
                even_money_tracker_consecutive_identical_dropdown
            ],
            outputs=[gr.State(), even_money_tracker_output]
        ).then(
            fn=summarize_spin_traits,  # Use summarize_spin_traits directly for now
            inputs=[last_spin_count],
            outputs=[traits_display]
        ).then(
            fn=select_next_spin_top_pick,
            inputs=[top_pick_spin_count],
            outputs=[top_pick_display]
        ).then(
            fn=lambda: print(f"After spins_textbox change: state.last_spins = {state.last_spins}"),
            inputs=[],
            outputs=[]
        )
    except Exception as e:
        print(f"Error in spins_textbox.change handler: {str(e)}")
        gr.Warning(f"Error during spin analysis: {str(e)}")
    
    try:
        spins_display.change(
            fn=update_spin_counter,
            inputs=[],
            outputs=[spin_counter]
        ).then(
            fn=lambda spins_display, count, show_trends: format_spins_as_html(spins_display, count, show_trends),
            inputs=[spins_display, last_spin_count, show_trends_state],
            outputs=[last_spin_display]
        ).then(
            fn=summarize_spin_traits,
            inputs=[last_spin_count],
            outputs=[traits_display]
        ).then(
            fn=calculate_hit_percentages,
            inputs=[last_spin_count],
            outputs=[hit_percentage_display]
        ).then(
            fn=select_next_spin_top_pick,
            inputs=[top_pick_spin_count],
            outputs=[top_pick_display]
        ).then(
            fn=lambda: print(f"After spins_display change: state.last_spins = {state.last_spins}"),
            inputs=[],
            outputs=[]
        )
    except Exception as e:
        print(f"Error in spins_display.change handler: {str(e)}")
    
    try:
        clear_spins_button.click(
            fn=clear_spins,
            inputs=[],
            outputs=[spins_display, spins_textbox, spin_analysis_output, last_spin_display, spin_counter, sides_of_zero_display]
        ).then(
            fn=lambda spins_display, count, show_trends: format_spins_as_html(spins_display, count, show_trends),
            inputs=[spins_display, last_spin_count, show_trends_state],
            outputs=[last_spin_display]
        ).then(
            fn=summarize_spin_traits,
            inputs=[last_spin_count],
            outputs=[traits_display]
        ).then(
            fn=calculate_hit_percentages,
            inputs=[last_spin_count],
            outputs=[hit_percentage_display]
        ).then(
            fn=select_next_spin_top_pick,
            inputs=[top_pick_spin_count],
            outputs=[top_pick_display]
        ).then(
            fn=lambda: print(f"After clear_spins_button click: state.last_spins = {state.last_spins}"),
            inputs=[],
            outputs=[]
        )
    except Exception as e:
        print(f"Error in clear_spins_button.click handler: {str(e)}")
    
    try:
        clear_all_button.click(
            fn=clear_all,
            inputs=[],
            outputs=[
                spins_display,
                spins_textbox,
                spin_analysis_output,
                last_spin_display,
                even_money_output,
                dozens_output,
                columns_output,
                streets_output,
                corners_output,
                six_lines_output,
                splits_output,
                sides_output,
                straight_up_html,
                top_18_html,
                strongest_numbers_output,
                spin_counter,
                sides_of_zero_display
            ]
        ).then(
            fn=clear_outputs,
            inputs=[],
            outputs=[
                spin_analysis_output,
                even_money_output,
                dozens_output,
                columns_output,
                streets_output,
                corners_output,
                six_lines_output,
                splits_output,
                sides_output,
                straight_up_html,
                top_18_html,
                strongest_numbers_output,
                dynamic_table_output,
                strategy_output,
                color_code_output
            ]
        ).then(
            fn=dozen_tracker,
            inputs=[
                dozen_tracker_spins_dropdown,
                dozen_tracker_consecutive_hits_dropdown,
                dozen_tracker_alert_checkbox,
                dozen_tracker_sequence_length_dropdown,
                dozen_tracker_follow_up_spins_dropdown,
                dozen_tracker_sequence_alert_checkbox
            ],
            outputs=[gr.State(), dozen_tracker_output, dozen_tracker_sequence_output]
        ).then(
            fn=summarize_spin_traits,
            inputs=[last_spin_count],
            outputs=[traits_display]
        ).then(
            fn=select_next_spin_top_pick,
            inputs=[top_pick_spin_count],
            outputs=[top_pick_display]
        ).then(
            fn=lambda: print(f"After clear_all_button click: state.last_spins = {state.last_spins}"),
            inputs=[],
            outputs=[]
        )
    except Exception as e:
        print(f"Error in clear_all_button.click handler: {str(e)}")
    
    try:
        generate_spins_button.click(
            fn=generate_random_spins,
            inputs=[gr.State(value="5"), spins_display, last_spin_count],
            outputs=[spins_display, spins_textbox, spin_analysis_output, spin_counter, sides_of_zero_display]
        ).then(
            fn=lambda spins_display, count, show_trends: format_spins_as_html(spins_display, count, show_trends),
            inputs=[spins_display, last_spin_count, show_trends_state],
            outputs=[last_spin_display]
        ).then(
            fn=summarize_spin_traits,
            inputs=[last_spin_count],
            outputs=[traits_display]
        ).then(
            fn=select_next_spin_top_pick,
            inputs=[top_pick_spin_count],
            outputs=[top_pick_display]
        ).then(
            fn=lambda: print(f"After generate_spins_button click: state.last_spins = {state.last_spins}"),
            inputs=[],
            outputs=[]
        )
    except Exception as e:
        print(f"Error in generate_spins_button.click handler: {str(e)}")

# Line 1: Slider change handler (updated)
    try:
        last_spin_count.change(
            fn=lambda spins_display, count, show_trends: format_spins_as_html(spins_display, count, show_trends),
            inputs=[spins_display, last_spin_count, show_trends_state],
            outputs=[last_spin_display]
        ).then(
            fn=summarize_spin_traits,
            inputs=[last_spin_count],
            outputs=[traits_display]
        ).then(
            fn=calculate_hit_percentages,
            inputs=[last_spin_count],
            outputs=[hit_percentage_display]
        ).then(
            fn=select_next_spin_top_pick,
            inputs=[top_pick_spin_count],
            outputs=[top_pick_display]
        ).then(
            fn=lambda: print(f"After last_spin_count change: state.last_spins = {state.last_spins}"),
            inputs=[],
            outputs=[]
        )
    except Exception as e:
        print(f"Error in last_spin_count.change handler: {str(e)}")
    
    def update_strategy_dropdown(category):
        if category == "None":
            return gr.update(choices=["None"], value="None")
        return gr.update(choices=strategy_categories[category], value=strategy_categories[category][0])
    
    try:
        category_dropdown.change(
            fn=update_strategy_dropdown,
            inputs=category_dropdown,
            outputs=strategy_dropdown
        )
    except Exception as e:
        print(f"Error in category_dropdown.change handler: {str(e)}")
    
    try:
        reset_strategy_button.click(
            fn=reset_strategy_dropdowns,
            inputs=[],
            outputs=[category_dropdown, strategy_dropdown, strategy_dropdown]
        ).then(
            fn=lambda category: gr.update(choices=strategy_categories[category], value=strategy_categories[category][0]),
            inputs=[category_dropdown],
            outputs=[strategy_dropdown]
        )
    except Exception as e:
        print(f"Error in reset_strategy_button.click handler: {str(e)}")
    
    def toggle_neighbours_slider(strategy_name):
        is_visible = strategy_name == "Neighbours of Strong Number"
        return (
            gr.update(visible=is_visible),
            gr.update(visible=is_visible)
        )

    # New: Orchestrating function to combine analysis steps
    def orchestrate_analysis(spins_display, strategy, neighbours_count, strong_numbers_count, dozen_tracker_spins, dozen_consecutive_hits, dozen_alert, dozen_sequence_length, dozen_follow_up_spins, dozen_sequence_alert, even_money_spins, even_money_consecutive_hits, even_money_alert, even_money_combination_mode, red, black, even, odd, low, high, identical_traits, consecutive_identical, top_color, middle_color, lower_color):
        """Orchestrate analysis, producing all outputs in one pass with scores always reset."""
        import time
        start_time = time.time()
        
        # Run analysis (scores are always reset in analyze_spins)
        spins_analysis, even_money, dozens, columns, streets, corners, six_lines, splits, sides, straight_up, top_18, strongest_numbers = analyze_spins(spins_display, strategy, neighbours_count, strong_numbers_count)
        
        # Run trackers and dynamic table
        dozen_text, dozen_html, dozen_sequence_html = dozen_tracker(
            dozen_tracker_spins, dozen_consecutive_hits, dozen_alert,
            dozen_sequence_length, dozen_follow_up_spins, dozen_sequence_alert
        )
        even_money_text, even_money_html = even_money_tracker(
            even_money_spins, even_money_consecutive_hits, even_money_alert,
            even_money_combination_mode, red, black, even, odd, low, high,
            identical_traits, consecutive_identical
        )
        dynamic_table = create_dynamic_table(
            strategy if strategy != "None" else None, neighbours_count,
            strong_numbers_count, dozen_tracker_spins, top_color, middle_color, lower_color
        )
        color_code = create_color_code_table()
        
        print(f"Analysis completed in {time.time() - start_time:.3f} seconds")
        return (
            spins_analysis, even_money, dozens, columns, streets, corners, six_lines,
            splits, sides, straight_up, top_18, strongest_numbers, dynamic_table,
            show_strategy_recommendations(strategy, neighbours_count, strong_numbers_count),
            render_sides_of_zero_display(), dozen_text, dozen_html, dozen_sequence_html,
            even_money_text, even_money_html, color_code, analysis_cache.value
        )
    
    try:
        strategy_dropdown.change(
            fn=toggle_neighbours_slider,
            inputs=[strategy_dropdown],
            outputs=[neighbours_count_slider, strong_numbers_count_slider]
        ).then(
            fn=show_strategy_recommendations,
            inputs=[strategy_dropdown, neighbours_count_slider, strong_numbers_count_slider],
            outputs=[strategy_output]
        ).then(
            fn=lambda strategy, neighbours_count, strong_numbers_count, dozen_tracker_spins, top_color, middle_color, lower_color: (print(f"Updating Dynamic Table with Strategy: {strategy}, Neighbours Count: {neighbours_count}, Strong Numbers Count: {strong_numbers_count}, Dozen Tracker Spins: {dozen_tracker_spins}, Colors: {top_color}, {middle_color}, {lower_color}"), create_dynamic_table(strategy if strategy != "None" else None, neighbours_count, strong_numbers_count, dozen_tracker_spins, top_color, middle_color, lower_color))[-1],
            inputs=[strategy_dropdown, neighbours_count_slider, strong_numbers_count_slider, dozen_tracker_spins_dropdown, top_color_picker, middle_color_picker, lower_color_picker],
            outputs=[dynamic_table_output]
        )
    except Exception as e:
        print(f"Error in strategy_dropdown.change handler: {str(e)}")

    try:
        analyze_button.click(
            fn=analyze_spins,
            inputs=[
                spins_display, strategy_dropdown, neighbours_count_slider,
                strong_numbers_count_slider,
                dozen_tracker_spins_dropdown, dozen_tracker_consecutive_hits_dropdown, dozen_tracker_alert_checkbox,
                dozen_tracker_sequence_length_dropdown, dozen_tracker_follow_up_spins_dropdown, dozen_tracker_sequence_alert_checkbox,
                even_money_tracker_spins_dropdown, even_money_tracker_consecutive_hits_dropdown, even_money_tracker_alert_checkbox,
                even_money_tracker_combination_mode_dropdown, even_money_tracker_red_checkbox, even_money_tracker_black_checkbox,
                even_money_tracker_even_checkbox, even_money_tracker_odd_checkbox, even_money_tracker_low_checkbox,
                even_money_tracker_high_checkbox, even_money_tracker_identical_traits_checkbox, even_money_tracker_consecutive_identical_dropdown
            ],
            outputs=[
                spin_analysis_output, even_money_output, dozens_output, columns_output,
                streets_output, corners_output, six_lines_output, splits_output,
                sides_output, straight_up_html, top_18_html, strongest_numbers_output,
                dynamic_table_output, strategy_output, sides_of_zero_display
            ]
        ).then(
            # Clear outputs to reset error state
            fn=lambda: ("", ""),
            inputs=[],
            outputs=[dynamic_table_output, strategy_output]
        ).then(
            fn=update_casino_data,
            inputs=[
                spins_count_dropdown, even_percent, odd_percent, red_percent, black_percent,
                low_percent, high_percent, dozen1_percent, dozen2_percent, dozen3_percent,
                col1_percent, col2_percent, col3_percent, use_winners_checkbox
            ],
            outputs=[casino_data_output]
        ).then(
            fn=lambda strategy, neighbours_count, strong_numbers_count, dozen_tracker_spins, top_color, middle_color, lower_color: create_dynamic_table(
                strategy if strategy != "None" else None, neighbours_count, strong_numbers_count, dozen_tracker_spins, top_color, middle_color, lower_color
            ),
            inputs=[strategy_dropdown, neighbours_count_slider, strong_numbers_count_slider, dozen_tracker_spins_dropdown, top_color_picker, middle_color_picker, lower_color_picker],
            outputs=[dynamic_table_output]
        ).then(
            fn=create_color_code_table,
            inputs=[],
            outputs=[color_code_output]
        ).then(
            fn=dozen_tracker,
            inputs=[
                dozen_tracker_spins_dropdown, dozen_tracker_consecutive_hits_dropdown, dozen_tracker_alert_checkbox,
                dozen_tracker_sequence_length_dropdown, dozen_tracker_follow_up_spins_dropdown, dozen_tracker_sequence_alert_checkbox
            ],
            outputs=[gr.State(), dozen_tracker_output, dozen_tracker_sequence_output]
        ).then(
            fn=even_money_tracker,
            inputs=[
                even_money_tracker_spins_dropdown,
                even_money_tracker_consecutive_hits_dropdown,
                even_money_tracker_alert_checkbox,
                even_money_tracker_combination_mode_dropdown,
                even_money_tracker_red_checkbox, even_money_tracker_black_checkbox,
                even_money_tracker_even_checkbox, even_money_tracker_odd_checkbox,
                even_money_tracker_low_checkbox, even_money_tracker_high_checkbox,
                even_money_tracker_identical_traits_checkbox, even_money_tracker_consecutive_identical_dropdown
            ],
            outputs=[gr.State(), even_money_tracker_output]
        ).then(
            fn=summarize_spin_traits,
            inputs=[last_spin_count],
            outputs=[traits_display]
        ).then(
            fn=calculate_hit_percentages,
            inputs=[last_spin_count],
            outputs=[hit_percentage_display]
        ).then(
            fn=select_next_spin_top_pick,
            inputs=[top_pick_spin_count],
            outputs=[top_pick_display]
        ).then(
            # Fast workaround: Re-run show_strategy_recommendations to repopulate strategy_output
            fn=show_strategy_recommendations,
            inputs=[strategy_dropdown, neighbours_count_slider, strong_numbers_count_slider],
            outputs=[strategy_output]
        ).then(
            fn=suggest_hot_cold_numbers,
            inputs=[],
            outputs=[hot_suggestions, cold_suggestions]
        ).then(
            fn=lambda: print(f"After analyze_button click: state.last_spins = {state.last_spins}"),
            inputs=[],
            outputs=[]
        )
    except Exception as e:
        print(f"Error in analyze_button.click handler: {str(e)}")
        gr.Warning(f"Error during analysis: {str(e)}")
    
    try:
        save_button.click(
            fn=save_session,
            inputs=[],
            outputs=[save_output]
        )
    except Exception as e:
        print(f"Error in save_button.click handler: {str(e)}")
    
    try:
        load_input.change(
            fn=load_session,
            inputs=[load_input, strategy_dropdown, neighbours_count_slider, strong_numbers_count_slider],
            outputs=[
                spins_display,
                spins_textbox,
                spin_analysis_output,
                even_money_output,
                dozens_output,
                columns_output,
                streets_output,
                corners_output,
                six_lines_output,
                splits_output,
                sides_output,
                straight_up_html,
                top_18_html,
                strongest_numbers_output,
                dynamic_table_output,
                strategy_output  # Removed betting_sections_display
            ]
        ).then(
            fn=lambda strategy, neighbours_count, strong_numbers_count, dozen_tracker_spins, top_color, middle_color, lower_color: create_dynamic_table(
                strategy if strategy != "None" else None,
                neighbours_count,
                strong_numbers_count,
                dozen_tracker_spins,
                top_color,
                middle_color,
                lower_color
            ),
            inputs=[
                strategy_dropdown,
                neighbours_count_slider,
                strong_numbers_count_slider,
                dozen_tracker_spins_dropdown,
                top_color_picker,
                middle_color_picker,
                lower_color_picker
            ],
            outputs=[dynamic_table_output]
        ).then(
            fn=lambda spins_display, count, show_trends: format_spins_as_html(spins_display, count, show_trends),
            inputs=[spins_display, last_spin_count, show_trends_state],
            outputs=[last_spin_display]
        ).then(
            fn=create_color_code_table,
            inputs=[],
            outputs=[color_code_output]
        ).then(
            fn=dozen_tracker,
            inputs=[
                dozen_tracker_spins_dropdown,
                dozen_tracker_consecutive_hits_dropdown,
                dozen_tracker_alert_checkbox,
                dozen_tracker_sequence_length_dropdown,
                dozen_tracker_follow_up_spins_dropdown,
                dozen_tracker_sequence_alert_checkbox
            ],
            outputs=[gr.State(), dozen_tracker_output, dozen_tracker_sequence_output]
        ).then(
            fn=select_next_spin_top_pick,
            inputs=[top_pick_spin_count],
            outputs=[top_pick_display]
        ).then(
            fn=lambda: print(f"After load_input change: state.last_spins = {state.last_spins}"),
            inputs=[],
            outputs=[]
        )
    except Exception as e:
        print(f"Error in load_input.change handler: {str(e)}")
    
    try:
        undo_button.click(
            fn=undo_last_spin,
            inputs=[spins_display, gr.State(value=1), strategy_dropdown, neighbours_count_slider, strong_numbers_count_slider],
            outputs=[
                spin_analysis_output,
                even_money_output,
                dozens_output,
                columns_output,
                streets_output,
                corners_output,
                six_lines_output,
                splits_output,
                sides_output,
                straight_up_html,
                top_18_html,
                strongest_numbers_output,
                spins_textbox,
                spins_display,
                dynamic_table_output,
                strategy_output,
                color_code_output,
                spin_counter,
                sides_of_zero_display
            ]
        ).then(
            fn=lambda spins_display, count, show_trends: format_spins_as_html(spins_display, count, show_trends),
            inputs=[spins_display, last_spin_count, show_trends_state],
            outputs=[last_spin_display]
        ).then(
            fn=lambda strategy, neighbours_count, strong_numbers_count, dozen_tracker_spins, top_color, middle_color, lower_color: create_dynamic_table(
                strategy if strategy != "None" else None,
                neighbours_count,
                strong_numbers_count,
                dozen_tracker_spins,
                top_color,
                middle_color,
                lower_color
            ),
            inputs=[
                strategy_dropdown,
                neighbours_count_slider,
                strong_numbers_count_slider,
                dozen_tracker_spins_dropdown,
                top_color_picker,
                middle_color_picker,
                lower_color_picker
            ],
            outputs=[dynamic_table_output]
        ).then(
            fn=dozen_tracker,
            inputs=[
                dozen_tracker_spins_dropdown,
                dozen_tracker_consecutive_hits_dropdown,
                dozen_tracker_alert_checkbox,
                dozen_tracker_sequence_length_dropdown,
                dozen_tracker_follow_up_spins_dropdown,
                dozen_tracker_sequence_alert_checkbox
            ],
            outputs=[gr.State(), dozen_tracker_output, dozen_tracker_sequence_output]
        ).then(
            fn=summarize_spin_traits,
            inputs=[last_spin_count],
            outputs=[traits_display]
        ).then(
            fn=select_next_spin_top_pick,
            inputs=[top_pick_spin_count],
            outputs=[top_pick_display]
        ).then(
            fn=lambda: print(f"After undo_button click: state.last_spins = {state.last_spins}"),
            inputs=[],
            outputs=[]
        )
    except Exception as e:
        print(f"Error in undo_button.click handler: {str(e)}")
    
    try:
        neighbours_count_slider.change(
            fn=lambda strategy, neighbours_count, strong_numbers_count, dozen_tracker_spins, top_color, middle_color, lower_color: create_dynamic_table(strategy if strategy != "None" else None, neighbours_count, strong_numbers_count, dozen_tracker_spins, top_color, middle_color, lower_color),
            inputs=[strategy_dropdown, neighbours_count_slider, strong_numbers_count_slider, dozen_tracker_spins_dropdown, top_color_picker, middle_color_picker, lower_color_picker],
            outputs=[dynamic_table_output]
        ).then(
            fn=show_strategy_recommendations,
            inputs=[strategy_dropdown, neighbours_count_slider, strong_numbers_count_slider],
            outputs=[strategy_output]
        )
    except Exception as e:
        print(f"Error in neighbours_count_slider.change handler: {str(e)}")
    
    try:
        strong_numbers_count_slider.change(
            fn=lambda strategy, neighbours_count, strong_numbers_count, dozen_tracker_spins, top_color, middle_color, lower_color: create_dynamic_table(strategy if strategy != "None" else None, neighbours_count, strong_numbers_count, dozen_tracker_spins, top_color, middle_color, lower_color),
            inputs=[strategy_dropdown, neighbours_count_slider, strong_numbers_count_slider, dozen_tracker_spins_dropdown, top_color_picker, middle_color_picker, lower_color_picker],
            outputs=[dynamic_table_output]
        ).then(
            fn=show_strategy_recommendations,
            inputs=[strategy_dropdown, neighbours_count_slider, strong_numbers_count_slider],
            outputs=[strategy_output]
        )
    except Exception as e:
        print(f"Error in strong_numbers_count_slider.change handler: {str(e)}")
    
    try:
        reset_colors_button.click(
            fn=reset_colors,
            inputs=[],
            outputs=[top_color_picker, middle_color_picker, lower_color_picker]
        ).then(
            fn=lambda strategy, neighbours_count, strong_numbers_count, dozen_tracker_spins, top_color, middle_color, lower_color: create_dynamic_table(strategy if strategy != "None" else None, neighbours_count, strong_numbers_count, dozen_tracker_spins, top_color, middle_color, lower_color),
            inputs=[strategy_dropdown, neighbours_count_slider, strong_numbers_count_slider, dozen_tracker_spins_dropdown, top_color_picker, middle_color_picker, lower_color_picker],
            outputs=[dynamic_table_output]
        )
    except Exception as e:
        print(f"Error in reset_colors_button.click handler: {str(e)}")

    try:
        clear_last_spins_button.click(
            fn=clear_last_spins_display,
            inputs=[],
            outputs=[last_spin_display, spin_counter]
        ).then(
            fn=lambda spins_display, count, show_trends: format_spins_as_html(spins_display, count, show_trends),
            inputs=[spins_display, last_spin_count, show_trends_state],
            outputs=[last_spin_display]
        ).then(
            fn=select_next_spin_top_pick,
            inputs=[top_pick_spin_count],
            outputs=[top_pick_display]
        ).then(
            fn=lambda: print(f"After clear_last_spins_button click: state.last_spins = {state.last_spins}"),
            inputs=[],
            outputs=[]
        )
    except Exception as e:
        print(f"Error in clear_last_spins_button.click handler: {str(e)}")

    # Define the toggle_trends function to update both state and label
    def toggle_trends(show_trends, current_label):
        new_show_trends = not show_trends
        new_label = "Hide Trends" if new_show_trends else "Show Trends"
        return new_show_trends, new_label, gr.update(value=new_label)

    # Event handler for toggle_trends_button (at the top level, not indented under the function)
    try:
        toggle_trends_button.click(
            fn=toggle_trends,
            inputs=[show_trends_state, toggle_trends_label],
            outputs=[show_trends_state, toggle_trends_label, toggle_trends_button]
        ).then(
            fn=lambda spins_display, count, show_trends: format_spins_as_html(spins_display, count, show_trends),
            inputs=[spins_display, last_spin_count, show_trends_state],
            outputs=[last_spin_display]
        ).then(
            fn=select_next_spin_top_pick,
            inputs=[top_pick_spin_count],
            outputs=[top_pick_display]
        ).then(
            fn=lambda: print(f"After toggle_trends_button click: state.last_spins = {state.last_spins}"),
            inputs=[],
            outputs=[]
        )
    except Exception as e:
        print(f"Error in toggle_trends_button.click handler: {str(e)}")

    try:
        top_color_picker.change(
            fn=lambda strategy, neighbours_count, strong_numbers_count, dozen_tracker_spins, top_color, middle_color, lower_color: create_dynamic_table(strategy if strategy != "None" else None, neighbours_count, strong_numbers_count, dozen_tracker_spins, top_color, middle_color, lower_color),
            inputs=[strategy_dropdown, neighbours_count_slider, strong_numbers_count_slider, dozen_tracker_spins_dropdown, top_color_picker, middle_color_picker, lower_color_picker],
            outputs=[dynamic_table_output]
        )
    except Exception as e:
        print(f"Error in top_color_picker.change handler: {str(e)}")

    try:
        middle_color_picker.change(
            fn=lambda strategy, neighbours_count, strong_numbers_count, dozen_tracker_spins, top_color, middle_color, lower_color: create_dynamic_table(strategy if strategy != "None" else None, neighbours_count, strong_numbers_count, dozen_tracker_spins, top_color, middle_color, lower_color),
            inputs=[strategy_dropdown, neighbours_count_slider, strong_numbers_count_slider, dozen_tracker_spins_dropdown, top_color_picker, middle_color_picker, lower_color_picker],
            outputs=[dynamic_table_output]
        )
    except Exception as e:
        print(f"Error in middle_color_picker.change handler: {str(e)}")

    try:
        lower_color_picker.change(
            fn=lambda strategy, neighbours_count, strong_numbers_count, dozen_tracker_spins, top_color, middle_color, lower_color: create_dynamic_table(strategy if strategy != "None" else None, neighbours_count, strong_numbers_count, dozen_tracker_spins, top_color, middle_color, lower_color),
            inputs=[strategy_dropdown, neighbours_count_slider, strong_numbers_count_slider, dozen_tracker_spins_dropdown, top_color_picker, middle_color_picker, lower_color_picker],
            outputs=[dynamic_table_output]
        )
    except Exception as e:
        print(f"Error in lower_color_picker.change handler: {str(e)}")

    # Dozen Tracker Event Handlers
    try:
        dozen_tracker_spins_dropdown.change(
            fn=dozen_tracker,
            inputs=[dozen_tracker_spins_dropdown, dozen_tracker_consecutive_hits_dropdown, dozen_tracker_alert_checkbox, dozen_tracker_sequence_length_dropdown, dozen_tracker_follow_up_spins_dropdown, dozen_tracker_sequence_alert_checkbox],
            outputs=[gr.State(), dozen_tracker_output, dozen_tracker_sequence_output]
        ).then(
            fn=lambda strategy, neighbours_count, strong_numbers_count, dozen_tracker_spins, top_color, middle_color, lower_color: create_dynamic_table(strategy if strategy != "None" else None, neighbours_count, strong_numbers_count, dozen_tracker_spins, top_color, middle_color, lower_color),
            inputs=[strategy_dropdown, neighbours_count_slider, strong_numbers_count_slider, dozen_tracker_spins_dropdown, top_color_picker, middle_color_picker, lower_color_picker],
            outputs=[dynamic_table_output]
        )
    except Exception as e:
        print(f"Error in dozen_tracker_spins_dropdown.change handler: {str(e)}")
    
    try:
        dozen_tracker_consecutive_hits_dropdown.change(
            fn=dozen_tracker,
            inputs=[dozen_tracker_spins_dropdown, dozen_tracker_consecutive_hits_dropdown, dozen_tracker_alert_checkbox, dozen_tracker_sequence_length_dropdown, dozen_tracker_follow_up_spins_dropdown, dozen_tracker_sequence_alert_checkbox],
            outputs=[gr.State(), dozen_tracker_output, dozen_tracker_sequence_output]
        ).then(
            fn=lambda strategy, neighbours_count, strong_numbers_count, dozen_tracker_spins, top_color, middle_color, lower_color: create_dynamic_table(strategy if strategy != "None" else None, neighbours_count, strong_numbers_count, dozen_tracker_spins, top_color, middle_color, lower_color),
            inputs=[strategy_dropdown, neighbours_count_slider, strong_numbers_count_slider, dozen_tracker_spins_dropdown, top_color_picker, middle_color_picker, lower_color_picker],
            outputs=[dynamic_table_output]
        )
    except Exception as e:
        print(f"Error in dozen_tracker_consecutive_hits_dropdown.change handler: {str(e)}")
    
    try:
        dozen_tracker_alert_checkbox.change(
            fn=dozen_tracker,
            inputs=[dozen_tracker_spins_dropdown, dozen_tracker_consecutive_hits_dropdown, dozen_tracker_alert_checkbox, dozen_tracker_sequence_length_dropdown, dozen_tracker_follow_up_spins_dropdown, dozen_tracker_sequence_alert_checkbox],
            outputs=[gr.State(), dozen_tracker_output, dozen_tracker_sequence_output]
        ).then(
            fn=lambda strategy, neighbours_count, strong_numbers_count, dozen_tracker_spins, top_color, middle_color, lower_color: create_dynamic_table(strategy if strategy != "None" else None, neighbours_count, strong_numbers_count, dozen_tracker_spins, top_color, middle_color, lower_color),
            inputs=[strategy_dropdown, neighbours_count_slider, strong_numbers_count_slider, dozen_tracker_spins_dropdown, top_color_picker, middle_color_picker, lower_color_picker],
            outputs=[dynamic_table_output]
        )
    except Exception as e:
        print(f"Error in dozen_tracker_alert_checkbox.change handler: {str(e)}")
    
    try:
        dozen_tracker_sequence_length_dropdown.change(
            fn=dozen_tracker,
            inputs=[dozen_tracker_spins_dropdown, dozen_tracker_consecutive_hits_dropdown, dozen_tracker_alert_checkbox, dozen_tracker_sequence_length_dropdown, dozen_tracker_follow_up_spins_dropdown, dozen_tracker_sequence_alert_checkbox],
            outputs=[gr.State(), dozen_tracker_output, dozen_tracker_sequence_output]
        ).then(
            fn=lambda strategy, neighbours_count, strong_numbers_count, dozen_tracker_spins, top_color, middle_color, lower_color: create_dynamic_table(strategy if strategy != "None" else None, neighbours_count, strong_numbers_count, dozen_tracker_spins, top_color, middle_color, lower_color),
            inputs=[strategy_dropdown, neighbours_count_slider, strong_numbers_count_slider, dozen_tracker_spins_dropdown, top_color_picker, middle_color_picker, lower_color_picker],
            outputs=[dynamic_table_output]
        )
    except Exception as e:
        print(f"Error in dozen_tracker_sequence_length_dropdown.change handler: {str(e)}")
    
    try:
        dozen_tracker_follow_up_spins_dropdown.change(
            fn=dozen_tracker,
            inputs=[dozen_tracker_spins_dropdown, dozen_tracker_consecutive_hits_dropdown, dozen_tracker_alert_checkbox, dozen_tracker_sequence_length_dropdown, dozen_tracker_follow_up_spins_dropdown, dozen_tracker_sequence_alert_checkbox],
            outputs=[gr.State(), dozen_tracker_output, dozen_tracker_sequence_output]
        ).then(
            fn=lambda strategy, neighbours_count, strong_numbers_count, dozen_tracker_spins, top_color, middle_color, lower_color: create_dynamic_table(strategy if strategy != "None" else None, neighbours_count, strong_numbers_count, dozen_tracker_spins, top_color, middle_color, lower_color),
            inputs=[strategy_dropdown, neighbours_count_slider, strong_numbers_count_slider, dozen_tracker_spins_dropdown, top_color_picker, middle_color_picker, lower_color_picker],
            outputs=[dynamic_table_output]
        )
    except Exception as e:
        print(f"Error in dozen_tracker_follow_up_spins_dropdown.change handler: {str(e)}")
    
    try:
        dozen_tracker_sequence_alert_checkbox.change(
            fn=dozen_tracker,
            inputs=[
                dozen_tracker_spins_dropdown,
                dozen_tracker_consecutive_hits_dropdown,
                dozen_tracker_alert_checkbox,
                dozen_tracker_sequence_length_dropdown,
                dozen_tracker_follow_up_spins_dropdown,
                dozen_tracker_sequence_alert_checkbox
            ],
            outputs=[gr.State(), dozen_tracker_output, dozen_tracker_sequence_output]
        ).then(
            fn=lambda strategy, neighbours_count, strong_numbers_count, dozen_tracker_spins, top_color, middle_color, lower_color: create_dynamic_table(
                strategy if strategy != "None" else None,
                neighbours_count,
                strong_numbers_count,
                dozen_tracker_spins,
                top_color,
                middle_color,
                lower_color
            ),
            inputs=[
                strategy_dropdown,
                neighbours_count_slider,
                strong_numbers_count_slider,
                dozen_tracker_spins_dropdown,
                top_color_picker,
                middle_color_picker,
                lower_color_picker
            ],
            outputs=[dynamic_table_output]
        )
    except Exception as e:
        print(f"Error in dozen_tracker_sequence_alert_checkbox.change handler: {str(e)}")
    
    # Even Money Tracker Event Handlers
    try:
        even_money_tracker_spins_dropdown.change(
            fn=even_money_tracker,
            inputs=[
                even_money_tracker_spins_dropdown,
                even_money_tracker_consecutive_hits_dropdown,
                even_money_tracker_alert_checkbox,
                even_money_tracker_combination_mode_dropdown,
                even_money_tracker_red_checkbox,
                even_money_tracker_black_checkbox,
                even_money_tracker_even_checkbox,
                even_money_tracker_odd_checkbox,
                even_money_tracker_low_checkbox,
                even_money_tracker_high_checkbox,
                even_money_tracker_identical_traits_checkbox,
                even_money_tracker_consecutive_identical_dropdown
            ],
            outputs=[gr.State(), even_money_tracker_output]
        )
    except Exception as e:
        print(f"Error in even_money_tracker_spins_dropdown.change handler: {str(e)}")
    
    try:
        even_money_tracker_consecutive_hits_dropdown.change(
            fn=even_money_tracker,
            inputs=[
                even_money_tracker_spins_dropdown,
                even_money_tracker_consecutive_hits_dropdown,
                even_money_tracker_alert_checkbox,
                even_money_tracker_combination_mode_dropdown,
                even_money_tracker_red_checkbox,
                even_money_tracker_black_checkbox,
                even_money_tracker_even_checkbox,
                even_money_tracker_odd_checkbox,
                even_money_tracker_low_checkbox,
                even_money_tracker_high_checkbox,
                even_money_tracker_identical_traits_checkbox,
                even_money_tracker_consecutive_identical_dropdown
            ],
            outputs=[gr.State(), even_money_tracker_output]
        )
    except Exception as e:
        print(f"Error in even_money_tracker_consecutive_hits_dropdown.change handler: {str(e)}")
    
    try:
        even_money_tracker_combination_mode_dropdown.change(
            fn=even_money_tracker,
            inputs=[
                even_money_tracker_spins_dropdown,
                even_money_tracker_consecutive_hits_dropdown,
                even_money_tracker_alert_checkbox,
                even_money_tracker_combination_mode_dropdown,
                even_money_tracker_red_checkbox,
                even_money_tracker_black_checkbox,
                even_money_tracker_even_checkbox,
                even_money_tracker_odd_checkbox,
                even_money_tracker_low_checkbox,
                even_money_tracker_high_checkbox,
                even_money_tracker_identical_traits_checkbox,
                even_money_tracker_consecutive_identical_dropdown
            ],
            outputs=[gr.State(), even_money_tracker_output]
        )
    except Exception as e:
        print(f"Error in even_money_tracker_combination_mode_dropdown.change handler: {str(e)}")
    
    try:
        even_money_tracker_red_checkbox.change(
            fn=even_money_tracker,
            inputs=[
                even_money_tracker_spins_dropdown,
                even_money_tracker_consecutive_hits_dropdown,
                even_money_tracker_alert_checkbox,
                even_money_tracker_combination_mode_dropdown,
                even_money_tracker_red_checkbox,
                even_money_tracker_black_checkbox,
                even_money_tracker_even_checkbox,
                even_money_tracker_odd_checkbox,
                even_money_tracker_low_checkbox,
                even_money_tracker_high_checkbox,
                even_money_tracker_identical_traits_checkbox,
                even_money_tracker_consecutive_identical_dropdown
            ],
            outputs=[gr.State(), even_money_tracker_output]
        )
    except Exception as e:
        print(f"Error in even_money_tracker_red_checkbox.change handler: {str(e)}")
    
    try:
        even_money_tracker_black_checkbox.change(
            fn=even_money_tracker,
            inputs=[
                even_money_tracker_spins_dropdown,
                even_money_tracker_consecutive_hits_dropdown,
                even_money_tracker_alert_checkbox,
                even_money_tracker_combination_mode_dropdown,
                even_money_tracker_red_checkbox,
                even_money_tracker_black_checkbox,
                even_money_tracker_even_checkbox,
                even_money_tracker_odd_checkbox,
                even_money_tracker_low_checkbox,
                even_money_tracker_high_checkbox,
                even_money_tracker_identical_traits_checkbox,
                even_money_tracker_consecutive_identical_dropdown
            ],
            outputs=[gr.State(), even_money_tracker_output]
        )
    except Exception as e:
        print(f"Error in even_money_tracker_black_checkbox.change handler: {str(e)}")
    
    try:
        even_money_tracker_even_checkbox.change(
            fn=even_money_tracker,
            inputs=[
                even_money_tracker_spins_dropdown,
                even_money_tracker_consecutive_hits_dropdown,
                even_money_tracker_alert_checkbox,
                even_money_tracker_combination_mode_dropdown,
                even_money_tracker_red_checkbox,
                even_money_tracker_black_checkbox,
                even_money_tracker_even_checkbox,
                even_money_tracker_odd_checkbox,
                even_money_tracker_low_checkbox,
                even_money_tracker_high_checkbox,
                even_money_tracker_identical_traits_checkbox,
                even_money_tracker_consecutive_identical_dropdown
            ],
            outputs=[gr.State(), even_money_tracker_output]
        )
    except Exception as e:
        print(f"Error in even_money_tracker_even_checkbox.change handler: {str(e)}")
    
    try:
        even_money_tracker_odd_checkbox.change(
            fn=even_money_tracker,
            inputs=[
                even_money_tracker_spins_dropdown,
                even_money_tracker_consecutive_hits_dropdown,
                even_money_tracker_alert_checkbox,
                even_money_tracker_combination_mode_dropdown,
                even_money_tracker_red_checkbox,
                even_money_tracker_black_checkbox,
                even_money_tracker_even_checkbox,
                even_money_tracker_odd_checkbox,
                even_money_tracker_low_checkbox,
                even_money_tracker_high_checkbox,
                even_money_tracker_identical_traits_checkbox,
                even_money_tracker_consecutive_identical_dropdown
            ],
            outputs=[gr.State(), even_money_tracker_output]
        )
    except Exception as e:
        print(f"Error in even_money_tracker_odd_checkbox.change handler: {str(e)}")
    
    try:
        even_money_tracker_low_checkbox.change(
            fn=even_money_tracker,
            inputs=[
                even_money_tracker_spins_dropdown,
                even_money_tracker_consecutive_hits_dropdown,
                even_money_tracker_alert_checkbox,
                even_money_tracker_combination_mode_dropdown,
                even_money_tracker_red_checkbox,
                even_money_tracker_black_checkbox,
                even_money_tracker_even_checkbox,
                even_money_tracker_odd_checkbox,
                even_money_tracker_low_checkbox,
                even_money_tracker_high_checkbox,
                even_money_tracker_identical_traits_checkbox,
                even_money_tracker_consecutive_identical_dropdown
            ],
            outputs=[gr.State(), even_money_tracker_output]
        )
    except Exception as e:
        print(f"Error in even_money_tracker_low_checkbox.change handler: {str(e)}")
    
    try:
        even_money_tracker_high_checkbox.change(
            fn=even_money_tracker,
            inputs=[
                even_money_tracker_spins_dropdown,
                even_money_tracker_consecutive_hits_dropdown,
                even_money_tracker_alert_checkbox,
                even_money_tracker_combination_mode_dropdown,
                even_money_tracker_red_checkbox,
                even_money_tracker_black_checkbox,
                even_money_tracker_even_checkbox,
                even_money_tracker_odd_checkbox,
                even_money_tracker_low_checkbox,
                even_money_tracker_high_checkbox,
                even_money_tracker_identical_traits_checkbox,
                even_money_tracker_consecutive_identical_dropdown
            ],
            outputs=[gr.State(), even_money_tracker_output]
        )
    except Exception as e:
        print(f"Error in even_money_tracker_high_checkbox.change handler: {str(e)}")
    
    try:
        even_money_tracker_alert_checkbox.change(
            fn=even_money_tracker,
            inputs=[
                even_money_tracker_spins_dropdown,
                even_money_tracker_consecutive_hits_dropdown,
                even_money_tracker_alert_checkbox,
                even_money_tracker_combination_mode_dropdown,
                even_money_tracker_red_checkbox,
                even_money_tracker_black_checkbox,
                even_money_tracker_even_checkbox,
                even_money_tracker_odd_checkbox,
                even_money_tracker_low_checkbox,
                even_money_tracker_high_checkbox,
                even_money_tracker_identical_traits_checkbox,
                even_money_tracker_consecutive_identical_dropdown
            ],
            outputs=[gr.State(), even_money_tracker_output]
        )
    except Exception as e:
        print(f"Error in even_money_tracker_alert_checkbox.change handler: {str(e)}")
    
    # Casino data event handlers
    inputs_list = [
        spins_count_dropdown, even_percent, odd_percent, red_percent, black_percent,
        low_percent, high_percent, dozen1_percent, dozen2_percent, dozen3_percent,
        col1_percent, col2_percent, col3_percent, use_winners_checkbox
    ]
    try:
        spins_count_dropdown.change(
            fn=update_casino_data,
            inputs=inputs_list,
            outputs=[casino_data_output]
        )
    except Exception as e:
        print(f"Error in spins_count_dropdown.change handler: {str(e)}")
    
    try:
        even_percent.change(
            fn=update_casino_data,
            inputs=inputs_list,
            outputs=[casino_data_output]
        )
    except Exception as e:
        print(f"Error in even_percent.change handler: {str(e)}")
    
    try:
        odd_percent.change(
            fn=update_casino_data,
            inputs=inputs_list,
            outputs=[casino_data_output]
        )
    except Exception as e:
        print(f"Error in odd_percent.change handler: {str(e)}")
    
    try:
        red_percent.change(
            fn=update_casino_data,
            inputs=inputs_list,
            outputs=[casino_data_output]
        )
    except Exception as e:
        print(f"Error in red_percent.change handler: {str(e)}")
    
    try:
        black_percent.change(
            fn=update_casino_data,
            inputs=inputs_list,
            outputs=[casino_data_output]
        )
    except Exception as e:
        print(f"Error in black_percent.change handler: {str(e)}")
    
    try:
        low_percent.change(
            fn=update_casino_data,
            inputs=inputs_list,
            outputs=[casino_data_output]
        )
    except Exception as e:
        print(f"Error in low_percent.change handler: {str(e)}")
    
    try:
        high_percent.change(
            fn=update_casino_data,
            inputs=inputs_list,
            outputs=[casino_data_output]
        )
    except Exception as e:
        print(f"Error in high_percent.change handler: {str(e)}")
    
    try:
        dozen1_percent.change(
            fn=update_casino_data,
            inputs=inputs_list,
            outputs=[casino_data_output]
        )
    except Exception as e:
        print(f"Error in dozen1_percent.change handler: {str(e)}")
    
    try:
        dozen2_percent.change(
            fn=update_casino_data,
            inputs=inputs_list,
            outputs=[casino_data_output]
        )
    except Exception as e:
        print(f"Error in dozen2_percent.change handler: {str(e)}")
    
    try:
        dozen3_percent.change(
            fn=update_casino_data,
            inputs=inputs_list,
            outputs=[casino_data_output]
        )
    except Exception as e:
        print(f"Error in dozen3_percent.change handler: {str(e)}")
    
    try:
        col1_percent.change(
            fn=update_casino_data,
            inputs=inputs_list,
            outputs=[casino_data_output]
        )
    except Exception as e:
        print(f"Error in col1_percent.change handler: {str(e)}")
    
    try:
        col2_percent.change(
            fn=update_casino_data,
            inputs=inputs_list,
            outputs=[casino_data_output]
        )
    except Exception as e:
        print(f"Error in col2_percent.change handler: {str(e)}")
    
    try:
        col3_percent.change(
            fn=update_casino_data,
            inputs=inputs_list,
            outputs=[casino_data_output]
        )
    except Exception as e:
        print(f"Error in col3_percent.change handler: {str(e)}")
    
    try:
        use_winners_checkbox.change(
            fn=update_casino_data,
            inputs=inputs_list,
            outputs=[casino_data_output]
        ).then(
            fn=lambda strategy, neighbours_count, strong_numbers_count, dozen_tracker_spins, top_color, middle_color, lower_color: create_dynamic_table(strategy if strategy != "None" else None, neighbours_count, strong_numbers_count, dozen_tracker_spins, top_color, middle_color, lower_color),
            inputs=[strategy_dropdown, neighbours_count_slider, strong_numbers_count_slider, dozen_tracker_spins_dropdown, top_color_picker, middle_color_picker, lower_color_picker],
            outputs=[dynamic_table_output]
        )
    except Exception as e:
        print(f"Error in use_winners_checkbox.change handler: {str(e)}")    
    
    try:
        reset_casino_data_button.click(
            fn=lambda: (
                "100", "00", "00", "00", "00", "00", "00", "00", "00", "00", "00", "00", "00", False,
                "", "", "<p>Casino data reset to defaults.</p>"  # Added hot_numbers_input, cold_numbers_input
            ),
            inputs=[],
            outputs=[
                spins_count_dropdown, even_percent, odd_percent, red_percent, black_percent,
                low_percent, high_percent, dozen1_percent, dozen2_percent, dozen3_percent,
                col1_percent, col2_percent, col3_percent, use_winners_checkbox,
                hot_numbers_input, cold_numbers_input, casino_data_output  # Added new inputs
            ]
        ).then(
            fn=create_dynamic_table,
            inputs=[strategy_dropdown, neighbours_count_slider, strong_numbers_count_slider, dozen_tracker_spins_dropdown, top_color_picker, middle_color_picker, lower_color_picker],
            outputs=[dynamic_table_output]
        )
    except Exception as e:
        print(f"Error in reset_casino_data_button.click handler: {str(e)}")

    try:
        play_hot_button.click(
            fn=play_specific_numbers,
            inputs=[hot_numbers_input, gr.State(value="Hot"), spins_display, last_spin_count],
            outputs=[spins_display, spins_textbox, casino_data_output, spin_counter, sides_of_zero_display]
        ).then(
            fn=lambda spins_display, count, show_trends: format_spins_as_html(spins_display, count, show_trends),
            inputs=[spins_display, last_spin_count, show_trends_state],
            outputs=[last_spin_display]
        ).then(
            fn=suggest_hot_cold_numbers,
            inputs=[],
            outputs=[hot_suggestions, cold_suggestions]
        ).then(
            fn=select_next_spin_top_pick,
            inputs=[top_pick_spin_count],
            outputs=[top_pick_display]
        ).then(
            fn=lambda: print(f"After play_hot_button click: state.last_spins = {state.last_spins}"),
            inputs=[],
            outputs=[]
        )
    except Exception as e:
        print(f"Error in play_hot_button.click handler: {str(e)}")
    
    try:
        play_cold_button.click(
            fn=play_specific_numbers,
            inputs=[cold_numbers_input, gr.State(value="Cold"), spins_display, last_spin_count],
            outputs=[spins_display, spins_textbox, casino_data_output, spin_counter, sides_of_zero_display]
        ).then(
            fn=lambda spins_display, count, show_trends: format_spins_as_html(spins_display, count, show_trends),
            inputs=[spins_display, last_spin_count, show_trends_state],
            outputs=[last_spin_display]
        ).then(
            fn=suggest_hot_cold_numbers,
            inputs=[],
            outputs=[hot_suggestions, cold_suggestions]
        ).then(
            fn=select_next_spin_top_pick,
            inputs=[top_pick_spin_count],
            outputs=[top_pick_display]
        ).then(
            fn=lambda: print(f"After play_cold_button click: state.last_spins = {state.last_spins}"),
            inputs=[],
            outputs=[]
        )
    except Exception as e:
        print(f"Error in play_cold_button.click handler: {str(e)}")
    
    try:
        clear_hot_button.click(
            fn=clear_hot_cold_picks,
            inputs=[gr.State(value="Hot"), spins_display],
            outputs=[hot_numbers_input, casino_data_output, spin_counter, sides_of_zero_display, spins_display]
        ).then(
            fn=select_next_spin_top_pick,
            inputs=[top_pick_spin_count],
            outputs=[top_pick_display]
        ).then(
            fn=lambda: print(f"After clear_hot_button click: state.last_spins = {state.last_spins}"),
            inputs=[],
            outputs=[]
        )
    except Exception as e:
        print(f"Error in clear_hot_button.click handler: {str(e)}")
    
    try:
        clear_cold_button.click(
            fn=clear_hot_cold_picks,
            inputs=[gr.State(value="Cold"), spins_display],
            outputs=[cold_numbers_input, casino_data_output, spin_counter, sides_of_zero_display, spins_display]
        ).then(
            fn=select_next_spin_top_pick,
            inputs=[top_pick_spin_count],
            outputs=[top_pick_display]
        ).then(
            fn=lambda: print(f"After clear_cold_button click: state.last_spins = {state.last_spins}"),
            inputs=[],
            outputs=[]
        )
    except Exception as e:
        print(f"Error in clear_cold_button.click handler: {str(e)}")

    try:
        spins_textbox.change(
            fn=validate_spins_input,
            inputs=[spins_textbox],
            outputs=[spins_display, last_spin_display]
        ).then(
            fn=lambda spins_display, count, show_trends: format_spins_as_html(spins_display, count, show_trends),
            inputs=[spins_display, last_spin_count, show_trends_state],
            outputs=[last_spin_display]
        ).then(
            fn=analyze_spins,
            inputs=[spins_display, strategy_dropdown, neighbours_count_slider, strong_numbers_count_slider],
            outputs=[
                spin_analysis_output, even_money_output, dozens_output, columns_output,
                streets_output, corners_output, six_lines_output, splits_output,
                sides_output, straight_up_html, top_18_html, strongest_numbers_output,
                dynamic_table_output, strategy_output, sides_of_zero_display
            ]
        ).then(
            fn=update_spin_counter,
            inputs=[],
            outputs=[spin_counter]
        ).then(
            fn=dozen_tracker,
            inputs=[dozen_tracker_spins_dropdown, dozen_tracker_consecutive_hits_dropdown, dozen_tracker_alert_checkbox, dozen_tracker_sequence_length_dropdown, dozen_tracker_follow_up_spins_dropdown, dozen_tracker_sequence_alert_checkbox],
            outputs=[gr.State(), dozen_tracker_output, dozen_tracker_sequence_output]
        ).then(
            fn=even_money_tracker,
            inputs=[
                even_money_tracker_spins_dropdown,
                even_money_tracker_consecutive_hits_dropdown,
                even_money_tracker_alert_checkbox,
                even_money_tracker_combination_mode_dropdown,
                even_money_tracker_red_checkbox,
                even_money_tracker_black_checkbox,
                even_money_tracker_even_checkbox,
                even_money_tracker_odd_checkbox,
                even_money_tracker_low_checkbox,
                even_money_tracker_high_checkbox,
                even_money_tracker_identical_traits_checkbox,
                even_money_tracker_consecutive_identical_dropdown
            ],
            outputs=[gr.State(), even_money_tracker_output]
        ).then(
            fn=select_next_spin_top_pick,
            inputs=[top_pick_spin_count],
            outputs=[top_pick_display]
        ).then(
            fn=lambda: print(f"After spins_textbox change: state.last_spins = {state.last_spins}"),
            inputs=[],
            outputs=[]
        )
    except Exception as e:
        print(f"Error in spins_textbox.change handler: {str(e)}")
    
    try:
        play_hot_button.click(
            fn=play_specific_numbers,
            inputs=[hot_numbers_input, gr.State(value="Hot"), spins_display, last_spin_count],
            outputs=[spins_display, spins_textbox, casino_data_output, spin_counter, sides_of_zero_display]
        ).then(
            fn=lambda spins_display, count, show_trends: format_spins_as_html(spins_display, count, show_trends),
            inputs=[spins_display, last_spin_count, show_trends_state],
            outputs=[last_spin_display]
        ).then(
            fn=suggest_hot_cold_numbers,
            inputs=[],
            outputs=[hot_suggestions, cold_suggestions]
        ).then(
            fn=select_next_spin_top_pick,
            inputs=[top_pick_spin_count],
            outputs=[top_pick_display]
        ).then(
            fn=lambda: print(f"After play_hot_button click: state.last_spins = {state.last_spins}"),
            inputs=[],
            outputs=[]
        )
    except Exception as e:
        print(f"Error in play_hot_button.click handler: {str(e)}")
    
    try:
        play_cold_button.click(
            fn=play_specific_numbers,
            inputs=[cold_numbers_input, gr.State(value="Cold"), spins_display, last_spin_count],
            outputs=[spins_display, spins_textbox, casino_data_output, spin_counter, sides_of_zero_display]
        ).then(
            fn=lambda spins_display, count, show_trends: format_spins_as_html(spins_display, count, show_trends),
            inputs=[spins_display, last_spin_count, show_trends_state],
            outputs=[last_spin_display]
        ).then(
            fn=suggest_hot_cold_numbers,
            inputs=[],
            outputs=[hot_suggestions, cold_suggestions]
        ).then(
            fn=select_next_spin_top_pick,
            inputs=[top_pick_spin_count],
            outputs=[top_pick_display]
        ).then(
            fn=lambda: print(f"After play_cold_button click: state.last_spins = {state.last_spins}"),
            inputs=[],
            outputs=[]
        )
    except Exception as e:
        print(f"Error in play_cold_button.click handler: {str(e)}")

    def toggle_labouchere(progression):
        """Show/hide Labouchere sequence input based on selected progression."""
        return gr.update(visible=progression == "Labouchere")
    
    # Betting progression event handlers
    def update_config(bankroll, base_unit, stop_loss, stop_win, bet_type, progression, sequence, target_profit):
        state.bankroll = bankroll
        state.initial_bankroll = bankroll
        state.base_unit = base_unit
        state.stop_loss = stop_loss
        state.stop_win = stop_win
        state.bet_type = bet_type
        state.progression = progression
        # Line 1: Enforce minimum value and reset labouchere_sequence
        target_profit = int(target_profit) if target_profit is not None else 10  # Ensure integer, default to 10
        state.target_profit = max(1, target_profit)  # Enforce minimum value of 1
        if progression == "Labouchere":
            try:
                # Only use the sequence if it's non-empty and valid; otherwise, auto-generate
                if sequence and sequence.strip():
                    parsed_sequence = [int(x.strip()) for x in sequence.split(",")]
                    if all(isinstance(x, int) and x > 0 for x in parsed_sequence):
                        state.progression_state = parsed_sequence
                        state.labouchere_sequence = sequence  # Keep the user-provided sequence
                    else:
                        state.progression_state = [1] * state.target_profit
                        state.labouchere_sequence = ""  # Clear the sequence to use auto-generated
                        return bankroll, base_unit, base_unit, f"Invalid sequence, using default {[1] * state.target_profit}", '<div style="background-color: white; padding: 5px; border-radius: 3px;">Active</div>', ""
                else:
                    state.progression_state = [1] * state.target_profit
                    state.labouchere_sequence = ""  # Ensure auto-generated sequence is used
            except ValueError:
                state.progression_state = [1] * state.target_profit
                state.labouchere_sequence = ""  # Clear the sequence on error
                return bankroll, base_unit, base_unit, f"Invalid sequence, using default {[1] * state.target_profit}", '<div style="background-color: white; padding: 5px; border-radius: 3px;">Active</div>', ""
        else:
            state.labouchere_sequence = ""  # Clear the sequence if not using Labouchere
        state.reset_progression()
        return state.bankroll, state.current_bet, state.next_bet, state.message, f'<div style="background-color: {state.status_color}; padding: 5px; border-radius: 3px;">{state.status}</div>', state.labouchere_sequence
    
    try:
        bankroll_input.change(
            fn=update_config,
            inputs=[bankroll_input, base_unit_input, stop_loss_input, stop_win_input, bet_type_dropdown, progression_dropdown, labouchere_sequence, target_profit_input],
            outputs=[bankroll_output, current_bet_output, next_bet_output, message_output, status_output, labouchere_sequence]
        )
    except Exception as e:
        print(f"Error in bankroll_input.change handler: {str(e)}")
    
    try:
        base_unit_input.change(
            fn=update_config,
            inputs=[bankroll_input, base_unit_input, stop_loss_input, stop_win_input, bet_type_dropdown, progression_dropdown, labouchere_sequence, target_profit_input],
            outputs=[bankroll_output, current_bet_output, next_bet_output, message_output, status_output, labouchere_sequence]
        )
    except Exception as e:
        print(f"Error in base_unit_input.change handler: {str(e)}")
    
    try:
        stop_loss_input.change(
            fn=update_config,
            inputs=[bankroll_input, base_unit_input, stop_loss_input, stop_win_input, bet_type_dropdown, progression_dropdown, labouchere_sequence, target_profit_input],
            outputs=[bankroll_output, current_bet_output, next_bet_output, message_output, status_output, labouchere_sequence]
        )
    except Exception as e:
        print(f"Error in stop_loss_input.change handler: {str(e)}")
    
    try:
        stop_win_input.change(
            fn=update_config,
            inputs=[bankroll_input, base_unit_input, stop_loss_input, stop_win_input, bet_type_dropdown, progression_dropdown, labouchere_sequence, target_profit_input],
            outputs=[bankroll_output, current_bet_output, next_bet_output, message_output, status_output, labouchere_sequence]
        )
    except Exception as e:
        print(f"Error in stop_win_input.change handler: {str(e)}")
    
    try:
        bet_type_dropdown.change(
            fn=update_config,
            inputs=[bankroll_input, base_unit_input, stop_loss_input, stop_win_input, bet_type_dropdown, progression_dropdown, labouchere_sequence, target_profit_input],
            outputs=[bankroll_output, current_bet_output, next_bet_output, message_output, status_output, labouchere_sequence]
        )
    except Exception as e:
        print(f"Error in bet_type_dropdown.change handler: {str(e)}")
    
    try:
        progression_dropdown.change(
            fn=update_config,
            inputs=[bankroll_input, base_unit_input, stop_loss_input, stop_win_input, bet_type_dropdown, progression_dropdown, labouchere_sequence, target_profit_input],
            outputs=[bankroll_output, current_bet_output, next_bet_output, message_output, status_output, labouchere_sequence]
        ).then(
            fn=toggle_labouchere,
            inputs=[progression_dropdown],
            outputs=[labouchere_sequence]
        )

    except Exception as e:
        print(f"Error in progression_dropdown.change handler: {str(e)}")
    
    try:
        labouchere_sequence.change(
            fn=update_config,
            inputs=[bankroll_input, base_unit_input, stop_loss_input, stop_win_input, bet_type_dropdown, progression_dropdown, labouchere_sequence, target_profit_input],
            outputs=[bankroll_output, current_bet_output, next_bet_output, message_output, status_output, labouchere_sequence]
        )
    except Exception as e:
        print(f"Error in labouchere_sequence.change handler: {str(e)}")
    
    try:
        win_button.click(
            fn=lambda: state.update_progression(True),
            inputs=[],
            outputs=[bankroll_output, current_bet_output, next_bet_output, message_output, status_output]
        )
    except Exception as e:
        print(f"Error in win_button.click handler: {str(e)}")
    
    try:
        lose_button.click(
            fn=lambda: state.update_progression(False),
            inputs=[],
            outputs=[bankroll_output, current_bet_output, next_bet_output, message_output, status_output]
        )
    except Exception as e:
        print(f"Error in lose_button.click handler: {str(e)}")
    
    try:
        reset_progression_button.click(
            fn=lambda: state.reset_progression(),
            inputs=[],
            outputs=[bankroll_output, current_bet_output, next_bet_output, message_output, status_output]
        )
    except Exception as e:
        print(f"Error in reset_progression_button.click handler: {str(e)}")
    
    # Video Category and Video Selection Event Handlers
    def update_video_dropdown(category):
        videos = video_categories.get(category, [])
        choices = [video["title"] for video in videos]
        default_value = choices[0] if choices else None
        return (
            gr.update(choices=choices, value=default_value),
            gr.update(value=f'<iframe width="100%" height="315" src="https://www.youtube.com/embed/{videos[0]["link"].split("/")[-1]}" frameborder="0" allowfullscreen></iframe>' if videos else "<p>No videos available in this category.</p>")
        )
    
    def update_video_display(video_title, category):
        videos = video_categories.get(category, [])
        selected_video = next((video for video in videos if video["title"] == video_title), None)
        if selected_video:
            video_id = selected_video["link"].split("/")[-1]
            return f'<iframe width="100%" height="315" src="https://www.youtube.com/embed/{video_id}" frameborder="0" allowfullscreen></iframe>'
        return "<p>Please select a video to watch.</p>"
    
    try:
        video_category_dropdown.change(
            fn=update_video_dropdown,
            inputs=[video_category_dropdown],
            outputs=[video_dropdown, video_output]
        )
    except Exception as e:
        print(f"Error in video_category_dropdown.change handler: {str(e)}")
    
    try:
        video_dropdown.change(
            fn=update_video_display,
            inputs=[video_dropdown, video_category_dropdown],
            outputs=[video_output]
        )
    except Exception as e:
        print(f"Error in video_dropdown.change handler: {str(e)}")

# Add the top pick slider change handler (was previously missing in your code)
    try:
        top_pick_spin_count.change(
            fn=select_next_spin_top_pick,
            inputs=[top_pick_spin_count],
            outputs=[top_pick_display]
        ).then(
            fn=lambda: print(f"After top_pick_spin_count change: state.last_spins = {state.last_spins}"),
            inputs=[],
            outputs=[]
        )
    except Exception as e:
        print(f"Error in top_pick_spin_count.change handler: {str(e)}")

# Launch the interface
print("Starting Gradio launch...")
demo.launch()
print("Gradio launch completed.")
