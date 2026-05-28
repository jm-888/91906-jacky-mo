

import tkinter as tk
from tkinter import messagebox
import json
import os

FILE_PATH = "recipes.json" # File to store recipes

class Recipe:
    def __init__(self, name, servings, ingredients, instructions):
        self.name         = name    
        self.servings     = servings       # float
        self.ingredients  = ingredients    # list of dicts
        self.instructions = instructions   # string


    def scale(self, new_servings):

        if self.servings == 0:
            return self.ingredients

        ratio  = new_servings / self.servings
        scaled = []

        for ing in self.ingredients:
            try:
                number  = float(ing["quantity"])
                new_num = number * ratio
                # Show whole numbers cleanly no weird decimals easier to read
                if new_num == int(new_num):
                    new_qty = str(int(new_num))
                else:
                    new_qty = f"{new_num:.2f}".rstrip("0").rstrip(".")
                scaled.append({"name": ing["name"], "quantity": new_qty})
            except ValueError:
                scaled.append({"name": ing["name"], "quantity": ing["quantity"]})

        return scaled

    def to_dict(self):
        """Changing it to a plain dict so json.dump() can save it."""
        return {
            "name":         self.name,
            "servings":     self.servings,
            "ingredients":  self.ingredients,
            "instructions": self.instructions,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name         = data["name"],
            servings     = data["servings"],
            ingredients  = data["ingredients"],
            instructions = data["instructions"],
        )
    
def load_recipes():
    """Read recipes.json and return a list of Recipe objects."""
    if not os.path.exists(FILE_PATH):
        return []
    with open(FILE_PATH, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            return [Recipe.from_dict(r) for r in data]
        except (json.JSONDecodeError, KeyError):
            return []   # if file empty start fresh


def save_recipes(recipe_list):
    """Save the full recipe list to recipes.json (overwrites each time)."""
    data = [r.to_dict() for r in recipe_list]
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    root = tk.Tk()
    root.mainloop()