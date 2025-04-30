import gradio as gr
import math
import pandas as pd
import json
from itertools import combinations
import random
import logging
from collections import deque
from typing import Dict, List, Set, Optional, Any, Tuple
from datetime import datetime
import html

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from roulette_data import (
        EVEN_MONEY, DOZENS, COLUMNS, STREETS, CORNERS, SIX_LINES, SPLITS,
        NEIGHBORS_EUROPEAN, LEFT_OF_ZERO_EUROPEAN, RIGHT_OF_ZERO_EUROPEAN
    )
except ImportError as e:
    logger.error("Failed to import roulette_data: %s", e)
    raise ImportError("roulette_data.py is missing or corrupted.")

BETTING_MAPPINGS: Dict[int, Dict[str, List[str]]] = {}
ANALYSIS_CACHE: Dict[str, Any] = {}
MAX_SPIN_HISTORY = 1000

def initialize_betting_mappings() -> None:
    global BETTING_MAPPINGS
    try:
        BETTING_MAPPINGS = {i: {"even_money": [], "dozens": [], "columns": [], "streets": [], "corners": [], "six_lines": [], "splits": []} for i in range(37)}
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
        logger.info("Betting mappings initialized successfully.")
    except Exception as e:
        logger.error("Error initializing betting mappings: %s", e)
        raise

def update_scores_batch(spins: List[str]) -> List[Dict[str, Any]]:
    try:
        action_log = []
        increments = {
            "even_money_scores": {},
            "dozen_scores": {},
            "column_scores": {},
            "street_scores": {},
            "corner_scores": {},
            "six_line_scores": {},
            "split_scores": {},
            "scores": {},
            "side_scores": {}
        }
        for spin in spins:
            try:
                spin_value = int(spin)
                if not 0 <= spin_value <= 36:
                    raise ValueError(f"Invalid spin value: {spin}")
                action = {"spin": spin_value, "increments": {}}
                categories = BETTING_MAPPINGS.get(spin_value, {})
                for name in categories.get("even_money", []):
                    increments["even_money_scores"].setdefault(name, 0)
                    increments["even_money_scores"][name] += 1
                    action["increments"].setdefault("even_money_scores", {})[name] = 1
                for name in categories.get("dozens", []):
                    increments["dozen_scores"].setdefault(name, 0)
                    increments["dozen_scores"][name] += 1
                    action["increments"].setdefault("dozen_scores", {})[name] = 1
                for name in categories.get("columns", []):
                    increments["column_scores"].setdefault(name, 0)
                    increments["column_scores"][name] += 1
                    action["increments"].setdefault("column_scores", {})[name] = 1
                for name in categories.get("streets", []):
                    increments["street_scores"].setdefault(name, 0)
                    increments["street_scores"][name] += 1
                    action["increments"].setdefault("street_scores", {})[name] = 1
                for name in categories.get("corners", []):
                    increments["corner_scores"].setdefault(name, 0)
                    increments["corner_scores"][name] += 1
                    action["increments"].setdefault("corner_scores", {})[name] = 1
                for name in categories.get("six_lines", []):
                    increments["six_line_scores"].setdefault(name, 0)
                    increments["six_line_scores"][name] += 1
                    action["increments"].setdefault("six_line_scores", {})[name] = 1
                for name in categories.get("splits", []):
                    increments["split_scores"].setdefault(name, 0)
                    increments["split_scores"][name] += 1
                    action["increments"].setdefault("split_scores", {})[name] = 1
                increments["scores"].setdefault(spin_value, 0)
                increments["scores"][spin_value] += 1
                action["increments"].setdefault("scores", {})[spin_value] = 1
                if spin_value in current_left_of_zero:
                    increments["side_scores"].setdefault("Left Side of Zero", 0)
                    increments["side_scores"]["Left Side of Zero"] += 1
                    action["increments"].setdefault("side_scores", {})["Left Side of Zero"] = 1
                if spin_value in current_right_of_zero:
                    increments["side_scores"].setdefault("Right Side of Zero", 0)
                    increments["side_scores"]["Right Side of Zero"] += 1
                    action["increments"].setdefault("side_scores", {})["Right Side of Zero"] = 1
                action_log.append(action)
            except ValueError as ve:
                logger.warning("Skipping invalid spin: %s", ve)
                continue
        for name, count in increments["even_money_scores"].items():
            state.even_money_scores[name] += count
        for name, count in increments["dozen_scores"].items():
            state.dozen_scores[name] += count
        for name, count in increments["column_scores"].items():
            state.column_scores[name] += count
        for name, count in increments["street_scores"].items():
            state.street_scores[name] += count
        for name, count in increments["corner_scores"].items():
            state.corner_scores[name] += count
        for name, count in increments["six_line_scores"].items():
            state.six_line_scores[name] += count
        for name, count in increments["split_scores"].items():
            state.split_scores[name] += count
        for num, count in increments["scores"].items():
            state.scores[num] += count
        for name, count in increments["side_scores"].items():
            state.side_scores[name] += count
        logger.info("Updated scores for %d spins", len(spins))
        return action_log
    except Exception as e:
        logger.error("Error updating scores: %s", e)
        raise

def validate_roulette_data() -> Optional[List[str]]:
    try:
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
        errors = []
        for name, data in required_dicts.items():
            if not isinstance(data, dict):
                errors.append(f"{name} must be a dictionary.")
                continue
            for key, value in data.items():
                if not isinstance(key, str) or not isinstance(value, (list, set, tuple)) or not all(isinstance(n, int) for n in value):
                    errors.append(f"{name}['{key}'] must map to a list/set/tuple of integers.")
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
        if errors:
            logger.error("Roulette data validation failed: %s", errors)
            return errors
        logger.info("Roulette data validated successfully.")
        return None
    except Exception as e:
        logger.error("Unexpected error in validate_roulette_data: %s", e)
        raise ValueError(f"Failed to validate roulette data: {str(e)}")

