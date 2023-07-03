import tkinter as tk
from tkinter import simpledialog, ttk, messagebox
import pandas as pd


class BaseCustomDialog(simpledialog.Dialog):
    def __init__(self, parent, title):
        self.font = ('Helvetica', 14)
        super().__init__(parent, title=title)

    def set_geometry(self, width, height):
        self.geometry(f"{width}x{height}")


class AllInOneInputDialog(BaseCustomDialog):
    def __init__(self, parent, title, labels, autocomplete_fields=None, width=300, height=200):
        self.labels = labels
        self.autocomplete_fields = autocomplete_fields or {}
        self.width = width
        self.height = height
        super().__init__(parent, title)

    def body(self, master):
        # Set geometry
        self.set_geometry(self.width, self.height)

        # Create a list to store the entry widgets
        self.entries = []

        # Create labels and entry widgets based on the labels passed
        for i, label_text in enumerate(self.labels):
            label = ttk.Label(master, text=label_text, font=self.font)
            label.grid(row=i, column=0, padx=5, pady=5)

            # Check if this field should have autocomplete
            if i in self.autocomplete_fields:
                entry = ttk.Combobox(master, font=self.font, values=self.autocomplete_fields[i])
            else:
                entry = tk.Entry(master, font=self.font)

            entry.grid(row=i, column=1, padx=5, pady=5)
            self.entries.append(entry)

        return master  # Return the widget that should have focus

    def apply(self):
        # Store the results in a list
        self.result = [entry.get() for entry in self.entries]

    def is_number(self, value):
        if str.isdigit(value) or value == "":
            return True
        else:
            return False



# Example usage:
if __name__ == "__main__":
    root = tk.Tk()


    def on_button_click():
        dialog = AllInOneInputDialog(root, "Enter Stock Details")
        print("EnteredStock Details:", dialog.result)


    button = tk.Button(root, text="Open Dialog", command=on_button_click)
    button.pack(padx=20, pady=20)

    root.mainloop()
