import tkinter as tk
from tkinter import messagebox
import json
import os

FILE_PATH = "recipes.json"


class Recipe:
    """Stores a single recipe with ingredients and instructions."""

    def __init__(self, name, servings, ingredients, instructions):
        self.name = name
        self.servings = servings # float
        self.ingredients = ingredients # list of dicts
        self.instructions = instructions # str


    def scale(self, new_servings):
        """Scale ingredient quantities to new servings."""
        if self.servings == 0:
            return self.ingredients

        ratio  = new_servings / self.servings
        scaled = []

        for ing in self.ingredients:
            try:
                number  = float(ing["quantity"])
                new_num = number * ratio
                # Show whole numbers cleanly no decimals
                if new_num == int(new_num):
                    new_qty = str(int(new_num))
                else:
                    new_qty = f"{new_num:.2f}".rstrip("0").rstrip(".")
                scaled.append({"name": ing["name"], "quantity": new_qty})
            except ValueError:
                scaled.append({"name": ing["name"], "quantity": ing["quantity"]})

        return scaled

    def to_dict(self):
        """Convert recipe to a dictionary."""
        return {
            "name":         self.name,
            "servings":     self.servings,
            "ingredients":  self.ingredients,
            "instructions": self.instructions,
        }

    @classmethod
    def from_dict(cls, data):
        """Create a Recipe from a dictionary."""
        return cls(
            name         = data["name"],
            servings     = data["servings"],
            ingredients  = data["ingredients"],
            instructions = data["instructions"],
        )


def load_recipes():
    """Load recipes from JSON file."""
    if not os.path.exists(FILE_PATH):
        return []
    with open(FILE_PATH, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            return [Recipe.from_dict(r) for r in data]
        except (json.JSONDecodeError, KeyError):
            return []


def save_recipes(recipe_list):
    """Save recipes to JSON file."""
    data = [r.to_dict() for r in recipe_list]
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

class RecipeApp:
    """Main application window."""

    def __init__(self, root):
        self.root = root
        self.root.title("Recipe Manager")
        self.root.geometry("620x500")
        self.root.minsize(480, 360)

        self.recipe_list   = load_recipes()
        self.filtered_list = list(self.recipe_list)

        self._build_main_screen()


    def _build_main_screen(self):
        """Build the main screen widgets."""

        # Top bar - title label + Add button
        top = tk.Frame(self.root, padx=14, pady=10)
        top.pack(fill="x")

        tk.Label(top, text="My Recipes",
                 font=("Helvetica", 18, "bold")).pack(side="left")

        tk.Button(top, text="+ Add Recipe",
                  command=self.open_add_screen).pack(side="right")
        
        search_frame = tk.Frame(self.root, padx=14, pady=2)
        search_frame.pack(fill="x")

        tk.Label(search_frame, text="Search by ingredient:").pack(side="left", padx=(0, 6))

        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame,
                                     textvariable=self.search_var, width=28)
        self.search_entry.pack(side="left", padx=(0, 6))
        self.search_entry.bind("<Return>", self.do_search)

        tk.Button(search_frame, text="Search",
                  command=self.do_search).pack(side="left", padx=(0, 4))
        
        # Clear Search button
        tk.Button(search_frame, text="Clear",
                  command=self.clear_search).pack(side="left")


        list_frame = tk.Frame(self.root, padx=14, pady=10)
        list_frame.pack(fill="both", expand=True)

        tk.Label(list_frame,
                 text="Double-click a recipe to open it",
                 font=("Helvetica", 9), fg="grey").pack(anchor="w", pady=(0, 4))

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        self.listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            font=("Helvetica", 12),
            selectmode="single",
            activestyle="none",
            cursor="hand2",
        )
        self.listbox.pack(fill="both", expand=True)
        scrollbar.config(command=self.listbox.yview)

        self.listbox.bind("<Double-Button-1>", self.open_detail_screen)
        self.listbox.bind("<Return>",          self.open_detail_screen)

        self.refresh_list()

    def refresh_list(self):
        """Update the listbox with filtered recipes."""
        self.listbox.delete(0, tk.END)
        if self.filtered_list:
            for recipe in self.filtered_list:
                self.listbox.insert(tk.END, f"  {recipe.name}")
        else:
            self.listbox.insert(tk.END, "  No recipes found.")


    def do_search(self, event=None):
        """Filter recipes by ingredient name."""
        term = self.search_var.get().strip().lower()
        if not term:
            self.filtered_list = list(self.recipe_list)
        else:
            self.filtered_list = [
                r for r in self.recipe_list
                if any(term in ing["name"].lower() for ing in r.ingredients)
            ]
        self.refresh_list()


    def clear_search(self):
        """Clear search and show all recipes."""
        self.search_var.set("")
        self.filtered_list = list(self.recipe_list)
        self.refresh_list()

    def open_add_screen(self):
        """Open the add recipe screen."""
        pass

    def open_detail_screen(self, event=None):
        """Open the recipe detail screen."""
        pass


if __name__ == "__main__":
    root = tk.Tk()
    RecipeApp(root)
    root.mainloop()
