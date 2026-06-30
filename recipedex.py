import tkinter as tk
from tkinter import messagebox
import json
import os

# file all the recipes get saved into
FILE_PATH = "recipes.json"


class Recipe:
    """Stores a single recipe with ingredients and instructions."""
    # basically just a container for all the recipe info so I'm not passing
    # like 4 different variables around everywhere

    def __init__(self, name, servings, ingredients, instructions):
        self.name = name
        self.servings = servings # float
        self.ingredients = ingredients # list of dicts
        self.instructions = instructions # str


    def scale(self, new_servings):
        """Scale ingredient quantities to new servings."""
        # if the og recipe has 0 servings ensure we don't divide by zero
        if self.servings == 0:
            return self.ingredients

        ratio  = new_servings / self.servings  
        # eg. want 8, recipe makes 4 --> ratio is 2
        scaled = []

        for ing in self.ingredients:
            try:
                number  = float(ing["quantity"])
                new_num = number * ratio
# if its a whole number don't show the decimals, looks cleaner
                if new_num == int(new_num):
                    new_qty = str(int(new_num))
                else:
                    # round to 2 decimals then remove trailing zeros 
                    # eg. 1.50 --> 1.5
                    new_qty = f"{new_num:.2f}".rstrip("0").rstrip(".")
                scaled.append({"name": ing["name"], "quantity": new_qty})
            except ValueError:
# quantity wasn't a number "pinch" or "to taste" just leave it alone
                scaled.append({"name": ing["name"], "quantity": ing["quantity"]})

        return scaled

    def to_dict(self):
        """Convert recipe to a dictionary."""
        # need this so json.dump can actually save it,
        # json doesn't know what to do with a Recipe object
        return {
            "name":         self.name,
            "servings":     self.servings,
            "ingredients":  self.ingredients,
            "instructions": self.instructions,
        }

    @classmethod
    def from_dict(cls, data):
        """Create a Recipe from a dictionary."""
# does the opposite of to_dict, 
# turns the saved json back into a real Recipe object
        return cls(
            name         = data["name"],
            servings     = data["servings"],
            ingredients  = data["ingredients"],
            instructions = data["instructions"],
        )


def load_recipes():
    """Load recipes from JSON file."""
    # if the file doesn't exist yet (like first time opening the app)
    #  just return an empty list
    if not os.path.exists(FILE_PATH):
        return []
    with open(FILE_PATH, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            return [Recipe.from_dict(r) for r in data]
        except (json.JSONDecodeError, KeyError):
    # if the json file got messed up somehow (corrupted or edited wrong) 
    # don't crash the whole app, just start fresh with no recipes
            return []


def save_recipes(recipe_list):
    """Save recipes to JSON file."""
    data = [r.to_dict() for r in recipe_list]
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)   
    # indent=2 just makes the file actually readable if you open it


