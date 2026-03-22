import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import csv
import os
import json
import math
from datetime import datetime
import sys
import threading
import time

# Create logs directory if it doesn't exist
LOGS_DIR = "logs"
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

# Create timestamped log file
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE = os.path.join(LOGS_DIR, f"pc_builder_debug_{timestamp}.log")

# Configuration file for live updates
CONFIG_FILE = "column_config.json"
DISPLAY_NAMES_FILE = "column_display_names.json"

# Global reference for app instance
_app_instance = None

def get_app_instance():
    """Get the current app instance"""
    return _app_instance

def set_app_instance(instance):
    """Set the app instance for configuration watcher"""
    global _app_instance
    _app_instance = instance

def load_display_names():
    """Load column display names from file"""
    if os.path.exists(DISPLAY_NAMES_FILE):
        try:
            with open(DISPLAY_NAMES_FILE, 'r') as f:
                config = json.load(f)
                app = get_app_instance()
                if app:
                    # Update display names with loaded values
                    for col_name, display_name in config.items():
                        app.column_display_names[col_name] = display_name
                logger.info(f"Loaded display names from {DISPLAY_NAMES_FILE}")
                return True
        except Exception as e:
            logger.error(f"Error loading display names: {e}")
    return False

def save_display_names():
    """Save current column display names to file"""
    try:
        app = get_app_instance()
        if app:
            with open(DISPLAY_NAMES_FILE, 'w') as f:
                json.dump(app.column_display_names, f, indent=2)
            logger.info(f"Saved display names to {DISPLAY_NAMES_FILE}")
    except Exception as e:
        logger.error(f"Error saving display names: {e}")

