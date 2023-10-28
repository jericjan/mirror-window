import json
from pathlib import Path
import copy
from decimal import Decimal, getcontext

def merge_nested_dicts(d1, d2):
    for key, value in d2.items():
        if key in d1 and isinstance(d1[key], dict) and isinstance(value, dict):
            merge_nested_dicts(d1[key], value)
        elif key not in d1:
            d1[key] = value


class JSONHandler:
    def __init__(self, file_path):
        self.file_path = file_path
        self.window_names = "window_names"
        initial_dict = {
            self.window_names: [],
            "current": {
                "window": "",
                "auto_popup": True,
                "auto_minimize": True,
                "active_delay": [250, 1],
                "paused_delay": [1000, 1],
            },
        }
        if not Path(file_path).exists():
            try:
                with open(file_path, "w") as file:
                    json.dump(initial_dict, file, indent=4)
                print(f"Data written to file '{file_path}'.")
            except IOError:
                print(f"Error writing data to file '{file_path}'.")
        else:
            saved_dic = self.read()
            old_saved = copy.deepcopy(saved_dic)
            merge_nested_dicts(saved_dic, initial_dict)
            if old_saved != saved_dic:
                self.write(saved_dic)

    def read(self):
        try:
            with open(self.file_path, "r") as file:
                data = json.load(file)
                return data
        except FileNotFoundError:
            print(f"File '{self.file_path}' not found.")
            return None
        except json.JSONDecodeError:
            print(f"Error decoding JSON from file '{self.file_path}'.")
            return None

    def write(self, data):
        try:
            with open(self.file_path, "w") as file:
                json.dump(data, file, indent=4)
                print(f"Data written to file '{self.file_path}'.")
        except IOError:
            print(f"Error writing data to file '{self.file_path}'.")

    def add(self, name):
        try:
            dic = self.read()
            dic[self.window_names].append(name)
            self.write(dic)
        except Exception as e:
            print(f"JSON add error: {e}")

    def remove(self, index):
        try:
            dic = self.read()
            dic[self.window_names].pop(index)
            self.write(dic)
        except Exception as e:
            print(f"JSON remove error: {e}")

    def get_window_names(self):
        dic = self.read()
        window_names = dic[self.window_names]
        return window_names

    def set_current(self, key, new_value, integer_ratio=False):
        dic = self.read()

        if integer_ratio:
            getcontext().prec = 28
            dic["current"][key] = list(new_value.as_integer_ratio())  # TODO: just use type checks instead
        else:
            dic["current"][key] = new_value
        self.write(dic)

    def get_current(self, key, integer_ratio=False):
        dic = self.read()
        current_dic = dic["current"]
        if integer_ratio:
            return (Decimal(current_dic[key][0]) / Decimal(current_dic[key][1])).normalize()
        return current_dic[key]
    