class RecipeApp:
    """Main application window."""
    # home screen, everything else pops up on top of this

    def __init__(self, root):
        self.root = root
        self.root.title("Recipe Manager")
        self.root.geometry("620x500")
        self.root.minsize(480, 360)  
        # stops people from shrinking it to unusable size

        self.recipe_list   = load_recipes()
        self.filtered_list = list(self.recipe_list) 
        # What's displayed in the listbox
        # (filtered_list and recipe_list are the same thing 
        # until you search for something)

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
        self.search_entry.bind("<Return>", lambda event: self.do_search())  
        # so you can hit enter instead of clicking search

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
            # makes the cursor turn into a little hand when hovering, 
            # feels more clickable
        )
        self.listbox.pack(fill="both", expand=True)
        scrollbar.config(command=self.listbox.yview)

        self.listbox.bind("<Double-Button-1>", self.open_detail_screen)
        self.listbox.bind("<Return>", self.open_detail_screen)   # lets you press enter too instead of just double clicking

        self.refresh_list()


    def refresh_list(self):
        """Update the listbox with filtered recipes."""
        # just wipes the listbox and rebuilds it 
        # from whatever is currently in filtered_list
        self.listbox.delete(0, tk.END)
        if self.filtered_list:
            for recipe in self.filtered_list:
                self.listbox.insert(tk.END, f"  {recipe.name}")
        else:
            self.listbox.insert(tk.END, "  No recipes found.")   
            # looks better than just showing a blank box


    def do_search(self):
        """Filter recipes by ingredient name."""
        term = self.search_var.get().strip().lower()
        if not term:
            self.filtered_list = list(self.recipe_list)
        else:
        # Checks every ingredient in every recipe for the search term
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

    def open_edit_screen(self, recipe):
        """Open the Edit screen pre-filled with an existing recipe."""
        AddEditScreen(self.root, recipe=recipe, app=self)



    def delete_recipe(self, recipe):
        """Delete recipe after confirmation."""
        # always ask first before deleting since its permanent 
        confirmed = messagebox.askyesno(
            "Delete Recipe",
            f"Delete '{recipe.name}' permanently?"
        )

        if confirmed:
            self.recipe_list.remove(recipe)

            save_recipes(self.recipe_list)

            self.clear_search()   
        # refreshes the list so the deleted recipe actually disappears

            return True

        return False


    # Gets the selected recipe and opens the detail window
    def open_add_screen(self):
        """Open blank Add Recipe screen to create a new recipe."""
        AddEditScreen(self.root, recipe=None, app=self)

    def open_detail_screen(self, event=None):
        """Open the detail screen for whichever recipe is selected."""
        sel = self.listbox.curselection()
        if not sel:
            return   # nothing selected, nothing to open
        index  = sel[0]
        recipe = self.filtered_list[index]   
        # Has to come from filtered_list not recipe_list or 
        # the indexes get messed up after a search
        DetailScreen(self.root, recipe, self)




class DetailScreen(tk.Toplevel):
    """Pop-up window showing a full recipe."""
# The popup that shows when you double click a recipe in the main list

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

# this box starts off showing the original servings, 
# user types a new number in here
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

# Ingredient list,readonly so the user can't accidentally edit it
# (they have to hit Edit to actually change ingredients)
        ing_frame = tk.LabelFrame(self, text="Ingredients", padx=10, pady=8)
        ing_frame.pack(fill="x", padx=14, pady=(0, 8))

        self.ing_text = tk.Text(
            ing_frame, height=6, state="disabled",
            wrap="word", font=("Helvetica", 11),  
        )
        self.ing_text.pack(fill="both")
        self._show_ingredients(self.recipe.ingredients)

    # Instructions, scrollable and also readonly
        inst_frame = tk.LabelFrame(self, text="Instructions", padx=10, pady=8)
        inst_frame.pack(fill="x", padx=14, pady=(0, 8))

        inst_scroll = tk.Scrollbar(inst_frame)
        inst_scroll.pack(side="right", fill="y")

        inst_text = tk.Text(
            inst_frame,
            height=12,# 12 makes it nicely cropped without weird spacing
            yscrollcommand=inst_scroll.set,
            state="disabled",
            wrap="word",
            font=("Helvetica", 11),
        )
        inst_text.pack(fill="x")
        inst_scroll.config(command=inst_text.yview)

# gotta flip state back to normal just to insert text,
#  then disable it again so it's not editable. 
# kind of annoying but that's how tkinter Text widgets work
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
# samething as instructions,
#  has to be "normal" to edit then back to "disabled" after
        self.ing_text.config(state="normal")
        self.ing_text.delete("1.0", tk.END)
        for ing in ingredients:
            self.ing_text.insert(tk.END, f"  •  {ing['quantity']}   {ing['name']}\n")
        self.ing_text.config(state="disabled")

    def do_scale(self):