def load_column_config():
    """Load column configuration from file"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                app = get_app_instance()
                if app:
                    # Update column_widths with loaded values
                    for part_type, columns in config.items():
                        if part_type in app.column_widths:
                            for col_name, width in columns.items():
                                if col_name in app.column_widths[part_type]:
                                    app.column_widths[part_type][col_name] = width
                logger.info(f"Loaded column config from {CONFIG_FILE}")
                return True
        except Exception as e:
            logger.error(f"Error loading config: {e}")
    return False

def save_column_config():
    """Save current column configuration to file"""
    try:
        config = {}
        app = get_app_instance()
        if app:
            for part_type in app.column_widths:
                config[part_type] = {}
                for col_name, width in app.column_widths[part_type].items():
                    config[part_type][col_name] = width
        
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info(f"Saved column config to {CONFIG_FILE}")
    except Exception as e:
        logger.error(f"Error saving config: {e}")

def watch_config_file():
    """Watch for configuration file changes and reload"""
    last_modified = 0
    
    def check_file():
        nonlocal last_modified
        try:
            if os.path.exists(CONFIG_FILE):
                current_modified = os.path.getmtime(CONFIG_FILE)
                if current_modified > last_modified:
                    logger.info("Configuration file changed, reloading...")
                    if load_column_config():
                        # Refresh all inventory displays
                        app = get_app_instance()
                        if app:
                            for part_type in PCBuilderApp.part_types:
                                if hasattr(app, f'{part_type.lower()}_tree'):
                                    tree = getattr(app, f'{part_type.lower()}_tree')
                                    # Update column widths
                                    for col in tree['columns']:
                                        if col != '#0' and part_type in app.column_widths and col in app.column_widths[part_type]:
                                            width = app.column_widths[part_type][col]
                                            minwidth = max(50, width // 2)
                                            if col in ["Price", "Sell Price", "Wattage", "Frequency", "Size", "VRAM (GB)", "Cores", "Number", "Size each (GB)", "Size (GB)"]:
                                                anchor = 'center'
                                            else:
                                                anchor = 'w'
                                            tree.column(col, width=width, minwidth=minwidth, anchor=anchor)
                    last_modified = current_modified
        except Exception as e:
            logger.error(f"Error watching config: {e}")
        
        # Check every 2 seconds
        app = get_app_instance()
        if app:
            app.root.after_idle(2000, check_file)
    
    # Start watching
    check_file()

# Configure logging for debugging
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=LOG_FILE,
    filemode='w'
)
logger = logging.getLogger(__name__)

class RedirectText:
    """Redirect stdout/stderr to log file"""
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open(LOG_FILE, 'w')
    
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()
    
    def flush(self):
        self.terminal.flush()
        self.log.flush()
import math
import re
from typing import Dict, List, Optional, Tuple, Any
import uuid
import pyperclip

# Custom combobox class for better styling
class DarkCombobox(tk.Menubutton):
    def __init__(self, master, textvariable=None, values=None, state='readonly', width=12, **kwargs):
        self.textvariable = textvariable or tk.StringVar()
        self.values = values or []
        self.state = state
        self.width = width
        
        # Create menubutton
        super().__init__(master, textvariable=self.textvariable, 
                       bg='#353535', fg='#ffffff', 
                       relief=tk.RAISED, bd=1, width=width)
        
        # Create menu
        self.menu = tk.Menu(self, tearoff=0, bg='#353535', fg='#ffffff',
                          activebackground='#505050', activeforeground='#ffffff')
        self.config(menu=self.menu)
        
        # Add options
        for value in self.values:
            self.menu.add_command(label=value, command=lambda v=value: self.set_value(v))
        
        # Set initial value
        if self.values:
            self.textvariable.set(self.values[0])
    
    def set_value(self, value):
        self.textvariable.set(value)
    
    def bind(self, event, handler):
        # Handle binding for combobox-like behavior
        if event == '<<ComboboxSelected>>':
            # Store handler to call when selection changes
            self.selection_handler = handler
            # Override set_value to call handler
            original_set_value = self.set_value
            def new_set_value(value):
                original_set_value(value)
                if hasattr(self, 'selection_handler'):
                    self.selection_handler(None)
            self.set_value = new_set_value
        else:
            super().bind(event, handler)

# Custom accordion filter class
class AccordionFilter:
    def __init__(self, parent, title, values, on_change_callback):
        self.parent = parent
        self.title = title
        self.values = values
        self.on_change_callback = on_change_callback
        self.is_expanded = False
        self.selected_values = set()
        
        # Main frame
        self.frame = tk.Frame(parent, bg=self.parent.cget('bg'), relief=tk.GROOVE, bd=1)
        
        # Header frame (clickable to expand/collapse)
        self.header_frame = tk.Frame(self.frame, bg=self.parent.cget('bg'))
        self.header_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # Expand/collapse button
        self.toggle_btn = tk.Button(self.header_frame, text="▶", 
                                   command=self.toggle,
                                   bg=self.parent.cget('bg'), fg='#ffffff',
                                   font=('Arial', 8, 'bold'), width=2)
        self.toggle_btn.pack(side=tk.LEFT, padx=(5, 2))
        
        # Title label
        self.title_label = tk.Label(self.header_frame, text=title, 
                                   bg=self.parent.cget('bg'), fg='#ffffff',
                                   font=('Arial', 9, 'bold'))
        self.title_label.pack(side=tk.LEFT, padx=2)
        
        # Content frame (for checkboxes) - start collapsed
        self.content_frame = tk.Frame(self.frame, bg=self.parent.cget('bg'))
        # Don't pack initially - start collapsed
        
        # Create checkboxes
        self.checkboxes = {}
        self.checkbox_vars = {}
        
        for value in values:
            var = tk.BooleanVar()
            checkbox = tk.Checkbutton(self.content_frame, text=value, 
                                     variable=var, bg=self.parent.cget('bg'), 
                                     fg='#ffffff', selectcolor='#505050',
                                     activebackground='#404040',
                                     command=lambda v=value, var=var: self.on_checkbox_change(v, var))
            checkbox.pack(anchor='w', padx=5, pady=1)
            
            self.checkbox_vars[value] = var
            self.checkboxes[value] = checkbox
    
    def toggle(self):
        """Toggle accordion expanded/collapsed"""
        self.is_expanded = not self.is_expanded
        
        if self.is_expanded:
            self.toggle_btn.config(text="▼")
            self.content_frame.pack(fill=tk.X, padx=5, pady=2)
        else:
            self.toggle_btn.config(text="▶")
            self.content_frame.pack_forget()
    
    def on_checkbox_change(self, value, var):
        """Handle checkbox change"""
        if var.get():
            self.selected_values.add(value)
        else:
            self.selected_values.discard(value)
        
        # Call callback with selected values
        self.on_change_callback(self.title, list(self.selected_values))
    
    def get_selected_values(self):
        """Get currently selected values"""
        return list(self.selected_values)
    
    def clear_selections(self):
        """Clear all checkbox selections"""
        for var in self.checkbox_vars.values():
            var.set(False)
        self.selected_values.clear()

# Check for command line arguments
HIDE_CONSOLE = "--no-console" in sys.argv

# Redirect output if console should be hidden
if HIDE_CONSOLE:
    sys.stdout = RedirectText()
    sys.stderr = RedirectText()

class PCBuilderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PC Builder - PC Building Simulator")
        self.root.geometry("1400x900")
        
        # Show startup message
        if HIDE_CONSOLE:
            logger.info("=== PC Builder Started (Console Hidden) ===")
            logger.info(f"Debug logs will be saved to '{LOG_FILE}'")
            logger.info("To show console: run without --no-console argument")
        else:
            print("=== PC Builder Debug Mode ===")
            print(f"Debug logs are being saved to '{LOG_FILE}'")
            print("To hide console: run with --no-console argument")
            print("=====================================")
        
        # Dark theme colors
        self.bg_color = "#2b2b2b"
        self.fg_color = "#ffffff"
        self.button_bg = "#404040"
        self.button_fg = "#ffffff"
        self.entry_bg = "#353535"
        self.entry_fg = "#ffffff"
        self.select_bg = "#505050"
        self.warning_bg = "#8B0000"
        self.warning_fg = "#FFFF00"
        
        # Tip colors
        self.tip_bg = "#1e3a3a"
        self.tip_fg = "#ffffff"
        
        # Link color for clickable help text
        self.link_color = "#4da6ff"
        
        self.root.configure(bg=self.bg_color)
        self.root.option_add("*Toplevel*background", self.bg_color)
        self.root.option_add("*Frame*background", self.bg_color)
        
        # Data storage
        self.inventory = []
        self.builds = []
        self.current_build_id = 1
        self.hem_enabled = False
        self.part_data = {}
        self.search_var = tk.StringVar()
        self.selected_part_suggestions = []
        
        # Accessibility settings
        self.text_size_multiplier = 1.0  # Default: Small (1.0x)
        self.tips_dismissed = {
            "double_click_add": False,
            "builds_tab": False,
            "jobs_tab": False,
            "story_job": False
        }
        
        # Filtering and sorting data
        self.current_filters = {}  # {part_type: {column: value}}
        self.current_sort = {}  # {part_type: (column, direction)}
        self.filtered_inventory = {}  # {part_type: [filtered_items]}
        self.show_tip = True  # Tip visibility state
        self.column_configs = {}  # Store column configurations for alignment
        self.filter_controls = {}  # Store filter controls for each part type
        self.accordion_filters = {}  # Store accordion filters for each part type
        self.part_trees = {}  # Store tree references for double-click functionality
        self.used_parts_trees = {}  # Store used parts tree references
        self.new_parts_trees = {}   # Store new parts tree references
        
        # New inventory system - separate used and new parts
        self.used_parts_inventory = []  # Used parts for builds
        self.new_parts_inventory = []   # New parts for jobs
        self.jobs = []  # Jobs list
        
        # Job data structures
        self.job_notebook = None
        self.job_frames = {}
        self.current_job = None
        
        # Part types and their CSV files
        self.part_types = {
            "CASE": "Base Game/Case.csv",
            "CASE FAN": "Base Game/Case Fan.csv", 
            "CPU": "Base Game/CPU.csv",
            "CPU COOLER": "Base Game/CPU Cooler.csv",
            "GPU": "Base Game/GPU.csv",
            "MOTHERBOARD": "Base Game/Motherboard.csv",
            "PSU": "Base Game/PSU.csv",
            "RAM": "Base Game/RAM.csv",
            "STORAGE": "Base Game/Storage.csv",
            "CABLE": "Base Game/Cables.csv"  # Add cable support (may not exist in base game)
        }
        
        # HEM part types and their CSV files
        self.hem_part_types = {
            "CASE": "HEM/Case.csv",
            "CASE FAN": "HEM/Case Fan.csv", 
            "CPU": "HEM/CPU.csv",
            "CPU COOLER": "HEM/CPU Cooler.csv",
            "GPU": "HEM/GPU.csv",
            "MOTHERBOARD": "HEM/Motherboard.csv",
            "PSU": "HEM/PSU.csv",
            "RAM": "HEM/RAM.csv",
            "STORAGE": "HEM/Storage.csv",
            "CABLE": "HEM/Cables.csv"  # Add cable support for HEM
        }
        
        # HEM file mappings (different names)
        self.hem_file_mappings = {
            "CASE": "Cases.csv",
            "CASE FAN": "Case Fans.csv", 
            "CPU": "CPUs.csv",
            "CPU COOLER": "CPU Coolers.csv",
            "GPU": "GPUs.csv",
            "MOTHERBOARD": "Motherboards.csv",
            "PSU": "Power Supplies.csv",
            "RAM": "Memory.csv",
            "STORAGE": "Storage.csv"
        }
        
        # Dynamic column definitions (populated from CSV files)
        self.part_columns = {}
        
        # Column visibility configuration for each part type
        # Format: {part_type: {column_name: True/False}}
        # True = visible, False = hidden
        self.column_visibility = {
            "CASE": {
                "Part Type": False, "Manufacturer": True, "Part Name": True,
                "HEM": True, "In Shop": True, "Price": True, "Sell Price": True,
                "Level": False, "Level %": False, "Steam Version": False,
                "Platform Lock": False, "Is DLC": False, "Lighting": True,
                "Size": True, "Mini-ITX": False, "Micro-ATX": False, "S-ATX": False,
                "E-ATX": False, "XL-ATX": False, "SSI-EEB": False, "PSU ATX": True,
                "PSU SFX": True, "Max 120mm Radiators": True, "Max 140mm Radiators": True,
                "Max PSU length": True, "Max GPU length": True, "Max CPU Fan Height": True,
                "Exclude From Random Jobs": False, "Use For WC Jobs": False,
                "DLC Epic Id": False, "Is Open Bench": False, "Case Fan Type 1 Count": False,
                "Case Fan Type 1 Model": False, "Case Fan Type 1 Decorator": False,
                "Case Fan Type 2 Count": False, "Case Fan Type 2 Model": False,
                "Case Fan Type 2 Decorator": False, "Case Fan Type 3 Count": False,
                "Case Fan Type 3 Model": False, "Case Fan Type 3 Decorator": False,
                "Restricted GPU length": False, "Inherent Cooling": False,
                "Price of Case Fans": True, "Price of Case Without Case Fans": True,
                "DLC2 Random Jobs": False, "Asset Path": False, "Full Part Name": False
            },
            "CASE FAN": {
                "Part Type": False, "Manufacturer": True, "Part Name": True,
                "HEM": True, "In Shop": True, "Price": True, "Sell Price": True,
                "Level": False, "Level %": False, "Steam Version": False,
                "Platform Lock": False, "Lighting": True, "Air Flow": True,
                "Size": True, "Thickness": False, "Exclude From Random Jobs": False,
                "Air Pressure": False, "DLC2 Random Jobs": False, "Asset Path": False,
                "Full Part Name": False
            },
            "CPU": {
                "Part Type": False, "Manufacturer": True, "Series": True, "Part Name": True,
                "HEM": True, "In Shop": True, "Price": True, "Sell Price": True,
                "Level": False, "Level %": False, "Steam Version": False,
                "Platform Lock": False, "Frequency": True, "Cores": True, "Socket": True,
                "Wattage": True, "Can Overclock": True, "Thermal Throttling": True,
                "Voltage": True, "Basic CPU Score": True, "Score to value ratio": True,
                "Default Memory Speed": False, "% increase": False, "Overclock Basic CPU Score": False,
                "Overclock CPU score increase": True, "Multiplier Step": False, "Number of dies": False,
                "Max Memory Channels": False, "OC Base Voltage": False, "OC Base Freq": False,
                "CoreClockMultiplier": False, "MemChannelsMultiplier": False, "MemClockMultiplier": False,
                "FinalAdjustment": False, "DLC2 Random Jobs": False, "Asset Path": False, "Full Part Name": False
            },
            "CPU COOLER": {
                "Part Type": False, "Manufacturer": True, "Part Name": True,
                "HEM": False, "In Shop": False, "Price": True, "Sell Price": True,
                "Level": False, "Level %": False, "Steam Version": False,
                "Platform Lock": False, "Lighting": True, "Type": True, "No Fan": True,
                "Air Flow": True, "AM4": False, "LGA 1151 (Skylake)": False,
                "LGA 1151 (Kaby Lake)": False, "LGA 1151 (Coffee Lake)": False,
                "LGA 1200": False, "TR4": False, "sTRX4": False, "LGA 2066": False,
                "AM3+": False, "FM2": False, "FM2+": False, "LGA 2011-V3": False,
                "LGA 2566": False, "LGA 3647-V1": False, "LGA 3647-V3": False,
                "LGA 4189": False, "LGA 4189 (2P)": False, "LGA 4926": False,
                "LGA 5903": False, "SP3r1": False, "SP3r2": False, "SP6": False,
                "LGA 3647-V3 (2P)": False, "LGA 3647-V3 (4P)": False,
                "LGA 3647-V3 (8P)": False, "LGA 4926 (2P)": False,
                "LGA 5903 (2P)": False, "SP3r1 (2P)": False, "SP3r2 (2P)": False,
                "SP6 (2P)": False, "CPU Socket List": True, "CPU Socket List (HEM)": True,
                "Height": True, "Size": True, "Slots": True, "Thickness": False,
                "Air Pressure": False, "DLC2 Random Jobs": False, "Exclude From Random Jobs": False,
                "Asset Path": False, "Full Part Name": False
            },
            "GPU": {
                "Part Type": False, "Chipset Brand": True, "Chipset Series": True, "Chipset": True,
                "Manufacturer": True, "Part Name": True, "HEM": True, "In Shop": True,
                "Part Ranking Score": True, "Price": True, "Sell Price": True, "Level": False,
                "Level %": False, "Steam Version": False, "Platform Lock": False, "Lighting": True,
                "VRAM (GB)": True, "GPU Tuner Min Core Freq": False, "Base Core Freq": False,
                "OC Base Core Freq": False, "Max Core Freq": False, "GPU Tuner Min Mem Freq": False,
                "Base Mem Freq": False, "OC Base Mem Freq": False, "Max Mem Freq": False,
                "Length": True, "Wattage": True, "Multi-GPU": True, "Slot Size": True,
                "GPU Thermal Throttling": True, "GPU % Power Increase": False, "Power Connectors": False,
                "Rigid SLI Bridge Model": False, "Score to value ratio": True, "Target STV ratio": False,
                "Single GPU Graphics Score": True, "Double GPU Graphics Score": True,
                "Dual GPU performance increase": True, "OC Single GPU score": False,
                "OC Double GPU score": False, "GT1 Single Core Clock Multiplier": False,
                "GT1 Single Mem Clock Multiplier": False, "GT1 Single Benchmark Adjustment": False,
                "GT2 Single Core Clock Multiplier": False, "GT2 Single Mem Clock Multiplier": False,
                "GT2 Single Benchmark Adjustment": False, "GT1 Dual Core Clock Multiplier": False,
                "GT1 Dual Mem Clock Multiplier": False, "GT1 Dual Benchmark Adjustment": False,
                "GT2 Dual Core Clock Multiplier": False, "GT2 Dual Mem Clock Multiplier": False,
                "GT2 Dual Benchmark Adjustment": False, "Normal GPU max clock": False,
                "Normal GPU Max mem clock": False, "Boost Multiplier": False, "Score increase": False,
                "Is AIO": True, "Next Part ID In Combo": False, "Exclude From Random Jobs": False,
                "DLC2 Random Jobs": False, "Chipset Series Sort": False, "Asset Path": False, "Full Part Name": False
            },
            "MOTHERBOARD": {
                "Part Type": False, "Manufacturer": True, "Part Name": True, "HEM": True,
                "In Shop": True, "Price": True, "Sell Price": True, "Level": False,
                "Level %": False, "Steam Version": False, "Platform Lock": False, "Is DLC": False,
                "Lighting": True, "Chipset": True, "CPU Socket": True, "Size": True,
                "RAM Type": True, "Max RAM Speed Step": True, "Support CrossFire": True,
                "Support SLI": True, "Dual GPU Max Slot Size": True, "Can Overclock": True,
                "M.2 Slots": True, "M.2 Slots Supporting Heatsinks": True, "RAM Slots": True,
                "SATA Slots Usable": True, "SATA Slots Visible": False, "Included CPU Block": False,
                "Default RAM Speed": False, "RAM Speed Steps": False, "Min RAM Speed Step": False,
                "Base Clock": False, "Custom BIOS Logo": False, "DLC2 Random Jobs": False,
                "Asset Path": False, "Full Part Name": False
            },
            "PSU": {
                "Part Type": False, "Manufacturer": True, "Part Name": True, "HEM": False,
                "In Shop": False, "Price": True, "Sell Price": True, "Level": False,
                "Level %": False, "Steam Version": False, "Platform Lock": False, "Wattage": True,
                "Length": True, "Type": True, "Size": True, "DLC2 Random Jobs": False,
                "Asset Path": False, "Full Part Name": False
            },
            "RAM": {
                "Part Type": False, "Manufacturer": True, "Part Name": True, "HEM": True,
                "In Shop": False, "Price": True, "Sell Price": True, "Level": False,
                "Level %": False, "Steam Version": False, "Platform Lock": False, "Lighting": True,
                "Size (GB)": True, "Frequency": True, "RAM Type": True, "Voltage": True,
                "Size each (GB)": True, "Number": True, "Price per GB": True, "Part Name (Base)": False,
                "DLC2 Random Jobs": False, "OC Base Voltage": False, "OC Base Freq": False,
                "Asset Path": False, "Full Part Name": False
            },
            "STORAGE": {
                "Part Type": False, "Manufacturer": True, "Part Name": True, "HEM": True,
                "In Shop": True, "Price": True, "Sell Price": True, "Level": False,
                "Level %": False, "Steam Version": False, "Platform Lock": False, "Lighting": True,
                "Type": True, "Size (GB)": True, "Transfer Speed (MB/s)": True,
                "Includes Heatsink": True, "Heatsink Thickness": False, "Form Factor": True,
                "Interface": True, "NAND Type": True, "Read Speed": True, "Write Speed": True,
                "DLC2 Random Jobs": False, "Asset Path": False, "Full Part Name": True
            }
        }
        
        # Column width configuration for each part type
        # Format: {part_type: {column_name: width_in_pixels}}
        # You can easily edit these values to adjust column widths
        self.column_widths = {
            "CASE": {
                "Part Type": 120, "Manufacturer": 100, "Part Name": 20,
                "HEM": 40, "In Shop": 80, "Price": 60, "Sell Price": 80,
                "Level": 80, "Level %": 100, "Steam Version": 120,
                "Platform Lock": 120, "Is DLC": 80, "Lighting": 80,
                "Size": 80, "Mini-ITX": 80, "Micro-ATX": 100, "S-ATX": 80,
                "E-ATX": 80, "XL-ATX": 80, "SSI-EEB": 80, "PSU ATX": 80,
                "PSU SFX": 80, "Max 120mm Radiators": 100, "Max 140mm Radiators": 100,
                "Max PSU length": 120, "Max GPU length": 120, "Max CPU Fan Height": 140,
                "Exclude From Random Jobs": 180, "Use For WC Jobs": 120,
                "DLC Epic Id": 120, "Is Open Bench": 120, "Case Fan Type 1 Count": 150,
                "Case Fan Type 1 Model": 150, "Case Fan Type 1 Decorator": 180,
                "Case Fan Type 2 Count": 150, "Case Fan Type 2 Model": 150, "Case Fan Type 2 Decorator": 180,
                "Case Fan Type 3 Count": 150, "Case Fan Type 3 Model": 150, "Case Fan Type 3 Decorator": 180,
                "Restricted GPU length": 160, "Inherent Cooling": 140,
                "Price of Case Fans": 140, "Price of Case Without Case Fans": 180,
                "DLC2 Random Jobs": 180, "Asset Path": 120, "Full Part Name": 120
            },
            "CASE FAN": {
                "Part Type": 120, "Manufacturer": 100, "Part Name": 500,
                "HEM": 50, "In Shop": 80, "Price": 100, "Sell Price": 100,
                "Level": 80, "Level %": 100, "Steam Version": 120,
                "Platform Lock": 120, "Lighting": 80, "Air Flow": 80,
                "Size": 80, "Thickness": 100, "Exclude From Random Jobs": 180,
                "Air Pressure": 120, "DLC2 Random Jobs": 180, "Asset Path": 120,
                "Full Part Name": 120
            },
            "CPU": {
                "Part Type": 120, "Manufacturer": 100, "Series": 120, "Part Name": 500,
                "HEM": 50, "In Shop": 80, "Price": 100, "Sell Price": 100,
                "Level": 80, "Level %": 100, "Steam Version": 120,
                "Platform Lock": 120, "Frequency": 100, "Cores": 80, "Socket": 120,
                "Wattage": 100, "Can Overclock": 120, "Thermal Throttling": 140,
                "Voltage": 80, "Basic CPU Score": 130, "Score to value ratio": 140,
                "Default Memory Speed": 150, "% increase": 100, "Overclock Basic CPU Score": 180,
                "Overclock CPU score increase": 200, "Multiplier Step": 140, "Number of dies": 120,
                "Max Memory Channels": 160, "OC Base Voltage": 140, "OC Base Freq": 120,
                "CoreClockMultiplier": 180, "MemChannelsMultiplier": 180, "MemClockMultiplier": 160,
                "FinalAdjustment": 140, "DLC2 Random Jobs": 180, "Asset Path": 120, "Full Part Name": 120
            },
            "CPU COOLER": {
                "Part Type": 120, "Manufacturer": 100, "Part Name": 500,
                "HEM": 50, "In Shop": 80, "Price": 100, "Sell Price": 100,
                "Level": 80, "Level %": 100, "Steam Version": 120,
                "Platform Lock": 120, "Lighting": 80, "Type": 80, "No Fan": 80,
                "Air Flow": 80, "AM4": 80, "LGA 1151 (Skylake)": 140,
                "LGA 1151 (Kaby Lake)": 140, "LGA 1151 (Coffee Lake)": 160,
                "LGA 1200": 100, "TR4": 80, "sTRX4": 80, "LGA 2066": 100,
                "LGA 2011-3": 120, "LGA 1700": 100, "Socket AM5": 120,
                "Socket AM4": 120, "Socket sTR5": 100, "Socket sTRX6": 120,
                "Socket LGA 1851": 140, "LGA 4677": 100, "LGA 3647-V3 (2P)": 160,
                "LGA 3647-V3 (4P)": 160, "LGA 3647-V3 (8P)": 160, "LGA 4926 (2P)": 140,
                "SP6 (2P)": 120, "CPU Socket List": 140, "CPU Socket List (HEM)": 180,
                "Height": 80, "Size": 80, "Slots": 80, "Thickness": 100,
                "Air Pressure": 120, "DLC2 Random Jobs": 180, "Exclude From Random Jobs": 180,
                "Asset Path": 120, "Full Part Name": 120
            },
            "GPU": {
                "Part Type": 120, "Chipset Brand": 120, "Chipset Series": 120, "Chipset": 120,
                "Manufacturer": 100, "Part Name": 500, "HEM": 50, "In Shop": 80,
                "Part Ranking Score": 140, "Price": 100, "Sell Price": 100, "Level": 80,
                "Level %": 100, "Steam Version": 120, "Platform Lock": 120, "Lighting": 80,
                "VRAM (GB)": 100, "GPU Tuner Min Core Freq": 160, "Base Core Freq": 120,
                "OC Base Core Freq": 140, "Max Core Freq": 120, "GPU Tuner Min Mem Freq": 160,
                "Base Mem Freq": 120, "OC Base Mem Freq": 140, "Max Mem Freq": 120,
                "Length": 80, "Wattage": 100, "Multi-GPU": 100, "Slot Size": 100,
                "GPU Thermal Throttling": 180, "Score to value ratio": 140, "Single GPU Graphics Score": 200,
                "Double GPU Graphics Score": 200, "Dual GPU performance increase": 200, "Is AIO": 80,
                "DLC2 Random Jobs": 180, "Exclude From Random Jobs": 180, "Asset Path": 120, "Full Part Name": 120
            },
            "MOTHERBOARD": {
                "Part Type": 120, "Manufacturer": 100, "Part Name": 500, "HEM": 50,
                "In Shop": 80, "Price": 100, "Sell Price": 100, "Level": 80,
                "Level %": 100, "Steam Version": 120, "Platform Lock": 120, "Is DLC": 120,
                "Lighting": 80, "Chipset": 100, "CPU Socket": 120, "Size": 80,
                "RAM Type": 100, "Max RAM Speed Step": 150, "Support CrossFire": 140,
                "Support SLI": 120, "Dual GPU Max Slot Size": 160, "Can Overclock": 120,
                "M.2 Slots": 100, "M.2 Slots Supporting Heatsinks": 200, "RAM Slots": 100,
                "SATA Slots Usable": 140, "DLC2 Random Jobs": 180, "Exclude From Random Jobs": 180,
                "Asset Path": 120, "Full Part Name": 120
            },
            "PSU": {
                "Part Type": 120, "Manufacturer": 100, "Part Name": 500, "HEM": 50,
                "In Shop": 80, "Price": 100, "Sell Price": 100, "Level": 80,
                "Level %": 100, "Steam Version": 120, "Platform Lock": 120, "Wattage": 100,
                "Length": 80, "Type": 80, "Size": 80, "DLC2 Random Jobs": 180,
                "Exclude From Random Jobs": 180, "Asset Path": 120, "Full Part Name": 120
            },
            "RAM": {
                "Part Type": 120, "Manufacturer": 100, "Part Name": 500, "HEM": 50,
                "In Shop": 80, "Price": 100, "Sell Price": 100, "Level": 80,
                "Level %": 100, "Steam Version": 120, "Platform Lock": 120, "Lighting": 80,
                "Size (GB)": 100, "Frequency": 100, "RAM Type": 100, "Voltage": 80,
                "Size each (GB)": 120, "Number": 80, "Price per GB": 100, "Part Name (Base)": 140,
                "DLC2 Random Jobs": 180, "OC Base Voltage": 140, "OC Base Freq": 120,
                "Asset Path": 120, "Full Part Name": 120
            },
            "STORAGE": {
                "Part Type": 120, "Manufacturer": 100, "Part Name": 500, "HEM": 50,
                "In Shop": 80, "Price": 100, "Sell Price": 100, "Level": 80,
                "Level %": 100, "Steam Version": 120, "Platform Lock": 120, "Lighting": 80,
                "Type": 80, "Size (GB)": 100, "Transfer Speed (MB/s)": 150,
                "Includes Heatsink": 140, "Heatsink Thickness": 140, "Form Factor": 100,
                "Interface": 120, "NAND Type": 100, "Read Speed": 100, "Write Speed": 100,
                "DLC2 Random Jobs": 180, "Exclude From Random Jobs": 180, "Asset Path": 120, "Full Part Name": 120
            }
        }
        
        # Column display names configuration
        # Format: {column_name: "display_name"}
        # You can easily edit these values to change what appears in column headers
        self.column_display_names = {
            "Part Type": "Type",
            "Manufacturer": "Brand", 
            "Part Name": "Component Name",
            "HEM": "HEM",
            "In Shop": "In Shop",
            "Price": "Buy ($)",
            "Sell Price": "Sell ($)",
            "Level": "Level",
            "Level %": "Level %",
            "Steam Version": "Steam",
            "Platform Lock": "Platform",
            "Is DLC": "DLC",
            "Lighting": "Lighting",
            "Size": "Size",
            "Mini-ITX": "Mini-ITX",
            "Micro-ATX": "Micro-ATX", 
            "S-ATX": "S-ATX",
            "E-ATX": "E-ATX",
            "XL-ATX": "XL-ATX",
            "SSI-EEB": "SSI-EEB",
            "PSU ATX": "PSU ATX",
            "PSU SFX": "PSU SFX",
            "Max 120mm Radiators": "120mm Fans",
            "Max 140mm Radiators": "140mm Fans", 
            "Max PSU length": "PSU Length",
            "Max GPU length": "GPU Length",
            "Max CPU Fan Height": "CPU Fan Height",
            "Exclude From Random Jobs": "Random Jobs",
            "Use For WC Jobs": "WC Jobs",
            "DLC Epic Id": "Epic ID",
            "Is Open Bench": "Open Bench",
            "Case Fan Type 1 Count": "Fan 1 Count",
            "Case Fan Type 1 Model": "Fan 1 Model",
            "Case Fan Type 1 Decorator": "Fan 1 Decor",
            "Case Fan Type 2 Count": "Fan 2 Count",
            "Case Fan Type 2 Model": "Fan 2 Model", 
            "Case Fan Type 2 Decorator": "Fan 2 Decor",
            "Case Fan Type 3 Count": "Fan 3 Count",
            "Case Fan Type 3 Model": "Fan 3 Model",
            "Case Fan Type 3 Decorator": "Fan 3 Decor",
            "Restricted GPU length": "GPU Restrict",
            "Inherent Cooling": "Cooling",
            "Price of Case Fans": "Fans Price",
            "Price of Case Without Case Fans": "Case Price",
            "DLC2 Random Jobs": "DLC2 Random Jobs",
            "Asset Path": "Asset",
            "Full Part Name": "Full Part Name",
            "Air Flow": "Air Flow",
            "Thickness": "Thickness",
            "Air Pressure": "Air Pressure",
            "Series": "Series",
            "Frequency": "Frequency",
            "Cores": "Cores",
            "Socket": "Socket",
            "Wattage": "Wattage",
            "Can Overclock": "OC",
            "Thermal Throttling": "Thermal",
            "Voltage": "Voltage",
            "Basic CPU Score": "CPU Score",
            "Score to value ratio": "Value Ratio",
            "Default Memory Speed": "Mem Speed",
            "% increase": "% Inc",
            "Overclock Basic CPU Score": "OC Score",
            "Overclock CPU score increase": "OC Inc",
            "Multiplier Step": "Mult Step",
            "Number of dies": "Dies",
            "Max Memory Channels": "Mem Chans",
            "OC Base Voltage": "OC Voltage",
            "OC Base Freq": "OC Freq",
            "CoreClockMultiplier": "Core Mult",
            "MemChannelsMultiplier": "Mem Mult",
            "MemClockMultiplier": "Mem Clock Mult",
            "FinalAdjustment": "Final Adj",
            "Type": "Type",
            "No Fan": "No Fan",
            "AM4": "AM4",
            "LGA 1151 (Skylake)": "LGA 1151S",
            "LGA 1151 (Kaby Lake)": "LGA 1151K",
            "LGA 1151 (Coffee Lake)": "LGA 1151C",
            "LGA 1200": "LGA 1200",
            "TR4": "TR4",
            "sTRX4": "sTRX4",
            "LGA 2066": "LGA 2066",
            "LGA 2011-3": "LGA 2011-3",
            "LGA 1700": "LGA 1700",
            "Socket AM5": "AM5",
            "Socket AM4": "AM4",
            "Socket sTR5": "sTR5",
            "Socket sTRX6": "sTRX6",
            "Socket LGA 1851": "LGA 1851",
            "LGA 4677": "LGA 4677",
            "LGA 3647-V3 (2P)": "LGA 3647-2P",
            "LGA 3647-V3 (4P)": "LGA 3647-4P",
            "LGA 3647-V3 (8P)": "LGA 3647-8P",
            "LGA 4926 (2P)": "LGA 4926-2P",
            "SP6 (2P)": "SP6-2P",
            "CPU Socket List": "CPU Sockets",
            "CPU Socket List (HEM)": "CPU Sockets (HEM)",
            "Height": "Height",
            "Slots": "Slots",
            "Chipset Brand": "Chipset Brand",
            "Chipset Series": "Chipset Series",
            "Chipset": "Chipset",
            "Part Ranking Score": "Rank Score",
            "VRAM (GB)": "VRAM",
            "GPU Tuner Min Core Freq": "Min GPU Freq",
            "Base Core Freq": "Base GPU Freq",
            "OC Base Core Freq": "OC GPU Freq",
            "Max Core Freq": "Max GPU Freq",
            "GPU Tuner Min Mem Freq": "Min Mem Freq",
            "Base Mem Freq": "Base Mem Freq",
            "OC Base Mem Freq": "OC Mem Freq",
            "Max Mem Freq": "Max Mem Freq",
            "Length": "Length",
            "Multi-GPU": "Multi-GPU",
            "Slot Size": "Slot Size",
            "GPU Thermal Throttling": "GPU Thermal",
            "Single GPU Graphics Score": "GPU Score",
            "Double GPU Graphics Score": "2x GPU Score",
            "Dual GPU performance increase": "2x GPU Inc",
            "Is AIO": "AIO",
            "CPU Socket": "CPU Socket",
            "RAM Type": "RAM Type",
            "Max RAM Speed Step": "Max RAM Speed",
            "Support CrossFire": "CrossFire",
            "Support SLI": "SLI",
            "Dual GPU Max Slot Size": "2x GPU Slot Size",
            "Can Overclock": "OC",
            "M.2 Slots": "M.2 Slots",
            "M.2 Slots Supporting Heatsinks": "M.2 + Heatsink",
            "RAM Slots": "RAM Slots",
            "SATA Slots Usable": "SATA Slots",
            "Size (GB)": "Size (GB)",
            "Size each (GB)": "GB Each",
            "Number": "Number",
            "Price per GB": "Price/GB",
            "Part Name (Base)": "Base Name",
            "Transfer Speed (MB/s)": "Transfer Speed",
            "Includes Heatsink": "Heatsink",
            "Heatsink Thickness": "HS Thickness",
            "Form Factor": "Form Factor",
            "Interface": "Interface",
            "NAND Type": "NAND Type",
            "Read Speed": "Read Speed",
            "Write Speed": "Write Speed"
        }
        
        # Build slot definitions
        self.build_slots = {
            "Case": 1,
            "PSU": 1, 
            "Motherboard": 1,
            "CPU": 1,
            "GPU": 2,
            "RAM": 4,
            "CPU Cooler": 1,
            "Case Fans": 4,
            "Storage": 6
        }
        
        # Simple loading without complex progress tracking
        self.load_state()
        self.load_part_data()
        
        # Set app instance for configuration system
        set_app_instance(self)
        
        # Load configurations (live watching disabled for now due to threading issue)
        load_column_config()
        load_display_names()
        # threading.Thread(target=watch_config_file, daemon=True).start()
        
        # Save initial configurations
        save_column_config()
        save_display_names()
        
        self.setup_ui()
        
        # Apply text size only if needed, after everything is loaded
        self.root.after(100, self.apply_text_size_simple)
        
    def apply_text_size_simple(self):
        """Apply text size changes in a simple, safe way"""
        # Always apply changes, don't skip default size
        try:
            # Calculate font sizes
            base_font_size = int(10 * self.text_size_multiplier)
            font_size = max(8, min(base_font_size, 20))  # Increased max for better scaling
            small_font_size = max(7, min(int(8 * self.text_size_multiplier), 16))
            large_font_size = max(10, min(int(12 * self.text_size_multiplier), 24))
            
            # Create fonts
            simple_font = ('Arial', font_size)
            small_font = ('Arial', small_font_size)
            large_font = ('Arial', large_font_size)
            
            # Apply to notebook tabs
            try:
                style = ttk.Style()
                style.configure('TNotebook.Tab', font=simple_font)
                style.configure('Treeview.Heading', font=('Arial', int(10 * self.text_size_multiplier), 'bold'))
            except:
                pass
            
            # Apply to all known widgets systematically
            self._apply_fonts_to_all_widgets(simple_font, small_font, large_font)
                
        except Exception as e:
            print(f"Error applying text size: {e}")
    
    def _apply_fonts_to_all_widgets(self, normal_font, small_font, large_font):
        """Apply fonts to all widgets in the application"""
        try:
            # Apply to main window and all children recursively
            self._apply_font_recursive(self.root, normal_font, small_font, large_font)
            
            # Apply to specific known widgets by their attributes
            known_widgets = [
                'jobs_listbox', 'builds_listbox', 'status_label', 'new_status_label',
                'search_entry', 'new_search_entry', 'suggestions_listbox', 'new_suggestions_listbox',
                'builds_listbox', 'jobs_listbox', 'text_size_var', 'hem_settings_var'
            ]
            
            for widget_name in known_widgets:
                if hasattr(self, widget_name):
                    widget = getattr(self, widget_name)
                    try:
                        if hasattr(widget, 'configure'):
                            widget.configure(font=normal_font)
                    except:
                        pass
            
            # Apply to all treeviews
            self._apply_treeview_fonts(normal_font)
            
            # Apply to all notebooks
            self._apply_notebook_fonts(normal_font)
            
            # Apply to builds and jobs specific elements
            self._apply_builds_jobs_fonts(normal_font)
            
        except Exception as e:
            print(f"Error in _apply_fonts_to_all_widgets: {e}")
    
    def _apply_builds_jobs_fonts(self, normal_font):
        """Apply fonts to builds and jobs specific elements"""
        try:
            # Apply to builds details frame
            if hasattr(self, 'build_details_frame'):
                self._apply_font_recursive(self.build_details_frame, normal_font, normal_font, normal_font)
            
            # Apply to job details frame
            if hasattr(self, 'job_details_frame'):
                self._apply_font_recursive(self.job_details_frame, normal_font, normal_font, normal_font)
            
            # Apply to current build details
            if hasattr(self, 'current_build') and self.current_build:
                self.refresh_build_details()  # This will recreate with new fonts
            
            # Apply to current job details
            if hasattr(self, 'current_job') and self.current_job:
                self.refresh_job_details()  # This will recreate with new fonts
                
        except Exception as e:
            print(f"Error applying builds/jobs fonts: {e}")
    
    def _apply_font_recursive(self, widget, normal_font, small_font, large_font):
        """Recursively apply fonts to all widgets"""
        try:
            widget_class = widget.winfo_class()
            
            # Skip certain widgets that handle their own sizing
            if widget_class in ['Canvas', 'Scrollbar']:
                return
            
            # Apply font based on widget type
            if hasattr(widget, 'configure'):
                try:
                    if 'Label' in widget_class or widget_class == 'Label':
                        widget.configure(font=normal_font)
                    elif 'Button' in widget_class or widget_class == 'Button':
                        widget.configure(font=normal_font)
                    elif 'Entry' in widget_class or widget_class == 'Entry':
                        widget.configure(font=normal_font)
                    elif 'Listbox' in widget_class or widget_class == 'Listbox':
                        widget.configure(font=normal_font)
                    elif 'Combobox' in widget_class or widget_class == 'Combobox':
                        widget.configure(font=normal_font)
                    elif 'Checkbutton' in widget_class or widget_class == 'Checkbutton':
                        widget.configure(font=normal_font)
                    elif 'Radiobutton' in widget_class or widget_class == 'Radiobutton':
                        widget.configure(font=normal_font)
                    elif 'Frame' in widget_class or widget_class == 'Frame':
                        pass  # Frames don't need font changes
                    elif 'TLabel' in widget_class:  # ttk.Label
                        widget.configure(font=normal_font)
                    elif 'TButton' in widget_class:  # ttk.Button
                        widget.configure(font=normal_font)
                    elif 'TCombobox' in widget_class:  # ttk.Combobox
                        widget.configure(font=normal_font)
                    elif 'TCheckbutton' in widget_class:  # ttk.Checkbutton
                        widget.configure(font=normal_font)
                    elif 'TRadiobutton' in widget_class:  # ttk.Radiobutton
                        widget.configure(font=normal_font)
                except:
                    pass
            
            # Recursively apply to children
            for child in widget.winfo_children():
                self._apply_font_recursive(child, normal_font, small_font, large_font)
                
        except:
            pass  # Skip widgets that don't support font configuration
    
    def _apply_treeview_fonts(self, normal_font):
        """Apply fonts to all treeview widgets"""
        try:
            # Apply to all part trees
            if hasattr(self, 'part_trees'):
                for tree_name, tree in self.part_trees.items():
                    try:
                        # Apply to treeview headings
                        style = ttk.Style()
                        style.configure(f'Treeview.{tree_name}.Heading', 
                                     font=('Arial', int(10 * self.text_size_multiplier), 'bold'))
                    except:
                        pass
            
            # Apply to used parts trees
            if hasattr(self, 'used_parts_trees'):
                for tree_name, tree in self.used_parts_trees.items():
                    try:
                        style = ttk.Style()
                        style.configure(f'Treeview.{tree_name}.Heading', 
                                     font=('Arial', int(10 * self.text_size_multiplier), 'bold'))
                    except:
                        pass
            
            # Apply to new parts trees
            if hasattr(self, 'new_parts_trees'):
                for tree_name, tree in self.new_parts_trees.items():
                    try:
                        style = ttk.Style()
                        style.configure(f'Treeview.{tree_name}.Heading', 
                                     font=('Arial', int(10 * self.text_size_multiplier), 'bold'))
                    except:
                        pass
                        
        except Exception as e:
            print(f"Error applying treeview fonts: {e}")
    
    def _apply_notebook_fonts(self, normal_font):
        """Apply fonts to all notebook widgets"""
        try:
            # Apply to main notebook
            if hasattr(self, 'notebook'):
                style = ttk.Style()
                style.configure('TNotebook.Tab', font=normal_font)
            
            # Apply to used parts notebook
            if hasattr(self, 'used_parts_notebook'):
                style = ttk.Style()
                style.configure('TNotebook.Tab', font=normal_font)
            
            # Apply to builds notebook (if exists)
            if hasattr(self, 'builds_notebook'):
                style = ttk.Style()
                style.configure('TNotebook.Tab', font=normal_font)
                
        except Exception as e:
            print(f"Error applying notebook fonts: {e}")
        
    def get_visible_columns(self, part_type):
        """Get list of visible columns for a part type based on visibility configuration"""
        all_columns = self.part_columns.get(part_type, [])
        visibility_config = self.column_visibility.get(part_type, {})
        
        visible_columns = []
        for col in all_columns:
            # Skip Full Part Name (used as tree text) and Part Type (redundant)
            if col in ["Full Part Name", "Part Type"]:
                continue
            
            # Check if column is visible in configuration
            if visibility_config.get(col, True):  # Default to visible if not specified
                visible_columns.append(col)
        
        return visible_columns
    
    def load_part_data(self):
        """Load all part data from CSV files and extract column names"""
        # Choose the correct part types based on HEM status
        part_types_to_use = self.hem_part_types if self.hem_enabled else self.part_types
        
        for part_type, csv_file in part_types_to_use.items():
            # Use HEM file mapping if HEM is enabled
            if self.hem_enabled and part_type in self.hem_file_mappings:
                csv_file = f"HEM/{self.hem_file_mappings[part_type]}"
            
            csv_path = csv_file  # Already includes the correct folder
            
            if os.path.exists(csv_path):
                try:
                    # Read CSV manually to avoid pandas parsing issues
                    import csv
                    with open(csv_path, 'r', encoding='utf-8-sig') as f:
                        reader = csv.DictReader(f)
                        rows = list(reader)
                        self.part_data[part_type] = rows
                        # Extract column names from CSV headers
                        all_columns = reader.fieldnames
                        # Include all CSV columns (don't skip any)
                        if all_columns:
                            self.part_columns[part_type] = all_columns
                        else:
                            self.part_columns[part_type] = []
                except Exception as e:
                    print(f"Error loading {csv_path}: {e}")
                    self.part_data[part_type] = []
                    self.part_columns[part_type] = []
            else:
                print(f"CSV file not found: {csv_path}")
                self.part_data[part_type] = []
                self.part_columns[part_type] = []
    
    def setup_ui(self):
        """Setup the main UI"""
        # Main container
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top controls
        top_frame = tk.Frame(main_frame, bg=self.bg_color)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Style for dark theme
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook', background=self.bg_color)
        style.configure('TNotebook.Tab', background=self.button_bg, foreground=self.fg_color)
        style.map('TNotebook.Tab', background=[('selected', self.select_bg)])
        
        # Create tabs
        self.used_parts_frame = tk.Frame(self.notebook, bg=self.bg_color)
        self.new_parts_frame = tk.Frame(self.notebook, bg=self.bg_color)
        self.builds_frame = tk.Frame(self.notebook, bg=self.bg_color)
        self.jobs_frame = tk.Frame(self.notebook, bg=self.bg_color)
        self.settings_frame = tk.Frame(self.notebook, bg=self.bg_color)
        
        self.notebook.add(self.used_parts_frame, text="Used Parts")
        self.notebook.add(self.new_parts_frame, text="New Parts")
        self.notebook.add(self.builds_frame, text="Builds")
        self.notebook.add(self.jobs_frame, text="Jobs")
        self.notebook.add(self.settings_frame, text="Settings")
        
        # Style for dark theme - global setup
        style = ttk.Style()
        
        # Use 'clam' theme which is more customizable
        style.theme_use('clam')
        
        # Treeview styling
        style.configure('Treeview', background=self.entry_bg, foreground=self.entry_fg, fieldbackground=self.entry_bg)
        style.configure('Treeview.Heading', background=self.button_bg, foreground=self.fg_color, font=('Arial', 10, 'bold'))
        style.map('Treeview', background=[('selected', self.select_bg)])
        
        # Style for notebook tabs
        style.configure('TNotebook', background=self.bg_color)
        style.configure('TNotebook.Tab', background=self.button_bg, foreground=self.fg_color)
        style.map('TNotebook.Tab', background=[('selected', self.select_bg)])
        
        self.setup_used_parts_tab()
        self.setup_new_parts_tab()
        self.setup_builds_tab()
        self.setup_jobs_tab()
        self.setup_settings_tab()
        
        # Bind close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def toggle_hem(self):
        """Toggle HEM parts and reload data"""
        self.hem_enabled = self.hem_settings_var.get()
        self.load_part_data()
        # Clear filters when switching between HEM and base game
        self.clear_all_filters()
        self.refresh_inventory_display()
        self.refresh_builds_display()
        
    def setup_used_parts_tab(self):
        """Setup the used parts tab"""
        # Search frame
        search_frame = tk.Frame(self.used_parts_frame, bg=self.bg_color)
        search_frame.pack(fill=tk.X, pady=(5, 10), padx=5)
        
        tk.Label(search_frame, text="Search Parts:", bg=self.bg_color, fg=self.fg_color).pack(side=tk.LEFT, padx=(0, 10))
        
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, bg=self.entry_bg, fg=self.entry_fg, width=40)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.search_var.trace('w', self.on_search_change)
        
        # Suggestions frame
        self.suggestions_frame = tk.Frame(search_frame, bg=self.bg_color)
        self.suggestions_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        self.suggestions_listbox = tk.Listbox(self.suggestions_frame, bg=self.entry_bg, fg=self.entry_fg, height=5, width=50)
        self.suggestions_listbox.pack()
        self.suggestions_listbox.bind('<Double-Button-1>', self.on_suggestion_double_click)
        
        # Tip frame with close button underneath
        if not self.tips_dismissed.get("double_click_add", False):
            self.tip_frame = tk.Frame(self.used_parts_frame, bg=self.tip_bg, relief=tk.RAISED, bd=1)
            self.tip_frame.pack(fill=tk.X, pady=(5, 10), padx=5)
            
            tip_label = tk.Label(self.tip_frame, 
                               text="💡 Double-click any part to copy its full name to clipboard",
                               bg=self.tip_bg, fg=self.tip_fg, wraplength=800, justify=tk.LEFT)
            tip_label.pack(side=tk.LEFT, padx=10, pady=8)
            
            close_tip_btn = tk.Button(self.tip_frame, text="X", command=self.hide_tip,
                                     bg=self.tip_bg, fg=self.tip_fg, bd=0, width=2)
            close_tip_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        else:
            # Create hidden tip frame for consistency
            self.tip_frame = tk.Frame(self.used_parts_frame, bg=self.tip_bg, relief=tk.RAISED, bd=1)
        
        # Part type tabs
        self.used_parts_notebook = ttk.Notebook(self.used_parts_frame)
        self.used_parts_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.used_parts_frames = {}
        self.used_parts_trees = {}
        self.used_parts_filter_frames = {}  # Store filter frames for each part type
        
        for part_type in self.part_types.keys():
            frame = tk.Frame(self.used_parts_notebook, bg=self.bg_color)
            self.used_parts_notebook.add(frame, text=part_type)
            self.used_parts_frames[part_type] = frame
            
            # Add padding to each part frame
            inner_frame = tk.Frame(frame, bg=self.bg_color)
            inner_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            self.setup_part_table_with_filters(inner_frame, part_type, "used")
        
        # Delete all button
        delete_frame = tk.Frame(self.used_parts_frame, bg=self.bg_color)
        delete_frame.pack(fill=tk.X, pady=(10, 5), padx=5)
        
        tk.Button(delete_frame, text="Delete All Parts", command=self.delete_all_parts,
                 bg=self.warning_bg, fg=self.warning_fg).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Clear all filters button
        self.clear_filters_btn = tk.Button(delete_frame, text="Clear All Filters", command=self.clear_all_filters,
                                          bg=self.button_bg, fg=self.button_fg)
        self.clear_filters_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Status bar
        self.status_label = tk.Label(self.used_parts_frame, text="", bg=self.bg_color, fg=self.fg_color)
        self.status_label.pack(fill=tk.X, pady=(0, 5), padx=5)
        
    def setup_new_parts_tab(self):
        """Setup the new parts tab"""
        # Search frame
        search_frame = tk.Frame(self.new_parts_frame, bg=self.bg_color)
        search_frame.pack(fill=tk.X, pady=(5, 10), padx=5)
        
        tk.Label(search_frame, text="Search Parts:", bg=self.bg_color, fg=self.fg_color).pack(side=tk.LEFT, padx=(0, 10))
        
        self.new_search_var = tk.StringVar()
        self.new_search_entry = tk.Entry(search_frame, textvariable=self.new_search_var, bg=self.entry_bg, fg=self.entry_fg, width=40)
        self.new_search_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.new_search_var.trace('w', self.on_new_search_change)
        
        # Suggestions frame
        self.new_suggestions_frame = tk.Frame(search_frame, bg=self.bg_color)
        self.new_suggestions_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        self.new_suggestions_listbox = tk.Listbox(self.new_suggestions_frame, bg=self.entry_bg, fg=self.entry_fg, height=5, width=50)
        self.new_suggestions_listbox.pack()
        self.new_suggestions_listbox.bind('<Double-Button-1>', self.on_new_suggestion_double_click)
        
        # Part type tabs
        self.new_parts_notebook = ttk.Notebook(self.new_parts_frame)
        self.new_parts_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.new_parts_frames = {}
        self.new_parts_trees = {}
        self.new_parts_filter_frames = {}  # Store filter frames for each part type
        
        for part_type in self.part_types.keys():
            frame = tk.Frame(self.new_parts_notebook, bg=self.bg_color)
            self.new_parts_notebook.add(frame, text=part_type)
            self.new_parts_frames[part_type] = frame
            
            # Add padding to each part frame
            inner_frame = tk.Frame(frame, bg=self.bg_color)
            inner_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            self.setup_part_table_with_filters(inner_frame, part_type, "new")
        
        # Delete all button
        delete_frame = tk.Frame(self.new_parts_frame, bg=self.bg_color)
        delete_frame.pack(fill=tk.X, pady=(10, 5), padx=5)
        
        tk.Button(delete_frame, text="Delete All Parts", command=self.delete_all_new_parts,
                 bg=self.warning_bg, fg=self.warning_fg).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Clear all filters button
        self.new_clear_filters_btn = tk.Button(delete_frame, text="Clear All Filters", command=self.clear_all_new_filters,
                                          bg=self.button_bg, fg=self.button_fg)
        self.new_clear_filters_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Status bar
        self.new_status_label = tk.Label(self.new_parts_frame, text="", bg=self.bg_color, fg=self.fg_color)
        self.new_status_label.pack(fill=tk.X, pady=(0, 5), padx=5)
        
        self.refresh_inventory_display()
        
    def setup_part_table_with_filters(self, parent, part_type, inventory_type="used"):
        """Setup table with Amazon-style accordion filter panel"""
        # Initialize filters for this part type
        if part_type not in self.current_filters:
            self.current_filters[part_type] = {}
        
        # Initialize filter controls for this part type
        if part_type not in self.filter_controls:
            self.filter_controls[part_type] = {}
        
        # Store accordion filters for this part type
        if part_type not in self.accordion_filters:
            self.accordion_filters[part_type] = []
        
        # Create main container with filter panel and treeview
        main_container = tk.Frame(parent, bg=self.bg_color)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create filter panel (left sidebar)
        filter_panel = tk.Frame(main_container, bg=self.button_bg, relief=tk.RAISED, bd=1, width=250)
        filter_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        filter_panel.pack_propagate(False)  # Maintain fixed width
        
        # Filter panel header
        filter_header = tk.Label(filter_panel, text=f"Filters - {part_type}", 
                               bg=self.button_bg, fg=self.fg_color, 
                               font=('Arial', 10, 'bold'))
        filter_header.pack(fill=tk.X, padx=10, pady=10)
        
        # Clear filters button
        clear_btn = tk.Button(filter_panel, text="Clear All Filters", 
                            command=lambda: self.clear_all_filters_for_type(part_type),
                            bg=self.warning_bg, fg=self.warning_fg, width=20)
        clear_btn.pack(padx=10, pady=(0, 10))
        
        # Create scrollable filter content
        filter_canvas = tk.Canvas(filter_panel, bg=self.button_bg, highlightthickness=0, height=400)
        filter_scrollbar = tk.Scrollbar(filter_panel, orient=tk.VERTICAL, command=filter_canvas.yview)
        filter_canvas.configure(yscrollcommand=filter_scrollbar.set)
        
        # Pack scrollbar first to ensure it's visible
        filter_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10))
        filter_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Filter content frame
        filter_content_frame = tk.Frame(filter_canvas, bg=self.button_bg)
        filter_canvas.create_window((0, 0), window=filter_content_frame, anchor='nw')
        
        # Create treeview container (right side)
        tree_container = tk.Frame(main_container, bg=self.bg_color)
        tree_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create scrollbars
        v_scrollbar = tk.Scrollbar(tree_container, orient=tk.VERTICAL)
        h_scrollbar = tk.Scrollbar(tree_container, orient=tk.HORIZONTAL)
        
        # Define treeview columns using visible columns only
        visible_columns = self.get_visible_columns(part_type)
        add_text = "[Add]" if inventory_type == "used" else "[Add to Job]"
        columns = [add_text, "Delete"] + visible_columns
        
        # Initialize column configurations
        if part_type not in self.column_configs:
            self.column_configs[part_type] = {}
        for col in columns[2:]:
            self.column_configs[part_type][col] = {"width": 120, "anchor": 'w'}
        
        # Create accordion filters for each visible column only
        for i, col in enumerate(visible_columns):
            # Get unique values for this column (limited to 50 most common)
            unique_values = self.get_unique_column_values(part_type, col)
            
            # Only create filter if there are values to filter
            if unique_values:
                # Create accordion filter
                accordion = AccordionFilter(filter_content_frame, col, unique_values, 
                                         lambda title, values: self.on_accordion_filter_change(part_type, title, values))
                accordion.frame.pack(fill=tk.X, pady=2)
                
                self.accordion_filters[part_type].append(accordion)
                self.filter_controls[part_type][col] = accordion
        
        # Update canvas scroll region after all filters are created
        filter_content_frame.update_idletasks()
        
        # Force canvas to update scroll region
        def update_scroll_region():
            filter_canvas.configure(scrollregion=filter_canvas.bbox("all"))
        
        # Update immediately and also bind for future changes
        update_scroll_region()
        filter_content_frame.bind('<Configure>', lambda e: update_scroll_region())
        
        # Create treeview
        tree = ttk.Treeview(tree_container, columns=columns, show='headings', height=15, displaycolumns=columns)
        tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Disable column resizing by binding events
        def prevent_resize(event):
            return "break"
        
        # Bind to prevent column resizing
        tree.bind("<Button-1>", prevent_resize)
        tree.bind("<B1-Motion>", prevent_resize)
        tree.bind("<ButtonRelease-1>", prevent_resize)
        
        # Configure scrollbars
        v_scrollbar.configure(command=tree.yview)
        h_scrollbar.configure(command=tree.xview)
        
        # Grid layout for treeview and scrollbars
        tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
        
        # Configure columns
        add_text_width = int(100 * self.text_size_multiplier)
        delete_width = int(60 * self.text_size_multiplier)
        
        tree.heading(add_text, text=add_text)
        tree.column(add_text, width=add_text_width, minwidth=max(50, add_text_width // 2), anchor='center')
        tree.heading("Delete", text="Delete")
        tree.column("Delete", width=delete_width, minwidth=max(50, delete_width // 2), anchor='center')
        
        # Configure remaining columns with proper widths from configuration
        for col in columns[2:]:
            # Use display name for header if available, otherwise use column name
            display_name = self.column_display_names.get(col, col)
            tree.heading(col, text=display_name, command=lambda c=col, pt=part_type: self.sort_column(tree, c, pt))
            
            # Get width from column_widths configuration, with fallback defaults
            if part_type in self.column_widths and col in self.column_widths[part_type]:
                base_width = self.column_widths[part_type][col]
                # Scale width by text size multiplier
                scaled_width = int(base_width * self.text_size_multiplier)
                minwidth = max(50, scaled_width // 2)  # Minimum width is half of scaled width
                # Determine anchor based on column type
                if col in ["Price", "Sell Price", "Wattage", "Frequency", "Size", "VRAM (GB)", "Cores", "Number", "Size each (GB)", "Size (GB)"]:
                    anchor = 'center'
                else:
                    anchor = 'w'
                tree.column(col, width=scaled_width, minwidth=minwidth, anchor=anchor)
            else:
                # Fallback to original logic if column not in configuration
                base_width = 120  # Default base width
                if col in ["Manufacturer", "Part Name", "Full Part Name"]:
                    base_width = 150
                elif col in ["Price", "Sell Price", "Wattage", "Frequency", "Size"]:
                    base_width = 100
                
                # Scale width by text size multiplier
                scaled_width = int(base_width * self.text_size_multiplier)
                minwidth = max(50, scaled_width // 2)
                
                if col in ["Price", "Sell Price", "Wattage", "Frequency", "Size"]:
                    anchor = 'center'
                else:
                    anchor = 'w'
                tree.column(col, width=scaled_width, minwidth=minwidth, anchor=anchor)
        
        # Bind mouse wheel for scrolling
        def on_mousewheel(event):
            if event.state & 0x0001:  # Shift key
                tree.xview_scroll(int(-1*(event.delta/120)), "units")
            else:
                tree.yview_scroll(int(-1*(event.delta/120)), "units")
        
        tree.bind('<MouseWheel>', on_mousewheel)
        tree.bind('<Button-4>', lambda e: tree.yview_scroll(-1, "units"))
        tree.bind('<Button-5>', lambda e: tree.yview_scroll(1, "units"))
        
        # Bind double-click for copying part name
        tree.bind('<Double-Button-1>', lambda e: self.on_tree_double_click(e, part_type, inventory_type))
        
        # Explicitly hide the tree column (#0)
        tree.column('#0', width=1, stretch=False, minwidth=1)
        tree.heading('#0', text='', anchor='w')
        
        # Store tree reference with inventory type
        tree_key = f"{inventory_type}_{part_type}"
        self.part_trees[tree_key] = tree
        
    def on_new_search_change(self, *args):
        """Handle new parts search input changes"""
        search_text = self.new_search_var.get().lower()
        
        if not search_text:
            self.new_suggestions_listbox.delete(0, tk.END)
            return
        
        # Get all parts from all types
        all_parts = []
        for part_type, parts in self.part_data.items():
            for part in parts:
                if 'Full Part Name' in part:
                    all_parts.append((part_type, part['Full Part Name']))
        
        # Split search text into individual words
        search_words = search_text.split()
        
        # Filter parts by search text - all words must be present (but in any order)
        suggestions = []
        for part_type, part_name in all_parts:
            part_name_lower = part_name.lower()
            # Check if all search words are present in the part name
            if all(word in part_name_lower for word in search_words):
                suggestions.append((part_type, part_name))
        
        # Update suggestions listbox
        self.new_suggestions_listbox.delete(0, tk.END)
        for part_type, part_name in suggestions[:20]:  # Limit to 20 suggestions
            self.new_suggestions_listbox.insert(tk.END, f"[{part_type}] {part_name}")
        
        self.selected_part_suggestions = suggestions
        
    def on_new_suggestion_double_click(self, event):
        """Handle double-click on new parts suggestion"""
        selection = self.new_suggestions_listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.selected_part_suggestions):
                part_type, part_name = self.selected_part_suggestions[index]
                self.add_part_to_new_parts_inventory(part_type, part_name)
                
    def add_part_to_new_parts_inventory(self, part_type, part_name):
        """Add a part to new parts inventory"""
        # Find part data
        part_data = None
        for part in self.part_data.get(part_type, []):
            if part.get('Full Part Name') == part_name:
                part_data = part
                break
        
        if not part_data:
            messagebox.showerror("Error", f"Part not found: {part_name}")
            return
        
        # Create inventory item
        inventory_item = {
            "id": len(self.new_parts_inventory) + 1000,  # Use different ID range
            "type": part_type,
            "name": part_name,
            "data": part_data,
            "status": "available",
            "added_date": datetime.now().isoformat()
        }
        
        self.new_parts_inventory.append(inventory_item)
        self.refresh_new_parts_display()
        self.save_state()
        
        # Clear search
        self.new_search_var.set("")
        
    def delete_all_new_parts(self):
        """Delete all parts from new parts inventory"""
        if messagebox.askyesno("Confirm Delete All", "Are you sure you want to delete ALL parts from new parts inventory? This cannot be undone!"):
            self.new_parts_inventory = []
            self.refresh_new_parts_display()
            self.save_state()
            
    def clear_all_new_filters(self):
        """Clear all filters for new parts"""
        self.current_filters = {}
        self.refresh_new_parts_display()
        
    def refresh_new_parts_display(self):
        """Refresh new parts display with filtering"""
        for part_type, tree in self.new_parts_trees.items():
            # Clear existing items
            for item in tree.get_children():
                tree.delete(item)
            
            # Get inventory items of this type
            type_inventory = [item for item in self.new_parts_inventory if item["type"] == part_type]
            
            # Apply filters
            filtered_items = self.apply_filters_to_items(type_inventory, part_type)
            
            # Sort items
            sorted_items = self.sort_items(filtered_items, part_type)
            
            # Add items to tree
            for item in sorted_items:
                # Create action buttons text
                add_text = "[Add to Job]"
                delete_text = "[X]"
                
                # Get other column values (use only visible columns)
                visible_columns = self.get_visible_columns(part_type)
                values = [add_text, delete_text]
                
                # Use only visible columns for values
                for col in visible_columns:
                    value = item["data"].get(col, "")
                    if value == "":
                        value = item["data"].get(col.replace(" ", "_"), "")
                    values.append(value)
                
                # Insert item with all data (use "Full Part Name" as tree text)
                part_name = item["data"].get("Full Part Name", item["name"])
                tree_item = tree.insert('', 'end', text=part_name, values=tuple(values), tags=(str(item["id"]),))
            
            # Bind click events for action buttons
            tree.bind('<Button-1>', lambda e, pt=part_type: self.on_new_tree_click(e, pt))
        
        # Update status
        self.update_new_status_bar()
        
    def on_new_tree_click(self, event, part_type):
        """Handle clicks on new parts tree for action buttons"""
        tree_key = f"new_{part_type}"
        tree = self.part_trees[tree_key]
        
        # Get clicked item and column
        item_id = tree.identify_row(event.y)
        column_id = tree.identify_column(event.x)
        
        if not item_id:
            return
        
        # Get the inventory item from tags
        item_tags = tree.item(item_id, "tags")
        if not item_tags:
            return
        
        inventory_item = None
        for item in self.new_parts_inventory:
            if str(item["id"]) == item_tags[0]:
                inventory_item = item
                break
        
        if not inventory_item:
            return
        
        # Check which column was clicked
        if column_id == "#1":  # Add to Job column
            self.add_part_to_current_job(inventory_item)
        elif column_id == "#2":  # Delete column
            self.delete_new_parts_item(inventory_item)
        # Other columns don't need special handling
        
    def delete_new_parts_item(self, inventory_item):
        """Delete item from new parts inventory"""
        if messagebox.askyesno("Confirm", f"Delete {inventory_item['name']} from new parts inventory?"):
            self.new_parts_inventory.remove(inventory_item)
            self.refresh_new_parts_display()
            self.save_state()
            
    def add_part_to_current_job(self, inventory_item):
        """Add part to currently selected job"""
        messagebox.showinfo("Info", "Job functionality will be implemented next!")
        
    def update_new_status_bar(self):
        """Update the new parts status bar"""
        total_parts = len(self.new_parts_inventory)
        total_available = len([i for i in self.new_parts_inventory if i["status"] == "available"])
        
        # Count filtered items
        total_filtered = 0
        has_filters = False
        
        for part_type, tree in self.new_parts_trees.items():
            items = tree.get_children()
            total_filtered += len(items)
            if part_type in self.current_filters and self.current_filters[part_type]:
                has_filters = True
        
        # Create status text
        if has_filters:
            status_text = f"Showing {total_filtered} of {total_parts} components (filtered) | Available: {total_available}"
        else:
            status_text = f"Showing {total_parts} of {total_parts} components | Available: {total_available}"
        
        self.new_status_label.config(text=status_text)
        
    def setup_jobs_tab(self):
        """Setup the jobs tab"""
        # Jobs tab tip
        if not self.tips_dismissed.get("jobs_tab", False):
            jobs_tip_frame = tk.Frame(self.jobs_frame, bg=self.tip_bg, relief=tk.RAISED, bd=1)
            jobs_tip_frame.pack(fill=tk.X, pady=(5, 10), padx=5)
            
            jobs_tip_label = tk.Label(jobs_tip_frame, 
                                     text="💡 This section is designed to help you build PC's to complete email jobs. It will only take parts from the New Parts inventory.",
                                     bg=self.tip_bg, fg=self.tip_fg, wraplength=800, justify=tk.LEFT)
            jobs_tip_label.pack(side=tk.LEFT, padx=10, pady=8)
            
            jobs_close_btn = tk.Button(jobs_tip_frame, text="X", 
                                      command=lambda: self.dismiss_tip("jobs_tab", jobs_tip_frame),
                                      bg=self.tip_bg, fg=self.tip_fg, bd=0, width=2)
            jobs_close_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Jobs management frame
        jobs_management_frame = tk.Frame(self.jobs_frame, bg=self.bg_color)
        jobs_management_frame.pack(fill=tk.X, pady=(5, 10), padx=5)
        
        # First row: Jobs label and dropdown
        top_row_frame = tk.Frame(jobs_management_frame, bg=self.bg_color)
        top_row_frame.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(top_row_frame, text="Jobs:", bg=self.bg_color, fg=self.fg_color).pack(side=tk.LEFT, padx=(0, 10))
        
        self.jobs_listbox = ttk.Combobox(top_row_frame, state="readonly", width=50)
        self.jobs_listbox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.jobs_listbox.bind('<<ComboboxSelected>>', self.on_job_select)
        
        # Second row: Job control buttons - horizontal layout
        button_frame = tk.Frame(jobs_management_frame, bg=self.bg_color)
        button_frame.pack(fill=tk.X)
        
        tk.Button(button_frame, text="New Job", command=self.new_job,
                 bg=self.button_bg, fg=self.button_fg).pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="Rename Job", command=self.rename_job,
                 bg=self.button_bg, fg=self.button_fg).pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="Delete Job", command=self.delete_job,
                 bg=self.button_bg, fg=self.button_fg).pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="Complete Job", command=self.complete_job,
                 bg=self.warning_bg, fg=self.warning_fg).pack(side=tk.LEFT, padx=2)
        
        # Job details frame with scrollbar
        job_details_container = tk.Frame(self.jobs_frame, bg=self.bg_color)
        job_details_container.pack(fill=tk.BOTH, expand=True)
        
        # Create canvas and scrollbar for job details
        job_canvas = tk.Canvas(job_details_container, bg=self.bg_color, highlightthickness=0)
        job_scrollbar = ttk.Scrollbar(job_details_container, orient="vertical", command=job_canvas.yview)
        self.job_details_frame = tk.Frame(job_canvas, bg=self.bg_color)
        
        # Configure scrolling
        self.job_details_frame.bind(
            "<Configure>",
            lambda e: job_canvas.configure(scrollregion=job_canvas.bbox("all"))
        )
        
        job_canvas.configure(yscrollcommand=job_scrollbar.set)
        
        # Pack canvas and scrollbar
        job_canvas.pack(side="left", fill="both", expand=True)
        job_scrollbar.pack(side="right", fill="y")
        
        # Create window in canvas
        job_canvas.create_window((0, 0), window=self.job_details_frame, anchor="nw")
        
        # Bind mousewheel to canvas
        def _on_job_mousewheel(event):
            job_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        job_canvas.bind("<MouseWheel>", _on_job_mousewheel)
        
        self.refresh_jobs_display()
        
    def setup_settings_tab(self):
        """Setup the settings tab"""
        # Accessibility settings frame
        accessibility_frame = tk.LabelFrame(self.settings_frame, text="Accessibility", bg=self.bg_color, fg=self.fg_color)
        accessibility_frame.pack(fill=tk.X, pady=(10, 5), padx=10)
        
        # Text size setting
        text_size_frame = tk.Frame(accessibility_frame, bg=self.bg_color)
        text_size_frame.pack(fill=tk.X, pady=5, padx=10)
        
        tk.Label(text_size_frame, text="Text Size:", bg=self.bg_color, fg=self.fg_color).pack(side=tk.LEFT, padx=(0, 10))
        
        self.text_size_var = tk.StringVar()
        text_sizes = ["Small", "Medium", "Large", "X Large"]
        
        # Set initial value based on loaded setting
        if self.text_size_multiplier == 1.0:
            self.text_size_var.set("Small")
        elif self.text_size_multiplier == 1.5:
            self.text_size_var.set("Medium")
        elif self.text_size_multiplier == 2.0:
            self.text_size_var.set("Large")
        elif self.text_size_multiplier == 3.0:
            self.text_size_var.set("X Large")
        else:
            self.text_size_var.set("Small")  # Default fallback
            
        text_size_dropdown = ttk.Combobox(text_size_frame, textvariable=self.text_size_var, 
                                         values=text_sizes, state="readonly", width=15)
        text_size_dropdown.pack(side=tk.LEFT, padx=(0, 10))
        text_size_dropdown.bind('<<ComboboxSelected>>', self.update_text_size)
        
        # Mod settings frame
        mod_frame = tk.LabelFrame(self.settings_frame, text="Mod Settings", bg=self.bg_color, fg=self.fg_color)
        mod_frame.pack(fill=tk.X, pady=(5, 10), padx=10)
        
        # HEM setting
        hem_settings_frame = tk.Frame(mod_frame, bg=self.bg_color)
        hem_settings_frame.pack(fill=tk.X, pady=5, padx=10)
        
        self.hem_settings_var = tk.BooleanVar(value=self.hem_enabled)
        hem_cb = tk.Checkbutton(hem_settings_frame, text="HEM (Hardware Expansion Mod)", variable=self.hem_settings_var,
                               bg=self.bg_color, fg=self.fg_color, selectcolor=self.select_bg,
                               command=self.toggle_hem_settings)
        hem_cb.pack(side=tk.LEFT, padx=(0, 10))
        
        # Tips management frame
        tips_frame = tk.LabelFrame(self.settings_frame, text="Tips Management", bg=self.bg_color, fg=self.fg_color)
        tips_frame.pack(fill=tk.X, pady=(5, 10), padx=10)
        
        reset_tips_btn = tk.Button(tips_frame, text="Reset Tips", command=self.reset_all_tips,
                                  bg=self.button_bg, fg=self.button_fg, width=15)
        reset_tips_btn.pack(pady=10, padx=10)
        
    def update_text_size(self, event=None):
        """Update text size based on selection"""
        size_map = {
            "Small": 1.0,
            "Medium": 1.5,
            "Large": 2.0,
            "X Large": 3.0
        }
        
        old_multiplier = self.text_size_multiplier
        self.text_size_multiplier = size_map[self.text_size_var.get()]
        
        # Only refresh if multiplier actually changed
        if old_multiplier != self.text_size_multiplier:
            self.apply_text_size_simple()
            self.refresh_all_column_widths()
            self.save_state()
        
    def refresh_all_column_widths(self):
        """Refresh all column widths with current text size multiplier"""
        # Refresh all inventory displays
        self.refresh_inventory_display()
        
        # Refresh used parts displays
        for part_type in self.part_types.keys():
            tree_key = f"used_{part_type}"
            if tree_key in self.part_trees:
                self.update_tree_column_widths(self.part_trees[tree_key], part_type)
        
        # Refresh new parts displays  
        for part_type in self.part_types.keys():
            tree_key = f"new_{part_type}"
            if tree_key in self.part_trees:
                self.update_tree_column_widths(self.part_trees[tree_key], part_type)
    
    def update_tree_column_widths(self, tree, part_type):
        """Update column widths for a specific tree"""
        # Get the actual columns from the tree
        tree_columns = tree['columns']
        
        # Update action columns if they exist
        if "[Add]" in tree_columns:
            add_text_width = int(100 * self.text_size_multiplier)
            tree.column("[Add]", width=add_text_width, minwidth=max(50, add_text_width // 2), anchor='center')
        
        if "[Add to Job]" in tree_columns:
            add_text_width = int(100 * self.text_size_multiplier)
            tree.column("[Add to Job]", width=add_text_width, minwidth=max(50, add_text_width // 2), anchor='center')
        
        if "Delete" in tree_columns:
            delete_width = int(60 * self.text_size_multiplier)
            tree.column("Delete", width=delete_width, minwidth=max(50, delete_width // 2), anchor='center')
        
        # Update data columns
        for col in tree_columns:
            if col in ["[Add]", "[Add to Job]", "Delete"]:
                continue  # Skip action columns
                
            if part_type in self.column_widths and col in self.column_widths[part_type]:
                base_width = self.column_widths[part_type][col]
                scaled_width = int(base_width * self.text_size_multiplier)
                minwidth = max(50, scaled_width // 2)
                
                if col in ["Price", "Sell Price", "Wattage", "Frequency", "Size", "VRAM (GB)", "Cores", "Number", "Size each (GB)", "Size (GB)"]:
                    anchor = 'center'
                else:
                    anchor = 'w'
                tree.column(col, width=scaled_width, minwidth=minwidth, anchor=anchor)
            else:
                # Fallback logic
                base_width = 120
                if col in ["Manufacturer", "Part Name", "Full Part Name"]:
                    base_width = 150
                elif col in ["Price", "Sell Price", "Wattage", "Frequency", "Size"]:
                    base_width = 100
                
                scaled_width = int(base_width * self.text_size_multiplier)
                minwidth = max(50, scaled_width // 2)
                
                if col in ["Price", "Sell Price", "Wattage", "Frequency", "Size"]:
                    anchor = 'center'
                else:
                    anchor = 'w'
                tree.column(col, width=scaled_width, minwidth=minwidth, anchor=anchor)
        
    def toggle_hem_settings(self):
        """Toggle HEM from settings"""
        self.hem_enabled = self.hem_settings_var.get()
        self.load_part_data()
        self.clear_all_filters()
        self.save_state()
        
    def reset_all_tips(self):
        """Reset all dismissed tips"""
        self.tips_dismissed = {
            "double_click_add": False,
            "builds_tab": False,
            "jobs_tab": False,
            "story_job": False
        }
        self.show_tip = True  # Reset the main tip
        messagebox.showinfo("Tips Reset", "All tips have been reset and will appear again.")
        self.save_state()
        
    def ask_string_dark(self, title, prompt, initialvalue=None):
        """Custom dark theme string input dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("400x150")
        dialog.configure(bg=self.bg_color)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (150 // 2)
        dialog.geometry(f"400x150+{x}+{y}")
        
        # Prompt label
        tk.Label(dialog, text=prompt, bg=self.bg_color, fg=self.fg_color,
                font=('Arial', 12)).pack(pady=(20, 10))
        
        # Entry field
        entry_var = tk.StringVar(value=initialvalue or "")
        entry = tk.Entry(dialog, textvariable=entry_var, bg=self.entry_bg, fg=self.entry_fg,
                      font=('Arial', 12), width=30)
        entry.pack(pady=(0, 20))
        entry.focus()
        entry.select_range(0, tk.END)
        
        # Button frame
        button_frame = tk.Frame(dialog, bg=self.bg_color)
        button_frame.pack(pady=(0, 20))
        
        result = None
        
        def ok_clicked():
            nonlocal result
            result = entry_var.get().strip()
            if result:
                dialog.destroy()
        
        def cancel_clicked():
            nonlocal result
            result = None
            dialog.destroy()
        
        tk.Button(button_frame, text="OK", command=ok_clicked,
                 bg=self.button_bg, fg=self.button_fg, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=cancel_clicked,
                 bg=self.button_bg, fg=self.button_fg, width=10).pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key to OK
        entry.bind('<Return>', lambda e: ok_clicked())
        dialog.bind('<Escape>', lambda e: cancel_clicked())
        
        # Wait for dialog to close
        dialog.wait_window()
        return result
    
    def new_job(self):
        """Create new job"""
        job_name = self.ask_string_dark("New Job", "Enter client name:")
        if job_name:
            new_job = {
                "id": len(self.jobs) + 1,
                "name": job_name,
                "budget": 0,
                "actual_budget": 0,
                "story_job": False,
                "job_details": {
                    "new_pc_build": False,
                    "replace_upgrade_parts": False,
                    "threedmark_score": False,
                    "replace_parts": {
                        "CPU": False,
                        "GPU": False,
                        "CPU Cooler": False,
                        "Motherboard": False,
                        "RAM": False,
                        "Power Supply": False,
                        "Storage": False
                    },
                    "bonus_objectives": {
                        "clean_out_dust": False,
                        "remove_viruses": False,
                        "new_cables": False,
                        "brand_preference": False
                    },
                    "cable_type": "",
                    "brand_name": ""
                },
                "original_parts": {},
                "replacement_parts": {},
                "threedmark_score": 0,
                "budget_left": 0
            }
            self.jobs.append(new_job)
            self.refresh_jobs_display()
            self.save_state()
            
    def rename_job(self):
        """Rename selected job"""
        selected_name = self.jobs_listbox.get()
        
        if not selected_name:
            messagebox.showwarning("Warning", "Please select a job first!")
            return
        
        # Find job by name
        job = None
        for j in self.jobs:
            if j["name"] == selected_name:
                job = j
                break
        
        if not job:
            return
        
        new_name = self.ask_string_dark("Rename Job", "Enter new client name:", initialvalue=job["name"])
        if new_name and new_name != job["name"]:
            job["name"] = new_name
            self.refresh_jobs_display()
            self.save_state()
            
    def delete_job(self):
        """Delete selected job"""
        selected_name = self.jobs_listbox.get()
        
        if not selected_name:
            messagebox.showwarning("Warning", "Please select a job first!")
            return
        
        # Find job by name
        job = None
        job_index = -1
        for i, j in enumerate(self.jobs):
            if j["name"] == selected_name:
                job = j
                job_index = i
                break
        
        if not job or job_index == -1:
            return
        
        if messagebox.askyesno("Confirm", f"Delete job for client '{job['name']}'?"):
            self.jobs.pop(job_index)
            self.refresh_jobs_display()
            self.save_state()
            
    def complete_job(self):
        """Complete selected job"""
        selected_name = self.jobs_listbox.get()
        
        if not selected_name:
            messagebox.showwarning("Warning", "Please select a job first!")
            return
        
        # Find job by name
        job = None
        job_index = -1
        for i, j in enumerate(self.jobs):
            if j["name"] == selected_name:
                job = j
                job_index = i
                break
        
        if not job or job_index == -1:
            return
        
        # Count parts used in replacement
        parts_used = []
        for part_type, parts in job["replacement_parts"].items():
            if isinstance(parts, list):
                for part_id in parts:
                    if part_id is not None:
                        parts_used.append(part_id)
            elif parts is not None:
                parts_used.append(parts)
        
        # Confirmation dialog
        confirm_msg = f"This job will be deleted, and the parts used will be removed from your inventory. Proceed?"
        if messagebox.askyesno("Complete Job", confirm_msg):
            # Remove parts from new parts inventory
            for part_id in parts_used:
                for item in self.new_parts_inventory:
                    if item["id"] == part_id:
                        self.new_parts_inventory.remove(item)
                        break
            
            # Delete job
            self.jobs.pop(job_index)
            self.refresh_jobs_display()
            self.refresh_new_parts_display()
            self.save_state()
            
    def on_job_select(self, event):
        """Handle job selection"""
        self.refresh_job_details()
        
    def refresh_jobs_display(self):
        """Refresh jobs dropdown list"""
        job_names = [job["name"] for job in self.jobs]
        self.jobs_listbox['values'] = job_names
        
        # Select first job if available, otherwise clear selection
        if job_names:
            self.jobs_listbox.set(job_names[0])
        else:
            self.jobs_listbox.set("")
        
        self.refresh_job_details()
        
    def refresh_job_details(self):
        """Refresh job details display"""
        selected_name = self.jobs_listbox.get()
        
        if not selected_name or not self.jobs:
            self.clear_job_details()
            return
        
        # Find job by name
        job = None
        for j in self.jobs:
            if j["name"] == selected_name:
                job = j
                break
        
        if not job:
            self.clear_job_details()
            return
        
        # Clear existing widgets
        for widget in self.job_details_frame.winfo_children():
            widget.destroy()
        
        self.current_job = job
        
        # Calculate font sizes based on text size multiplier
        label_font_size = int(12 * self.text_size_multiplier)  # Increased from 10 to 12
        label_font_size = max(10, min(label_font_size, 18))  # Increased from 8 to 10
        checkbox_font_size = int(11 * self.text_size_multiplier)  # Increased from 9 to 11
        checkbox_font_size = max(9, min(checkbox_font_size, 16))  # Increased from 7 to 9
        
        # Budget section
        budget_frame = tk.LabelFrame(self.job_details_frame, text="BUDGET", bg=self.bg_color, fg=self.fg_color,
                                   font=('Arial', label_font_size, 'bold'))
        budget_frame.pack(fill=tk.X, pady=(0, 10), padx=5)
        
        # Story job section (inside budget box)
        story_job_frame = tk.Frame(budget_frame, bg=self.bg_color)
        story_job_frame.pack(fill=tk.X, padx=10, pady=(5, 5))
        
        story_job_var = tk.BooleanVar(value=job.get("story_job", False))
        story_job_cb = tk.Checkbutton(story_job_frame, text="Story Job", variable=story_job_var,
                                     bg=self.bg_color, fg=self.fg_color, selectcolor=self.select_bg,
                                     font=('Arial', checkbox_font_size),
                                     command=lambda: self.update_story_job(job, story_job_var.get()))
        story_job_cb.pack(side=tk.LEFT)
        
        # Story job help text
        story_help_label = tk.Label(story_job_frame, text="(What's this?)", 
                                   bg=self.bg_color, fg=self.link_color, cursor="hand2",
                                   font=('Arial', checkbox_font_size))
        story_help_label.pack(side=tk.LEFT, padx=(5, 0))
        story_help_label.bind("<Button-1>", lambda e: self.show_story_job_help())
        
        # Budget input frame (inside LabelFrame)
        budget_input_frame = tk.Frame(budget_frame, bg=self.bg_color)
        budget_input_frame.pack(fill=tk.X, padx=10, pady=(0, 5))
        
        # Budget input
        tk.Label(budget_input_frame, text="Budget ($):", bg=self.bg_color, fg=self.fg_color,
                font=('Arial', label_font_size)).pack(side=tk.LEFT, padx=(0, 5))
        
        budget_var = tk.StringVar(value=str(job.get("budget", 0)))
        budget_entry = tk.Entry(budget_input_frame, textvariable=budget_var, bg=self.entry_bg, fg=self.entry_fg, width=20, 
                               font=('Arial', label_font_size))
        budget_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        # Add focus and selection functionality
        budget_entry.bind('<FocusIn>', lambda e: budget_entry.select_range(0, tk.END))
        
        # Actual budget display (whole numbers with commas)
        tk.Label(budget_input_frame, text="Actual Budget:", bg=self.bg_color, fg=self.fg_color,
                font=('Arial', label_font_size)).pack(side=tk.LEFT, padx=(0, 5))
        
        if job.get("story_job", False):
            actual_budget_label = tk.Label(budget_input_frame, text="Unlimited", bg=self.bg_color, fg=self.fg_color,
                                          font=('Arial', label_font_size))
        else:
            actual_budget = int(job.get("budget", 0) * 1.1)  # 10% markup, whole number
            actual_budget_label = tk.Label(budget_input_frame, text=f"${actual_budget:,}", bg=self.bg_color, fg=self.fg_color,
                                          font=('Arial', label_font_size))
        actual_budget_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Budget left display (whole numbers with commas)
        if not job.get("story_job", False):
            budget_left = int(job.get("budget_left", 0))  # Whole number
            budget_left_label = tk.Label(budget_input_frame, text=f"Budget Left: ${budget_left:,}", 
                                       bg=self.bg_color, fg="yellow", font=('Arial', label_font_size, 'bold'))
            budget_left_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # Bind budget change (only on Enter key or focus out)
        budget_entry.bind('<Return>', lambda e: self.update_job_budget(job, budget_var.get()))
        budget_entry.bind('<FocusOut>', lambda e: self.update_job_budget(job, budget_var.get()))
        
        # Job details checkboxes
        details_frame = tk.LabelFrame(self.job_details_frame, text="Job Details", bg=self.bg_color, fg=self.fg_color,
                                     font=('Arial', label_font_size, 'bold'))
        details_frame.pack(fill=tk.X, pady=(0, 10), padx=5)
        
        # Main job checkboxes
        main_frame = tk.Frame(details_frame, bg=self.bg_color)
        main_frame.pack(fill=tk.X, padx=10, pady=5)
        
        new_pc_var = tk.BooleanVar(value=job["job_details"]["new_pc_build"])
        new_pc_cb = tk.Checkbutton(main_frame, text="New PC Build", variable=new_pc_var,
                                  bg=self.bg_color, fg=self.fg_color, selectcolor=self.select_bg,
                                  font=('Arial', checkbox_font_size),
                                  command=lambda: self.update_job_detail(job, "new_pc_build", new_pc_var.get()))
        new_pc_cb.pack(side=tk.LEFT, padx=(0, 20))
        
        replace_var = tk.BooleanVar(value=job["job_details"]["replace_upgrade_parts"])
        replace_cb = tk.Checkbutton(main_frame, text="Replace / Upgrade Part(s)", variable=replace_var,
                                   bg=self.bg_color, fg=self.fg_color, selectcolor=self.select_bg,
                                   font=('Arial', checkbox_font_size),
                                   command=lambda: self.update_job_detail(job, "replace_upgrade_parts", replace_var.get()))
        replace_cb.pack(side=tk.LEFT, padx=(0, 20))
        
        threedmark_var = tk.BooleanVar(value=job["job_details"]["threedmark_score"])
        threedmark_cb = tk.Checkbutton(main_frame, text="3DMark Score", variable=threedmark_var,
                                      bg=self.bg_color, fg=self.fg_color, selectcolor=self.select_bg,
                                      font=('Arial', checkbox_font_size),
                                      command=lambda: self.update_job_detail(job, "threedmark_score", threedmark_var.get()))
        threedmark_cb.pack(side=tk.LEFT)
        
        # Replace parts checkboxes (shown when replace/upgrade is checked)
        self.replace_parts_frame = tk.Frame(details_frame, bg=self.bg_color)
        if job["job_details"]["replace_upgrade_parts"]:
            self.replace_parts_frame.pack(fill=tk.X, padx=10, pady=5)
        
        replace_parts_label = tk.Label(self.replace_parts_frame, text="Parts to Replace/Upgrade:", 
                                     bg=self.bg_color, fg=self.fg_color, font=('Arial', checkbox_font_size, 'bold'))
        replace_parts_label.pack(anchor='w')
        
        replace_checkboxes_frame = tk.Frame(self.replace_parts_frame, bg=self.bg_color)
        replace_checkboxes_frame.pack(fill=tk.X, padx=(20, 0))
        
        self.replace_vars = {}
        for part_type in ["CPU", "GPU", "CPU Cooler", "Motherboard", "RAM", "Power Supply", "Storage"]:
            # Ensure Storage key exists for backward compatibility
            if part_type == "Storage" and part_type not in job["job_details"]["replace_parts"]:
                job["job_details"]["replace_parts"][part_type] = False
            
            var = tk.BooleanVar(value=job["job_details"]["replace_parts"][part_type])
            cb = tk.Checkbutton(replace_checkboxes_frame, text=part_type, variable=var,
                              bg=self.bg_color, fg=self.fg_color, selectcolor=self.select_bg,
                              font=('Arial', checkbox_font_size),
                              command=lambda pt=part_type, v=var: self.update_replace_part(job, pt, v.get()))
            cb.pack(side=tk.LEFT, padx=(0, 10))
            self.replace_vars[part_type] = var
        
        # Bonus objectives
        bonus_frame = tk.LabelFrame(self.job_details_frame, text="Bonus Objectives", bg=self.bg_color, fg=self.fg_color,
                                   font=('Arial', label_font_size, 'bold'))
        bonus_frame.pack(fill=tk.X, pady=(0, 10), padx=5)
        
        bonus_checkboxes_frame = tk.Frame(bonus_frame, bg=self.bg_color)
        bonus_checkboxes_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.bonus_vars = {}
        for bonus in ["clean_out_dust", "remove_viruses", "new_cables", "brand_preference"]:
            display_name = bonus.replace("_", " ").title()
            var = tk.BooleanVar(value=job["job_details"]["bonus_objectives"][bonus])
            cb = tk.Checkbutton(bonus_checkboxes_frame, text=display_name, variable=var,
                              bg=self.bg_color, fg=self.fg_color, selectcolor=self.select_bg,
                              font=('Arial', checkbox_font_size),
                              command=lambda b=bonus, v=var: self.update_bonus_objective(job, b, v.get()))
            cb.pack(side=tk.LEFT, padx=(0, 20))
            self.bonus_vars[bonus] = var
        
        # Bonus objectives sections
        self.bonus_sections_frame = tk.Frame(self.job_details_frame, bg=self.bg_color)
        self.bonus_sections_frame.pack(fill=tk.X, pady=(0, 10), padx=5)
        
        self.create_bonus_sections(job)
        
        # 3DMark Score section
        if job["job_details"]["threedmark_score"]:
            self.create_threedmark_section(job)
        
        # Parts sections
        self.create_parts_sections(job)
        
    def clear_job_details(self):
        """Clear job details display"""
        for widget in self.job_details_frame.winfo_children():
            widget.destroy()
        self.current_job = None
        
    def update_story_job(self, job, is_story):
        """Update story job status"""
        job["story_job"] = is_story
        self.refresh_job_details()
        self.save_state()
        
    def update_job_budget(self, job, budget_str):
        """Update job budget"""
        try:
            # Handle empty string as 0
            if not budget_str or budget_str.strip() == "":
                budget = 0
            else:
                # Remove currency symbols and commas for better input handling
                clean_str = budget_str.replace('$', '').replace(',', '').strip()
                budget = int(float(clean_str))  # Convert to int to remove .0
            
            job["budget"] = budget
            if not job.get("story_job", False):
                job["actual_budget"] = int(budget * 1.1)  # Whole number
                self.calculate_budget_left(job)
                # Update only the budget-related labels without refreshing entire job details
                self.update_budget_display(job)
            self.save_state()
        except ValueError:
            # Don't update if invalid input
            pass
    
    def update_budget_display(self, job):
        """Update only budget-related labels without refreshing entire job details"""
        # Find and update the actual budget and budget left labels
        for widget in self.job_details_frame.winfo_children():
            if isinstance(widget, tk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, tk.Label):
                        text = child.cget("text")
                        if "Actual Budget:" in text or "Budget Left:" in text:
                            # Update the labels
                            if "Actual Budget:" in text:
                                if job.get("story_job", False):
                                    child.config(text="Unlimited")
                                else:
                                    actual_budget = int(job.get("budget", 0) * 1.1)  # Whole number with commas
                                    child.config(text=f"${actual_budget:,}")
                            elif "Budget Left:" in text and not job.get("story_job", False):
                                budget_left = int(job.get("budget_left", 0))  # Whole number with commas
                                child.config(text=f"Budget Left: ${budget_left:,}", fg="yellow", font=('Arial', 10, 'bold'))
                            break
            
    def update_job_detail(self, job, detail, value):
        """Update job detail"""
        job["job_details"][detail] = value
        
        # Handle interdependencies
        if detail == "new_pc_build" and value:
            # Disable replace/upgrade when new build is selected
            job["job_details"]["replace_upgrade_parts"] = False
            # Ensure Storage key exists for backward compatibility
            if "Storage" not in job["job_details"]["replace_parts"]:
                job["job_details"]["replace_parts"]["Storage"] = False
            for part_type in job["job_details"]["replace_parts"]:
                job["job_details"]["replace_parts"][part_type] = False
        elif detail == "replace_upgrade_parts":
            # Show/hide replace parts frame
            if value:
                self.replace_parts_frame.pack(fill=tk.X, padx=10, pady=5)
            else:
                self.replace_parts_frame.pack_forget()
                # Clear all replace part selections
                # Ensure Storage key exists for backward compatibility
                if "Storage" not in job["job_details"]["replace_parts"]:
                    job["job_details"]["replace_parts"]["Storage"] = False
                for part_type in job["job_details"]["replace_parts"]:
                    job["job_details"]["replace_parts"][part_type] = False
        
        self.refresh_job_details()
        
        # Refresh replacement parts display to update locking (only if not New PC Build)
        if hasattr(self, 'replacement_build_slots_frame') and not job["job_details"]["new_pc_build"]:
            try:
                self.create_replacement_build_slots(job)
            except:
                pass  # Frame might not exist
        
        # Refresh new PC build display if applicable
        if hasattr(self, 'new_pc_build_slots_frame') and job["job_details"]["new_pc_build"]:
            try:
                self.create_new_pc_build_slots(job)
            except:
                pass  # Frame might not exist
        
        self.save_state()
        
    def update_replace_part(self, job, part_type, value):
        """Update replace part selection"""
        # Ensure Storage key exists for backward compatibility
        if "Storage" not in job["job_details"]["replace_parts"]:
            job["job_details"]["replace_parts"]["Storage"] = False
        
        job["job_details"]["replace_parts"][part_type] = value
        
        # Refresh replacement parts display to update locking (only if not New PC Build)
        if hasattr(self, 'replacement_build_slots_frame') and not job["job_details"]["new_pc_build"]:
            try:
                self.create_replacement_build_slots(job)
            except:
                pass  # Frame might not exist
        
        # Refresh new PC build display if applicable
        if hasattr(self, 'new_pc_build_slots_frame') and job["job_details"]["new_pc_build"]:
            try:
                self.create_new_pc_build_slots(job)
            except:
                pass  # Frame might not exist
        
        self.save_state()
        
    def update_bonus_objective(self, job, bonus, value):
        """Update bonus objective"""
        job["job_details"]["bonus_objectives"][bonus] = value
        self.create_bonus_sections(job)
        self.save_state()
        
    def create_bonus_sections(self, job):
        """Create bonus objectives sections"""
        # Clear existing bonus sections
        for widget in self.bonus_sections_frame.winfo_children():
            widget.destroy()
        
        # Calculate font sizes based on text size multiplier
        label_font_size = int(12 * self.text_size_multiplier)  # Increased from 10 to 12
        label_font_size = max(10, min(label_font_size, 18))  # Increased from 8 to 10
        checkbox_font_size = int(11 * self.text_size_multiplier)  # Increased from 9 to 11
        checkbox_font_size = max(9, min(checkbox_font_size, 16))  # Increased from 7 to 9
        entry_font_size = int(11 * self.text_size_multiplier)  # Increased from 9 to 11
        entry_font_size = max(9, min(entry_font_size, 16))  # Increased from 7 to 9
        
        # Cable type section
        if job["job_details"]["bonus_objectives"]["new_cables"]:
            cable_frame = tk.Frame(self.bonus_sections_frame, bg=self.bg_color)
            cable_frame.pack(fill=tk.X, pady=(0, 5))
            
            tk.Label(cable_frame, text="Cable Type:", bg=self.bg_color, fg=self.fg_color,
                    font=('Arial', label_font_size)).pack(side=tk.LEFT, padx=(0, 5))
            
            # Search interface for cables
            cable_search_var = tk.StringVar()
            cable_search_entry = tk.Entry(cable_frame, textvariable=cable_search_var, bg=self.entry_bg, fg=self.entry_fg, width=30,
                                         font=('Arial', entry_font_size))
            cable_search_entry.pack(side=tk.LEFT, padx=(0, 10))
            cable_search_var.trace('w', lambda *args: self.on_cable_search_change(job, cable_search_var.get()))
            
            # Suggestions frame
            cable_suggestions_frame = tk.Frame(cable_frame, bg=self.bg_color)
            cable_suggestions_frame.pack(side=tk.LEFT, padx=(0, 20))
            
            cable_suggestions_listbox = tk.Listbox(cable_suggestions_frame, bg=self.entry_bg, fg=self.entry_fg, height=5, width=40,
                                                  font=('Arial', entry_font_size))
            cable_suggestions_listbox.pack()
            cable_suggestions_listbox.bind('<Double-Button-1>', lambda e: self.on_cable_suggestion_double_click(job, cable_search_var, cable_suggestions_listbox))
            
            # Selected cable display
            self.selected_cable_var = tk.StringVar(value=job.get("cable_type", ""))
            selected_cable_label = tk.Label(cable_frame, textvariable=self.selected_cable_var, bg=self.bg_color, fg=self.fg_color, width=30,
                                          font=('Arial', entry_font_size))
            selected_cable_label.pack(side=tk.LEFT, padx=(0, 5))
            
            # Remove cable button
            if job.get("cable_type", ""):
                remove_cable_btn = tk.Button(cable_frame, text="X", command=lambda: self.remove_cable(job),
                                           font=('Arial', entry_font_size),
                                           bg=self.warning_bg, fg=self.warning_fg, width=3)
                remove_cable_btn.pack(side=tk.LEFT, padx=(0, 5))
            
            # Store references
            self.cable_search_var = cable_search_var
            self.cable_suggestions_listbox = cable_suggestions_listbox
            self.cable_suggestions = []
        
        # Reminder section
        reminders = []
        if job["job_details"]["bonus_objectives"]["clean_out_dust"]:
            reminders.append("clean out dust")
        if job["job_details"]["bonus_objectives"]["remove_viruses"]:
            reminders.append("remove viruses")
        
        if reminders:
            reminder_frame = tk.Frame(self.bonus_sections_frame, bg=self.warning_bg)
            reminder_frame.pack(fill=tk.X, pady=(0, 5))
            
            reminder_text = f"Don't forget to {' and '.join(reminders)}!"
            reminder_label = tk.Label(reminder_frame, text=reminder_text, bg=self.warning_bg, fg=self.warning_fg,
                                    font=('Arial', checkbox_font_size))
            reminder_label.pack(side=tk.LEFT, padx=10, pady=5)
            
            # Dismiss button
            dismiss_btn = tk.Button(reminder_frame, text="X", command=lambda: reminder_frame.destroy(),
                                  font=('Arial', checkbox_font_size),
                                  bg=self.warning_bg, fg=self.warning_fg, width=3)
            dismiss_btn.pack(side=tk.RIGHT, padx=5)
        
        # Brand preference section
        if job["job_details"]["bonus_objectives"]["brand_preference"]:
            brand_frame = tk.Frame(self.bonus_sections_frame, bg=self.bg_color)
            brand_frame.pack(fill=tk.X, pady=(0, 5))
            
            tk.Label(brand_frame, text="Brand Preference:", bg=self.bg_color, fg=self.fg_color,
                    font=('Arial', label_font_size)).pack(side=tk.LEFT, padx=(0, 5))
            
            # Search interface for brands
            brand_var = tk.StringVar(value=job.get("brand_name", ""))
            brand_entry = tk.Entry(brand_frame, textvariable=brand_var, bg=self.entry_bg, fg=self.entry_fg, width=30,
                                   font=('Arial', entry_font_size))
            brand_entry.pack(side=tk.LEFT, padx=(0, 10))
            brand_var.trace('w', lambda *args: self.on_brand_search_change(job, brand_var.get()))
            
            # Suggestions frame
            brand_suggestions_frame = tk.Frame(brand_frame, bg=self.bg_color)
            brand_suggestions_frame.pack(side=tk.LEFT, padx=(0, 20))
            
            brand_suggestions_listbox = tk.Listbox(brand_suggestions_frame, bg=self.entry_bg, fg=self.entry_fg, height=5, width=40,
                                                  font=('Arial', entry_font_size))
            brand_suggestions_listbox.pack()
            brand_suggestions_listbox.bind('<Double-Button-1>', lambda e: self.on_brand_suggestion_double_click(job, brand_var, brand_suggestions_listbox))
            
            # Store references
            self.brand_search_var = brand_var
            self.brand_suggestions_listbox = brand_suggestions_listbox
            self.brand_suggestions = []
            
            # Bind brand change
            brand_var.trace('w', lambda *args: self.update_brand_name(job, brand_var.get()))
            
    def on_cable_search_change(self, job, search_text):
        """Handle cable search input changes"""
        search_text = search_text.lower()
        
        if not search_text:
            self.cable_suggestions_listbox.delete(0, tk.END)
            return
        
        # Get all cable parts from part_data
        cable_parts = []
        if "CABLE" in self.part_data and self.part_data["CABLE"]:
            for part in self.part_data["CABLE"]:
                # Try multiple possible name fields
                cable_name = None
                if 'Full Part Name' in part and part['Full Part Name']:
                    cable_name = part['Full Part Name']
                elif 'Part Name' in part and part['Part Name']:
                    cable_name = part['Part Name']
                elif 'Name' in part and part['Name']:
                    cable_name = part['Name']
                
                if cable_name:
                    cable_parts.append(cable_name)
        
        # If no cable data found, show message
        if not cable_parts:
            self.cable_suggestions_listbox.delete(0, tk.END)
            if self.hem_enabled:
                self.cable_suggestions_listbox.insert(tk.END, "No cable data available")
            else:
                self.cable_suggestions_listbox.insert(tk.END, "Cables only available in HEM mode")
            return
        
        # Filter cables by search text
        suggestions = []
        for cable_name in cable_parts:
            if search_text in cable_name.lower():
                suggestions.append(cable_name)
        
        # Update suggestions listbox (limit to 20)
        self.cable_suggestions_listbox.delete(0, tk.END)
        if suggestions:
            for cable_name in suggestions[:20]:
                self.cable_suggestions_listbox.insert(tk.END, cable_name)
        else:
            self.cable_suggestions_listbox.insert(tk.END, "No matching cables found")
        
        self.cable_suggestions = suggestions
        
    def on_cable_suggestion_double_click(self, job, search_var, listbox):
        """Handle double-click on cable suggestion"""
        selection = listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.cable_suggestions):
                cable_name = self.cable_suggestions[index]
                self.add_cable_to_job(job, cable_name)
                
    def add_cable_to_job(self, job, cable_name):
        """Add cable to job"""
        # Only one cable allowed, so replace any existing cable
        job["cable_type"] = cable_name
        self.selected_cable_var.set(cable_name)
        
        # Clear search
        self.cable_search_var.set("")
        self.cable_suggestions_listbox.delete(0, tk.END)
        
        # Refresh bonus sections to show remove button
        self.create_bonus_sections(job)
        
        self.save_state()
        
    def remove_cable(self, job):
        """Remove cable from job"""
        job["cable_type"] = ""
        self.selected_cable_var.set("")
        
        # Refresh bonus sections to hide remove button
        self.create_bonus_sections(job)
        
        self.save_state()
        
    def on_brand_search_change(self, job, search_text):
        """Handle brand search input changes"""
        search_text = search_text.lower()
        
        # Check if brand suggestions listbox exists
        if not hasattr(self, 'brand_suggestions_listbox') or self.brand_suggestions_listbox is None:
            return
            
        if not search_text:
            self.brand_suggestions_listbox.delete(0, tk.END)
            return
        
        # Get all manufacturers from part_data
        manufacturers = set()
        for part_type, parts in self.part_data.items():
            if parts:
                for part in parts:
                    if 'Manufacturer' in part and part['Manufacturer']:
                        manufacturers.add(part['Manufacturer'])
        
        # Filter manufacturers by search text
        suggestions = []
        for manufacturer in sorted(manufacturers):
            if search_text in manufacturer.lower():
                suggestions.append(manufacturer)
        
        # Update suggestions listbox (limit to 20)
        if hasattr(self, 'brand_suggestions_listbox') and self.brand_suggestions_listbox is not None:
            self.brand_suggestions_listbox.delete(0, tk.END)
            if suggestions:
                for manufacturer in suggestions[:20]:
                    self.brand_suggestions_listbox.insert(tk.END, manufacturer)
            else:
                self.brand_suggestions_listbox.insert(tk.END, "No matching brands found")
        
        self.brand_suggestions = suggestions
        
    def on_brand_suggestion_double_click(self, job, search_var, listbox):
        """Handle double-click on brand suggestion"""
        selection = listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.brand_suggestions):
                brand_name = self.brand_suggestions[index]
                self.add_brand_to_job(job, brand_name)
                
    def add_brand_to_job(self, job, brand_name):
        """Add brand to job"""
        job["brand_name"] = brand_name
        
        # Update brand search variable if it exists
        if hasattr(self, 'brand_search_var') and self.brand_search_var is not None:
            self.brand_search_var.set(brand_name)
        
        # Clear suggestions if listbox exists
        if hasattr(self, 'brand_suggestions_listbox') and self.brand_suggestions_listbox is not None:
            self.brand_suggestions_listbox.delete(0, tk.END)
        
        self.save_state()
            
    def create_threedmark_section(self, job):
        """Create 3DMark score section"""
        threedmark_frame = tk.LabelFrame(self.job_details_frame, text="3DMark Score", bg=self.bg_color, fg=self.fg_color)
        threedmark_frame.pack(fill=tk.X, pady=(0, 10), padx=5)
        
        score_label = tk.Label(threedmark_frame, text=f"Score: {job.get('threedmark_score', 0)}", 
                              bg=self.bg_color, fg=self.fg_color, font=('Arial', 12, 'bold'))
        score_label.pack(padx=10, pady=5)
        
    def create_parts_sections(self, job):
        """Create original and replacement parts sections"""
        parts_frame = tk.LabelFrame(self.job_details_frame, text="Parts", bg=self.bg_color, fg=self.fg_color)
        parts_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5), padx=5)
        
        # Check if this is a New PC Build
        if job["job_details"]["new_pc_build"]:
            # For New PC Build, only show replacement parts (direct from New Parts inventory)
            self.setup_new_pc_build_display(parts_frame, job)
        else:
            # For other job types, show original and replacement parts
            # Create notebook for parts tabs
            parts_notebook = ttk.Notebook(parts_frame)
            parts_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Original customer parts tab
            original_frame = tk.Frame(parts_notebook, bg=self.bg_color)
            parts_notebook.add(original_frame, text="Original Customer Parts")
            
            # Player replacement parts tab
            replacement_frame = tk.Frame(parts_notebook, bg=self.bg_color)
            parts_notebook.add(replacement_frame, text="Player Replacement Parts")
            
            # Setup parts displays
            self.setup_original_parts_display(original_frame, job)
            self.setup_replacement_parts_display(replacement_frame, job)
        
    def setup_new_pc_build_display(self, parent, job):
        """Setup New PC Build display - direct selection from New Parts inventory"""
        # Calculate font sizes based on text size multiplier
        label_font_size = int(12 * self.text_size_multiplier)  # Increased from 10 to 12
        label_font_size = max(10, min(label_font_size, 18))  # Increased from 8 to 10
        
        tk.Label(parent, text="Select parts for new PC build:", bg=self.bg_color, fg=self.fg_color,
                font=('Arial', label_font_size)).pack(pady=5)
        
        # Create build-style slots for new PC build (no locking)
        self.new_pc_build_slots_frame = tk.Frame(parent, bg=self.bg_color)
        self.new_pc_build_slots_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create new PC build slots
        self.create_new_pc_build_slots(job)
        
    def create_new_pc_build_slots(self, job):
        """Create build-style slots for new PC build (no locking)"""
        # Calculate font sizes based on text size multiplier
        slot_font_size = int(12 * self.text_size_multiplier)  # Increased from 10 to 12
        slot_font_size = max(10, min(slot_font_size, 18))  # Increased from 8 to 10
        part_font_size = int(11 * self.text_size_multiplier)  # Increased from 9 to 11
        part_font_size = max(9, min(part_font_size, 16))  # Increased from 7 to 9
        
        # Clear existing slots
        for widget in self.new_pc_build_slots_frame.winfo_children():
            widget.destroy()
        
        # Create slot displays
        row = 0
        col = 0
        max_cols = 3
        
        slot_types = ["CASE", "PSU", "MOTHERBOARD", "CPU", "GPU", "RAM", "CPU COOLER", "CASE FAN", "STORAGE"]
        
        for slot_type in slot_types:
            slot_frame = tk.Frame(self.new_pc_build_slots_frame, bg=self.button_bg, relief=tk.RAISED, bd=2)
            slot_frame.grid(row=row, column=col, padx=5, pady=5, sticky='ew')
            
            tk.Label(slot_frame, text=slot_type, bg=self.button_bg, fg=self.fg_color,
                    font=('Arial', slot_font_size, 'bold')).pack()
            
            # Part display area
            part_display_frame = tk.Frame(slot_frame, bg=self.button_bg)
            part_display_frame.pack(fill=tk.X, padx=5, pady=2)
            
            # Check if this part exists in job's replacement parts (for New PC Build, we use replacement_parts)
            replacement_parts = job.get("replacement_parts", {})
            
            if slot_type in replacement_parts and replacement_parts[slot_type]:
                # Part is already selected
                part_id = replacement_parts[slot_type]
                part_info = self.get_new_parts_info(part_id)
                if part_info:
                    part_name = part_info["name"]
                    part_label = tk.Label(part_display_frame, text=part_name, 
                                         bg=self.button_bg, fg=self.fg_color, wraplength=200,
                                         font=('Arial', part_font_size))
                    part_label.pack(fill=tk.X)
                    
                    # Remove button
                    remove_btn = tk.Button(part_display_frame, text="Remove", 
                                       command=lambda st=slot_type: self.remove_replacement_part(job, st),
                                       font=('Arial', part_font_size),
                                       bg=self.warning_bg, fg=self.warning_fg, width=8)
                    remove_btn.pack(pady=2)
                else:
                    # Part not found, show empty
                    empty_label = tk.Label(part_display_frame, text="Empty", 
                                         bg=self.button_bg, fg='gray',
                                         font=('Arial', part_font_size))
                    empty_label.pack(fill=tk.X)
            else:
                # Empty slot - show available parts from new parts inventory (no locking)
                available_parts = [item for item in self.new_parts_inventory if item["type"] == slot_type]
                if available_parts:
                    # Create dropdown for selection
                    part_var = tk.StringVar()
                    part_names = [part["name"] for part in available_parts]
                    part_names.insert(0, "Select part...")
                    part_var.set("Select part...")
                    
                    dropdown = ttk.Combobox(part_display_frame, textvariable=part_var, 
                                          values=part_names, state="readonly", width=25)
                    dropdown.pack(fill=tk.X, pady=2)
                    
                    # Add button
                    add_btn = tk.Button(part_display_frame, text="Add", 
                                      command=lambda st=slot_type, pv=part_var, ap=available_parts: 
                                      self.add_replacement_part(job, st, pv, ap),
                                      font=('Arial', part_font_size),
                                      bg=self.success_bg, fg=self.success_fg, width=8)
                    add_btn.pack(pady=2)
                else:
                    # No parts available in new parts inventory
                    no_parts_label = tk.Label(part_display_frame, text="No parts available", 
                                            bg=self.button_bg, fg='gray',
                                            font=('Arial', part_font_size))
                    no_parts_label.pack(fill=tk.X)
            
            # Grid configuration
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # Configure grid weights
        for i in range(max_cols):
            self.new_pc_build_slots_frame.grid_columnconfigure(i, weight=1)
        
    def setup_original_parts_display(self, parent, job):
        """Setup original customer parts display"""
        # Calculate font sizes based on text size multiplier
        label_font_size = int(12 * self.text_size_multiplier)  # Increased from 10 to 12
        label_font_size = max(10, min(label_font_size, 18))  # Increased from 8 to 10
        entry_font_size = int(11 * self.text_size_multiplier)  # Increased from 9 to 11
        entry_font_size = max(9, min(entry_font_size, 16))  # Increased from 7 to 9
        
        # Search frame similar to inventory
        search_frame = tk.Frame(parent, bg=self.bg_color)
        search_frame.pack(fill=tk.X, pady=(5, 10), padx=5)
        
        tk.Label(search_frame, text="Search Parts:", bg=self.bg_color, fg=self.fg_color,
                font=('Arial', label_font_size)).pack(side=tk.LEFT, padx=(0, 10))
        
        self.original_search_var = tk.StringVar()
        self.original_search_entry = tk.Entry(search_frame, textvariable=self.original_search_var, bg=self.entry_bg, fg=self.entry_fg, width=40,
                                             font=('Arial', entry_font_size))
        self.original_search_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.original_search_var.trace('w', self.on_original_search_change)
        
        # Suggestions frame
        self.original_suggestions_frame = tk.Frame(search_frame, bg=self.bg_color)
        self.original_suggestions_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        self.original_suggestions_listbox = tk.Listbox(self.original_suggestions_frame, bg=self.entry_bg, fg=self.entry_fg, height=5, width=50,
                                                      font=('Arial', entry_font_size))
        self.original_suggestions_listbox.pack()
        self.original_suggestions_listbox.bind('<Double-Button-1>', self.on_original_suggestion_double_click)
        
        # Build-style parts display
        self.original_build_slots_frame = tk.Frame(parent, bg=self.bg_color)
        self.original_build_slots_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create slot displays similar to build section
        self.create_original_build_slots(job)
        
        # Store search suggestions
        self.original_part_suggestions = []
        
    def create_original_build_slots(self, job):
        """Create build-style slots for original parts"""
        # Calculate font sizes based on text size multiplier
        slot_font_size = int(12 * self.text_size_multiplier)  # Increased from 10 to 12
        slot_font_size = max(10, min(slot_font_size, 18))  # Increased from 8 to 10
        part_font_size = int(11 * self.text_size_multiplier)  # Increased from 9 to 11
        part_font_size = max(9, min(part_font_size, 16))  # Increased from 7 to 9
        
        # Clear existing slots
        for widget in self.original_build_slots_frame.winfo_children():
            widget.destroy()
        
        # Create slot displays
        row = 0
        col = 0
        max_cols = 3
        
        slot_types = ["CPU", "GPU", "CPU Cooler", "Motherboard", "RAM", "Power Supply", "Storage"]
        
        for slot_type in slot_types:
            slot_frame = tk.Frame(self.original_build_slots_frame, bg=self.button_bg, relief=tk.RAISED, bd=2)
            slot_frame.grid(row=row, column=col, padx=5, pady=5, sticky='ew')
            
            tk.Label(slot_frame, text=slot_type, bg=self.button_bg, fg=self.fg_color,
                    font=('Arial', slot_font_size, 'bold')).pack()
            
            # Part display area
            part_display_frame = tk.Frame(slot_frame, bg=self.button_bg)
            part_display_frame.pack(fill=tk.X, padx=5, pady=2)
            
            # Check if this part exists in job data
            original_parts = job.get("original_parts", {})
            if slot_type in original_parts and original_parts[slot_type]:
                part_name = original_parts[slot_type].get("Full Part Name", "Unknown Part")
                part_label = tk.Label(part_display_frame, text=part_name, 
                                     bg=self.button_bg, fg=self.fg_color, wraplength=200,
                                     font=('Arial', part_font_size))
                part_label.pack(fill=tk.X)
                
                # Remove button
                remove_btn = tk.Button(part_display_frame, text="Remove", 
                                   command=lambda st=slot_type: self.remove_original_part(self.current_job, st),
                                   font=('Arial', part_font_size),
                                   bg=self.warning_bg, fg=self.warning_fg, width=8)
                remove_btn.pack(pady=2)
            else:
                # Empty slot
                empty_label = tk.Label(part_display_frame, text="Empty", 
                                     bg=self.button_bg, fg='gray',
                                     font=('Arial', part_font_size))
                empty_label.pack(fill=tk.X)
            
            # Grid configuration
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # Configure grid weights
        for i in range(max_cols):
            self.original_build_slots_frame.grid_columnconfigure(i, weight=1)
        
    def on_original_search_change(self, *args):
        """Handle original parts search input changes"""
        search_text = self.original_search_var.get().lower()
        
        if not search_text:
            self.original_suggestions_listbox.delete(0, tk.END)
            return
        
        # Get all parts from both inventories
        all_parts = []
        for part_type, parts in self.part_data.items():
            for part in parts:
                if 'Full Part Name' in part:
                    all_parts.append((part_type, part['Full Part Name']))
        
        # Split search text into individual words
        search_words = search_text.split()
        
        # Filter parts by search text - all words must be present (but in any order)
        suggestions = []
        for part_type, part_name in all_parts:
            part_name_lower = part_name.lower()
            # Check if all search words are present in the part name
            if all(word in part_name_lower for word in search_words):
                suggestions.append((part_type, part_name))
        
        # Update suggestions listbox
        self.original_suggestions_listbox.delete(0, tk.END)
        for part_type, part_name in suggestions[:20]:  # Limit to 20 suggestions
            self.original_suggestions_listbox.insert(tk.END, f"[{part_type}] {part_name}")
        
        self.original_part_suggestions = suggestions
        
    def on_original_suggestion_double_click(self, event):
        """Handle double-click on original parts suggestion"""
        selection = self.original_suggestions_listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.original_part_suggestions):
                part_type, part_name = self.original_part_suggestions[index]
                self.add_original_part_to_job(part_type, part_name)
                
    def add_original_part_to_job(self, part_type, part_name):
        """Add part to original parts (doesn't take from inventory)"""
        # Find part data from part_data
        part_data = None
        for part in self.part_data.get(part_type, []):
            if part.get('Full Part Name') == part_name:
                part_data = part.copy()  # Create a copy to avoid reference issues
                break
        
        if not part_data:
            # Create basic data if not found
            part_data = {
                "Full Part Name": part_name,
                "Type": part_type
            }
        
        # Add to job's original parts
        if "original_parts" not in self.current_job:
            self.current_job["original_parts"] = {}
        
        self.current_job["original_parts"][part_type] = part_data
        
        # Update display
        self.create_original_build_slots(self.current_job)
        
        # Update 3DMark score if enabled
        if self.current_job["job_details"]["threedmark_score"]:
            self.update_job_3dmark_score(self.current_job)
            self.refresh_job_details()
        
        # Clear search
        self.original_search_var.set("")
        
        self.save_state()
        
    def remove_original_part(self, job, part_type):
        """Remove original part from job"""
        if "original_parts" in job and part_type in job["original_parts"]:
            del job["original_parts"][part_type]
            
            # Update display
            self.create_original_build_slots(job)
            
            # Update 3DMark score if enabled
            if job["job_details"]["threedmark_score"]:
                self.update_job_3dmark_score(job)
                self.refresh_job_details()
            
            self.save_state()
        
    def setup_replacement_parts_display(self, parent, job):
        """Setup player replacement parts display with locking"""
        # Calculate font sizes based on text size multiplier
        label_font_size = int(12 * self.text_size_multiplier)  # Increased from 10 to 12
        label_font_size = max(10, min(label_font_size, 18))  # Increased from 8 to 10
        
        tk.Label(parent, text="Select replacement parts from New Parts inventory:", bg=self.bg_color, fg=self.fg_color,
                font=('Arial', label_font_size)).pack(pady=5)
        
        # Create build-style slots for replacement parts
        self.replacement_build_slots_frame = tk.Frame(parent, bg=self.bg_color)
        self.replacement_build_slots_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create replacement slots with locking
        self.create_replacement_build_slots(job)
        
    def create_replacement_build_slots(self, job):
        """Create build-style slots for replacement parts with locking"""
        # Calculate font sizes based on text size multiplier
        slot_font_size = int(12 * self.text_size_multiplier)  # Increased from 10 to 12
        slot_font_size = max(10, min(slot_font_size, 18))  # Increased from 8 to 10
        part_font_size = int(11 * self.text_size_multiplier)  # Increased from 9 to 11
        part_font_size = max(9, min(part_font_size, 16))  # Increased from 7 to 9
        
        # Clear existing slots
        for widget in self.replacement_build_slots_frame.winfo_children():
            widget.destroy()
        
        # Create slot displays
        row = 0
        col = 0
        max_cols = 3
        
        slot_types = ["CASE", "PSU", "MOTHERBOARD", "CPU", "GPU", "RAM", "CPU COOLER", "CASE FAN", "STORAGE"]
        allowed_parts = self.get_allowed_parts_for_job(job)
        
        for slot_type in slot_types:
            slot_frame = tk.Frame(self.replacement_build_slots_frame, bg=self.button_bg, relief=tk.RAISED, bd=2)
            slot_frame.grid(row=row, column=col, padx=5, pady=5, sticky='ew')
            
            tk.Label(slot_frame, text=slot_type, bg=self.button_bg, fg=self.fg_color,
                    font=('Arial', slot_font_size, 'bold')).pack()
            
            # Part display area
            part_display_frame = tk.Frame(slot_frame, bg=self.button_bg)
            part_display_frame.pack(fill=tk.X, padx=5, pady=2)
            
            # Check if part is allowed for this job
            is_allowed = slot_type in allowed_parts
            is_locked = not is_allowed and not job["job_details"]["new_pc_build"]
            
            # If new_pc_build is checked, everything is allowed
            if job["job_details"]["new_pc_build"]:
                is_allowed = True
                is_locked = False
            
            # Check if this part exists in job's replacement parts
            replacement_parts = job.get("replacement_parts", {})
            original_parts = job.get("original_parts", {})
            
            if slot_type in replacement_parts and replacement_parts[slot_type]:
                # Part is already selected
                part_id = replacement_parts[slot_type]
                part_info = self.get_new_parts_info(part_id)
                if part_info:
                    part_name = part_info["name"]
                    part_label = tk.Label(part_display_frame, text=part_name, 
                                         bg=self.button_bg, fg=self.fg_color, wraplength=200,
                                         font=('Arial', part_font_size))
                    part_label.pack(fill=tk.X)
                    
                    # Remove button
                    remove_btn = tk.Button(part_display_frame, text="Remove", 
                                       command=lambda st=slot_type: self.remove_replacement_part(self.current_job, st),
                                       font=('Arial', part_font_size),
                                       bg=self.warning_bg, fg=self.warning_fg, width=8)
                    remove_btn.pack(pady=2)
                else:
                    # Part not found, show empty
                    empty_label = tk.Label(part_display_frame, text="Empty", 
                                         bg=self.button_bg, fg='gray',
                                         font=('Arial', part_font_size))
                    empty_label.pack(fill=tk.X)
            elif is_locked and slot_type in original_parts and original_parts[slot_type]:
                # Show locked original part
                self.create_locked_part_display(part_display_frame, slot_type, 
                                              original_parts[slot_type].get("Full Part Name", "Unknown"))
            else:
                # Empty slot - show add button if allowed
                if is_allowed:
                    # Show available parts from new parts inventory
                    available_parts = [item for item in self.new_parts_inventory if item["type"] == slot_type]
                    if available_parts:
                        # Create dropdown for selection
                        part_var = tk.StringVar()
                        part_names = [part["name"] for part in available_parts]
                        part_names.insert(0, "Select part...")
                        part_var.set("Select part...")
                        
                        dropdown = ttk.Combobox(part_display_frame, textvariable=part_var, 
                                              values=part_names, state="readonly", width=25)
                        dropdown.pack(fill=tk.X, pady=2)
                        
                        # Add button
                        add_btn = tk.Button(part_display_frame, text="Add", 
                                          command=lambda st=slot_type, pv=part_var, ap=available_parts: 
                                          self.add_replacement_part(job, st, pv, ap),
                                          font=('Arial', part_font_size),
                                          bg=self.success_bg, fg=self.success_fg, width=8)
                        add_btn.pack(pady=2)
                    else:
                        # No parts available in new parts inventory
                        no_parts_label = tk.Label(part_display_frame, text="No parts available", 
                                                bg=self.button_bg, fg='gray',
                                                font=('Arial', part_font_size))
                        no_parts_label.pack(fill=tk.X)
                else:
                    # Locked slot
                    locked_label = tk.Label(part_display_frame, text="Locked", 
                                         bg=self.button_bg, fg=self.warning_fg,
                                         font=('Arial', part_font_size))
                    locked_label.pack(fill=tk.X)
            
            # Grid configuration
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # Configure grid weights
        for i in range(max_cols):
            self.replacement_build_slots_frame.grid_columnconfigure(i, weight=1)
            
    def get_new_parts_info(self, part_id):
        """Get part info from new parts inventory"""
        for item in self.new_parts_inventory:
            if item["id"] == part_id:
                return item
        return None
        
    def add_replacement_part(self, job, slot_type, part_var, available_parts):
        """Add replacement part to job"""
        selected_name = part_var.get()
        if selected_name == "Select part..." or not selected_name:
            return
        
        # Find the selected part
        selected_part = None
        for part in available_parts:
            if part["name"] == selected_name:
                selected_part = part
                break
        
        if not selected_part:
            return
        
        # Validate upgrade if original part exists (skip for New PC Build)
        if not job["job_details"]["new_pc_build"]:
            original_parts = job.get("original_parts", {})
            if slot_type in original_parts and original_parts[slot_type]:
                # Create mock original part for validation
                original_part = {
                    "type": slot_type,
                    "data": original_parts[slot_type],
                    "name": original_parts[slot_type].get("Full Part Name", "Original Part")
                }
                
                # Validate the upgrade
                is_valid, message = self.validate_part_upgrade(original_part, selected_part)
                if not is_valid:
                    messagebox.showwarning("Invalid Upgrade", message)
                    part_var.set("Select part...")
                    return
        
        # Check compatibility with other parts (skip for New PC Build)
        if not job["job_details"]["new_pc_build"]:
            # Collect all parts for compatibility check
            all_parts = []
            
            # Add replacement parts
            for part_type, part_id in job.get("replacement_parts", {}).items():
                if part_id and part_type != slot_type:  # Don't include the part we're adding
                    part_info = self.get_new_parts_info(part_id)
                    if part_info:
                        all_parts.append(part_info)
            
            # Add the new part
            all_parts.append(selected_part)
            
            # Check compatibility
            compatibility_issues = self.check_compatibility(all_parts)
            if compatibility_issues:
                issue_text = "\n".join(compatibility_issues)
                if not messagebox.askyesno("Compatibility Issues", 
                                           f"Compatibility issues found:\n\n{issue_text}\n\nContinue anyway?"):
                    part_var.set("Select part...")
                    return
        
        # Add part to job
        if "replacement_parts" not in job:
            job["replacement_parts"] = {}
        
        job["replacement_parts"][slot_type] = selected_part["id"]
        
        # Update display
        if job["job_details"]["new_pc_build"]:
            self.create_new_pc_build_slots(job)
        else:
            self.create_replacement_build_slots(job)
        
        # Update 3DMark score if enabled
        if job["job_details"]["threedmark_score"]:
            self.update_job_3dmark_score(job)
            self.refresh_job_details()
        
        # Update budget left
        self.calculate_budget_left(job)
        
        self.save_state()
        
    def remove_replacement_part(self, job, slot_type):
        """Remove replacement part from job"""
        if "replacement_parts" in job and slot_type in job["replacement_parts"]:
            del job["replacement_parts"][slot_type]
            
            # Update display
            if job["job_details"]["new_pc_build"]:
                self.create_new_pc_build_slots(job)
            else:
                self.create_replacement_build_slots(job)
            
            # Update 3DMark score if enabled
            if job["job_details"]["threedmark_score"]:
                self.update_job_3dmark_score(job)
                self.refresh_job_details()
            
            # Update budget left
            self.calculate_budget_left(job)
            
            self.save_state()
        
    def update_cable_type(self, job, cable_type):
        """Update cable type"""
        job["cable_type"] = cable_type
        self.save_state()
        
    def update_brand_name(self, job, brand_name):
        """Update brand name"""
        job["brand_name"] = brand_name
        self.save_state()
        
    def calculate_budget_left(self, job):
        """Calculate budget left including replacement parts costs"""
        if job.get("story_job", False):
            return
        
        # Calculate cost of replacement parts
        total_cost = 0
        replacement_parts = job.get("replacement_parts", {})
        
        for part_type, part_id in replacement_parts.items():
            if part_id:
                part_info = self.get_new_parts_info(part_id)
                if part_info:
                    # Get price from data
                    price_str = part_info["data"].get("Price", "0")
                    try:
                        # Remove currency symbols and convert to float
                        price = float(price_str.replace('$', '').replace(',', '').strip())
                        total_cost += price
                    except (ValueError, AttributeError):
                        pass
        
        job["budget_left"] = job.get("actual_budget", 0) - total_cost
        self.save_state()
        
    def get_allowed_parts_for_job(self, job):
        """Get list of allowed parts based on job requirements"""
        allowed_parts = set()
        
        # If 3DMark Score is checked, enable specific parts
        if job["job_details"]["threedmark_score"]:
            allowed_parts.update(["MOTHERBOARD", "CPU", "CPU COOLER", "GPU", "RAM", "PSU"])
        
        # If Replace/Upgrade Parts is checked, enable based on selections
        if job["job_details"]["replace_upgrade_parts"]:
            replace_parts = job["job_details"]["replace_parts"]
            if replace_parts["CPU"]:
                allowed_parts.update(["CPU", "CPU COOLER", "MOTHERBOARD", "PSU"])
            if replace_parts["GPU"]:
                allowed_parts.update(["GPU", "PSU"])
            if replace_parts["CPU Cooler"]:
                allowed_parts.add("CPU COOLER")
            if replace_parts["Motherboard"]:
                allowed_parts.add("MOTHERBOARD")
            if replace_parts["RAM"]:
                allowed_parts.add("RAM")
            if replace_parts["Power Supply"]:
                allowed_parts.add("PSU")
            if replace_parts["Storage"]:
                allowed_parts.add("STORAGE")
        
        # If New PC Build is checked, allow all parts
        if job["job_details"]["new_pc_build"]:
            allowed_parts.update(["CASE", "PSU", "MOTHERBOARD", "CPU", "GPU", "RAM", 
                                "CPU COOLER", "CASE FAN", "STORAGE"])
        
        return allowed_parts
        
    def is_part_allowed_for_job(self, job, part_type):
        """Check if a part type is allowed for the current job"""
        allowed_parts = self.get_allowed_parts_for_job(job)
        return part_type in allowed_parts
        
    def create_locked_part_display(self, parent, part_type, original_part_name):
        """Create a locked part display showing original part"""
        locked_frame = tk.Frame(parent, bg=self.button_bg, relief=tk.RIDGE, bd=2)
        locked_frame.pack(fill=tk.X, pady=2, padx=5)
        
        # Lock icon and original part name in red
        lock_label = tk.Label(locked_frame, text="🔒", bg=self.button_bg, fg=self.warning_fg, font=('Arial', 12))
        lock_label.pack(side=tk.LEFT, padx=5)
        
        part_label = tk.Label(locked_frame, text=f"Locked: {original_part_name}", 
                             bg=self.button_bg, fg=self.warning_fg, font=('Arial', 9, 'bold'))
        part_label.pack(side=tk.LEFT, padx=5)
        
        # Make it non-interactive
        locked_frame.bind("<Button-1>", lambda e: None)
        part_label.bind("<Button-1>", lambda e: None)
        lock_label.bind("<Button-1>", lambda e: None)
        
        return locked_frame
        
    def validate_part_upgrade(self, original_part, replacement_part):
        """Validate that replacement part is same or improved"""
        if not original_part or not replacement_part:
            return True, "No comparison needed"
        
        part_type = original_part["type"]
        original_data = original_part["data"]
        replacement_data = replacement_part["data"]
        
        # Validation rules based on part type
        if part_type == "CASE FAN" or part_type == "CPU COOLER":
            # Check Air Flow
            orig_air = self.get_numeric_value(original_data.get("Air Flow", 0))
            repl_air = self.get_numeric_value(replacement_data.get("Air Flow", 0))
            if repl_air < orig_air:
                return False, f"Inferior {part_type}: Air Flow {repl_air} < {orig_air}"
                
        elif part_type == "CPU":
            # Check Frequency and Cores
            orig_freq = self.get_numeric_value(original_data.get("Frequency", 0))
            repl_freq = self.get_numeric_value(replacement_data.get("Frequency", 0))
            if repl_freq < orig_freq:
                return False, f"Inferior CPU: Frequency {repl_freq} < {orig_freq}"
            
            orig_cores = self.get_numeric_value(original_data.get("Cores", 0))
            repl_cores = self.get_numeric_value(replacement_data.get("Cores", 0))
            if repl_cores < orig_cores:
                return False, f"Inferior CPU: Cores {repl_cores} < {orig_cores}"
                
        elif part_type == "MOTHERBOARD":
            # Check Max RAM Speed
            orig_ram = self.get_numeric_value(original_data.get("Max RAM Speed", 0))
            repl_ram = self.get_numeric_value(replacement_data.get("Max RAM Speed", 0))
            if repl_ram < orig_ram:
                return False, f"Inferior Motherboard: Max RAM Speed {repl_ram} < {orig_ram}"
                
        elif part_type == "RAM":
            # Check Size (GB) and Frequency
            orig_size = self.get_numeric_value(original_data.get("Size (GB)", 0))
            repl_size = self.get_numeric_value(replacement_data.get("Size (GB)", 0))
            if repl_size < orig_size:
                return False, f"Inferior RAM: Size {repl_size} < {orig_size}"
            
            orig_freq = self.get_numeric_value(original_data.get("Frequency", 0))
            repl_freq = self.get_numeric_value(replacement_data.get("Frequency", 0))
            if repl_freq < orig_freq:
                return False, f"Inferior RAM: Frequency {repl_freq} < {orig_freq}"
                
        elif part_type == "STORAGE":
            # Check Size (GB) and Transfer Speed
            orig_size = self.get_numeric_value(original_data.get("Size (GB)", 0))
            repl_size = self.get_numeric_value(replacement_data.get("Size (GB)", 0))
            if repl_size < orig_size:
                return False, f"Inferior Storage: Size {repl_size} < {orig_size}"
            
            orig_speed = self.get_numeric_value(original_data.get("Transfer Speed (MB/s)", 0))
            repl_speed = self.get_numeric_value(replacement_data.get("Transfer Speed (MB/s)", 0))
            if repl_speed < orig_speed:
                return False, f"Inferior Storage: Transfer Speed {repl_speed} < {orig_speed}"
                
        elif part_type == "GPU":
            # Check VRAM, Base Core Freq, Base Mem Freq
            orig_vram = self.get_numeric_value(original_data.get("VRAM (GB)", 0))
            repl_vram = self.get_numeric_value(replacement_data.get("VRAM (GB)", 0))
            if repl_vram < orig_vram:
                return False, f"Inferior GPU: VRAM {repl_vram} < {orig_vram}"
            
            orig_core = self.get_numeric_value(original_data.get("Base Core Freq", 0))
            repl_core = self.get_numeric_value(replacement_data.get("Base Core Freq", 0))
            if repl_core < orig_core:
                return False, f"Inferior GPU: Base Core Freq {repl_core} < {orig_core}"
            
            orig_mem = self.get_numeric_value(original_data.get("Base Mem Freq", 0))
            repl_mem = self.get_numeric_value(replacement_data.get("Base Mem Freq", 0))
            if repl_mem < orig_mem:
                return False, f"Inferior GPU: Base Mem Freq {repl_mem} < {orig_mem}"
        
        return True, "Valid upgrade"
        
    def get_numeric_value(self, value):
        """Extract numeric value from string"""
        if isinstance(value, (int, float)):
            return float(value)
        
        if isinstance(value, str):
            # Remove common non-numeric characters and extract number
            import re
            # Look for numbers (including decimals)
            matches = re.findall(r'[\d,.]+', value)
            if matches:
                try:
                    # Remove commas and convert to float
                    return float(matches[0].replace(',', ''))
                except ValueError:
                    pass
        
        return 0.0
        
    def check_compatibility(self, parts):
        """Check if parts are compatible with each other"""
        # This is a simplified compatibility check
        # In a real implementation, this would be more comprehensive
        
        cpu = None
        motherboard = None
        ram = None
        gpu = None
        psu = None
        
        # Find key components
        for part in parts:
            if part and part["type"] == "CPU":
                cpu = part
            elif part and part["type"] == "MOTHERBOARD":
                motherboard = part
            elif part and part["type"] == "RAM":
                ram = part
            elif part and part["type"] == "GPU":
                gpu = part
            elif part and part["type"] == "PSU":
                psu = part
        
        issues = []
        
        # Check CPU-Motherboard compatibility
        if cpu and motherboard:
            cpu_socket = cpu["data"].get("Socket", "")
            mb_socket = motherboard["data"].get("CPU Socket", "")
            if cpu_socket and mb_socket and cpu_socket != mb_socket:
                issues.append(f"CPU socket {cpu_socket} incompatible with Motherboard socket {mb_socket}")
        
        # Check RAM-Motherboard compatibility
        if ram and motherboard:
            ram_type = ram["data"].get("Type", "")
            mb_type = motherboard["data"].get("RAM Type", "")
            if ram_type and mb_type and ram_type != mb_type:
                issues.append(f"RAM type {ram_type} incompatible with Motherboard type {mb_type}")
        
        # Check PSU wattage (simplified)
        if psu and (cpu or gpu):
            psu_watts = self.get_numeric_value(psu["data"].get("Wattage", 0))
            total_watts = 0
            
            if cpu:
                cpu_watts = self.get_numeric_value(cpu["data"].get("Wattage", 0))
                total_watts += cpu_watts
            
            if gpu:
                gpu_watts = self.get_numeric_value(gpu["data"].get("Wattage", 0))
                total_watts += gpu_watts
            
            # Add 100W buffer for other components
            total_watts += 100
            
            if psu_watts < total_watts:
                issues.append(f"PSU wattage {psu_watts}W insufficient for components requiring {total_watts}W")
        
        return issues
        
    def calculate_3dmark_score(self, parts):
        """Calculate 3DMark score based on components"""
        score = 0
        
        for part in parts:
            if not part:
                continue
                
            part_type = part["type"]
            data = part["data"]
            
            # CPU contribution (based on cores and frequency)
            if part_type == "CPU":
                cores = self.get_numeric_value(data.get("Cores", 0))
                freq = self.get_numeric_value(data.get("Frequency", 0))
                cpu_score = (cores * 100) + (freq * 10)
                score += cpu_score
            
            # GPU contribution (based on VRAM and frequencies)
            elif part_type == "GPU":
                vram = self.get_numeric_value(data.get("VRAM (GB)", 0))
                core_freq = self.get_numeric_value(data.get("Base Core Freq", 0))
                mem_freq = self.get_numeric_value(data.get("Base Mem Freq", 0))
                gpu_score = (vram * 500) + (core_freq * 5) + (mem_freq * 2)
                score += gpu_score
            
            # RAM contribution (based on size and speed)
            elif part_type == "RAM":
                size = self.get_numeric_value(data.get("Size (GB)", 0))
                freq = self.get_numeric_value(data.get("Frequency", 0))
                ram_score = (size * 50) + (freq * 2)
                score += ram_score
            
            # Motherboard contribution (based on max RAM speed)
            elif part_type == "MOTHERBOARD":
                ram_speed = self.get_numeric_value(data.get("Max RAM Speed", 0))
                mb_score = ram_speed * 10
                score += mb_score
            
            # Storage contribution (based on size and speed)
            elif part_type == "STORAGE":
                size = self.get_numeric_value(data.get("Size (GB)", 0))
                speed = self.get_numeric_value(data.get("Transfer Speed (MB/s)", 0))
                storage_score = (size * 2) + (speed / 10)
                score += storage_score
        
        return int(score)
        
    def update_job_3dmark_score(self, job):
        """Update job's 3DMark score"""
        parts = []
        
        # Collect all parts (both original and replacement)
        all_parts = {}
        
        # Add original parts
        for part_type, part_data in job.get("original_parts", {}).items():
            if part_data:
                # Create a mock part object for original parts
                original_part = {
                    "type": part_type,
                    "data": part_data,
                    "name": part_data.get("Full Part Name", "Original Part")
                }
                all_parts[part_type] = original_part
        
        # Add replacement parts (they override original parts)
        for part_type, part_data in job.get("replacement_parts", {}).items():
            if part_data:
                if isinstance(part_data, list):
                    # Handle multiple slots (like GPU, RAM, etc.)
                    for slot_part in part_data:
                        if slot_part:
                            # Find the actual part from new parts inventory
                            for item in self.new_parts_inventory:
                                if item["id"] == slot_part:
                                    all_parts[part_type] = item
                                    break
                else:
                    # Handle single slot
                    for item in self.new_parts_inventory:
                        if item["id"] == part_data:
                            all_parts[part_type] = item
                            break
        
        # Calculate score
        parts_list = list(all_parts.values())
        score = self.calculate_3dmark_score(parts_list)
        job["threedmark_score"] = score
        
        return score
        
    def get_unique_column_values(self, part_type, column):
        """Get unique values for a column, limited to 50 most common"""
        values = []
        type_inventory = [item for item in self.inventory if item["type"] == part_type]
        
        # Collect all non-empty values, excluding "Full Part Name"
        for item in type_inventory:
            if column == "Full Part Name":
                continue  # Skip Full Part Name column
            
            value = item["data"].get(column, "")
            if value == "":
                value = item["data"].get(column.replace(" ", "_"), "")
            if value and value != "":
                values.append(value)
        
        # Count frequency and get top 50
        from collections import Counter
        value_counts = Counter(values)
        most_common = [val for val, count in value_counts.most_common(50)]
        
        return most_common
        
    def apply_filter(self, part_type, column, filter_values):
        """Apply filter for a specific column"""
        if not filter_values:  # Empty list means no filter
            if part_type in self.current_filters and column in self.current_filters[part_type]:
                del self.current_filters[part_type][column]
        else:
            if part_type not in self.current_filters:
                self.current_filters[part_type] = {}
            self.current_filters[part_type][column] = filter_values
        
        self.refresh_inventory_display()
        
    def on_accordion_filter_change(self, part_type, column, selected_values):
        """Handle accordion filter change"""
        if not selected_values:
            # No values selected, remove filter
            if part_type in self.current_filters and column in self.current_filters[part_type]:
                del self.current_filters[part_type][column]
        else:
            # Values selected, add filter
            if part_type not in self.current_filters:
                self.current_filters[part_type] = {}
            self.current_filters[part_type][column] = selected_values
        
        self.refresh_inventory_display()
        
    def clear_all_filters_for_type(self, part_type):
        """Clear all filters for a specific part type"""
        if part_type in self.current_filters:
            self.current_filters[part_type].clear()
        
        # Clear all accordion filters
        if part_type in self.accordion_filters:
            for accordion in self.accordion_filters[part_type]:
                accordion.clear_selections()
        
        self.refresh_inventory_display()
        
    def clear_all_filters(self):
        """Clear all filters for all part types"""
        self.current_filters = {}
        self.refresh_inventory_display()
        
    def on_tree_double_click(self, event, part_type, inventory_type):
        """Handle double-click on tree to copy part name"""
        tree_key = f"{inventory_type}_{part_type}"
        tree = self.part_trees[tree_key]
        selection = tree.selection()
        if selection:
            item = tree.item(selection[0])
            # Get the part name from the item's text
            part_name = item['text']
            if part_name:
                self.copy_part_name_by_name(part_name)
                
    def hide_tip(self):
        """Hide the tip and remember the preference"""
        self.dismiss_tip("double_click_add", self.tip_frame)
        
    def show_story_job_help(self):
        """Show Story Job help popup"""
        help_window = tk.Toplevel(self.root)
        help_window.title("Story Jobs Help")
        help_window.geometry("500x150")
        help_window.configure(bg=self.bg_color)
        
        # Help text
        help_text = ("Story jobs are special, recurring email tasks in Career Mode that offer unique "
                   "narratives, such as repairing PCs for a \"Nigerian Prince,\" a famous streamer, "
                   "or Santa Claus. These jobs are unique in that they allow you to exceed the listed "
                   "budget while still achieving a five-star rating.")
        
        help_label = tk.Label(help_window, text=help_text, bg=self.bg_color, fg=self.fg_color,
                             wraplength=460, justify=tk.LEFT, padx=10, pady=10)
        help_label.pack(fill=tk.BOTH, expand=True)
        
        # Close button
        close_btn = tk.Button(help_window, text="X", command=help_window.destroy,
                            bg=self.button_bg, fg=self.button_fg, width=3)
        close_btn.place(relx=0.95, rely=0.05)
        
        # Center the window
        help_window.transient(self.root)
        help_window.grab_set()
        help_window.wait_window()
        
    def dismiss_tip(self, tip_name, tip_frame):
        """Dismiss a tip and remember the preference"""
        self.tips_dismissed[tip_name] = True
        tip_frame.pack_forget()
        self.save_state()
        
    def copy_part_name_by_name(self, part_name):
        """Copy part name to clipboard by name"""
        try:
            pyperclip.copy(part_name)
            # Show brief confirmation
            self.root.title(f"PC Builder - Copied: {part_name}")
            self.root.after(2000, lambda: self.root.title("PC Builder - PC Building Simulator"))
        except:
            messagebox.showerror("Error", "Could not copy to clipboard")
        
    def setup_builds_tab(self):
        """Setup the builds tab"""
        # Builds tab tip
        if not self.tips_dismissed.get("builds_tab", False):
            builds_tip_frame = tk.Frame(self.builds_frame, bg=self.tip_bg, relief=tk.RAISED, bd=1)
            builds_tip_frame.pack(fill=tk.X, pady=(5, 10), padx=5)
            
            builds_tip_label = tk.Label(builds_tip_frame, 
                                       text="💡 This section is designed to help you build PC's to sell on PCBay. It will only take parts from the Used Parts inventory.",
                                       bg=self.tip_bg, fg=self.tip_fg, wraplength=800, justify=tk.LEFT)
            builds_tip_label.pack(side=tk.LEFT, padx=10, pady=8)
            
            builds_close_btn = tk.Button(builds_tip_frame, text="X", 
                                        command=lambda: self.dismiss_tip("builds_tab", builds_tip_frame),
                                        bg=self.tip_bg, fg=self.tip_fg, bd=0, width=2)
            builds_close_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Builds list frame
        builds_list_frame = tk.Frame(self.builds_frame, bg=self.bg_color)
        builds_list_frame.pack(fill=tk.X, pady=(0, 10))
        
        # First row: Builds label and dropdown
        top_row_frame = tk.Frame(builds_list_frame, bg=self.bg_color)
        top_row_frame.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(top_row_frame, text="Builds:", bg=self.bg_color, fg=self.fg_color).pack(side=tk.LEFT, padx=(0, 10))
        
        self.builds_listbox = ttk.Combobox(top_row_frame, state="readonly", width=50)
        self.builds_listbox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.builds_listbox.bind('<<ComboboxSelected>>', self.on_build_select)
        
        # Second row: Build control buttons - horizontal layout
        button_frame = tk.Frame(builds_list_frame, bg=self.bg_color)
        button_frame.pack(fill=tk.X)
        
        tk.Button(button_frame, text="New Build", command=self.new_build,
                 bg=self.button_bg, fg=self.button_fg).pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="Rename Build", command=self.rename_build,
                 bg=self.button_bg, fg=self.button_fg).pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="Delete Build", command=self.delete_build,
                 bg=self.button_bg, fg=self.button_fg).pack(side=tk.LEFT, padx=2)
        
        # Build details frame with scrollbar
        build_details_container = tk.Frame(self.builds_frame, bg=self.bg_color)
        build_details_container.pack(fill=tk.BOTH, expand=True)
        
        # Create canvas and scrollbar for build details
        build_canvas = tk.Canvas(build_details_container, bg=self.bg_color, highlightthickness=0)
        build_scrollbar = ttk.Scrollbar(build_details_container, orient="vertical", command=build_canvas.yview)
        self.build_details_frame = tk.Frame(build_canvas, bg=self.bg_color)
        
        # Configure scrolling
        self.build_details_frame.bind(
            "<Configure>",
            lambda e: build_canvas.configure(scrollregion=build_canvas.bbox("all"))
        )
        
        build_canvas.configure(yscrollcommand=build_scrollbar.set)
        
        # Pack canvas and scrollbar
        build_canvas.pack(side="left", fill="both", expand=True)
        build_scrollbar.pack(side="right", fill="y")
        
        # Create window in canvas
        build_canvas.create_window((0, 0), window=self.build_details_frame, anchor="nw")
        
        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            build_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        build_canvas.bind("<MouseWheel>", _on_mousewheel)
        
        # Compatibility warning frame
        self.warning_frame = tk.Frame(self.build_details_frame, bg=self.warning_bg)
        self.warning_label = tk.Label(self.warning_frame, text="", bg=self.warning_bg, fg=self.warning_fg, wraplength=800)
        self.warning_label.pack(pady=5)
        
        # Build slots frame
        self.slots_frame = tk.Frame(self.build_details_frame, bg=self.bg_color)
        self.slots_frame.pack(fill=tk.BOTH, expand=True)
        
        # Score frame
        self.score_frame = tk.Frame(self.build_details_frame, bg=self.bg_color)
        self.score_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.score_label = tk.Label(self.score_frame, text="", bg=self.bg_color, fg=self.fg_color, font=('Arial', 12, 'bold'))
        self.score_label.pack()
        
        self.bottleneck_label = tk.Label(self.score_frame, text="", bg=self.bg_color, fg=self.warning_fg, wraplength=800)
        self.bottleneck_label.pack()
        
        # Complete build button
        tk.Button(self.score_frame, text="Complete Build", command=self.complete_build,
                 bg=self.warning_bg, fg=self.warning_fg, font=('Arial', 10, 'bold')).pack(pady=5)
        
        self.refresh_builds_display()
        
    def on_search_change(self, *args):
        """Handle search input changes"""
        search_text = self.search_var.get().lower()
        
        if not search_text:
            self.suggestions_listbox.delete(0, tk.END)
            return
        
        # Get all parts from all types
        all_parts = []
        for part_type, parts in self.part_data.items():
            for part in parts:
                if 'Full Part Name' in part:
                    all_parts.append((part_type, part['Full Part Name']))
        
        # Split search text into individual words
        search_words = search_text.split()
        
        # Filter parts by search text - all words must be present (but in any order)
        suggestions = []
        for part_type, part_name in all_parts:
            part_name_lower = part_name.lower()
            # Check if all search words are present in the part name
            if all(word in part_name_lower for word in search_words):
                suggestions.append((part_type, part_name))
        
        # Update suggestions listbox
        self.suggestions_listbox.delete(0, tk.END)
        for part_type, part_name in suggestions[:20]:  # Limit to 20 suggestions
            self.suggestions_listbox.insert(tk.END, f"[{part_type}] {part_name}")
        
        self.selected_part_suggestions = suggestions
        
    def on_suggestion_double_click(self, event):
        """Handle double-click on suggestion"""
        selection = self.suggestions_listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.selected_part_suggestions):
                part_type, part_name = self.selected_part_suggestions[index]
                self.add_part_to_inventory(part_type, part_name)
                
    def add_part_to_inventory(self, part_type, part_name):
        """Add a part to inventory"""
        # Find part data
        part_data = None
        for part in self.part_data.get(part_type, []):
            if part.get('Full Part Name') == part_name:
                part_data = part
                break
        
        if not part_data:
            messagebox.showerror("Error", f"Part not found: {part_name}")
            return
        
        # Create inventory item
        inventory_item = {
            "id": len(self.inventory) + 1,
            "type": part_type,
            "name": part_name,
            "data": part_data,
            "status": "available",
            "added_date": datetime.now().isoformat()
        }
        
        self.inventory.append(inventory_item)
        self.refresh_inventory_display()
        self.save_state()
        
        # Clear search
        self.search_var.set("")
        
    def refresh_inventory_display(self):
        """Refresh inventory display with filtering and proper action buttons"""
        # Refresh used parts display
        for part_type in self.part_types.keys():
            tree_key = f"used_{part_type}"
            if tree_key in self.part_trees:
                tree = self.part_trees[tree_key]
                # Clear existing items
                for item in tree.get_children():
                    tree.delete(item)
                
                # Get inventory items of this type
                type_inventory = [item for item in self.inventory if item["type"] == part_type]
                
                # Apply filters
                filtered_items = self.apply_filters_to_items(type_inventory, part_type)
                self.filtered_inventory[part_type] = filtered_items
                
                # Sort items
                sorted_items = self.sort_items(filtered_items, part_type)
                
                # Add items to tree
                for item in sorted_items:
                    # Create action buttons text
                    add_text = "[Add]" if item["status"] == "available" else "[Remove]"
                    delete_text = "[X]"
                    
                    # Get other column values (use only visible columns)
                    visible_columns = self.get_visible_columns(part_type)
                    values = [add_text, delete_text]
                    
                    # Use only visible columns for values
                    for col in visible_columns:
                        value = item["data"].get(col, "")
                        if value == "":
                            value = item["data"].get(col.replace(" ", "_"), "")
                        values.append(value)
                    
                    # Insert item with all data (use "Full Part Name" as tree text)
                    part_name = item["data"].get("Full Part Name", item["name"])
                    tree_item = tree.insert('', 'end', text=part_name, values=tuple(values), tags=(str(item["id"]),))
                    
                    # Store the full item data as a tag for later reference
                    tree.item(tree_item, tags=(str(item["id"]),))
                    
                    # Color code based on status
                    if item["status"] == "used":
                        # Tag used items
                        tree.item(tree_item, tags=(str(item["id"]), "used"))
                    else:
                        tree.item(tree_item, tags=(str(item["id"]), "available"))
            
            # Bind click events for action buttons
            tree.bind('<Button-1>', lambda e, pt=part_type: self.on_used_tree_click(e, pt))
        
        # Refresh new parts display
        for part_type in self.part_types.keys():
            tree_key = f"new_{part_type}"
            if tree_key in self.part_trees:
                tree = self.part_trees[tree_key]
                # Clear existing items
                for item in tree.get_children():
                    tree.delete(item)
                
                # Get new parts inventory items of this type
                type_inventory = [item for item in self.new_parts_inventory if item["type"] == part_type]
                
                # Apply filters (using same filter logic as used parts)
                filtered_items = self.apply_filters_to_items(type_inventory, part_type)
                
                # Sort items
                sorted_items = self.sort_items(filtered_items, part_type)
                
                # Add items to tree
                for item in sorted_items:
                    # Create action buttons text
                    add_text = "[Add]"
                    delete_text = "[X]"
                    
                    # Get other column values (use all CSV columns except "Full Part Name" and "Part Type" for tree text)
                    columns = self.part_columns.get(part_type, ["Sell Price"])
                    values = [add_text, delete_text]
                    
                    # Use all columns except "Full Part Name" and "Part Type" for values (used as tree text)
                    for col in columns:
                        if col not in ["Full Part Name", "Part Type"]:  # Skip Full Part Name (tree text) and Part Type (redundant)
                            value = item["data"].get(col, "")
                            if value == "":
                                value = item["data"].get(col.replace(" ", "_"), "")
                            values.append(value)
                    
                    # Insert item with all data (use "Full Part Name" as tree text)
                    part_name = item["data"].get("Full Part Name", item["name"])
                    tree_item = tree.insert('', 'end', text=part_name, values=tuple(values), tags=(str(item["id"]),))
                    
                    # Store the full item data as a tag for later reference
                    tree.item(tree_item, tags=(str(item["id"]),))
            
            # Bind click events for action buttons
            tree.bind('<Button-1>', lambda e, pt=part_type: self.on_new_tree_click(e, pt))
        
        # Update status
        self.update_status_bar()
        
    def on_used_tree_click(self, event, part_type):
        """Handle clicks on used parts tree for action buttons"""
        tree_key = f"used_{part_type}"
        tree = self.part_trees[tree_key]
        
        # Get clicked item and column
        item_id = tree.identify_row(event.y)
        column_id = tree.identify_column(event.x)
        
        if not item_id:
            return
        
        # Get the inventory item from tags
        item_tags = tree.item(item_id, "tags")
        if not item_tags:
            return
        
        inventory_item = None
        for item in self.inventory:
            if str(item["id"]) == item_tags[0]:
                inventory_item = item
                break
        
        if not inventory_item:
            return
        
        # Check which column was clicked
        if column_id == "#1":  # Add/Remove from Build column
            if inventory_item["status"] == "available":
                self.add_part_to_current_build(inventory_item)
            else:
                self.remove_part_from_build(inventory_item)
        elif column_id == "#2":  # Delete column
            self.delete_inventory_item(inventory_item)
        # Other columns don't need special handling
        
    def apply_filters_to_items(self, items, part_type):
        """Apply current filters to items"""
        filtered_items = []
        filters = self.current_filters.get(part_type, {})
        
        for item in items:
            matches_all_filters = True
            
            for column, filter_values in filters.items():
                item_value = item["data"].get(column, "")
                if item_value == "":
                    item_value = item["data"].get(column.replace(" ", "_"), "")
                
                # Check if item value matches any of the selected filter values
                if isinstance(filter_values, list):
                    # Multiple values selected (accordion filter)
                    if item_value not in filter_values:
                        matches_all_filters = False
                        break
                else:
                    # Single value selected (old dropdown filter)
                    if item_value != filter_values:
                        matches_all_filters = False
                        break
            
            if matches_all_filters:
                filtered_items.append(item)
        
        return filtered_items
        
    def sort_items(self, items, part_type):
        """Sort items based on current sort settings"""
        if part_type not in self.current_sort:
            return items
        
        column, direction = self.current_sort[part_type]
        
        def sort_key(item):
            value = item["data"].get(column, "")
            if value == "":
                value = item["data"].get(column.replace(" ", "_"), "")
            
            # Try to convert to number for numeric sorting
            try:
                if value.replace('.', '').replace('-', '').isdigit():
                    return float(value)
            except:
                pass
            
            return str(value).lower()
        
        reverse = (direction == "desc")
        return sorted(items, key=sort_key, reverse=reverse)
        
    def on_tree_click(self, event, part_type):
        """Handle clicks on tree for action buttons"""
        tree = self.part_trees[part_type]
        
        # Get clicked item and column
        item_id = tree.identify_row(event.y)
        column_id = tree.identify_column(event.x)
        
        if not item_id:
            return
        
        # Get the inventory item from tags
        item_tags = tree.item(item_id, "tags")
        if not item_tags:
            return
        
        inventory_item = None
        for item in self.inventory:
            if str(item["id"]) == item_tags[0]:
                inventory_item = item
                break
        
        if not inventory_item:
            return
        
        # Check which column was clicked
        if column_id == "#1":  # Add/Remove from Build column
            if inventory_item["status"] == "available":
                self.add_part_to_current_build(inventory_item)
            else:
                self.remove_part_from_build(inventory_item)
        elif column_id == "#2":  # Delete column
            self.delete_inventory_item(inventory_item)
        # Other columns don't need special handling
        
    def update_status_bar(self):
        """Update the status bar with component count and filter status"""
        total_parts = len(self.inventory)
        total_available = len([i for i in self.inventory if i["status"] == "available"])
        
        # Count filtered items
        total_filtered = 0
        has_filters = False
        
        for part_type, items in self.filtered_inventory.items():
            total_filtered += len(items)
            if part_type in self.current_filters and self.current_filters[part_type]:
                has_filters = True
        
        # Create status text
        if has_filters:
            status_text = f"Showing {total_filtered} of {total_parts} components (filtered) | Available: {total_available}"
        else:
            status_text = f"Showing {total_parts} of {total_parts} components | Available: {total_available}"
        
        self.status_label.config(text=status_text)
        
    def copy_part_name(self, inventory_item):
        """Copy part name to clipboard"""
        try:
            pyperclip.copy(inventory_item["name"])
            # Show brief confirmation
            self.root.title(f"PC Builder - Copied: {inventory_item['name']}")
            self.root.after(2000, lambda: self.root.title("PC Builder - PC Building Simulator"))
        except:
            messagebox.showerror("Error", "Could not copy to clipboard")
        
    def add_part_to_current_build(self, inventory_item):
        """Add part to currently selected build"""
        if inventory_item["status"] == "used":
            messagebox.showwarning("Warning", "This part is already used in a build!")
            return
        
        selected_name = self.builds_listbox.get()
        
        if not selected_name:
            messagebox.showwarning("Warning", "Please select a build first!")
            return
        
        # Find build by name
        build = None
        for b in self.builds:
            if b["name"] == selected_name:
                build = b
                break
        
        if not build:
            return
        part_type = inventory_item["type"]
        
        # Map part types to build slots
        slot_mapping = {
            "CASE": "Case",
            "PSU": "PSU",
            "MOTHERBOARD": "Motherboard", 
            "CPU": "CPU",
            "GPU": "GPU",
            "RAM": "RAM",
            "CPU COOLER": "CPU Cooler",
            "CASE FAN": "Case Fans",
            "STORAGE": "Storage"
        }
        
        slot_name = slot_mapping.get(part_type)
        if not slot_name:
            messagebox.showerror("Error", f"Unknown part type: {part_type}")
            return
        
        # Add to appropriate slot
        if slot_name in ["GPU", "RAM", "Case Fans", "Storage"]:
            # Multiple slots
            slots = build["parts"][slot_name]
            empty_slot = None
            for i, slot in enumerate(slots):
                if slot is None:
                    empty_slot = i
                    break
            
            if empty_slot is None:
                messagebox.showwarning("Warning", f"No empty {slot_name} slots available!")
                return
            
            build["parts"][slot_name][empty_slot] = inventory_item["id"]
        else:
            # Single slot
            if build["parts"][slot_name] is not None:
                messagebox.showwarning("Warning", f"{slot_name} slot is already occupied!")
                return
            
            build["parts"][slot_name] = inventory_item["id"]
        
        # Mark part as used
        inventory_item["status"] = "used"
        
        # Update displays without recreating tabs
        self.refresh_inventory_display()
        self.refresh_builds_display()
        self.refresh_build_details()
        self.save_state()
        
    def remove_part_from_build(self, inventory_item):
        """Remove part from build and mark as available"""
        if inventory_item["status"] == "available":
            messagebox.showwarning("Warning", "This part is not currently used in any build!")
            return
        
        # Find which build contains this part
        build_found = False
        for build in self.builds:
            for slot_name, slot_data in build["parts"].items():
                if isinstance(slot_data, list):
                    for i, part_id in enumerate(slot_data):
                        if part_id == inventory_item["id"]:
                            slot_data[i] = None
                            build_found = True
                            break
                elif slot_data == inventory_item["id"]:
                    build["parts"][slot_name] = None
                    build_found = True
                    break
            
            if build_found:
                break
        
        if build_found:
            # Mark part as available
            inventory_item["status"] = "available"
            
            self.refresh_inventory_display()
            self.refresh_builds_display()
            self.save_state()
        else:
            messagebox.showerror("Error", "Could not find part in any build!")
        
    def delete_inventory_item(self, inventory_item):
        """Delete item from inventory"""
        if inventory_item["status"] == "used":
            messagebox.showwarning("Warning", "Cannot delete a part that's used in a build!")
            return
        
        if messagebox.askyesno("Confirm", f"Delete {inventory_item['name']} from inventory?"):
            self.inventory.remove(inventory_item)
            self.refresh_inventory_display()
            self.save_state()
            
    def delete_all_parts(self):
        """Delete all parts from inventory"""
        used_parts = [i for i in self.inventory if i["status"] == "used"]
        if used_parts:
            messagebox.showwarning("Warning", f"Cannot delete all parts! {len(used_parts)} parts are currently used in builds.")
            return
        
        if messagebox.askyesno("Confirm Delete All", "Are you sure you want to delete ALL parts from inventory? This cannot be undone!"):
            self.inventory = []
            self.refresh_inventory_display()
            self.save_state()
            
    def sort_column(self, tree, column, part_type):
        """Sort tree column"""
        # Get current sort state
        if part_type in self.current_sort:
            current_col, current_dir = self.current_sort[part_type]
        else:
            current_col, current_dir = None, "asc"
        
        # Determine new sort direction
        if current_col == column:
            new_dir = "desc" if current_dir == "asc" else "asc"
        else:
            new_dir = "asc"
        
        # Update sort state
        self.current_sort[part_type] = (column, new_dir)
        
        # Refresh display to apply sorting
        self.refresh_inventory_display()
        
    def new_build(self):
        """Create new build"""
        build_name = self.ask_string_dark("New Build", "Enter build name:")
        if build_name:
            new_build = {
                "id": len(self.builds) + 1,
                "name": build_name,
                "parts": {
                    "Case": None,
                    "PSU": None,
                    "Motherboard": None,
                    "CPU": None,
                    "GPU": [None, None],
                    "RAM": [None, None, None, None],
                    "CPU Cooler": None,
                    "Case Fans": [None, None, None, None],
                    "Storage": [None, None, None, None, None, None, None, None]
                }
            }
            self.builds.append(new_build)
            self.refresh_builds_display()
            self.save_state()
            
    def rename_build(self):
        """Rename selected build"""
        selected_name = self.builds_listbox.get()
        
        if not selected_name:
            messagebox.showwarning("Warning", "Please select a build first!")
            return
        
        # Find build by name
        build = None
        for b in self.builds:
            if b["name"] == selected_name:
                build = b
                break
        
        if not build:
            return
        
        new_name = self.ask_string_dark("Rename Build", "Enter new name:", initialvalue=build["name"])
        if new_name and new_name != build["name"]:
            build["name"] = new_name
            self.refresh_builds_display()
            self.save_state()
            
    def delete_build(self):
        """Delete selected build"""
        selected_name = self.builds_listbox.get()
        
        if not selected_name:
            messagebox.showwarning("Warning", "Please select a build first!")
            return
        
        # Find build by name
        build = None
        build_index = -1
        for i, b in enumerate(self.builds):
            if b["name"] == selected_name:
                build = b
                build_index = i
                break
        
        if not build or build_index == -1:
            return
        
        # Check if any parts are used
        used_parts = []
        for slot_parts in build["parts"].values():
            if isinstance(slot_parts, list):
                for part_id in slot_parts:
                    if part_id is not None:
                        used_parts.append(part_id)
            elif slot_parts is not None:
                used_parts.append(slot_parts)
        
        if used_parts:
            if not messagebox.askyesno("Confirm", f"This build has {len(used_parts)} parts. These parts will be marked as available again. Continue?"):
                return
            
            # Mark parts as available
            for part_id in used_parts:
                for item in self.inventory:
                    if item["id"] == part_id:
                        item["status"] = "available"
                        break
        
        self.builds.pop(build_index)
        self.refresh_inventory_display()
        self.refresh_builds_display()
        self.save_state()
        
    def on_build_select(self, event):
        """Handle build selection"""
        self.refresh_build_details()
        
    def refresh_builds_display(self):
        """Refresh builds dropdown list"""
        build_names = [build["name"] for build in self.builds]
        self.builds_listbox['values'] = build_names
        
        # Select first build if available, otherwise clear selection
        if build_names:
            self.builds_listbox.set(build_names[0])
        else:
            self.builds_listbox.set("")
        
        self.refresh_build_details()
        
    def refresh_build_details(self):
        """Refresh build details display"""
        selected_name = self.builds_listbox.get()
        
        if not selected_name or not self.builds:
            self.clear_build_details()
            return
        
        # Find build by name
        build = None
        for b in self.builds:
            if b["name"] == selected_name:
                build = b
                break
        
        if not build:
            self.clear_build_details()
            return
        
        # Clear existing widgets
        for widget in self.slots_frame.winfo_children():
            widget.destroy()
        
        # Create slot displays
        row = 0
        col = 0
        max_cols = 3
        
        # Calculate font sizes based on text size multiplier
        slot_font_size = int(12 * self.text_size_multiplier)  # Increased from 10 to 12
        slot_font_size = max(10, min(slot_font_size, 18))  # Increased from 8 to 10
        part_font_size = int(11 * self.text_size_multiplier)  # Increased from 9 to 11
        part_font_size = max(9, min(part_font_size, 16))  # Increased from 7 to 9
        
        for slot_name, slot_data in build["parts"].items():
            slot_frame = tk.Frame(self.slots_frame, bg=self.button_bg, relief=tk.RAISED, bd=2)
            slot_frame.grid(row=row, column=col, padx=5, pady=5, sticky='ew')
            
            tk.Label(slot_frame, text=slot_name, bg=self.button_bg, fg=self.fg_color, 
                    font=('Arial', slot_font_size, 'bold')).pack()
            
            if isinstance(slot_data, list):
                # Multiple slots
                for i, part_id in enumerate(slot_data):
                    part_info = self.get_part_info(part_id)
                    if part_info:
                        # Create frame for part and remove button
                        part_frame = tk.Frame(slot_frame, bg=self.button_bg)
                        part_frame.pack(fill=tk.X, pady=1)
                        
                        # Part name label
                        label = tk.Label(part_frame, text=f"Slot {i+1}: {part_info['name']}", 
                                      bg=self.button_bg, fg=self.fg_color,
                                      font=('Arial', part_font_size))
                        label.pack(side=tk.LEFT, padx=2)
                        
                        # Remove button
                        remove_btn = tk.Button(part_frame, text="Remove", 
                                            font=('Arial', part_font_size),
                                            command=lambda pi=part_info: self.remove_part_from_build(pi),
                                            bg=self.warning_bg, fg=self.warning_fg, width=6)
                        remove_btn.pack(side=tk.RIGHT, padx=2)
                        
                        # Bind double-click to copy part name
                        label.bind('<Double-Button-1>', lambda e, p=part_info: self.copy_part_name(p))
                    else:
                        label = tk.Label(slot_frame, text=f"Slot {i+1}: Empty", 
                                      bg=self.button_bg, fg='gray',
                                      font=('Arial', part_font_size))
                        label.pack()
            else:
                # Single slot
                part_info = self.get_part_info(slot_data)
                if part_info:
                    # Create frame for part and remove button
                    part_frame = tk.Frame(slot_frame, bg=self.button_bg)
                    part_frame.pack(fill=tk.X, pady=1)
                    
                    # Part name label
                    label = tk.Label(part_frame, text=part_info['name'], 
                                  bg=self.button_bg, fg=self.fg_color,
                                  font=('Arial', part_font_size))
                    label.pack(side=tk.LEFT, padx=2)
                    
                    # Remove button
                    remove_btn = tk.Button(part_frame, text="Remove", 
                                         font=('Arial', part_font_size),
                                         command=lambda pi=part_info: self.remove_part_from_build(pi),
                                         bg=self.warning_bg, fg=self.warning_fg, width=6)
                    remove_btn.pack(side=tk.RIGHT, padx=2)
                    
                    # Bind double-click to copy part name
                    label.bind('<Double-Button-1>', lambda e, p=part_info: self.copy_part_name(p))
                else:
                    label = tk.Label(slot_frame, text="Empty", 
                                  bg=self.button_bg, fg='gray',
                                  font=('Arial', part_font_size))
                    label.pack()
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # Check compatibility
        self.check_compatibility(build)
        
        # Calculate score
        self.calculate_build_score(build)
        
    def get_part_info(self, part_id):
        """Get part information by ID"""
        if part_id is None:
            return None
        
        for item in self.inventory:
            if item["id"] == part_id:
                return item
        
        return None
        
    def calculate_total_sell_price(self, build):
        """Calculate total sell price of all parts in build"""
        total_price = 0.0
        
        for slot_name, slot_data in build["parts"].items():
            if isinstance(slot_data, list):
                # Multiple slots (like GPU, RAM)
                for part_id in slot_data:
                    if part_id is not None:
                        part_info = self.get_part_info(part_id)
                        if part_info:
                            price_str = part_info["data"].get("Sell Price", "0")
                            try:
                                price = float(price_str.replace('$', '').replace(',', '').strip())
                                total_price += price
                            except (ValueError, AttributeError):
                                pass
            else:
                # Single slot
                if slot_data is not None:
                    part_info = self.get_part_info(slot_data)
                    if part_info:
                        price_str = part_info["data"].get("Sell Price", "0")
                        try:
                            price = float(price_str.replace('$', '').replace(',', '').strip())
                            total_price += price
                        except (ValueError, AttributeError):
                            pass
        
        return total_price
        
    def clear_build_details(self):
        """Clear build details display"""
        for widget in self.slots_frame.winfo_children():
            widget.destroy()
        
        self.warning_frame.pack_forget()
        self.score_label.config(text="")
        self.bottleneck_label.config(text="")
        
    def check_compatibility(self, build):
        """Check build compatibility"""
        issues = []
        
        # Get parts
        case_info = self.get_part_info(build["parts"]["Case"])
        motherboard_info = self.get_part_info(build["parts"]["Motherboard"])
        cpu_info = self.get_part_info(build["parts"]["CPU"])
        psu_info = self.get_part_info(build["parts"]["PSU"])
        gpu_parts = [self.get_part_info(pid) for pid in build["parts"]["GPU"] if pid is not None]
        ram_parts = [self.get_part_info(pid) for pid in build["parts"]["RAM"] if pid is not None]
        cooler_info = self.get_part_info(build["parts"]["CPU Cooler"])
        storage_parts = [self.get_part_info(pid) for pid in build["parts"]["Storage"] if pid is not None]
        
        # Socket compatibility (CPU-Motherboard)
        if cpu_info and motherboard_info:
            cpu_socket = cpu_info["data"].get("Socket", "")
            mb_socket = motherboard_info["data"].get("CPU Socket", "")
            
            # Log compatibility check details
            logger.info(f"Checking CPU-Motherboard compatibility:")
            logger.info(f"  CPU: {cpu_info['name']} (Socket: {cpu_socket}, Series: {cpu_info['data'].get('Series', 'N/A')})")
            logger.info(f"  Motherboard: {motherboard_info['name']} (Socket: {mb_socket}, Chipset: {motherboard_info['data'].get('Chipset', 'N/A')})")
            
            # Check for Kaby Lake/Skylake compatibility exception
            cpu_is_kaby = "Kaby Lake" in cpu_info["data"].get("Series", "") or "Kaby Lake" in cpu_socket
            mb_is_skylake = "Skylake" in motherboard_info["data"].get("Chipset", "") or "Skylake" in mb_socket
            cpu_is_skylake = "Skylake" in cpu_info["data"].get("Series", "") or "Skylake" in cpu_socket
            mb_is_kaby = "Kaby Lake" in motherboard_info["data"].get("Chipset", "") or "Kaby Lake" in mb_socket
            
            logger.info(f"  CPU is Kaby Lake: {cpu_is_kaby}")
            logger.info(f"  Motherboard is Skylake: {mb_is_skylake}")
            logger.info(f"  CPU is Skylake: {cpu_is_skylake}")
            logger.info(f"  Motherboard is Kaby Lake: {mb_is_kaby}")
            
            # Allow compatibility between Kaby Lake and Skylake
            if (cpu_is_kaby and mb_is_skylake) or (cpu_is_skylake and mb_is_kaby):
                logger.info("  ✓ Kaby Lake/Skylake compatibility - PASS")
            elif cpu_socket != mb_socket:
                issues.append(f"CPU socket ({cpu_socket}) doesn't match motherboard socket ({mb_socket})")
                logger.warning(f"  ✗ Socket mismatch: {cpu_socket} vs {mb_socket}")
            else:
                logger.info("  ✓ Socket compatibility - PASS")
        
        # Case size compatibility
        if case_info and motherboard_info:
            mb_size = motherboard_info["data"].get("Size", "")
            case_support = {
                "Mini-ITX": case_info["data"].get("Mini-ITX") == "Y",
                "Micro-ATX": case_info["data"].get("Micro-ATX") == "Y", 
                "S-ATX": case_info["data"].get("S-ATX") == "Y",
                "E-ATX": case_info["data"].get("E-ATX") == "Y",
                "XL-ATX": case_info["data"].get("XL-ATX") == "Y",
                "SSI-EEB": case_info["data"].get("SSI-EEB") == "Y"
            }
            
            if not case_support.get(mb_size, False):
                issues.append(f"Motherboard size ({mb_size}) not supported by case")
        
        # PSU compatibility
        if case_info and psu_info:
            psu_type = psu_info["data"].get("Type", "")
            max_length = float(case_info["data"].get("Max PSU length", "0"))
            psu_length = float(psu_info["data"].get("Length", "0"))
            
            if psu_type == "ATX" and case_info["data"].get("PSU ATX") != "Y":
                issues.append("Case doesn't support ATX PSU")
            elif psu_type == "SFX" and case_info["data"].get("PSU SFX") != "Y":
                issues.append("Case doesn't support SFX PSU")
            
            if psu_length > max_length > 0:
                issues.append(f"PSU length ({psu_length}mm) exceeds case maximum ({max_length}mm)")
        
        # GPU compatibility
        if case_info and gpu_parts:
            max_gpu_length = float(case_info["data"].get("Max GPU length", "0"))
            for gpu in gpu_parts:
                if gpu:
                    gpu_length = float(gpu["data"].get("Length", "0"))
                    if gpu_length > max_gpu_length > 0:
                        issues.append(f"GPU length ({gpu_length}mm) exceeds case maximum ({max_gpu_length}mm)")
        
        # CPU Cooler compatibility
        if case_info and cooler_info:
            max_height = float(case_info["data"].get("Max CPU Fan Height", "0"))
            cooler_height = float(cooler_info["data"].get("Height", "0"))
            if cooler_height > max_height > 0:
                issues.append(f"CPU cooler height ({cooler_height}mm) exceeds case maximum ({max_height}mm)")
        
        # RAM compatibility
        if motherboard_info and ram_parts:
            ram_type = motherboard_info["data"].get("RAM Type", "")
            for ram in ram_parts:
                if ram:
                    ram_part_type = ram["data"].get("Type", "")
                    if ram_part_type != ram_type:
                        issues.append(f"RAM type ({ram_part_type}) doesn't match motherboard ({ram_type})")
        
        # Storage compatibility
        if motherboard_info and storage_parts:
            # Get motherboard slot counts
            sata_slots = self.get_numeric_value(motherboard_info["data"].get("SATA Slots Usable", 0))
            m2_slots = self.get_numeric_value(motherboard_info["data"].get("M.2 Slots", 0))
            
            # Count storage drives by type
            sata_drives = 0
            m2_drives = 0
            
            for storage in storage_parts:
                if storage:
                    storage_type = storage["data"].get("Type", "")
                    if storage_type == "HDD":
                        sata_drives += 1
                    elif storage_type == "SATA SSD":
                        sata_drives += 1
                    elif storage_type == "NVMe":
                        m2_drives += 1
            
            # Check SATA slots
            if sata_drives > sata_slots:
                issues.append(f"Not enough SATA slots! Need {sata_drives} slots but motherboard only has {sata_slots} SATA slots")
            
            # Check M.2 slots
            if m2_drives > m2_slots:
                issues.append(f"Not enough M.2 slots! Need {m2_drives} slots but motherboard only has {m2_slots} M.2 slots")
        
        # Display warnings
        if issues:
            warning_text = "WARNING! Selected parts are not compatible!\n\n" + "\n".join(issues)
            self.warning_label.config(text=warning_text)
            self.warning_frame.pack(fill=tk.X, pady=(0, 10))
        else:
            self.warning_frame.pack_forget()
            
    def calculate_build_score(self, build):
        """Calculate 3DMark score for build"""
        cpu_info = self.get_part_info(build["parts"]["CPU"])
        gpu_parts = [self.get_part_info(pid) for pid in build["parts"]["GPU"] if pid is not None]
        ram_parts = [self.get_part_info(pid) for pid in build["parts"]["RAM"] if pid is not None]
        
        if not cpu_info or not gpu_parts:
            self.score_label.config(text="Incomplete build - cannot calculate score")
            self.bottleneck_label.config(text="")
            return
        
        # Calculate total sell price
        total_sell_price = self.calculate_total_sell_price(build)
        
        # Calculate 3DMark score
        cpu_data = cpu_info["data"]
        try:
            frequency = float(cpu_data.get("Frequency", "0"))
            core_mult = float(cpu_data.get("CoreClockMultiplier", "1"))
            mem_channels_mult = float(cpu_data.get("MemChannelsMultiplier", "0"))
            mem_clock_mult = float(cpu_data.get("MemClockMultiplier", "0"))
            final_adjustment = float(cpu_data.get("FinalAdjustment", "0"))
            
            # Calculate actual memory channels
            actual_mem_channels = 1
            if len(ram_parts) >= 2:
                actual_mem_channels = 2  # Dual channel
            
            # Calculate actual RAM speed
            actual_ram_speed = 0
            if ram_parts:
                ram_speeds = []
                for ram in ram_parts:
                    try:
                        speed = float(ram["data"].get("Speed", "0"))
                        ram_speeds.append(speed)
                    except:
                        pass
                if ram_speeds:
                    actual_ram_speed = min(ram_speeds)  # Use slowest RAM speed
            
            cpu_score = math.floor(((core_mult * frequency) + (mem_channels_mult * actual_mem_channels) + 
                                  (mem_clock_mult * actual_ram_speed) + final_adjustment) * 298)
        except:
            cpu_score = 1000  # Default if calculation fails
        
        # GPU Score Calculation
        gpu_scores = []
        for gpu in gpu_parts:
            try:
                gpu_score = float(gpu["data"].get("Single GPU Graphics Score", "1000"))
                gpu_scores.append(gpu_score)
            except:
                gpu_scores.append(1000)
        
        if len(gpu_scores) == 1:
            gpu_score = gpu_scores[0]
        else:
            gpu_score = sum(gpu_scores) // len(gpu_scores)  # Average for dual GPU
        
        # Total Score Calculation
        try:
            total_score = math.floor(1 / ((0.85 / gpu_score) + (0.15 / cpu_score)))
        except:
            total_score = 0
        
        # Calculate benchmarked price
        if total_score < 10000:
            benchmarked_price = total_sell_price + 100
        else:
            benchmarked_price = (total_sell_price * 3) + 100
        
        self.score_label.config(text=f"3DMark Score: {total_score:,} (CPU: {cpu_score:,}, GPU: {gpu_score:,})\nPrice (Benchmarked): ${benchmarked_price:,}")
        
        # Identify bottlenecks
        bottlenecks = []
        
        # Check if CPU is bottlenecking GPU (rule of thumb: CPU should be at least 50% of GPU score)
        if cpu_score < gpu_score * 0.5:
            bottlenecks.append(f"CPU may be bottlenecking GPU (CPU: {cpu_score:,} vs GPU: {gpu_score:,})")
        
        # Check for single channel RAM when CPU supports dual channel
        if len(ram_parts) == 1 and cpu_info:
            bottlenecks.append("Single channel RAM - consider adding another stick for dual channel")
        
        # Check RAM speed vs motherboard maximum
        motherboard_info = self.get_part_info(build["parts"]["Motherboard"])
        if motherboard_info and ram_parts:
            try:
                max_ram_speed = float(motherboard_info["data"].get("Max RAM Speed Step", "0"))
                actual_ram_speed = min([float(ram["data"].get("Speed", "0")) for ram in ram_parts])
                if actual_ram_speed < max_ram_speed * 0.8:
                    bottlenecks.append(f"RAM speed ({actual_ram_speed}MHz) below motherboard maximum ({max_ram_speed}MHz)")
            except:
                pass
        
        if bottlenecks:
            self.bottleneck_label.config(text="Potential Bottlenecks:\n" + "\n".join(bottlenecks))
        else:
            self.bottleneck_label.config(text="No significant bottlenecks detected")
            
    def complete_build(self):
        """Complete and remove build"""
        selected_name = self.builds_listbox.get()
        
        if not selected_name:
            messagebox.showwarning("Warning", "Please select a build first!")
            return
        
        # Find build by name
        build = None
        build_index = -1
        for i, b in enumerate(self.builds):
            if b["name"] == selected_name:
                build = b
                build_index = i
                break
        
        if not build or build_index == -1:
            return
        
        # Check if build is complete
        used_parts = []
        for slot_parts in build["parts"].values():
            if isinstance(slot_parts, list):
                for part_id in slot_parts:
                    if part_id is not None:
                        used_parts.append(part_id)
            elif slot_parts is not None:
                used_parts.append(slot_parts)
        
        if not used_parts:
            messagebox.showwarning("Warning", "Build is empty - nothing to complete!")
            return
        
        # Confirm completion
        if messagebox.askyesno("Complete Build", 
                              "This build will be deleted, and the parts used will be removed from your inventory. Proceed?"):
            # Remove used parts from inventory
            parts_to_remove = []
            for part_id in used_parts:
                for i, item in enumerate(self.inventory):
                    if item["id"] == part_id:
                        parts_to_remove.append(i)
                        break
            
            # Remove parts (in reverse order to maintain indices)
            for i in sorted(parts_to_remove, reverse=True):
                self.inventory.pop(i)
            
            # Remove build
            self.builds.pop(build_index)
            
            self.refresh_inventory_display()
            self.refresh_builds_display()
            self.save_state()
            
            messagebox.showinfo("Success", "Build completed successfully!")
            
    def save_state(self):
        """Save application state efficiently"""
        # Create a minimal state object to reduce memory usage
        state = {
            "inventory": self.inventory,
            "builds": self.builds,
            "hem_enabled": self.hem_enabled,
            "show_tip": self.show_tip,
            "new_parts_inventory": self.new_parts_inventory,
            "jobs": self.jobs,
            "text_size_multiplier": self.text_size_multiplier,
            "tips_dismissed": self.tips_dismissed
        }
        
        try:
            # Use temporary file and atomic write to prevent corruption
            temp_file = "pc_builder_state.tmp"
            with open(temp_file, "w", encoding='utf-8') as f:
                json.dump(state, f, indent=2, separators=(',', ':'))
            
            # Atomic rename to final file
            import os
            if os.path.exists("pc_builder_state.json"):
                os.remove("pc_builder_state.json")
            os.rename(temp_file, "pc_builder_state.json")
            
        except Exception as e:
            print(f"Error saving state: {e}")
            # Clean up temp file if it exists
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except:
                pass
            
    def load_state(self):
        """Load application state"""
        if os.path.exists("pc_builder_state.json"):
            try:
                with open("pc_builder_state.json", "r") as f:
                    state = json.load(f)
                
                self.inventory = state.get("inventory", [])
                self.builds = state.get("builds", [])
                self.hem_enabled = state.get("hem_enabled", False)
                self.show_tip = state.get("show_tip", True)
                self.new_parts_inventory = state.get("new_parts_inventory", [])
                self.jobs = state.get("jobs", [])
                
                # Load accessibility settings
                self.text_size_multiplier = state.get("text_size_multiplier", 1.0)
                self.tips_dismissed = state.get("tips_dismissed", {
                    "double_click_add": False,
                    "builds_tab": False,
                    "jobs_tab": False,
                    "story_job": False
                })
                
                # Ensure all builds have storage slots (for backward compatibility)
                for build in self.builds:
                    if "Storage" not in build["parts"]:
                        build["parts"]["Storage"] = [None] * 8
                
                # Ensure all jobs have required fields (for backward compatibility)
                for job in self.jobs:
                    if "job_details" not in job:
                        job["job_details"] = {
                            "new_pc_build": False,
                            "replace_upgrade_parts": False,
                            "threedmark_score": False,
                            "replace_parts": {
                                "CPU": False, "GPU": False, "CPU Cooler": False,
                                "Motherboard": False, "RAM": False, "Power Supply": False,
                                "Storage": False
                            },
                            "bonus_objectives": {
                                "clean_out_dust": False, "remove_viruses": False,
                                "new_cables": False, "brand_preference": False
                            },
                            "cable_type": "", "brand_name": ""
                        }
                    if "original_parts" not in job:
                        job["original_parts"] = {}
                    if "replacement_parts" not in job:
                        job["replacement_parts"] = {}
                    if "threedmark_score" not in job:
                        job["threedmark_score"] = 0
                    if "budget_left" not in job:
                        job["budget_left"] = 0
                
            except Exception as e:
                print(f"Error loading state: {e}")
                self.inventory = []
                self.builds = []
                self.hem_enabled = False
                self.show_tip = True
                self.new_parts_inventory = []
                self.jobs = []
                
    def on_closing(self):
        """Handle window closing efficiently"""
        # Save state in background and close immediately
        try:
            # Create minimal state quickly
            state = {
                "inventory": self.inventory,
                "builds": self.builds,
                "hem_enabled": self.hem_enabled,
                "show_tip": self.show_tip,
                "new_parts_inventory": self.new_parts_inventory,
                "jobs": self.jobs
            }
            
            # Write to temp file quickly
            temp_file = "pc_builder_state.tmp"
            with open(temp_file, "w", encoding='utf-8') as f:
                json.dump(state, f, separators=(',', ':'))
            
            # Quick rename
            import os
            if os.path.exists("pc_builder_state.json"):
                os.remove("pc_builder_state.json")
            os.rename(temp_file, "pc_builder_state.json")
            
        except Exception as e:
            print(f"Quick save error: {e}")
            # Don't block closing even if save fails
        
        # Close immediately
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PCBuilderApp(root)
    root.mainloop()