class RouletteState:
    def __init__(self):
        try:
            self.scores = {n: 0 for n in range(37)}
            self.even_money_scores = {name: 0 for name in EVEN_MONEY.keys()}
            self.dozen_scores = {name: 0 for name in DOZENS.keys()}
            self.column_scores = {name: 0 for name in COLUMNS.keys()}
            self.street_scores = {name: 0 for name in STREETS.keys()}
            self.corner_scores = {name: 0 for name in CORNERS.keys()}
            self.six_line_scores = {name: 0 for name in SIX_LINES.keys()}
            self.split_scores = {name: 0 for name in SPLITS.keys()}
            self.side_scores = {"Left Side of Zero": 0, "Right Side of Zero": 0}
            self.selected_numbers: Set[int] = set()
            self.last_spins: List[str] = []
            self.spin_history: deque = deque(maxlen=MAX_SPIN_HISTORY)
            self.casino_data = {
                "spins_count": 100,
                "hot_numbers": {},
                "cold_numbers": {},
                "even_odd": {"Even": 0.0, "Odd": 0.0},
                "red_black": {"Red": 0.0, "Black": 0.0},
                "low_high": {"Low": 0.0, "High": 0.0},
                "dozens": {"1st Dozen": 0.0, "2nd Dozen": 0.0, "3rd Dozen": 0.0},
                "columns": {"1st Column": 0.0, "2nd Column": 0.0, "3rd Column": 0.0}
            }
            self.hot_suggestions: str = ""
            self.cold_suggestions: str = ""
            self.use_casino_winners: bool = False
            self.bankroll: float = 1000
            self.initial_bankroll: float = 1000
            self.base_unit: float = 10
            self.stop_loss: float = -500
            self.stop_win: float = 200
            self.target_profit: int = 10
            self.bet_type: str = "Even Money"
            self.progression: str = "Martingale"
            self.current_bet: float = self.base_unit
            self.next_bet: float = self.base_unit
            self.progression_state: Optional[List[int]] = None
            self.message: str = f"Start with base bet of {self.base_unit} on {self.bet_type} ({self.progression})"
            self.status: str = "Active"
            self.status_color: str = "white"
            self.last_dozen_alert_index: int = -1
            self.alerted_patterns: Set[tuple] = set()
            self.last_alerted_spins: Optional[tuple] = None
            self.labouchere_sequence: str = ""
            self.is_stopped: bool = False
            logger.info("RouletteState initialized successfully.")
        except Exception as e:
            logger.error("Error initializing RouletteState: %s", e)
            raise

    def reset(self) -> None:
        try:
            use_casino_winners = self.use_casino_winners
            casino_data = self.casino_data.copy()
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
            self.spin_history = deque(maxlen=MAX_SPIN_HISTORY)
            self.use_casino_winners = use_casino_winners
            self.casino_data = casino_data
            self.reset_progression()
            logger.info("RouletteState reset successfully.")
        except Exception as e:
            logger.error("Error resetting RouletteState: %s", e)
            raise

    def calculate_aggregated_scores_for_spins(self, numbers: List[int]) -> Tuple[Dict[str, int], Dict[str, int], Dict[str, int]]:
        try:
            cache_key = f"agg_scores_{hash(tuple(numbers))}"
            if cache_key in ANALYSIS_CACHE:
                logger.info("Returning cached aggregated scores for %d numbers", len(numbers))
                return ANALYSIS_CACHE[cache_key]
            even_money_scores = {name: 0 for name in EVEN_MONEY.keys()}
            dozen_scores = {name: 0 for name in DOZENS.keys()}
            column_scores = {name: 0 for name in COLUMNS.keys()}
            for number in numbers:
                if number == 0:
                    continue
                for name, numbers_set in EVEN_MONEY.items():
                    if number in numbers_set:
                        even_money_scores[name] += 1
                for name, numbers_set in DOZENS.items():
                    if number in numbers_set:
                        dozen_scores[name] += 1
                for name, numbers_set in COLUMNS.items():
                    if number in numbers_set:
                        column_scores[name] += 1
            result = (even_money_scores, dozen_scores, column_scores)
            ANALYSIS_CACHE[cache_key] = result
            logger.info("Calculated aggregated scores for %d numbers", len(numbers))
            return result
        except Exception as e:
            logger.error("Error calculating aggregated scores: %s", e)
            raise

    def reset_progression(self) -> Tuple[float, float, float, str, str]:
        try:
            self.current_bet = self.base_unit
            self.next_bet = self.base_unit
            self.progression_state = None
            self.is_stopped = False
            self.message = f"Progression reset. Start with base bet of {self.base_unit} on {self.bet_type} ({self.progression})"
            self.status = "Active"
            self.status_color = "white"
            logger.info("Progression reset for %s", self.progression)
            return self.bankroll, self.current_bet, self.next_bet, self.message, self.status
        except Exception as e:
            logger.error("Error resetting progression: %s", e)
            raise

    def update_bankroll(self, won: bool) -> None:
        try:
            payout = {"Even Money": 1, "Dozens": 2, "Columns": 2, "Straight Bets": 35}[self.bet_type]
            if won:
                self.bankroll += self.current_bet * payout
            else:
                self.bankroll -= self.current_bet
            profit = self.bankroll - self.initial_bankroll
            if profit <= self.stop_loss:
                self.is_stopped = True
                self.status = f"Stopped: Hit Stop Loss of {self.stop_loss}"
                self.status_color = "red"
            elif profit >= self.stop_win:
                self.is_stopped = True
                self.status = f"Stopped: Hit Stop Win of {self.stop_win}"
                self.status_color = "green"
            else:
                self.status_color = "white"
            logger.info("Bankroll updated: won=%s, new bankroll=%.2f", won, self.bankroll)
        except KeyError as e:
            logger.error("Invalid bet type: %s", e)
            raise ValueError(f"Invalid bet type: {self.bet_type}")
        except Exception as e:
            logger.error("Error updating bankroll: %s", e)
            raise

    def update_progression(self, won: bool) -> Tuple[float, float, float, str, str, str]:
        try:
            if self.is_stopped:
                logger.info("Progression stopped, returning current state")
                return self.bankroll, self.current_bet, self.next_bet, self.message, self.status, self.status_color
            self.update_bankroll(won)
            if self.bankroll < self.current_bet:
                self.is_stopped = True
                self.status = "Stopped: Insufficient bankroll"
                self.status_color = "red"
                self.message = "Cannot continue: Bankroll too low."
                gr.Warning(self.message)
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
                if self.progression_state is None:
                    try:
                        if self.labouchere_sequence and self.labouchere_sequence.strip():
                            sequence = [int(x.strip()) for x in self.labouchere_sequence.split(",")]
                            if not sequence or not all(isinstance(x, int) and x > 0 for x in sequence):
                                sequence = [1] * max(1, self.target_profit)
                        else:
                            sequence = [1] * max(1, self.target_profit)
                    except ValueError:
                        sequence = [1] * max(1, self.target_profit)
                    self.progression_state = sequence
                self.current_bet = self.next_bet
                if not self.progression_state:
                    self.progression_state = [1] * max(1, self.target_profit)
                    self.next_bet = self.base_unit
                    self.message = f"Sequence cleared! Reset to {self.next_bet}"
                elif len(self.progression_state) == 1:
                    self.next_bet = self.progression_state[0] * self.base_unit
                    if won:
                        self.progression_state = []
                        self.message = f"Win! Sequence completed, next bet: {self.next_bet}"
                    else:
                        self.message = f"Loss! Next bet: {self.next_bet}"
                else:
                    if won:
                        self.progression_state = self.progression_state[1:-1] if len(self.progression_state) > 2 else []
                        self.next_bet = (self.progression_state[0] + self.progression_state[-1]) * self.base_unit if self.progression_state else self.base_unit
                        self.message = f"Win! Sequence: {self.progression_state}, next bet: {self.next_bet}"
                    else:
                        lost_bet = max(1, self.current_bet // self.base_unit)
                        self.progression_state.append(lost_bet)
                        self.next_bet = (self.progression_state[0] + self.progression_state[-1]) * self.base_unit
                        self.message = f"Loss! Sequence: {self.progression_state}, next bet: {self.next_bet}"
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
            profit = self.bankroll - self.initial_bankroll
            if profit <= self.stop_loss:
                self.is_stopped = True
                self.status = "Stopped: Stop Loss Reached"
                self.status_color = "red"
                self.message = f"Stop Loss reached at {profit}. Current bankroll: {self.bankroll}"
                gr.Warning(self.message)
            elif profit >= self.stop_win:
                self.is_stopped = True
                self.status = "Stopped: Stop Win Reached"
                self.status_color = "green"
                self.message = f"Stop Win reached at {profit}. Current bankroll: {self.bankroll}"
                gr.Warning(self.message)
            logger.info("Progression updated: won=%s, next_bet=%.2f, message=%s", won, self.next_bet, self.message)
            return self.bankroll, self.current_bet, self.next_bet, self.message, self.status, self.status_color
        except Exception as e:
            logger.error("Error updating progression: %s", e)
            gr.Warning(f"Error in progression: {str(e)}")
            raise

state = RouletteState()
current_neighbors = NEIGHBORS_EUROPEAN
current_left_of_zero = set(LEFT_OF_ZERO_EUROPEAN)
current_right_of_zero = set(RIGHT_OF_ZERO_EUROPEAN)
TABLE_TYPE = "European"

colors = {
    "0": "green",
    "1": "red", "3": "red", "5": "red", "7": "red", "9": "red",
    "12": "red", "14": "red", "16": "red", "18": "red",
    "19": "red", "21": "red", "23": "red", "25": "red", "27": "red",
    "30": "red", "32": "red", "34": "red", "36": "red",
    "2": "black", "4": "black", "6": "black", "8": "black", "10": "black",
    "11": "black", "13": "black", "15": "black", "17": "black",
    "20": "black", "22": "black", "24": "black", "26": "black", "28": "black",
    "29": "black", "31": "black", "33": "black", "35": "black"
}

def add_spin(spin: str, current_spins: str, last_spin_count: int) -> Tuple[str, str, str, str, str]:
    try:
        spin = spin.strip()
        if not spin.isdigit() or not 0 <= int(spin) <= 36:
            gr.Warning(f"Invalid spin: {spin}. Must be a number between 0 and 36.")
            return current_spins, current_spins, format_spins_as_html(current_spins, last_spin_count), update_spin_counter(), render_sides_of_zero_display()
        new_spins = [spin]
        update_scores_batch(new_spins)
        if current_spins and current_spins.strip():
            current_spins_list = current_spins.split(", ")
            updated_spins = current_spins_list + new_spins
        else:
            updated_spins = new_spins
        if len(updated_spins) > MAX_SPIN_HISTORY:
            updated_spins = updated_spins[-MAX_SPIN_HISTORY:]
            gr.Warning(f"Spin history truncated to {MAX_SPIN_HISTORY} spins to manage memory.")
        state.last_spins = updated_spins
        spins_text = ", ".join(updated_spins)
        logger.info("Added spin: %s, total spins: %d", spin, len(updated_spins))
        return (
            spins_text,
            spins_text,
            format_spins_as_html(spins_text, last_spin_count),
            update_spin_counter(),
            render_sides_of_zero_display()
        )
    except Exception as e:
        logger.error("Error adding spin: %s", e)
        gr.Warning(f"Error adding spin: {str(e)}")
        return current_spins, current_spins, format_spins_as_html(current_spins, last_spin_count), update_spin_counter(), render_sides_of_zero_display()

def validate_spins_input(spins_input: str) -> Tuple[str, str]:
    try:
        if not spins_input or not spins_input.strip():
            state.last_spins = []
            logger.info("Spins input cleared")
            return "", "<h4>Last Spins</h4><p>No spins entered.</p>"
        spins = [s.strip() for s in spins_input.split(",") if s.strip()]
        valid_spins = []
        for spin in spins:
            if not spin.isdigit() or not 0 <= int(spin) <= 36:
                gr.Warning(f"Invalid spin: {spin}. Must be between 0 and 36.")
                continue
            valid_spins.append(spin)
        if not valid_spins:
            logger.warning("No valid spins provided")
            return "", "<h4>Last Spins</h4><p>No valid spins entered.</p>"
        if len(valid_spins) > MAX_SPIN_HISTORY:
            valid_spins = valid_spins[-MAX_SPIN_HISTORY:]
            gr.Warning(f"Spin history truncated to {MAX_SPIN_HISTORY} spins.")
        update_scores_batch(valid_spins)
        state.last_spins = valid_spins
        spins_text = ", ".join(valid_spins)
        logger.info("Validated %d spins", len(valid_spins))
        return spins_text, format_spins_as_html(spins_text, 36)
    except Exception as e:
        logger.error("Error validating spins input: %s", e)
        gr.Warning(f"Error processing spins: {str(e)}")
        return "", "<h4>Last Spins</h4><p>Error processing spins.</p>"

def format_spins_as_html(spins_input: str, last_spin_count: int) -> str:
    try:
        cache_key = f"format_spins_{hash(spins_input)}_{last_spin_count}"
        if cache_key in ANALYSIS_CACHE:
            logger.info("Returning cached spins HTML")
            return ANALYSIS_CACHE[cache_key]
        if not spins_input or not spins_input.strip():
            result = "<h4>Last Spins</h4><p>No spins to display.</p>"
            ANALYSIS_CACHE[cache_key] = result
            return result
        spins = spins_input.split(", ")
        last_spin_count = min(int(last_spin_count), MAX_SPIN_HISTORY)
        spins_to_show = spins[-last_spin_count:] if len(spins) > last_spin_count else spins
        if not spins_to_show:
            result = "<h4>Last Spins</h4><p>No spins to display.</p>"
            ANALYSIS_CACHE[cache_key] = result
            return result
        html_output = '<h4>Last Spins</h4><div class="fade-in" style="display: flex; flex-wrap: wrap; gap: 5px;">'
        for i, spin in enumerate(spins_to_show):
            color = colors.get(spin, "black")
            spin_safe = html.escape(spin)
            animation_class = "flip" if i >= len(spins_to_show) - 3 and len(spins) >= 3 else ""
            html_output += (
                f'<span class="roulette-button {color} {animation_class}" '
                f'style="padding: 5px 10px; border-radius: 5px; color: white; '
                f'font-size: 14px; min-width: 30px; text-align: center;">{spin_safe}</span>'
            )
        html_output += '</div>'
        ANALYSIS_CACHE[cache_key] = html_output
        logger.debug("Formatted %d spins as HTML", len(spins_to_show))
        return html_output
    except Exception as e:
        logger.error("Error formatting spins as HTML: %s", e)
        return "<h4>Last Spins</h4><p>Error displaying spins.</p>"

def render_sides_of_zero_display() -> str:
    try:
        cache_key = "sides_of_zero_display"
        if cache_key in ANALYSIS_CACHE:
            logger.info("Returning cached sides of zero display")
            return ANALYSIS_CACHE[cache_key]
        left_count = state.side_scores.get("Left Side of Zero", 0)
        right_count = state.side_scores.get("Right Side of Zero", 0)
        total_spins = left_count + right_count
        sorted_scores = sorted(state.scores.items(), key=lambda x: x[1], reverse=True)
        hot_numbers = [str(num) for num, score in sorted_scores[:5] if score > 0]
        cold_numbers = [str(num) for num, score in sorted_scores[-5:] if score >= 0]
        hot_numbers_safe = [html.escape(num) for num in hot_numbers]
        cold_numbers_safe = [html.escape(num) for num in cold_numbers]
        svg_width = 300
        svg_height = 300
        center_x = svg_width / 2
        center_y = svg_height / 2
        radius = 100
        html_output = (
            '<div class="sides-of-zero-container" style="text-align: center; '
            'max-width: 100%; overflow-x: auto;">'
            '<h4>Dealer’s Spin Tracker</h4>'
            f'<p>Left Side Hits: {left_count} | Right Side Hits: {right_count}</p>'
            f'<p>Total Spins: {total_spins}</p>'
            f'<p>Hot Numbers (🔥): {", ".join(hot_numbers_safe) or "None"}</p>'
            f'<p>Cold Numbers (❄️): {", ".join(cold_numbers_safe) or "None"}</p>'
            '<svg width="100%" height="100%" viewBox="0 0 300 300" '
            'style="max-width: 300px; margin: 0 auto;">'
            f'<circle cx="{center_x}" cy="{center_y}" r="{radius}" fill="#2e7d32" />'
            f'<path d="M{center_x},{center_y} L{center_x},{center_y-radius} A{radius},{radius} 0 0,1 {center_x},{center_y+radius} Z" fill="red" opacity="0.5" />'
            f'<path d="M{center_x},{center_y} L{center_x},{center_y+radius} A{radius},{radius} 0 0,1 {center_x},{center_y-radius} Z" fill="black" opacity="0.5" />'
            f'<circle cx="{center_x}" cy="{center_y-radius*0.8}" r="20" fill="green" />'
            f'<text x="{center_x}" y="{center_y-radius*0.8+5}" text-anchor="middle" fill="white" font-size="14">0</text>'
            '<animateTransform attributeName="transform" type="rotate" from="0 150 150" to="360 150 150" dur="10s" repeatCount="indefinite" />'
            '</svg>'
        )
        betting_sections = {
            "Voisins du Zero": list(set([0, 2, 3, 4, 7, 12, 15, 18, 19, 21, 22, 25, 26, 28, 29, 32, 35])),
            "Tiers du Cylindre": list(set([5, 8, 10, 11, 13, 16, 23, 24, 27, 30, 33, 36])),
            "Orphelins": list(set([1, 6, 9, 14, 17, 20, 31, 34]))
        }
        html_output += '<h4>Betting Sections</h4><ul style="list-style-type: none; padding: 0;">'
        for name, numbers in betting_sections.items():
            hits = sum(state.scores.get(num, 0) for num in numbers)
            name_safe = html.escape(name)
            numbers_safe = [html.escape(str(num)) for num in numbers]
            html_output += (
                f'<li>{name_safe}: {hits} hits (Numbers: {", ".join(numbers_safe)})</li>'
            )
        html_output += '</ul></div>'
        ANALYSIS_CACHE[cache_key] = html_output
        logger.debug("Rendered sides of zero display")
        return html_output
    except Exception as e:
        logger.error("Error rendering sides of zero display: %s", e)
        return "<h4>Dealer’s Spin Tracker</h4><p>Error rendering wheel.</p>"

def update_spin_counter() -> str:
    try:
        spin_count = len(state.last_spins)
        spin_count_safe = html.escape(str(spin_count))
        html_output = (
            f'<span class="spin-counter" style="font-size: 14px; padding: 4px 8px;">'
            f'Total Spins: {spin_count_safe}</span>'
        )
        logger.debug("Updated spin counter: %d spins", spin_count)
        return html_output
    except Exception as e:
        logger.error("Error updating spin counter: %s", e)
        return '<span class="spin-counter">Error</span>'

def generate_random_spins(num_spins: str, current_spins: str, last_spin_count: int) -> Tuple[str, str, str, str, str]:
    try:
        try:
            num_spins = int(num_spins)
            if num_spins < 1:
                raise ValueError("Number of spins must be positive")
        except (ValueError, TypeError) as e:
            gr.Warning(f"Invalid number of spins: {num_spins}. Using default of 5.")
            num_spins = 5
        new_spins = [str(random.randint(0, 36)) for _ in range(num_spins)]
        update_scores_batch(new_spins)
        if current_spins and current_spins.strip():
            current_spins_list = current_spins.split(", ")
            updated_spins = current_spins_list + new_spins
        else:
            updated_spins = new_spins
        if len(updated_spins) > MAX_SPIN_HISTORY:
            updated_spins = updated_spins[-MAX_SPIN_HISTORY:]
            gr.Warning(f"Spin history truncated to {MAX_SPIN_HISTORY} spins.")
        state.last_spins = updated_spins
        spins_text = ", ".join(updated_spins)
        analysis = f"Generated {num_spins} random spins: {', '.join(new_spins)}"
        logger.info("Generated %d random spins", num_spins)
        return (
            spins_text,
            spins_text,
            analysis,
            update_spin_counter(),
            render_sides_of_zero_display()
        )
    except Exception as e:
        logger.error("Error generating random spins: %s", e)
        gr.Warning(f"Error generating spins: {str(e)}")
        return (
            current_spins,
            current_spins,
            f"Error: {str(e)}",
            update_spin_counter(),
            render_sides_of_zero_display()
        )

def clear_spins() -> Tuple[str, str, str, str, str, str]:
    try:
        state.reset()
        logger.info("Cleared all spins")
        return (
            "",
            "",
            "Spins cleared.",
            "<h4>Last Spins</h4><p>No spins to display.</p>",
            update_spin_counter(),
            render_sides_of_zero_display()
        )
    except Exception as e:
        logger.error("Error clearing spins: %s", e)
        gr.Warning(f"Error clearing spins: {str(e)}")
        return (
            "",
            "",
            f"Error: {str(e)}",
            "<h4>Last Spins</h4><p>Error clearing spins.</p>",
            update_spin_counter(),
            render_sides_of_zero_display()
        )

def undo_last_spin() -> Tuple[str, str, str, str, str]:
    try:
        if not state.spin_history:
            gr.Warning("No spins to undo.")
            return (
                ", ".join(state.last_spins),
                ", ".join(state.last_spins),
                format_spins_as_html(", ".join(state.last_spins), 36),
                update_spin_counter(),
                render_sides_of_zero_display()
            )
        last_action = state.spin_history.pop()
        spin_value = last_action["spin"]
        increments = last_action["increments"]
        for category, updates in increments.items():
            for name, count in updates.items():
                getattr(state, category)[name] -= count
        state.last_spins = state.last_spins[:-1]
        spins_text = ", ".join(state.last_spins) if state.last_spins else ""
        logger.info("Undid spin: %d", spin_value)
        return (
            spins_text,
            spins_text,
            format_spins_as_html(spins_text, 36),
            update_spin_counter(),
            render_sides_of_zero_display()
        )
    except Exception as e:
        logger.error("Error undoing spin: %s", e)
        gr.Warning(f"Error undoing spin: {str(e)}")
        return (
            ", ".join(state.last_spins),
            ", ".join(state.last_spins),
            format_spins_as_html(", ".join(state.last_spins), 36),
            update_spin_counter(),
            render_sides_of_zero_display()
        )

def best_even_money_bets() -> str:
    try:
        cache_key = "best_even_money_bets"
        if cache_key in ANALYSIS_CACHE:
            logger.info("Returning cached best even money bets")
            return ANALYSIS_CACHE[cache_key]
        sorted_scores = sorted(state.even_money_scores.items(), key=lambda x: x[1], reverse=True)
        recommendations = []
        hits = [item for item in sorted_scores if item[1] > 0]
        if not hits:
            recommendations.append("No even money bets have hit yet.")
        else:
            recommendations.append("Best Even Money Bets:")
            for i, (name, score) in enumerate(hits[:3], 1):
                name_safe = html.escape(name)
                recommendations.append(f"{i}. {name_safe}: {score} hits")
        result = "<br>".join(recommendations)
        ANALYSIS_CACHE[cache_key] = result
        logger.info("Generated best even money bets: %s", result)
        return result
    except Exception as e:
        logger.error("Error in best_even_money_bets: %s", e)
        gr.Warning(f"Error generating even money bets: {str(e)}")
        return "<p>Error generating recommendations.</p>"

def hot_bet_strategy() -> str:
    try:
        cache_key = "hot_bet_strategy"
        if cache_key in ANALYSIS_CACHE:
            logger.info("Returning cached hot bet strategy")
            return ANALYSIS_CACHE[cache_key]
        recommendations = []
        sorted_scores = sorted(state.scores.items(), key=lambda x: x[1], reverse=True)
        hot_numbers = [item for item in sorted_scores if item[1] > 0]
        if not hot_numbers:
            recommendations.append("Hot Bet Strategy: No numbers have hit yet.")
        else:
            recommendations.append("Hot Bet Strategy (Top 5 Numbers):")
            for i, (num, score) in enumerate(hot_numbers[:5], 1):
                num_safe = html.escape(str(num))
                recommendations.append(f"{i}. Number {num_safe}: {score} hits")
            even_money_hits = sorted(state.even_money_scores.items(), key=lambda x: x[1], reverse=True)
            if even_money_hits and even_money_hits[0][1] > 0:
                name_safe = html.escape(even_money_hits[0][0])
                recommendations.append(f"Top Even Money: {name_safe}: {even_money_hits[0][1]} hits")
        result = "<br>".join(recommendations)
        ANALYSIS_CACHE[cache_key] = result
        logger.info("Generated hot bet strategy")
        return result
    except Exception as e:
        logger.error("Error in hot_bet_strategy: %s", e)
        gr.Warning(f"Error generating hot bet strategy: {str(e)}")
        return "<p>Error generating recommendations.</p>"

def cold_bet_strategy() -> str:
    try:
        cache_key = "cold_bet_strategy"
        if cache_key in ANALYSIS_CACHE:
            logger.info("Returning cached cold bet strategy")
            return ANALYSIS_CACHE[cache_key]
        recommendations = []
        sorted_scores = sorted(state.scores.items(), key=lambda x: x[1])
        cold_numbers = [item for item in sorted_scores if item[1] >= 0]
        if not cold_numbers:
            recommendations.append("Cold Bet Strategy: No data available.")
        else:
            recommendations.append("Cold Bet Strategy (Top 5 Cold Numbers):")
            for i, (num, score) in enumerate(cold_numbers[:5], 1):
                num_safe = html.escape(str(num))
                recommendations.append(f"{i}. Number {num_safe}: {score} hits")
            even_money_hits = sorted(state.even_money_scores.items(), key=lambda x: x[1])
            if even_money_hits:
                name_safe = html.escape(even_money_hits[0][0])
                recommendations.append(f"Coldest Even Money: {name_safe}: {even_money_hits[0][1]} hits")
        result = "<br>".join(recommendations)
        ANALYSIS_CACHE[cache_key] = result
        logger.info("Generated cold bet strategy")
        return result
    except Exception as e:
        logger.error("Error in cold_bet_strategy: %s", e)
        gr.Warning(f"Error generating cold bet strategy: {str(e)}")
        return "<p>Error generating recommendations.</p>"

def best_dozens() -> str:
    try:
        cache_key = "best_dozens"
        if cache_key in ANALYSIS_CACHE:
            logger.info("Returning cached best dozens")
            return ANALYSIS_CACHE[cache_key]
        sorted_dozens = sorted(state.dozen_scores.items(), key=lambda x: x[1], reverse=True)
        recommendations = []
        hits = [item for item in sorted_dozens if item[1] > 0]
        if not hits:
            recommendations.append("No dozen bets have hit yet.")
        else:
            recommendations.append("Best Dozen Bets:")
            for i, (name, score) in enumerate(hits[:2], 1):
                name_safe = html.escape(name)
                recommendations.append(f"{i}. {name_safe}: {score} hits")
        result = "<br>".join(recommendations)
        ANALYSIS_CACHE[cache_key] = result
        logger.info("Generated best dozens")
        return result
    except Exception as e:
        logger.error("Error in best_dozens: %s", e)
        gr.Warning(f"Error generating dozen bets: {str(e)}")
        return "<p>Error generating recommendations.</p>"

def best_columns() -> str:
    try:
        cache_key = "best_columns"
        if cache_key in ANALYSIS_CACHE:
            logger.info("Returning cached best columns")
            return ANALYSIS_CACHE[cache_key]
        sorted_columns = sorted(state.column_scores.items(), key=lambda x: x[1], reverse=True)
        recommendations = []
        hits = [item for item in sorted_columns if item[1] > 0]
        if not hits:
            recommendations.append("No column bets have hit yet.")
        else:
            recommendations.append("Best Column Bets:")
            for i, (name, score) in enumerate(hits[:2], 1):
                name_safe = html.escape(name)
                recommendations.append(f"{i}. {name_safe}: {score} hits")
        result = "<br>".join(recommendations)
        ANALYSIS_CACHE[cache_key] = result
        logger.info("Generated best columns")
        return result
    except Exception as e:
        logger.error("Error in best_columns: %s", e)
        gr.Warning(f"Error generating column bets: {str(e)}")
        return "<p>Error generating recommendations.</p>"

def best_even_money_and_top_18() -> str:
    try:
        cache_key = "best_even_money_and_top_18"
        if cache_key in ANALYSIS_CACHE:
            logger.info("Returning cached best even money and top 18")
            return ANALYSIS_CACHE[cache_key]
        recommendations = []
        sorted_even_money = sorted(state.even_money_scores.items(), key=lambda x: x[1], reverse=True)
        even_money_hits = [item for item in sorted_even_money if item[1] > 0]
        if even_money_hits:
            recommendations.append("Best Even Money Bets:")
            for i, (name, score) in enumerate(even_money_hits[:2], 1):
                name_safe = html.escape(name)
                recommendations.append(f"{i}. {name_safe}: {score} hits")
        else:
            recommendations.append("No even money bets have hit yet.")
        sorted_numbers = sorted(state.scores.items(), key=lambda x: x[1], reverse=True)
        top_numbers = [item for item in sorted_numbers if item[1] > 0]
        if top_numbers:
            recommendations.append("Top 18 Numbers:")
            for i, (num, score) in enumerate(top_numbers[:18], 1):
                num_safe = html.escape(str(num))
                recommendations.append(f"{i}. Number {num_safe}: {score} hits")
        else:
            recommendations.append("No numbers have hit yet.")
        result = "<br>".join(recommendations)
        ANALYSIS_CACHE[cache_key] = result
        logger.info("Generated best even money and top 18")
        return result
    except Exception as e:
        logger.error("Error in best_even_money_and_top_18: %s", e)
        gr.Warning(f"Error generating recommendations: {str(e)}")
        return "<p>Error generating recommendations.</p>"

def best_dozens_and_top_18() -> str:
    try:
        cache_key = "best_dozens_and_top_18"
        if cache_key in ANALYSIS_CACHE:
            logger.info("Returning cached best dozens and top 18")
            return ANALYSIS_CACHE[cache_key]
        recommendations = []
        sorted_dozens = sorted(state.dozen_scores.items(), key=lambda x: x[1], reverse=True)
        dozen_hits = [item for item in sorted_dozens if item[1] > 0]
        if dozen_hits:
            recommendations.append("Best Dozen Bets:")
            for i, (name, score) in enumerate(dozen_hits[:2], 1):
                name_safe = html.escape(name)
                recommendations.append(f"{i}. {name_safe}: {score} hits")
        else:
            recommendations.append("No dozen bets have hit yet.")
        sorted_numbers = sorted(state.scores.items(), key=lambda x: x[1], reverse=True)
        top_numbers = [item for item in sorted_numbers if item[1] > 0]
        if top_numbers:
            recommendations.append("Top 18 Numbers:")
            for i, (num, score) in enumerate(top_numbers[:18], 1):
                num_safe = html.escape(str(num))
                recommendations.append(f"{i}. Number {num_safe}: {score} hits")
        else:
            recommendations.append("No numbers have hit yet.")
        result = "<br>".join(recommendations)
        ANALYSIS_CACHE[cache_key] = result
        logger.info("Generated best dozens and top 18")
        return result
    except Exception as e:
        logger.error("Error in best_dozens_and_top_18: %s", e)
        gr.Warning(f"Error generating recommendations: {str(e)}")
        return "<p>Error generating recommendations.</p>"

def best_columns_and_top_18() -> str:
    try:
        cache_key = "best_columns_and_top_18"
        if cache_key in ANALYSIS_CACHE:
            logger.info("Returning cached best columns and top 18")
            return ANALYSIS_CACHE[cache_key]
        recommendations = []
        sorted_columns = sorted(state.column_scores.items(), key=lambda x: x[1], reverse=True)
        column_hits = [item for item in sorted_columns if item[1] > 0]
        if column_hits:
            recommendations.append("Best Column Bets:")
            for i, (name, score) in enumerate(column_hits[:2], 1):
                name_safe = html.escape(name)
                recommendations.append(f"{i}. {name_safe}: {score} hits")
        else:
            recommendations.append("No column bets have hit yet.")
        sorted_numbers = sorted(state.scores.items(), key=lambda x: x[1], reverse=True)
        top_numbers = [item for item in sorted_numbers if item[1] > 0]
        if top_numbers:
            recommendations.append("Top 18 Numbers:")
            for i, (num, score) in enumerate(top_numbers[:18], 1):
                num_safe = html.escape(str(num))
                recommendations.append(f"{i}. Number {num_safe}: {score} hits")
        else:
            recommendations.append("No numbers have hit yet.")
        result = "<br>".join(recommendations)
        ANALYSIS_CACHE[cache_key] = result
        logger.info("Generated best columns and top 18")
        return result
    except Exception as e:
        logger.error("Error in best_columns_and_top_18: %s", e)
        gr.Warning(f"Error generating recommendations: {str(e)}")
        return "<p>Error generating recommendations.</p>"

def best_dozens_even_money_and_top_18() -> str:
    try:
        cache_key = "best_dozens_even_money_and_top_18"
        if cache_key in ANALYSIS_CACHE:
            logger.info("Returning cached best dozens, even money, and top 18")
            return ANALYSIS_CACHE[cache_key]
        recommendations = []
        sorted_dozens = sorted(state.dozen_scores.items(), key=lambda x: x[1], reverse=True)
        dozen_hits = [item for item in sorted_dozens if item[1] > 0]
        if dozen_hits:
            recommendations.append("Best Dozen Bets:")
            for i, (name, score) in enumerate(dozen_hits[:2], 1):
                name_safe = html.escape(name)
                recommendations.append(f"{i}. {name_safe}: {score} hits")
        else:
            recommendations.append("No dozen bets have hit yet.")
        sorted_even_money = sorted(state.even_money_scores.items(), key=lambda x: x[1], reverse=True)
        even_money_hits = [item for item in sorted_even_money if item[1] > 0]
        if even_money_hits:
            recommendations.append("Best Even Money Bets:")
            for i, (name, score) in enumerate(even_money_hits[:2], 1):
                name_safe = html.escape(name)
                recommendations.append(f"{i}. {name_safe}: {score} hits")
        else:
            recommendations.append("No even money bets have hit yet.")
        sorted_numbers = sorted(state.scores.items(), key=lambda x: x[1], reverse=True)
        top_numbers = [item for item in sorted_numbers if item[1] > 0]
        if top_numbers:
            recommendations.append("Top 18 Numbers:")
            for i, (num, score) in enumerate(top_numbers[:18], 1):
                num_safe = html.escape(str(num))
                recommendations.append(f"{i}. Number {num_safe}: {score} hits")
        else:
            recommendations.append("No numbers have hit yet.")
        result = "<br>".join(recommendations)
        ANALYSIS_CACHE[cache_key] = result
        logger.info("Generated best dozens, even money, and top 18")
        return result
    except Exception as e:
        logger.error("Error in best_dozens_even_money_and_top_18: %s", e)
        gr.Warning(f"Error generating recommendations: {str(e)}")
        return "<p>Error generating recommendations.</p>"

def best_columns_even_money_and_top_18() -> str:
    try:
        cache_key = "best_columns_even_money_and_top_18"
        if cache_key in ANALYSIS_CACHE:
            logger.info("Returning cached best columns, even money, and top 18")
            return ANALYSIS_CACHE[cache_key]
        recommendations = []
        sorted_columns = sorted(state.column_scores.items(), key=lambda x: x[1], reverse=True)
        column_hits = [item for item in sorted_columns if item[1] > 0]
        if column_hits:
            recommendations.append("Best Column Bets:")
            for i, (name, score) in enumerate(column_hits[:2], 1):
                name_safe = html.escape(name)
                recommendations.append(f"{i}. {name_safe}: {score} hits")
        else:
            recommendations.append("No column bets have hit yet.")
        sorted_even_money = sorted(state.even_money_scores.items(), key=lambda x: x[1], reverse=True)
        even_money_hits = [item for item in sorted_even_money if item[1] > 0]
        if even_money_hits:
            recommendations.append("Best Even Money Bets:")
            for i, (name, score) in enumerate(even_money_hits[:2], 1):
                name_safe = html.escape(name)
                recommendations.append(f"{i}. {name_safe}: {score} hits")
        else:
            recommendations.append("No even money bets have hit yet.")
        sorted_numbers = sorted(state.scores.items(), key=lambda x: x[1], reverse=True)
        top_numbers = [item for item in sorted_numbers if item[1] > 0]
        if top_numbers:
            recommendations.append("Top 18 Numbers:")
            for i, (num, score) in enumerate(top_numbers[:18], 1):
                num_safe = html.escape(str(num))
                recommendations.append(f"{i}. Number {num_safe}: {score} hits")
        else:
            recommendations.append("No numbers have hit yet.")
        result = "<br>".join(recommendations)
        ANALYSIS_CACHE[cache_key] = result
        logger.info("Generated best columns, even money, and top 18")
        return result
    except Exception as e:
        logger.error("Error in best_columns_even_money_and_top_18: %s", e)
        gr.Warning(f"Error generating recommendations: {str(e)}")
        return "<p>Error generating recommendations.</p>"

def fibonacci_strategy() -> str:
    try:
        cache_key = "fibonacci_strategy"
        if cache_key in ANALYSIS_CACHE:
            logger.info("Returning cached Fibonacci strategy")
            return ANALYSIS_CACHE[cache_key]
        recommendations = []
        sorted_dozens = sorted(state.dozen_scores.items(), key=lambda x: x[1], reverse=True)
        dozen_hits = [item for item in sorted_dozens if item[1] > 0]
        if dozen_hits:
            name_safe = html.escape(dozen_hits[0][0])
            recommendations.append(f"Bet on {name_safe} (Fibonacci Progression): {dozen_hits[0][1]} hits")
        else:
            recommendations.append("No dozen hits yet for Fibonacci strategy.")
        sorted_columns = sorted(state.column_scores.items(), key=lambda x: x[1], reverse=True)
        column_hits = [item for item in sorted_columns if item[1] > 0]
        if column_hits:
            name_safe = html.escape(column_hits[0][0])
            recommendations.append(f"Bet on {name_safe} (Fibonacci Progression): {column_hits[0][1]} hits")
        else:
            recommendations.append("No column hits yet for Fibonacci strategy.")
        result = "<br>".join(recommendations)
        ANALYSIS_CACHE[cache_key] = result
        logger.info("Generated Fibonacci strategy")
        return result
    except Exception as e:
        logger.error("Error in fibonacci_strategy: %s", e)
        gr.Warning(f"Error generating Fibonacci strategy: {str(e)}")
        return "<p>Error generating recommendations.</p>"

def best_streets() -> str:
    try:
        cache_key = "best_streets"
        if cache_key in ANALYSIS_CACHE:
            logger.info("Returning cached best streets")
            return ANALYSIS_CACHE[cache_key]
        sorted_streets = sorted(state.street_scores.items(), key=lambda x: x[1], reverse=True)
        recommendations = []
        hits = [item for item in sorted_streets if item[1] > 0]
        if not hits:
            recommendations.append("No street bets have hit yet.")
        else:
            recommendations.append("Best Street Bets:")
            for i, (name, score) in enumerate(hits[:3], 1):
                name_safe = html.escape(name)
                recommendations.append(f"{i}. {name_safe}: {score} hits")
        result = "<br>".join(recommendations)
        ANALYSIS_CACHE[cache_key] = result
        logger.info("Generated best streets")
        return result
    except Exception as e:
        logger.error("Error in best_streets: %s", e)
        gr.Warning(f"Error generating street bets: {str(e)}")
        return "<p>Error generating recommendations.</p>"

def best_double_streets() -> str:
    try:
        cache_key = "best_double_streets"
        if cache_key in ANALYSIS_CACHE:
            logger.info("Returning cached best double streets")
            return ANALYSIS_CACHE[cache_key]
        sorted_six_lines = sorted(state.six_line_scores.items(), key=lambda x: x[1], reverse=True)
        recommendations = []
        hits = [item for item in sorted_six_lines if item[1] > 0]
        if not hits:
            recommendations.append("No double street bets have hit yet.")
        else:
            recommendations.append("Best Double Street Bets:")
            for i, (name, score) in enumerate(hits[:3], 1):
                name_safe = html.escape(name)
                recommendations.append(f"{i}. {name_safe}: {score} hits")
        result = "<br>".join(recommendations)
        ANALYSIS_CACHE[cache_key] = result
        logger.info("Generated best double streets")
        return result
    except Exception as e:
        logger.error("Error in best_double_streets: %s", e)
        gr.Warning(f"Error generating double street bets: {str(e)}")
        return "<p>Error generating recommendations.</p>"

def best_corners() -> str:
    try:
        cache_key = "best_corners"
        if cache_key in ANALYSIS_CACHE:
            logger.info("Returning cached best corners")
            return ANALYSIS_CACHE[cache_key]
        sorted_corners = sorted(state.corner_scores.items(), key=lambda x: x[1], reverse=True)
        recommendations = []
        hits = [item for item in sorted_corners if item[1] > 0]
        if not hits:
            recommendations.append("No corner bets have hit yet.")
        else:
            recommendations.append("Best Corner Bets:")
            for i, (name, score) in enumerate(hits[:3], 1):
                name_safe = html.escape(name)
                recommendations.append(f"{i}. {name_safe}: {score} hits")
        result = "<br>".join(recommendations)
        ANALYSIS_CACHE[cache_key] = result
        logger.info("Generated best corners")
        return result
    except Exception as e:
        logger.error("Error in best_corners: %s", e)
        gr.Warning(f"Error generating corner bets: {str(e)}")
        return "<p>Error generating recommendations.</p>"

def best_splits() -> str:
    try:
        cache_key = "best_splits"
        if cache_key in ANALYSIS_CACHE:
            logger.info("Returning cached best splits")
            return ANALYSIS_CACHE[cache_key]
        sorted_splits = sorted(state.split_scores.items(), key=lambda x: x[1], reverse=True)
        recommendations = []
        hits = [item for item in sorted_splits if item[1] > 0]
        if not hits:
            recommendations.append("No split bets have hit yet.")
        else:
            recommendations.append("Best Split Bets:")
            for i, (name, score) in enumerate(hits[:3], 1):
                name_safe = html.escape(name)
                recommendations.append(f"{i}. {name_safe}: {score} hits")
        result = "<br>".join(recommendations)
        ANALYSIS_CACHE[cache_key] = result
        logger.info("Generated best splits")
        return result
    except Exception as e:
        logger.error("Error in best_splits: %s", e)
        gr.Warning(f"Error generating split bets: {str(e)}")
        return "<p>Error generating recommendations.</p>"

def best_dozens_and_streets() -> str:
    try:
        cache_key = "best_dozens_and_streets"
        if cache_key in ANALYSIS_CACHE:
            logger.info("Returning cached best dozens and streets")
            return ANALYSIS_CACHE[cache_key]
        recommendations = []
        sorted_dozens = sorted(state.dozen_scores.items(), key=lambda x: x[1], reverse=True)
        dozen_hits = [item for item in sorted_dozens if item[1] > 0]
        if dozen_hits:
            recommendations.append("Best Dozen Bets:")
            for i, (name, score) in enumerate(dozen_hits[:2], 1):
                name_safe = html.escape(name)
                recommendations.append(f"{i}. {name_safe}: {score} hits")
        else:
            recommendations.append("No dozen bets have hit yet.")
        sorted_streets = sorted(state.street_scores.items(), key=lambda x: x[1], reverse=True)
        street_hits = [item for item in sorted_streets if item[1] > 0]
        if street_hits:
            recommendations.append("Best Street Bets:")
            for i, (name, score) in enumerate(street_hits[:3], 1):
                name_safe = html.escape(name)
                recommendations.append(f"{i}. {name_safe}: {score} hits")
        else:
            recommendations.append("No street bets have hit yet.")
        result = "<br>".join(recommendations)
        ANALYSIS_CACHE[cache_key] = result
        logger.info("Generated best dozens and streets")
        return result
    except Exception as e:
        logger.error("Error in best_dozens_and_streets: %s", e)
        gr.Warning(f"Error generating recommendations: {str(e)}")
        return "<p>Error generating recommendations.</p>"

def best_columns_and_streets() -> str:
    try:
        cache_key = "best_columns_and_streets"
        if cache_key in ANALYSIS_CACHE:
            logger.info("Returning cached best columns and streets")
            return ANALYSIS_CACHE[cache_key]
        recommendations = []
        sorted_columns = sorted(state.column_scores.items(), key=lambda x: x[1], reverse=True)
        column_hits = [item for item in sorted_columns if item[1] > 0]
        if column_hits:
            recommendations.append("Best Column Bets:")
            for i, (name, score) in enumerate(column_hits[:2], 1):
                name_safe = html.escape(name)
                recommendations.append(f"{i}. {name_safe}: {score} hits")
        else:
            recommendations.append("No column bets have hit yet.")
        sorted_streets = sorted(state.street_scores.items(), key=lambda x: x[1], reverse=True)
        street_hits = [item for item in sorted_streets if item[1] > 0]
        if street_hits:
            recommendations.append("Best Street Bets:")
            for i, (name, score) in enumerate(street_hits[:3], 1):
                name_safe = html.escape(name)
                recommendations.append(f"{i}. {name_safe}: {score} hits")
        else:
            recommendations.append("No street bets have hit yet.")
        result = "<br>".join(recommendations)
        ANALYSIS_CACHE[cache_key] = result
        logger.info("Generated best columns and streets")
        return result
    except Exception as e:
        logger.error("Error in best_columns_and_streets: %s", e)
        gr.Warning(f"Error generating recommendations: {str(e)}")
        return "<p>Error generating recommendations.</p>"

def non_overlapping_double_street_strategy() -> str:
    try:
        cache_key = "non_overlapping_double_street_strategy"
        if cache_key in ANALYSIS_CACHE:
            logger.info("Returning cached non-overlapping double street strategy")
            return ANALYSIS_CACHE[cache_key]
        sorted_six_lines = sorted(state.six_line_scores.items(), key=lambda x: x[1], reverse=True)
        recommendations = []
        hits = [item for item in sorted_six_lines if item[1] > 0]
        if not hits:
            recommendations.append("No double street bets have hit yet.")
        else:
            recommendations.append("Non-Overlapping Double Street Bets:")
            selected = []
            numbers_covered = set()
            for name, score in hits:
                numbers = set(SIX_LINES.get(name, []))
                if not numbers_covered.intersection(numbers):
                    numbers_covered.update(numbers)
                    name_safe = html.escape(name)
                    recommendations.append(f"- {name_safe}: {score} hits")
                    selected.append(name)
                if len(selected) >= 3:
                    break
        result = "<br>".join(recommendations)
        ANALYSIS_CACHE[cache_key] = result
        logger.info("Generated non-overlapping double street strategy")
        return result
    except Exception as e:
        logger.error("Error in non_overlapping_double_street_strategy: %s", e)
        gr.Warning(f"Error generating double street strategy: {str(e)}")
        return "<p>Error generating recommendations.</p>"

def non_overlapping_corner_strategy() -> str:
    try:
        cache_key = "non_overlapping_corner_strategy"
        if cache_key in ANALYSIS_CACHE:
            logger.info("Returning cached non-overlapping corner strategy")
            return ANALYSIS_CACHE[cache_key]
        sorted_corners = sorted(state.corner_scores.items(), key=lambda x: x[1], reverse=True)
        recommendations = []
        hits = [item for item in sorted_corners if item[1] > 0]
        if not hits:
            recommendations.append("No corner bets have hit yet.")
        else:
            recommendations.append("Non-Overlapping Corner Bets:")
            selected = []
            numbers_covered = set()
            for name, score in hits:
                numbers = set(CORNERS.get(name, []))
                if not numbers_covered.intersection(numbers):
                    numbers_covered.update(numbers)
                    name_safe = html.escape(name)
                    recommendations.append(f"- {name_safe}: {score} hits")
                    selected.append(name)
                if len(selected) >= 5:
                    break
        result = "<br>".join(recommendations)
        ANALYSIS_CACHE[cache_key] = result
        logger.info("Generated non-overlapping corner strategy")
        return result
    except Exception as e:
        logger.error("Error in non_overlapping_corner_strategy: %s", e)
        gr.Warning(f"Error generating corner strategy: {str(e)}")
        return "<p>Error generating recommendations.</p>"

def romanowksy_missing_dozen_strategy() -> str:
    try:
        cache_key = "romanowksy_missing_dozen_strategy"
        if cache_key in ANALYSIS_CACHE:
            logger.info("Returning cached Romanowksy missing dozen strategy")
            return ANALYSIS_CACHE[cache_key]
        sorted_dozens = sorted(state.dozen_scores.items(), key=lambda x: x[1])
        recommendations = []
        if not sorted_dozens or sorted_dozens[0][1] == 0:
            recommendations.append("Romanowksy Missing Dozen: No dozen data available.")
        else:
            missing_dozen = sorted_dozens[0][0]
            missing_dozen_safe = html.escape(missing_dozen)
            numbers = [num for num in range(1, 37) if num not in DOZENS.get(missing_dozen, [])]
            recommendations.append(f"Romanowksy Missing Dozen: Bet on numbers outside {missing_dozen_safe}")
            for i, num in enumerate(numbers, 1):
                num_safe = html.escape(str(num))
                score = state.scores.get(num, 0)
                recommendations.append(f"{i}. Number {num_safe}: {score} hits")
        result = "<br>".join(recommendations)
        ANALYSIS_CACHE[cache_key] = result
        logger.info("Generated Romanowksy missing dozen strategy")
        return result
    except Exception as e:
        logger.error("Error in romanowksy_missing_dozen_strategy: %s", e)
        gr.Warning(f"Error generating Romanowksy strategy: {str(e)}")
        return "<p>Error generating recommendations.</p>"

def fibonacci_to_fortune_strategy() -> str:
    try:
        cache_key = "fibonacci_to_fortune_strategy"
        if cache_key in ANALYSIS_CACHE:
            logger.info("Returning cached Fibonacci to Fortune strategy")
            return ANALYSIS_CACHE[cache_key]
        recommendations = []
        sorted_even_money = sorted(state.even_money_scores.items(), key=lambda x: x[1], reverse=True)
        if sorted_even_money and sorted_even_money[0][1] > 0:
            name_safe = html.escape(sorted_even_money[0][0])
            recommendations.append(f"Even Money (Fibonacci): {name_safe}: {sorted_even_money[0][1]} hits")
        sorted_dozens = sorted(state.dozen_scores.items(), key=lambda x: x[1], reverse=True)
        if sorted_dozens and sorted_dozens[0][1] > 0:
            name_safe = html.escape(sorted_dozens[0][0])
            recommendations.append(f"Dozen (Fibonacci): {name_safe}: {sorted_dozens[0][1]} hits")
        sorted_columns = sorted(state.column_scores.items(), key=lambda x: x[1], reverse=True)
        if sorted_columns and sorted_columns[0][1] > 0:
            name_safe = html.escape(sorted_columns[0][0])
            recommendations.append(f"Column (Fibonacci): {name_safe}: {sorted_columns[0][1]} hits")
        sorted_six_lines = sorted(state.six_line_scores.items(), key=lambda x: x[1], reverse=True)
        if sorted_six_lines and sorted_six_lines[0][1] > 0:
            name_safe = html.escape(sorted_six_lines[0][0])
            recommendations.append(f"Double Street (Fibonacci): {name_safe}: {sorted_six_lines[0][1]} hits")
        if not recommendations:
            recommendations.append("Fibonacci to Fortune: No data available.")
        result = "<br>".join(recommendations)
        ANALYSIS_CACHE[cache_key] = result
        logger.info("Generated Fibonacci to Fortune strategy")
        return result
    except Exception as e:
        logger.error("Error in fibonacci_to_fortune_strategy: %s", e)
        gr.Warning(f"Error generating Fibonacci to Fortune strategy: {str(e)}")
        return "<p>Error generating recommendations.</p>"

def three_eight_six_rising_martingale() -> str:
    try:
        cache_key = "three_eight_six_rising_martingale"
        if cache_key in ANALYSIS_CACHE:
            logger.info("Returning cached 3-8-6 Rising Martingale strategy")
            return ANALYSIS_CACHE[cache_key]
        sorted_streets = sorted(state.street_scores.items(), key=lambda x: x[1], reverse=True)
        recommendations = []
        hits = [item for item in sorted_streets if item[1] > 0]
        if not hits:
            recommendations.append("3-8-6 Rising Martingale: No street bets have hit yet.")
        else:
            recommendations.append("3-8-6 Rising Martingale (Street Bets):")
            for i, (name, score) in enumerate(hits[:3], 1):
                name_safe = html.escape(name)
                recommendations.append(f"{i}. {name_safe}: {score} hits")
        result = "<br>".join(recommendations)
        ANALYSIS_CACHE[cache_key] = result
        logger.info("Generated 3-8-6 Rising Martingale strategy")
        return result
    except Exception as e:
        logger.error("Error in three_eight_six_rising_martingale: %s", e)
        gr.Warning(f"Error generating 3-8-6 Rising Martingale strategy: {str(e)}")
        return "<p>Error generating recommendations.</p>"

def one_dozen_one_column_strategy() -> str:
    try:
        cache_key = "one_dozen_one_column_strategy"
        if cache_key in ANALYSIS_CACHE:
            logger.info("Returning cached 1 Dozen + 1 Column strategy")
            return ANALYSIS_CACHE[cache_key]
        recommendations = []
        sorted_dozens = sorted(state.dozen_scores.items(), key=lambda x: x[1], reverse=True)
        if sorted_dozens and sorted_dozens[0][1] > 0:
            name_safe = html.escape(sorted_dozens[0][0])
            recommendations.append(f"Bet on Dozen: {name_safe}: {sorted_dozens[0][1]} hits")
        else:
            recommendations.append("No dozen hits yet.")
        sorted_columns = sorted(state.column_scores.items(), key=lambda x: x[1], reverse=True)
        if sorted_columns and sorted_columns[0][1] > 0:
            name_safe = html.escape(sorted_columns[0][0])
            recommendations.append(f"Bet on Column: {name_safe}: {sorted_columns[0][1]} hits")
        else:
            recommendations.append("No column hits yet.")
        result = "<br>".join(recommendations)
        ANALYSIS_CACHE[cache_key] = result
        logger.info("Generated 1 Dozen + 1 Column strategy")
        return result
    except Exception as e:
        logger.error("Error in one_dozen_one_column_strategy: %s", e)
        gr.Warning(f"Error generating 1 Dozen + 1 Column strategy: {str(e)}")
        return "<p>Error generating recommendations.</p>"

def top_pick_18_numbers_without_neighbours() -> str:
    try:
        cache_key = "top_pick_18_numbers_without_neighbours"
        if cache_key in ANALYSIS_CACHE:
            logger.info("Returning cached top 18 numbers without neighbors")
            return ANALYSIS_CACHE[cache_key]
        sorted_numbers = sorted(state.scores.items(), key=lambda x: x[1], reverse=True)
        recommendations = []
        top_numbers = [item for item in sorted_numbers if item[1] > 0]
        if not top_numbers:
            recommendations.append("Top Pick 18 Numbers: No numbers have hit yet.")
        else:
            recommendations.append("Top Pick 18 Numbers (No Neighbors):")
            for i, (num, score) in enumerate(top_numbers[:18], 1):
                num_safe = html.escape(str(num))
                recommendations.append(f"{i}. Number {num_safe}: {score} hits")
        result = "<br>".join(recommendations)
        ANALYSIS_CACHE[cache_key] = result
        logger.info("Generated top 18 numbers without neighbors")
        return result
    except Exception as e:
        logger.error("Error in top_pick_18_numbers_without_neighbours: %s", e)
        gr.Warning(f"Error generating top 18 numbers: {str(e)}")
        return "<p>Error generating recommendations.</p>"

def top_numbers_with_neighbours_tiered() -> str:
    try:
        cache_key = "top_numbers_with_neighbours_tiered"
        if cache_key in ANALYSIS_CACHE:
            logger.info("Returning cached top numbers with neighbors tiered")
            return ANALYSIS_CACHE[cache_key]
        recommendations = []
        straight_up_df = pd.DataFrame(list(state.scores.items()), columns=["Number", "Score"])
        straight_up_df = straight_up_df[straight_up_df["Score"] > 0].sort_values(by="Score", ascending=False)
        if straight_up_df.empty:
            recommendations.append("<p>Top Numbers with Neighbours (Tiered): No numbers have hit yet.</p>")
            result = "\n".join(recommendations)
            ANALYSIS_CACHE[cache_key] = result
            return result
        table_html = (
            '<table border="1" style="border-collapse: collapse; text-align: center; '
            'font-family: Arial, sans-serif; width: 100%; max-width: 300px;">'
            '<tr><th>Hit</th><th>Left N.</th><th>Right N.</tr>'
        )
        for _, row in straight_up_df.iterrows():
            num = str(row["Number"])
            left, right = current_neighbors.get(row["Number"], ("", ""))
            left_safe = html.escape(str(left)) if left is not None else ""
            right_safe = html.escape(str(right)) if right is not None else ""
            num_safe = html.escape(num)
            table_html += f"<tr><td>{num_safe}</td><td>{left_safe}</td><td>{right_safe}</td></tr>"
        table_html += "</table>"
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
            num_safe = html.escape(str(num))
            score_safe = html.escape(str(score))
            recommendations.append(f"<p>{i}. Number {num_safe} (Score: {score_safe})</p>")
        recommendations.append("<p><strong>Second Tier (Blue):</strong></p>")
        for i, num in enumerate(next_8, 1):
            score = number_scores.get(num, "Neighbor")
            num_safe = html.escape(str(num))
            score_safe = html.escape(str(score))
            recommendations.append(f"<p>{i}. Number {num_safe} (Score: {score_safe})</p>")
        recommendations.append("<p><strong>Third Tier (Green):</strong></p>")
        for i, num in enumerate(last_8, 1):
            score = number_scores.get(num, "Neighbor")
            num_safe = html.escape(str(num))
            score_safe = html.escape(str(score))
            recommendations.append(f"<p>{i}. Number {num_safe} (Score: {score_safe})</p>")
        result = "\n".join(recommendations)
        ANALYSIS_CACHE[cache_key] = result
        logger.info("Generated top numbers with neighbors tiered")
        return result
    except Exception as e:
        logger.error("Error in top_numbers_with_neighbours_tiered: %s", e)
        gr.Warning(f"Error generating tiered neighbors: {str(e)}")
        return "<p>Error generating recommendations.</p>"

def neighbours_of_strong_number(neighbours_count: int, strong_numbers_count: int) -> Tuple[str, Dict[str, str]]:
    try:
        cache_key = f"neighbours_of_strong_number_{neighbours_count}_{strong_numbers_count}"
        if cache_key in ANALYSIS_CACHE:
            logger.info("Returning cached neighbours of strong number")
            return ANALYSIS_CACHE[cache_key]
        recommendations = []
        try:
            neighbours_count = int(neighbours_count)
            strong_numbers_count = int(strong_numbers_count)
            if neighbours_count < 0 or strong_numbers_count < 0:
                raise ValueError("Neighbours count and strong numbers count must be non-negative.")
            if strong_numbers_count == 0:
                raise ValueError("Strong numbers count must be at least 1.")
        except (ValueError, TypeError) as e:
            gr.Warning(f"Invalid input: {str(e)}")
            return (
                f"Error: Invalid input - {html.escape(str(e))}. Please use positive integers.",
                {}
            )
        if not isinstance(current_neighbors, dict):
            gr.Warning("Neighbor data is not properly configured.")
            return (
                "Error: Neighbor data is not properly configured. Contact support.",
                {}
            )
        for key, value in current_neighbors.items():
            if not isinstance(key, int) or not isinstance(value, tuple) or len(value) != 2:
                gr.Warning("Neighbor data is malformed.")
                return (
                    "Error: Neighbor data is malformed. Contact support.",
                    {}
                )
        sorted_numbers = sorted(state.scores.items(), key=lambda x: (-x[1], x[0]))
        numbers_hits = [item for item in sorted_numbers if item[1] > 0]
        if not numbers_hits:
            recommendations.append("Neighbours of Strong Number: No numbers have hit yet.")
            result = ("\n".join(recommendations), {})
            ANALYSIS_CACHE[cache_key] = result
            return result
        strong_numbers_count = min(strong_numbers_count, len(numbers_hits))
        top_numbers = [item[0] for item in numbers_hits[:strong_numbers_count]]
        top_scores = {item[0]: item[1] for item in numbers_hits[:strong_numbers_count]}
        selected_numbers = set(top_numbers)
        neighbors_set = set()
        for strong_number in top_numbers:
            if strong_number not in current_neighbors:
                strong_number_safe = html.escape(str(strong_number))
                recommendations.append(
                    f"Warning: No neighbor data for number {strong_number_safe}. Skipping its neighbors."
                )
                continue
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
        neighbors_set = neighbors_set - selected_numbers
        bet_numbers = list(selected_numbers) + list(neighbors_set)
        even_money_scores, dozen_scores, column_scores = state.calculate_aggregated_scores_for_spins(bet_numbers)
        sorted_even_money = sorted(even_money_scores.items(), key=lambda x: (-x[1], x[0]))
        best_even_money = sorted_even_money[0] if sorted_even_money else ("None", 0)
        best_even_money_name, best_even_money_hits = best_even_money
        even_money_ties = [
            f"{html.escape(name)}: {score}" for name, score in sorted_even_money
            if score == best_even_money_hits and name != best_even_money_name
        ]
        even_money_tie_text = f" (Tied with {', '.join(even_money_ties)})" if even_money_ties else ""
        best_even_money_name_safe = html.escape(best_even_money_name)
        best_dozen = max(dozen_scores.items(), key=lambda x: x[1], default=("None", 0))
        best_dozen_name, best_dozen_hits = best_dozen
        best_column = max(column_scores.items(), key=lambda x: x[1], default=("None", 0))
        best_column_name, best_column_hits = best_column
        suggestion = ""
        winner_category = ""
        best_bet_tie_text = ""
        sorted_dozens = sorted(dozen_scores.items(), key=lambda x: (-x[1], x[0]))
        sorted_columns = sorted(column_scores.items(), key=lambda x: (-x[1], x[0]))
        if best_dozen_hits > best_column_hits:
            suggestion = f"{html.escape(best_dozen_name)}: {best_dozen_hits}"
            winner_category = "dozen"
            dozen_ties = [
                f"{html.escape(name)}: {score}" for name, score in sorted_dozens
                if score == best_dozen_hits and name != best_dozen_name
            ]
            best_bet_tie_text = f" (Tied with {', '.join(dozen_ties)})" if dozen_ties else ""
        elif best_column_hits > best_dozen_hits:
            suggestion = f"{html.escape(best_column_name)}: {best_column_hits}"
            winner_category = "column"
            column_ties = [
                f"{html.escape(name)}: {score}" for name, score in sorted_columns
                if score == best_column_hits and name != best_column_name
            ]
            best_bet_tie_text = f" (Tied with {', '.join(column_ties)})" if column_ties else ""
        else:
            if len(sorted_dozens) >= 2 and sorted_dozens[0][1] == sorted_dozens[1][1] and sorted_dozens[0][1] > 0:
                suggestion = f"{html.escape(sorted_dozens[0][0])} and {html.escape(sorted_dozens[1][0])}: {sorted_dozens[0][1]}"
                winner_category = "dozen"
                dozen_ties = [
                    f"{html.escape(name)}: {score}" for name, score in sorted_dozens[2:]
                    if score == sorted_dozens[0][1]
                ]
                best_bet_tie_text = f" (Tied with {', '.join(dozen_ties)})" if dozen_ties else ""
            elif len(sorted_columns) >= 2 and sorted_columns[0][1] == sorted_columns[1][1] and sorted_columns[0][1] > 0:
                suggestion = f"{html.escape(sorted_columns[0][0])} and {html.escape(sorted_columns[1][0])}: {sorted_columns[0][1]}"
                winner_category = "column"
                column_ties = [
                    f"{html.escape(name)}: {score}" for name, score in sorted_columns[2:]
                    if score == sorted_columns[0][1]
                ]
                best_bet_tie_text = f" (Tied with {', '.join(column_ties)})" if column_ties else ""
            else:
                suggestion = f"{html.escape(best_dozen_name)}: {best_dozen_hits}"
                winner_category = "dozen"
                if best_dozen_hits == best_column_hits and best_column_hits > 0:
                    best_bet_tie_text = f" (Tied with {html.escape(best_column_name)}: {best_column_hits})"
        two_winners_suggestion = ""
        two_winners_tie_text = ""
        if winner_category == "dozen":
            top_two_dozens = sorted_dozens[:2]
            if top_two_dozens[0][1] > 0:
                two_winners_suggestion = (
                    f"Play Two Dozens: {html.escape(top_two_dozens[0][0])} ({top_two_dozens[0][1]}) "
                    f"and {html.escape(top_two_dozens[1][0])} ({top_two_dozens[1][1]})"
                )
                if len(sorted_dozens) > 2:
                    second_score = top_two_dozens[1][1]
                    ties = [
                        f"{html.escape(name)}: {score}" for name, score in sorted_dozens[2:]
                        if score == second_score
                    ]
                    two_winners_tie_text = f" (Tied with {', '.join(ties)})" if ties else ""
            else:
                two_winners_suggestion = "Play Two Dozens: Not enough hits to suggest two dozens."
        elif winner_category == "column":
            top_two_columns = sorted_columns[:2]
            if top_two_columns[0][1] > 0:
                two_winners_suggestion = (
                    f"Play Two Columns: {html.escape(top_two_columns[0][0])} ({top_two_columns[0][1]}) "
                    f"and {html.escape(top_two_columns[1][0])} ({top_two_columns[1][1]})"
                )
                if len(sorted_columns) > 2:
                    second_score = top_two_columns[1][1]
                    ties = [
                        f"{html.escape(name)}: {score}" for name, score in sorted_columns[2:]
                        if score == second_score
                    ]
                    two_winners_tie_text = f" (Tied with {', '.join(ties)})" if ties else ""
            else:
                two_winners_suggestion = "Play Two Columns: Not enough hits to suggest two columns."
        suggestions = {
            "best_even_money": f"{best_even_money_name_safe}: {best_even_money_hits}{even_money_tie_text}",
            "best_bet": f"{suggestion}{best_bet_tie_text}",
            "play_two": f"{two_winners_suggestion}{two_winners_tie_text}"
        }
        recommendations.append("Suggestions:")
        recommendations.append(f"Best Even Money Bet: {best_even_money_name_safe}: {best_even_money_hits}{even_money_tie_text}")
        recommendations.append(f"Best Bet: {suggestion}{best_bet_tie_text}")
        recommendations.append(f"{two_winners_suggestion}{two_winners_tie_text}")
        recommendations.append(f"\nTop {strong_numbers_count} Strongest Numbers and Their Neighbours:")
        recommendations.append("\nStrongest Numbers (Yellow):")
        for i, num in enumerate(sorted(top_numbers), 1):
            score = top_scores[num]
            num_safe = html.escape(str(num))
            recommendations.append(f"{i}. Number {num_safe} (Score: {score})")
        if neighbors_set:
            recommendations.append(f"\nNeighbours ({neighbours_count} Left + {neighbours_count} Right, Cyan):")
            for i, num in enumerate(sorted(list(neighbors_set)), 1):
                num_safe = html.escape(str(num))
                recommendations.append(f"{i}. Number {num_safe}")
        else:
            recommendations.append(f"\nNeighbours ({neighbours_count} Left + {neighbours_count} Right, Cyan): None")
        result = ("\n".join(recommendations), suggestions)
        ANALYSIS_CACHE[cache_key] = result
        logger.info("Generated neighbours of strong number")
        return result
    except Exception as e:
        logger.error("Error in neighbours_of_strong_number: %s", e)
        gr.Warning(f"Error generating neighbors strategy: {str(e)}")
        return (
            f"Error in Neighbours of Strong Number: Unexpected issue - {html.escape(str(e))}.",
            {}
        )

def dozen_tracker(
    num_spins_to_check: int,
    consecutive_hits_threshold: int,
    alert_enabled: bool,
    sequence_length: int,
    follow_up_spins: int,
    sequence_alert_enabled: bool
) -> Tuple[str, str, str]:
    try:
        cache_key = f"dozen_tracker_{num_spins_to_check}_{consecutive_hits_threshold}_{sequence_length}_{follow_up_spins}"
        if cache_key in ANALYSIS_CACHE:
            logger.info("Returning cached dozen tracker output")
            return ANALYSIS_CACHE[cache_key]
        try:
            num_spins_to_check = int(num_spins_to_check)
            consecutive_hits_threshold = int(consecutive_hits_threshold)
            sequence_length = int(sequence_length)
            follow_up_spins = int(follow_up_spins)
            if num_spins_to_check < 1 or consecutive_hits_threshold < 1 or sequence_length < 1 or follow_up_spins < 1:
                gr.Warning("All inputs must be positive integers.")
                return (
                    "Error: Inputs must be at least 1.",
                    "<p>Error: Inputs must be at least 1.</p>",
                    "<p>Error: Inputs must be at least 1.</p>"
                )
        except (ValueError, TypeError) as e:
            gr.Warning(f"Invalid inputs: {str(e)}")
            return (
                f"Error: Invalid inputs - {html.escape(str(e))}.",
                f"<p>Error: Invalid inputs - {html.escape(str(e))}.</p>",
                f"<p>Error: Invalid inputs - {html.escape(str(e))}.</p>"
            )
        recent_spins = state.last_spins[-num_spins_to_check:] if len(state.last_spins) >= num_spins_to_check else state.last_spins
        if not recent_spins:
            result = (
                "Dozen Tracker: No spins recorded yet.",
                "<p>Dozen Tracker: No spins recorded yet.</p>",
                "<p>Dozen Tracker: No spins recorded yet.</p>"
            )
            ANALYSIS_CACHE[cache_key] = result
            return result
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
        recommendations = []
        if alert_enabled:
            last_three_spins = state.last_spins[-3:] if len(state.last_spins) >= 3 else state.last_spins
            if len(last_three_spins) < 3:
                state.last_dozen_alert_index = -1
                state.last_alerted_spins = None
            else:
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
                if (
                    last_three_dozens[0] == last_three_dozens[1] == last_three_dozens[2]
                    and last_three_dozens[0] != "Not in Dozen"
                ):
                    current_dozen = last_three_dozens[0]
                    current_spins_tuple = tuple(last_three_spins)
                    if state.last_alerted_spins != current_spins_tuple:
                        alert_message = f"Alert: {html.escape(current_dozen)} has hit 3 times consecutively!"
                        gr.Warning(alert_message)
                        recommendations.append(alert_message)
                        state.last_dozen_alert_index = len(state.last_spins) - 1
                        state.last_alerted_spins = current_spins_tuple
                else:
                    state.last_dozen_alert_index = -1
                    state.last_alerted_spins = None
        sequence_matches = []
        sequence_follow_ups = []
        sequence_recommendations = []
        if sequence_alert_enabled and len(full_dozen_pattern) >= sequence_length:
            last_x_spins = (
                full_dozen_pattern[-sequence_length:]
                if len(full_dozen_pattern) >= sequence_length
                else full_dozen_pattern
            )
            if len(last_x_spins) < sequence_length:
                pass
            else:
                last_x_pattern = tuple(last_x_spins)
                sequences = []
                for i in range(len(dozen_pattern) - sequence_length + 1):
                    seq = tuple(dozen_pattern[i:i + sequence_length])
                    if i + sequence_length <= len(dozen_pattern) - sequence_length:
                        sequences.append((i, seq))
                for start_idx, seq in sequences:
                    if seq == last_x_pattern and seq not in state.alerted_patterns:
                        sequence_matches.append((start_idx, seq))
                        follow_up_start = start_idx + sequence_length
                        follow_up_end = follow_up_start + follow_up_spins
                        if follow_up_end <= len(dozen_pattern):
                            follow_up = dozen_pattern[follow_up_start:follow_up_end]
                            sequence_follow_ups.append((start_idx, seq, follow_up))
                        state.alerted_patterns.add(seq)
                if sequence_matches:
                    latest_match = max(sequence_matches, key=lambda x: x[0])
                    latest_start_idx, matched_sequence = latest_match
                    first_occurrence = min(
                        (seq for seq in sequences if seq[1] == matched_sequence),
                        key=lambda x: x[0]
                    )[0]
                    follow_up_start = first_occurrence + sequence_length
                    follow_up_end = follow_up_start + follow_up_spins
                    latest_start_idx_full = len(full_dozen_pattern) - sequence_length
                    if follow_up_end <= len(dozen_pattern):
                        follow_up = dozen_pattern[follow_up_start:follow_up_end]
                        matched_sequence_safe = [html.escape(s) for s in matched_sequence]
                        follow_up_safe = [html.escape(s) for s in follow_up]
                        alert_message = (
                            f"Alert: Sequence {', '.join(matched_sequence_safe)} has repeated at spins "
                            f"{latest_start_idx_full + 1} to {latest_start_idx_full + sequence_length}!"
                        )
                        gr.Warning(alert_message)
                        sequence_recommendations.append(alert_message)
                        sequence_recommendations.append(
                            f"Previous follow-up spins (next {follow_up_spins}): {', '.join(follow_up_safe)}"
                        )
                        sequence_recommendations.append("Betting Recommendations (Bet Against Historical Follow-Ups):")
                        all_dozens = ["1st Dozen", "2nd Dozen", "3rd Dozen"]
                        for idx, dozen in enumerate(follow_up):
                            if dozen == "Not in Dozen":
                                sequence_recommendations.append(
                                    f"Spin {idx + 1}: 0 (Not in Dozen) - No bet recommendation."
                                )
                            else:
                                dozens_to_bet = [d for d in all_dozens if d != dozen]
                                dozens_to_bet_safe = [html.escape(d) for d in dozens_to_bet]
                                dozen_safe = html.escape(dozen)
                                sequence_recommendations.append(
                                    f"Spin {idx + 1}: Bet against {dozen_safe} - Bet on {', '.join(dozens_to_bet_safe)}"
                                )
                else:
                    state.alerted_patterns.clear()
        recommendations.append(f"Dozen Tracker (Last {len(recent_spins)} Spins):")
        dozen_pattern_safe = [html.escape(p) for p in dozen_pattern]
        recommendations.append("Dozen History: " + ", ".join(dozen_pattern_safe))
        recommendations.append("\nSummary of Dozen Hits:")
        for name, count in dozen_counts.items():
            name_safe = html.escape(name)
            recommendations.append(f"{name_safe}: {count} hits")
        html_output = (
            f'<h4>Dozen Tracker (Last {len(recent_spins)} Spins):</h4>'
            '<div style="display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 10px;">'
        )
        for dozen in dozen_pattern:
            color = {
                "1st Dozen": "#FF6347",
                "2nd Dozen": "#4682B4",
                "3rd Dozen": "#32CD32",
                "Not in Dozen": "#808080"
            }.get(dozen, "#808080")
            dozen_safe = html.escape(dozen)
            html_output += (
                f'<span style="background-color: {color}; color: white; padding: 2px 5px; '
                f'border-radius: 3px; display: inline-block; font-size: 12px;">{dozen_safe}</span>'
            )
        html_output += '</div>'
        if alert_enabled and "Alert:" in "\n".join(recommendations):
            alert_message = next((line for line in recommendations if line.startswith("Alert:")), "")
            alert_message_safe = html.escape(alert_message)
            html_output += f'<p style="color: red; font-weight: bold;">{alert_message_safe}</p>'
        html_output += '<h4>Summary of Dozen Hits:</h4><ul style="list-style-type: none; padding-left: 0;">'
        for name, count in dozen_counts.items():
            name_safe = html.escape(name)
            html_output += f'<li>{name_safe}: {count} hits</li>'
        html_output += '</ul>'
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
                display_start_idx = len(full_dozen_pattern) - sequence_length
                seq_safe = [html.escape(s) for s in seq]
                sequence_html_output += (
                    f"<li>Match found at spins {display_start_idx + 1} to "
                    f"{display_start_idx + sequence_length}: {', '.join(seq_safe)}</li>"
                )
            sequence_html_output += "</ul>"
            if sequence_recommendations:
                sequence_html_output += "<h4>Latest Match Details:</h4><ul style='list-style-type: none; padding-left: 0;'>"
                for rec in sequence_recommendations:
                    rec_safe = html.escape(rec)
                    if "Alert:" in rec:
                        sequence_html_output += f"<li style='color: red; font-weight: bold;'>{rec_safe}</li>"
                    else:
                        sequence_html_output += f"<li>{rec_safe}</li>"
                sequence_html_output += "</ul>"
        result = ("\n".join(recommendations), html_output, sequence_html_output)
        ANALYSIS_CACHE[cache_key] = result
        logger.info("Generated dozen tracker output")
        return result
    except Exception as e:
        logger.error("Error in dozen_tracker: %s", e)
        gr.Warning(f"Error in dozen tracker: {str(e)}")
        return (
            f"Error: {html.escape(str(e))}.",
            f"<p>Error: {html.escape(str(e))}.</p>",
            f"<p>Error: {html.escape(str(e))}.</p>"
        )

def even_money_tracker(
    spins_to_check: int,
    consecutive_hits_threshold: int,
    alert_enabled: bool,
    combination_mode: str,
    track_red: bool,
    track_black: bool,
    track_even: bool,
    track_odd: bool,
    track_low: bool,
    track_high: bool,
    identical_traits_enabled: bool,
    consecutive_identical_count: int
) -> Tuple[str, str]:
    try:
        cache_key = (
            f"even_money_tracker_{spins_to_check}_{consecutive_hits_threshold}_"
            f"{combination_mode}_{identical_traits_enabled}_{consecutive_identical_count}"
        )
        if cache_key in ANALYSIS_CACHE:
            logger.info("Returning cached even money tracker output")
            return ANALYSIS_CACHE[cache_key]
        spins_to_check = int(spins_to_check) if spins_to_check and str(spins_to_check).strip().isdigit() else 5
        consecutive_hits_threshold = int(consecutive_hits_threshold) if consecutive_hits_threshold and str(consecutive_hits_threshold).strip().isdigit() else 3
        consecutive_identical_count = int(consecutive_identical_count) if consecutive_identical_count and str(consecutive_identical_count).strip().isdigit() else 2
        if spins_to_check < 1 or consecutive_hits_threshold < 1 or consecutive_identical_count < 1:
            gr.Warning("Inputs must be at least 1.")
            return (
                "Error: Inputs must be at least 1.",
                "<div class='even-money-tracker-container'><p>Error: Inputs must be at least 1.</p></div>"
            )
        recent_spins = state.last_spins[-spins_to_check:] if len(state.last_spins) >= spins_to_check else state.last_spins
        if not recent_spins:
            result = (
                "Even Money Tracker: No spins recorded yet.",
                "<div class='even-money-tracker-container'><p>Even Money Tracker: No spins recorded yet.</p></div>"
            )
            ANALYSIS_CACHE[cache_key] = result
            return result
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
        if not categories_to_track:
            categories_to_track = ["Red", "Black", "Even", "Odd", "Low", "High"]
        pattern = []
        category_counts = {name: 0 for name in EVEN_MONEY.keys()}
        trait_combinations = []
        for spin in recent_spins:
            spin_value = int(spin)
            spin_categories = []
            for name, numbers in EVEN_MONEY.items():
                if spin_value in numbers:
                    spin_categories.append(name)
                    category_counts[name] += 1
            if combination_mode == "And":
                if all(cat in spin_categories for cat in categories_to_track):
                    pattern.append("Hit")
                else:
                    pattern.append("Miss")
            else:
                if any(cat in spin_categories for cat in categories_to_track):
                    pattern.append("Hit")
                else:
                    pattern.append("Miss")
            color = "Red" if "Red" in spin_categories else ("Black" if "Black" in spin_categories else "None")
            parity = "Even" if "Even" in spin_categories else ("Odd" if "Odd" in spin_categories else "None")
            range_ = "Low" if "Low" in spin_categories else ("High" if "High" in spin_categories else "None")
            trait_combination = f"{color}, {parity}, {range_}"
            trait_combinations.append(trait_combination)
        current_streak = 1 if pattern and pattern[0] == "Hit" else 0
        max_streak = current_streak
        max_streak_start = 0
        for i in range(1, len(pattern)):
            if pattern[i] == "Hit" and pattern[i-1] == "Hit":
                current_streak += 1
                if current_streak > max_streak:
                    max_streak = current_streak
                    max_streak_start = i - current_streak + 1
            else:
                current_streak = 1 if pattern[i] == "Hit" else 0
        identical_recommendations = []
        identical_html_output = ""
        betting_recommendation = None
        if identical_traits_enabled:
            identical_streak = 1
            identical_streak_start = 0
            identical_matches = []
            for i in range(1, len(trait_combinations)):
                if trait_combinations[i] == trait_combinations[i-1] and trait_combinations[i] != "None, None, None":
                    identical_streak += 1
                    if identical_streak >= consecutive_identical_count:
                        identical_matches.append((i - identical_streak + 1, trait_combinations[i]))
                else:
                    identical_streak = 1
                    identical_streak_start = i
            if identical_matches:
                latest_match = max(identical_matches, key=lambda x: x[0])
                start_idx, matched_traits = latest_match
                matched_traits_safe = html.escape(matched_traits)
                alert_message = (
                    f"Alert: {matched_traits_safe} has appeared {consecutive_identical_count} times "
                    f"consecutively starting at spin {start_idx + 1}!"
                )
                gr.Warning(alert_message)
                identical_recommendations.append(alert_message)
                traits = matched_traits.split(", ")
                color, parity, range_ = traits
                opposite_traits = []
                if color == "Red":
                    opposite_traits.append("Black")
                elif color == "Black":
                    opposite_traits.append("Red")
                if parity == "Even":
                    opposite_traits.append("Odd")
                elif parity == "Odd":
                    opposite_traits.append("Even")
                if range_ == "Low":
                    opposite_traits.append("High")
                elif range_ == "High":
                    opposite_traits.append("Low")
                opposite_traits_safe = [html.escape(t) for t in opposite_traits]
                betting_recommendation = f"Consider betting on: {', '.join(opposite_traits_safe)}"
                identical_recommendations.append(betting_recommendation)
                identical_html_output = (
                    f"<p style='color: red; font-weight: bold;'>{alert_message}</p>"
                    f"<p>{betting_recommendation}</p>"
                )
            else:
                identical_html_output = "<p>No identical trait sequences found yet.</p>"
        recommendations = []
        recommendations.append(f"Even Money Tracker (Last {len(recent_spins)} Spins):")
        categories_to_track_safe = [html.escape(cat) for cat in categories_to_track]
        recommendations.append(f"Tracking: {', '.join(categories_to_track_safe)} (Mode: {combination_mode})")
        pattern_safe = [html.escape(p) for p in pattern]
        recommendations.append("Pattern: " + ", ".join(pattern_safe))
        recommendations.append(f"Max Streak: {max_streak} hits starting at spin {max_streak_start + 1}")
        recommendations.extend(identical_recommendations)
        recommendations.append("\nCategory Hits:")
        for name, count in category_counts.items():
            name_safe = html.escape(name)
            recommendations.append(f"{name_safe}: {count} hits")
        html_output = (
            f"<h4>Even Money Tracker (Last {len(recent_spins)} Spins):</h4>"
            f"<p>Tracking: {', '.join(categories_to_track_safe)} (Mode: {combination_mode})</p>"
            '<div style="display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 10px;">'
        )
        for p in pattern:
            color = "green" if p == "Hit" else "red"
            p_safe = html.escape(p)
            html_output += (
                f'<span style="background-color: {color}; color: white; padding: 2px 5px; '
                f'border-radius: 3px; display: inline-block; font-size: 12px;">{p_safe}</span>'
            )
        html_output += '</div>'
        html_output += f"<p>Max Streak: {max_streak} hits starting at spin {max_streak_start + 1}</p>"
        html_output += identical_html_output
        html_output += '<h4>Category Hits:</h4><ul style="list-style-type: none; padding-left: 0;">'
        for name, count in category_counts.items():
            name_safe = html.escape(name)
            html_output += f'<li>{name_safe}: {count} hits</li>'
        html_output += '</ul>'
        result = ("\n".join(recommendations), html_output)
        ANALYSIS_CACHE[cache_key] = result
        logger.info("Generated even money tracker output")
        return result
    except Exception as e:
        logger.error("Error in even_money_tracker: %s", e)
        gr.Warning(f"Error in even money tracker: {str(e)}")
        return (
            f"Error: {html.escape(str(e))}.",
            f"<div class='even-money-tracker-container'><p>Error: {html.escape(str(e))}.</p></div>"
        )

def validate_hot_cold_numbers() -> str:
    try:
        cache_key = "validate_hot_cold_numbers"
        if cache_key in ANALYSIS_CACHE:
            logger.info("Returning cached hot/cold numbers")
            return ANALYSIS_CACHE[cache_key]
        if not state.use_casino_winners or not state.casino_data.get("hot_numbers") or not state.casino_data.get("cold_numbers"):
            return "<p>No casino data available for hot/cold numbers.</p>"
        hot_numbers = state.casino_data["hot_numbers"]
        cold_numbers = state.casino_data["cold_numbers"]
        recommendations = []
        recommendations.append("<h4>Hot Numbers (🔥):</h4>")
        if hot_numbers:
            for num, hits in sorted(hot_numbers.items(), key=lambda x: x[1], reverse=True):
                num_safe = html.escape(str(num))
                recommendations.append(f"Number {num_safe}: {hits} hits")
        else:
            recommendations.append("No hot numbers available.")
        recommendations.append("<h4>Cold Numbers (❄️):</h4>")
        if cold_numbers:
            for num, hits in sorted(cold_numbers.items(), key=lambda x: x[1]):
                num_safe = html.escape(str(num))
                recommendations.append(f"Number {num_safe}: {hits} hits")
        else:
            recommendations.append("No cold numbers available.")
        result = "<br>".join(recommendations)
        ANALYSIS_CACHE[cache_key] = result
        logger.info("Generated hot/cold numbers")
        return result
    except Exception as e:
        logger.error("Error in validate_hot_cold_numbers: %s", e)
        gr.Warning(f"Error generating hot/cold numbers: {str(e)}")
        return "<p>Error generating hot/cold numbers.</p>"

def play_specific_numbers(numbers: str) -> Tuple[str, float, float, float, str, str, str]:
    try:
        if not numbers or not numbers.strip():
            gr.Warning("No numbers provided to bet on.")
            return (
                "Error: No numbers provided.",
                state.bankroll,
                state.current_bet,
                state.next_bet,
                state.message,
                state.status,
                state.status_color
            )
        bet_numbers = [int(n.strip()) for n in numbers.split(",") if n.strip().isdigit() and 0 <= int(n.strip()) <= 36]
        if not bet_numbers:
            gr.Warning("Invalid numbers provided. Must be between 0 and 36.")
            return (
                "Error: Invalid numbers provided.",
                state.bankroll,
                state.current_bet,
                state.next_bet,
                state.message,
                state.status,
                state.status_color
            )
        if not state.last_spins:
            gr.Warning("No spins recorded to evaluate bet.")
            return (
                "Error: No spins recorded.",
                state.bankroll,
                state.current_bet,
                state.next_bet,
                state.message,
                state.status,
                state.status_color
            )
        last_spin = int(state.last_spins[-1])
        won = last_spin in bet_numbers
        bankroll, current_bet, next_bet, message, status, status_color = state.update_progression(won)
        analysis = f"Bet on numbers: {', '.join(map(str, bet_numbers))}\n"
        analysis += f"Last spin: {last_spin}\n"
        analysis += f"Result: {'Win' if won else 'Loss'}\n"
        analysis += f"Bankroll: {bankroll:.2f}, Next Bet: {next_bet:.2f}"
        logger.info("Played specific numbers: won=%s, bankroll=%.2f", won, bankroll)
        return (analysis, bankroll, current_bet, next_bet, message, status, status_color)
    except Exception as e:
        logger.error("Error in play_specific_numbers: %s", e)
        gr.Warning(f"Error playing specific numbers: {str(e)}")
        return (
            f"Error: {str(e)}",
            state.bankroll,
            state.current_bet,
            state.next_bet,
            state.message,
            state.status,
            state.status_color
        )

def summarize_spin_traits() -> str:
    try:
        cache_key = "summarize_spin_traits"
        if cache_key in ANALYSIS_CACHE:
            logger.info("Returning cached spin traits")
            return ANALYSIS_CACHE[cache_key]
        if not state.last_spins:
            result = "<p>No spins recorded yet.</p>"
            ANALYSIS_CACHE[cache_key] = result
            return result
        last_spin = int(state.last_spins[-1])
        traits = []
        for name, numbers in EVEN_MONEY.items():
            if last_spin in numbers:
                traits.append(name)
        color = colors.get(str(last_spin), "unknown")
        traits.append(f"Color: {color.capitalize()}")
        traits_safe = [html.escape(t) for t in traits]
        result = f"<h4>Last Spin Traits (Spin: {last_spin}):</h4><p>{', '.join(traits_safe)}</p>"
        ANALYSIS_CACHE[cache_key] = result
        logger.info("Generated spin traits for spin %d", last_spin)
        return result
    except Exception as e:
        logger.error("Error in summarize_spin_traits: %s", e)
        gr.Warning(f"Error summarizing spin traits: {str(e)}")
        return "<p>Error summarizing spin traits.</p>"

def create_dynamic_table() -> str:
    try:
        cache_key = "create_dynamic_table"
        if cache_key in ANALYSIS_CACHE:
            logger.info("Returning cached dynamic table")
            return ANALYSIS_CACHE[cache_key]
        data = []
        for num in range(37):
            row = {"Number": num, "Hits": state.scores.get(num, 0)}
            categories = BETTING_MAPPINGS.get(num, {})
            row["Even Money"] = ", ".join(categories.get("even_money", []))
            row["Dozens"] = ", ".join(categories.get("dozens", []))
            row["Columns"] = ", ".join(categories.get("columns", []))
            data.append(row)
        df = pd.DataFrame(data)
        table_html = (
            '<table border="1" style="border-collapse: collapse; width: 100%; max-width: 600px; '
            'font-family: Arial, sans-serif; text-align: center;">'
            '<tr><th>Number</th><th>Hits</th><th>Even Money</th><th>Dozens</th><th>Columns</th></tr>'
        )
        for _, row in df.iterrows():
            num_safe = html.escape(str(row["Number"]))
            hits_safe = html.escape(str(row["Hits"]))
            even_money_safe = html.escape(row["Even Money"])
            dozens_safe = html.escape(row["Dozens"])
            columns_safe = html.escape(row["Columns"])
            table_html += (
                f"<tr><td>{num_safe}</td><td>{hits_safe}</td><td>{even_money_safe}</td>"
                f"<td>{dozens_safe}</td><td>{columns_safe}</td></tr>"
            )
        table_html += "</table>"
        result = f"<h4>Spin Statistics Table</h4>{table_html}"
        ANALYSIS_CACHE[cache_key] = result
        logger.info("Generated dynamic table")
        return result
    except Exception as e:
        logger.error("Error in create_dynamic_table: %s", e)
        gr.Warning(f"Error generating dynamic table: {str(e)}")
        return "<p>Error generating dynamic table.</p>"

css = """
body { font-family: Arial, sans-serif; background-color: #f0f0f0; }
.roulette-button.green { background-color: #2e7d32; }
.roulette-button.red { background-color: #d32f2f; }
.roulette-button.black { background-color: #424242; }
.fade-in { animation: fadeIn 0.5s; }
.flip { animation: flip 0.5s; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes flip { from { transform: rotateY(0deg); } to { transform: rotateY(360deg); } }
.sides-of-zero-container { max-width: 100%; overflow-x: auto; }
.even-money-tracker-container { max-width: 100%; overflow-x: auto; }
@media (max-width: 600px) {
    table { font-size: 12px; }
    .roulette-button { font-size: 12px; padding: 3px 6px; }
    .sides-of-zero-container svg { max-width: 200px; }
}
"""

with gr.Blocks(css=css, theme=gr.themes.Soft()) as demo:
    gr.Markdown("# Roulette Spin Analyzer")
    with gr.Row():
        with gr.Column(scale=1):
            spin_input = gr.Textbox(label="Enter Spin (0-36)", placeholder="e.g., 23")
            add_spin_button = gr.Button("Add Spin")
            spins_textbox = gr.Textbox(label="All Spins (Comma-separated)", placeholder="e.g., 23, 12, 0")
            validate_spins_button = gr.Button("Validate Spins")
            random_spins_input = gr.Textbox(label="Number of Random Spins", placeholder="e.g., 5")
            generate_random_button = gr.Button("Generate Random Spins")
            clear_spins_button = gr.Button("Clear Spins")
            undo_spin_button = gr.Button("Undo Last Spin")
            last_spin_count = gr.Slider(label="Number of Spins to Display", minimum=1, maximum=100, value=36, step=1)
        with gr.Column(scale=2):
            last_spins_output = gr.HTML(label="Last Spins")
            spin_counter_output = gr.HTML(label="Spin Counter")
            sides_of_zero_output = gr.HTML(label="Sides of Zero Display")
            analysis_output = gr.Textbox(label="Analysis Output", lines=5)
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("## Betting Configuration")
            bankroll_input = gr.Number(label="Bankroll", value=1000)
            base_unit_input = gr.Number(label="Base Unit", value=10)
            stop_loss_input = gr.Number(label="Stop Loss", value=-500)
            stop_win_input = gr.Number(label="Stop Win", value=200)
            target_profit_input = gr.Number(label="Target Profit", value=10)
            bet_type_input = gr.Dropdown(
                label="Bet Type",
                choices=["Even Money", "Dozens", "Columns", "Straight Bets"],
                value="Even Money"
            )
            progression_input = gr.Dropdown(
                label="Progression",
                choices=[
                    "Martingale", "Fibonacci", "Triple Martingale", "Oscar’s Grind",
                    "Labouchere", "Ladder", "D’Alembert", "Double After a Win",
                    "+1 Win / -1 Loss", "+2 Win / -1 Loss"
                ],
                value="Martingale"
            )
            labouchere_sequence_input = gr.Textbox(
                label="Labouchere Sequence (Comma-separated)",
                placeholder="e.g., 1, 2, 3"
            )
            specific_numbers_input = gr.Textbox(
                label="Specific Numbers to Bet (Comma-separated)",
                placeholder="e.g., 1, 12, 23"
            )
            play_numbers_button = gr.Button("Play Specific Numbers")
            reset_progression_button = gr.Button("Reset Progression")
        with gr.Column(scale=2):
            bankroll_output = gr.Number(label="Current Bankroll")
            current_bet_output = gr.Number(label="Current Bet")
            next_bet_output = gr.Number(label="Next Bet")
            message_output = gr.Textbox(label="Message", lines=2)
            status_output = gr.Textbox(label="Status", lines=1)
    with gr.Row():
        with gr.Column():
            gr.Markdown("## Strategy Recommendations")
            strategy_tabs = gr.Tabs()
            with strategy_tabs:
                with gr.Tab("Even Money"):
                    even_money_output = gr.HTML(label="Best Even Money Bets")
                with gr.Tab("Hot Bets"):
                    hot_bets_output = gr.HTML(label="Hot Bet Strategy")
                with gr.Tab("Cold Bets"):
                    cold_bets_output = gr.HTML(label="Cold Bet Strategy")
                with gr.Tab("Dozens"):
                    dozens_output = gr.HTML(label="Best Dozen Bets")
                with gr.Tab("Columns"):
                    columns_output = gr.HTML(label="Best Column Bets")
                with gr.Tab("Even Money + Top 18"):
                    even_money_top_18_output = gr.HTML(label="Best Even Money + Top 18")
                with gr.Tab("Dozens + Top 18"):
                    dozens_top_18_output = gr.HTML(label="Best Dozens + Top 18")
                with gr.Tab("Columns + Top 18"):
                    columns_top_18_output = gr.HTML(label="Best Columns + Top 18")
                with gr.Tab("Dozens + Even Money + Top 18"):
                    dozens_even_money_top_18_output = gr.HTML(label="Best Dozens + Even Money + Top 18")
                with gr.Tab("Columns + Even Money + Top 18"):
                    columns_even_money_top_18_output = gr.HTML(label="Best Columns + Even Money + Top 18")
                with gr.Tab("Fibonacci"):
                    fibonacci_output = gr.HTML(label="Fibonacci Strategy")
                with gr.Tab("Streets"):
                    streets_output = gr.HTML(label="Best Street Bets")
                with gr.Tab("Double Streets"):
                    double_streets_output = gr.HTML(label="Best Double Street Bets")
                with gr.Tab("Corners"):
                    corners_output = gr.HTML(label="Best Corner Bets")
                with gr.Tab("Splits"):
                    splits_output = gr.HTML(label="Best Split Bets")
                with gr.Tab("Dozens + Streets"):
                    dozens_streets_output = gr.HTML(label="Best Dozens + Streets")
                with gr.Tab("Columns + Streets"):
                    columns_streets_output = gr.HTML(label="Best Columns + Streets")
                with gr.Tab("Non-Overlapping Double Streets"):
                    non_overlapping_double_streets_output = gr.HTML(label="Non-Overlapping Double Streets")
                with gr.Tab("Non-Overlapping Corners"):
                    non_overlapping_corners_output = gr.HTML(label="Non-Overlapping Corners")
                with gr.Tab("Romanowksy Missing Dozen"):
                    romanowksy_output = gr.HTML(label="Romanowksy Missing Dozen")
                with gr.Tab("Fibonacci to Fortune"):
                    fibonacci_fortune_output = gr.HTML(label="Fibonacci to Fortune")
                with gr.Tab("3-8-6 Rising Martingale"):
                    three_eight_six_output = gr.HTML(label="3-8-6 Rising Martingale")
                with gr.Tab("One Dozen + One Column"):
                    one_dozen_one_column_output = gr.HTML(label="One Dozen + One Column")
                with gr.Tab("Top 18 Numbers"):
                    top_18_numbers_output = gr.HTML(label="Top 18 Numbers Without Neighbors")
                with gr.Tab("Top Numbers with Neighbors"):
                    top_numbers_neighbors_output = gr.HTML(label="Top Numbers with Neighbors Tiered")
                with gr.Tab("Neighbors of Strong Number"):
                    neighbors_count_input = gr.Slider(label="Neighbors Count", minimum=1, maximum=5, value=2, step=1)
                    strong_numbers_count_input = gr.Slider(label="Strong Numbers Count", minimum=1, maximum=10, value=5, step=1)
                    neighbors_strong_output = gr.HTML(label="Neighbors of Strong Number")
                    neighbors_strong_button = gr.Button("Generate Neighbors Strategy")
    with gr.Row():
        with gr.Column():
            gr.Markdown("## Trackers")
            with gr.Tabs():
                with gr.Tab("Dozen Tracker"):
                    dozen_spins_input = gr.Slider(label="Spins to Check", minimum=1, maximum=100, value=10, step=1)
                    dozen_consecutive_input = gr.Slider(label="Consecutive Hits Threshold", minimum=1, maximum=10, value=3, step=1)
                    dozen_alert_enabled = gr.Checkbox(label="Enable Consecutive Hits Alert", value=True)
                    dozen_sequence_length = gr.Slider(label="Sequence Length", minimum=1, maximum=10, value=3, step=1)
                    dozen_follow_up_spins = gr.Slider(label="Follow-Up Spins", minimum=1, maximum=10, value=3, step=1)
                    dozen_sequence_alert_enabled = gr.Checkbox(label="Enable Sequence Matching Alert", value=True)
                    dozen_tracker_button = gr.Button("Run Dozen Tracker")
                    dozen_tracker_text_output = gr.Textbox(label="Dozen Tracker Summary", lines=5)
                    dozen_tracker_html_output = gr.HTML(label="Dozen Tracker Visualization")
                    dozen_sequence_html_output = gr.HTML(label="Sequence Matching Results")
                with gr.Tab("Even Money Tracker"):
                    even_money_spins_input = gr.Slider(label="Spins to Check", minimum=1, maximum=100, value=10, step=1)
                    even_money_consecutive_input = gr.Slider(label="Consecutive Hits Threshold", minimum=1, maximum=10, value=3, step=1)
                    even_money_alert_enabled = gr.Checkbox(label="Enable Alerts", value=True)
                    even_money_combination_mode = gr.Radio(label="Combination Mode", choices=["And", "Or"], value="Or")
                    even_money_track_red = gr.Checkbox(label="Track Red", value=True)
                    even_money_track_black = gr.Checkbox(label="Track Black", value=True)
                    even_money_track_even = gr.Checkbox(label="Track Even", value=True)
                    even_money_track_odd = gr.Checkbox(label="Track Odd", value=True)
                    even_money_track_low = gr.Checkbox(label="Track Low", value=True)
                    even_money_track_high = gr.Checkbox(label="Track High", value=True)
                    even_money_identical_traits = gr.Checkbox(label="Track Identical Traits", value=True)
                    even_money_identical_count = gr.Slider(label="Consecutive Identical Traits", minimum=1, maximum=10, value=2, step=1)
                    even_money_tracker_button = gr.Button("Run Even Money Tracker")
                    even_money_tracker_text_output = gr.Textbox(label="Even Money Tracker Summary", lines=5)
                    even_money_tracker_html_output = gr.HTML(label="Even Money Tracker Visualization")
    with gr.Row():
        with gr.Column():
            gr.Markdown("## Additional Analysis")
            hot_cold_output = gr.HTML(label="Hot/Cold Numbers")
            spin_traits_output = gr.HTML(label="Last Spin Traits")
            dynamic_table_output = gr.HTML(label="Spin Statistics Table")
    add_spin_button.click(
        fn=add_spin,
        inputs=[spin_input, spins_textbox, last_spin_count],
        outputs=[spins_textbox, spins_textbox, last_spins_output, spin_counter_output, sides_of_zero_output]
    )
    validate_spins_button.click(
        fn=validate_spins_input,
        inputs=[spins_textbox],
        outputs=[spins_textbox, last_spins_output]
    )
    generate_random_button.click(
        fn=generate_random_spins,
        inputs=[random_spins_input, spins_textbox, last_spin_count],
        outputs=[spins_textbox, spins_textbox, analysis_output, spin_counter_output, sides_of_zero_output]
    )
    clear_spins_button.click(
        fn=clear_spins,
        inputs=[],
        outputs=[spins_textbox, spins_textbox, analysis_output, last_spins_output, spin_counter_output, sides_of_zero_output]
    )
    undo_spin_button.click(
        fn=undo_last_spin,
        inputs=[],
        outputs=[spins_textbox, spins_textbox, last_spins_output, spin_counter_output, sides_of_zero_output]
    )
    play_numbers_button.click(
        fn=play_specific_numbers,
        inputs=[specific_numbers_input],
        outputs=[analysis_output, bankroll_output, current_bet_output, next_bet_output, message_output, status_output, status_output]
    )
    reset_progression_button.click(
        fn=state.reset_progression,
        inputs=[],
        outputs=[bankroll_output, current_bet_output, next_bet_output, message_output, status_output]
    )
    neighbors_strong_button.click(
        fn=neighbours_of_strong_number,
        inputs=[neighbors_count_input, strong_numbers_count_input],
        outputs=[neighbors_strong_output]
    )
    dozen_tracker_button.click(
        fn=dozen_tracker,
        inputs=[
            dozen_spins_input,
            dozen_consecutive_input,
            dozen_alert_enabled,
            dozen_sequence_length,
            dozen_follow_up_spins,
            dozen_sequence_alert_enabled
        ],
        outputs=[dozen_tracker_text_output, dozen_tracker_html_output, dozen_sequence_html_output]
    )
    even_money_tracker_button.click(
        fn=even_money_tracker,
        inputs=[
            even_money_spins_input,
            even_money_consecutive_input,
            even_money_alert_enabled,
            even_money_combination_mode,
            even_money_track_red,
            even_money_track_black,
            even_money_track_even,
            even_money_track_odd,
            even_money_track_low,
            even_money_track_high,
            even_money_identical_traits,
            even_money_identical_count
        ],
        outputs=[even_money_tracker_text_output, even_money_tracker_html_output]
    )
    spins_textbox.change(
        fn=lambda: [
            best_even_money_bets(),
            hot_bet_strategy(),
            cold_bet_strategy(),
            best_dozens(),
            best_columns(),
            best_even_money_and_top_18(),
            best_dozens_and_top_18(),
            best_columns_and_top_18(),
            best_dozens_even_money_and_top_18(),
            best_columns_even_money_and_top_18(),
            fibonacci_strategy(),
            best_streets(),
            best_double_streets(),
            best_corners(),
            best_splits(),
            best_dozens_and_streets(),
            best_columns_and_streets(),
            non_overlapping_double_street_strategy(),
            non_overlapping_corner_strategy(),
            romanowksy_missing_dozen_strategy(),
            fibonacci_to_fortune_strategy(),
            three_eight_six_rising_martingale(),
            one_dozen_one_column_strategy(),
            top_pick_18_numbers_without_neighbours(),
            top_numbers_with_neighbours_tiered(),
            validate_hot_cold_numbers(),
            summarize_spin_traits(),
            create_dynamic_table()
        ],
        inputs=[],
        outputs=[
            even_money_output,
            hot_bets_output,
            cold_bets_output,
            dozens_output,
            columns_output,
            even_money_top_18_output,
            dozens_top_18_output,
            columns_top_18_output,
            dozens_even_money_top_18_output,
            columns_even_money_top_18_output,
            fibonacci_output,
            streets_output,
            double_streets_output,
            corners_output,
            splits_output,
            dozens_streets_output,
            columns_streets_output,
            non_overlapping_double_streets_output,
            non_overlapping_corners_output,
            romanowksy_output,
            fibonacci_fortune_output,
            three_eight_six_output,
            one_dozen_one_column_output,
            top_18_numbers_output,
            top_numbers_neighbors_output,
            hot_cold_output,
            spin_traits_output,
            dynamic_table_output
        ]
    )

if __name__ == "__main__":
    try:
        initialize_betting_mappings()
        validation_errors = validate_roulette_data()
        if validation_errors:
            raise ValueError(f"Validation errors: {validation_errors}")
        logger.info("Starting Gradio interface")
        demo.launch()
    except Exception as e:
        logger.error("Failed to launch Gradio interface: %s", e)
        raise
```
        