# this doesn't actually change the saved recipe, 
# it just recalculates what's shown on screen. 
# so scaling to 8 servings and closing the window won't save it as 8
        try:
            new_servings = float(self.serving_var.get())
            if new_servings <= 0:
                raise ValueError 
            # Prevents users from scaling to 0 or negative servings
            scaled = self.recipe.scale(new_servings)
            self._show_ingredients(scaled)
        except ValueError:
            messagebox.showerror(
                "Invalid Input",
                "Enter a positive number."
            )

    def do_edit(self):
        """Close this window and open the Edit screen."""
        self.destroy()
        self.app.open_edit_screen(self.recipe)

    def do_delete(self):
        """Delete this recipe and close the window if confirmed."""
        deleted = self.app.delete_recipe(self.recipe)
        if deleted:
            self.destroy()  
            # Only closes the popup if they actually confirmed the delete

class AddEditScreen(tk.Toplevel):
    """
    Scrollable form for adding a new recipe or editing an existing one.
    Pass recipe=None to add, or a Recipe object to edit.
    """
    # didn't want to write two almost identical classes for add vs edit 
    # just handles both depending on whether recipe is None or not

    def __init__(self, parent, recipe, app):
        super().__init__(parent)
        self.recipe   = recipe # None = adding,  Recipe object = editing
        self.app      = app
        self.ing_rows = [] # keeps track of ingredient row widgets

        self.title("Edit Recipe" if recipe else "Add Recipe")
        self.geometry("500x700")
        self.minsize(420, 600)
        self.grab_set()

        self._build_scrollable_form()
        
        if recipe:
            self._prefill()   
            # Only fill stuff in if we're editing, not adding new

    def _build_scrollable_form(self):
        """Wrap the form in a Canvas so it scrolls on small screens """
    # tkinter doesn't have a built in scrollable frame
    # Created one with Canvas + Frame
        canvas    = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)

        self.form     = tk.Frame(canvas, padx=14, pady=10)
        self._form_id = canvas.create_window((0, 0), window=self.form, anchor="nw")

        # Updates the scroll region whenever the form changes size 
        # (eg. when you add more ingredient rows)
        self.form.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        # keeps the form the same width as the canvas
        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfig(self._form_id, width=e.width)
        )

# Lets the user scroll with their mouse wheel when hovering over the form
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))   # linux scroll up
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll( 1, "units"))   # linux scroll down

        self._build_form_widgets()

    def _build_form_widgets(self):
        """Add all the labels and buttons to self.form"""

        # Recipe name
        tk.Label(self.form, text="Recipe name *",
                 font=("Helvetica", 11, "bold")).pack(anchor="w")
        self.name_var = tk.StringVar()
        tk.Entry(self.form, textvariable=self.name_var,
                 width=42).pack(anchor="w", pady=(2, 12))

        # Default servings
        tk.Label(self.form, text="Default servings *",
                 font=("Helvetica", 11, "bold")).pack(anchor="w")
        self.servings_var = tk.StringVar(value="4")   
        # 4 since thats a normal recipe size
        tk.Entry(self.form, textvariable=self.servings_var,
                 width=10).pack(anchor="w", pady=(2, 12))
        
        tk.Label(self.form, text="Ingredients *",
                 font=("Helvetica", 11, "bold")).pack(anchor="w")

        # Column headers, labels not actual entry boxes
        col_header = tk.Frame(self.form)
        col_header.pack(fill="x", pady=(2, 0))
        tk.Label(col_header, text="Ingredient name", width=24, anchor="w",
                 font=("Helvetica", 9), fg="grey").pack(side="left")
        tk.Label(col_header, text="Quantity",        width=14, anchor="w",
                 font=("Helvetica", 9), fg="grey").pack(side="left")

