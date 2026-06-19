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


    def do_search(self):
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



    def open_edit_screen(self):
         """Open edit screen for an existing recipe."""
    messagebox.showinfo(
        "Edit Recipe",
        "Editing recipes will be added later."
    )

    def delete_recipe(self, recipe):
        """Delete recipe after confirmation."""
        confirmed = messagebox.askyesno(
            "Delete Recipe",
            f"Delete '{recipe.name}' permanently?"
        )

        if confirmed:
            self.recipe_list.remove(recipe)

            save_recipes(self.recipe_list)

            self.clear_search()

            return True

        return False


    # Gets the selected recipe and opens the detail window
    def open_add_screen(self):
        """Open the add recipe screen."""
        pass

    def open_detail_screen(self, event=None):
        """Open the detail screen for whichever recipe is selected."""
        sel = self.listbox.curselection()
        if not sel:
            return
        index  = sel[0]
        recipe = self.filtered_list[index]
        DetailScreen(self.root, recipe, self)




class DetailScreen(tk.Toplevel):
    """Pop-up window showing a full recipe."""

    def __init__(self, parent, recipe, app):
        super().__init__(parent)
        self.recipe = recipe
        self.app    = app

        self.title(recipe.name)
        self.geometry("500x570")
        self.minsize(420, 420)
        self.grab_set()   # blocks the main window while this is open

        self._build()

    # doubletap a recipe to see all the info


    def _build(self):
        """Build every widget on the detail screen."""

        # Recipe name at the top
        header = tk.Frame(self, padx=14, pady=10)
        header.pack(fill="x")
        tk.Label(header, text=self.recipe.name,
                 font=("Helvetica", 16, "bold"),
                 wraplength=440, justify="left").pack(side="left")
        
        scale_frame = tk.LabelFrame(self, text="Servings", padx=10, pady=8)

        scale_frame.pack(fill="x", padx=14, pady=(0, 8))

        tk.Label(
            scale_frame,
            text=f"Original: {self.recipe.servings}"
        ).pack(side="left", padx=(0, 8))

        self.serving_var = tk.StringVar(
            value=str(self.recipe.servings)
        )

        tk.Entry(
            scale_frame,
            textvariable=self.serving_var,
            width=6
        ).pack(side="left", padx=4)

        tk.Button(
            scale_frame,
            text="Scale",
            command=self.do_scale
        ).pack(side="left")


        self.scale_error_var = tk.StringVar()
        tk.Label(scale_frame, textvariable=self.scale_error_var,
                 fg="red", font=("Helvetica", 9)).pack(side="left", padx=8)

        # Ingredient list its readonly so user cant edit it
        ing_frame = tk.LabelFrame(self, text="Ingredients", padx=10, pady=8)
        ing_frame.pack(fill="x", padx=14, pady=(0, 8))

        self.ing_text = tk.Text(
            ing_frame, height=8, state="disabled",
            wrap="word", font=("Helvetica", 11),
        )
        self.ing_text.pack(fill="both")
        self._show_ingredients(self.recipe.ingredients)

        # Instructions scrollable and readonly
        inst_frame = tk.LabelFrame(self, text="Instructions", padx=10, pady=8)
        inst_frame.pack(fill="both", expand=True, padx=14, pady=(0, 8))

        inst_scroll = tk.Scrollbar(inst_frame)
        inst_scroll.pack(side="right", fill="y")

        inst_text = tk.Text(
            inst_frame,
            yscrollcommand=inst_scroll.set,
            state="disabled",
            wrap="word",
            font=("Helvetica", 11),
        )
        inst_text.pack(fill="both", expand=True)
        inst_scroll.config(command=inst_text.yview)

        inst_text.config(state="normal")
        inst_text.insert("1.0", self.recipe.instructions or "(no instructions added)")
        inst_text.config(state="disabled")

        btn_frame = tk.Frame(self, padx=14, pady=10)
        btn_frame.pack(fill="x")

        tk.Button(
            btn_frame,
            text="Back",
            command=self.destroy
        ).pack(side="left")

        tk.Button(
            btn_frame,
            text="Delete",
            command=self.do_delete
        ).pack(side="right")

        tk.Button(
            btn_frame,
            text="Edit",
            command=self.do_edit
        ).pack(side="right", padx=(0, 6))


    def _show_ingredients(self, ingredients):
        """Fill the ingredient text box with the ingredient list."""
        self.ing_text.config(state="normal")
        self.ing_text.delete("1.0", tk.END)
        for ing in ingredients:
            self.ing_text.insert(tk.END, f"  •  {ing['quantity']}   {ing['name']}\n")
        self.ing_text.config(state="disabled")

    def do_scale(self):
        try:
            new_servings = float(self.serving_var.get())

            if new_servings <= 0:
                raise ValueError

            scaled = self.recipe.scale(new_servings)

            self._show_ingredients(scaled)

        except ValueError:
            messagebox.showerror(
                "Invalid Input",
                "Enter a positive number."
            )


    def do_delete(self):
        deleted = self.app.delete_recipe(self.recipe)

        if deleted:
            self.destroy()


    def do_edit(self):
        self.app.open_edit_screen()


if __name__ == "__main__":
    root = tk.Tk()
    RecipeApp(root)
    root.mainloop()