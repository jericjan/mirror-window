import json
from pathlib import Path


class JSONHandler:
    def __init__(self, file_path):
        self.file_path = file_path
        self.key = "window_names"
        if not Path(file_path).exists():
            data = {self.key: []}
            try:
                with open(file_path, "w") as file:
                    json.dump(data, file, indent=4)
                print(f"Data written to file '{file_path}'.")
            except IOError:
                print(f"Error writing data to file '{file_path}'.")

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
            dic[self.key].append(name)
            self.write(dic)
        except Exception as e:
            print(f"JSON add error: {e}")

    def remove(self, index):
        try:
            dic = self.read()
            dic[self.key].pop(index)
            self.write(dic)
        except Exception as e:
            print(f"JSON remove error: {e}")