# New ingredient rows get packed inside this container as they're added
        self.ing_container = tk.Frame(self.form)
        self.ing_container.pack(fill="x")

        # always start with one blank row so the form doesn't look empty
        self.add_ingredient_row()

        tk.Button(self.form, text="+ Add ingredient",
                  command=self.add_ingredient_row).pack(anchor="w", pady=(6, 12))


        # Instructions
        tk.Label(self.form, text="Instructions",
                 font=("Helvetica", 11, "bold")).pack(anchor="w")
        self.inst_text = tk.Text(self.form, height=8, wrap="word",
                                 font=("Helvetica", 11))
        self.inst_text.pack(fill="x", pady=(2, 12))



        self.error_var = tk.StringVar()
        tk.Label(self.form, textvariable=self.error_var,
                 fg="red", wraplength=460, justify="left").pack(anchor="w")

        # Save / Cancel buttons
        btn_frame = tk.Frame(self.form)
        btn_frame.pack(fill="x", pady=(8, 4))

        tk.Button(btn_frame, text="Save",
                  command=self.do_save, width=10).pack(side="left", padx=(0, 8))
        tk.Button(btn_frame, text="Cancel",
                  command=self.destroy, width=10).pack(side="left")

        tk.Label(self.form, text="* required",
                 font=("Helvetica", 9), fg="grey").pack(anchor="w", pady=(4, 0))


        

    def add_ingredient_row(self, name="", qty=""):
        """
        Add one ingredient row 
        Prefill name and quantity when called from _prefill (editing mode).
        """
        row      = tk.Frame(self.ing_container)
        row.pack(fill="x", pady=1)

        name_var = tk.StringVar(value=name)
        qty_var  = tk.StringVar(value=qty)

        tk.Entry(row, textvariable=name_var, width=24).pack(side="left", padx=(0, 6))
        tk.Entry(row, textvariable=qty_var,  width=14).pack(side="left", padx=(0, 6))

        def remove_this_row():
# Always keeps one row so the forms never completely empty
# (also keeps do_save from breaking with zero rows to loop through)
            if len(self.ing_rows) > 1:
                self.ing_rows.remove((name_var, qty_var, row))
                row.destroy()

        tk.Button(row, text="✕", command=remove_this_row, width=2).pack(side="left")
        self.ing_rows.append((name_var, qty_var, row))

    def _prefill(self):
        """Fill every field with the existing recipe's data."""
        self.name_var.set(self.recipe.name)
        self.servings_var.set(str(int(self.recipe.servings)))
        self.inst_text.insert("1.0", self.recipe.instructions)

# Gets rid of the default blank row so there isn't a extra empty one
        for _, _, frame in self.ing_rows:
            frame.destroy()
        self.ing_rows.clear()

# Add one row per existing ingredient, prefilled with its name/qty
        for ing in self.recipe.ingredients:
            self.add_ingredient_row(name=ing["name"], qty=ing["quantity"])

    def do_save(self):
        """Validate all fields then add or update the recipe."""
        self.error_var.set("") # clear any previous error message first

        # Name must not be empty
        name = self.name_var.get().strip()
        if not name:
            self.error_var.set("Recipe name cannot be empty.")
            return

        # Servings must be a positive number
        try:
            servings = float(self.servings_var.get())
            if servings <= 0:
                raise ValueError
        except ValueError:
            self.error_var.set("Servings must be a positive number (e.g. 4).")
            return

        # Collect ingredient rows, 
        # skip ones with no name typed in (silently, no error needed)
        ingredients = []
        for name_var, qty_var, _ in self.ing_rows:
            ing_name = name_var.get().strip()
            qty      = qty_var.get().strip()
            if ing_name:
                ingredients.append({"name": ing_name, "quantity": qty})

# Requires atleast one real ingredient
        if not ingredients:
            self.error_var.set("Please add at least one ingredient.")
            return

        # Instructions are optional so no validation needed for those
        instructions = self.inst_text.get("1.0", "end-1c").strip()

        # Update existing Recipe or create a new one
        if self.recipe:
            # editing, just update the fields on the existing object
            self.recipe.name         = name
            self.recipe.servings     = servings
            self.recipe.ingredients  = ingredients
            self.recipe.instructions = instructions
        else:
# Adding, make a brand new Recipe and stick it onto the master list
            new_recipe = Recipe(name, servings, ingredients, instructions)
            self.app.recipe_list.append(new_recipe)

        # Save everything to the json file and refresh the main screen 
        save_recipes(self.app.recipe_list)
        self.app.clear_search()
        self.destroy()




if __name__ == "__main__":
    root = tk.Tk()
    RecipeApp(root)
    root.mainloop()