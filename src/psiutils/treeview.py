
from pathlib import Path
import tkinter as tk
from tkinter import ttk
import dateutil  # type: ignore
from dateutil.parser import parse  # type: ignore
from PIL import Image, ImageTk

CHECK_BOX_SIZE = (20, 20)


def sort_treeview(tree: ttk.Treeview, col: int, reverse: bool) -> None:
    """Sort the Treeview by column."""
    children = [
            (tree.set(child, col), child) for child in tree.get_children('')
        ]
    is_date = True
    try:
        date_children = []
        for child in children:
            if len(child[0]) < 8:
                is_date = False
                break
            date = parse(child[0])
            date_children.append((date, child[1]))
    except dateutil.parser._parser.ParserError:
        is_date = False
    if is_date:
        children = date_children
    try:
        children.sort(key=lambda t: float(t[0]), reverse=reverse)
    except TypeError:
        children.sort(key=lambda t: t[0], reverse=reverse)
    except ValueError:
        children.sort(reverse=reverse)

    for index, (val, child) in enumerate(children):
        tree.move(child, '', index)

    tree.heading(col, command=lambda: sort_treeview(tree, col, not reverse))


class CheckTreeView(ttk.Treeview):
    def __init__(
            self,
            master,
            column_defs,
            **kwargs):
        """

        :param column_defs: a tuple defining column (key, text, width)
        Other parameters are passed to the `TreeView`.
        """
        super().__init__(master, **kwargs)
        self.column_defs = column_defs
        self["show"] = "tree headings"
        self._configure_columns()

        (
            self.unchecked_image,
            self.checked_image
        ) = self._get_checkbox_images()

        if "selectmode" not in kwargs:
            kwargs["selectmode"] = "none"
        if "show" not in kwargs:
            kwargs["show"] = "tree"

    def _get_checkbox_images(
            self) -> tuple[ImageTk.PhotoImage, ImageTk.PhotoImage]:

        icon_path = f'{Path(__file__).parent}/icons/'
        unchecked_img = Image.open(f"{icon_path}checkbox_unchecked.png")
        unchecked_img = unchecked_img.resize(CHECK_BOX_SIZE, Image.LANCZOS)
        unchecked = ImageTk.PhotoImage(unchecked_img)

        checked_img = tk.PhotoImage(file=f"{icon_path}checkbox_checked.png")
        checked_img = Image.open(f"{icon_path}checkbox_checked.png")
        checked_img = checked_img.resize(CHECK_BOX_SIZE, Image.LANCZOS)
        checked = ImageTk.PhotoImage(checked_img)
        return (unchecked, checked)

    def _configure_columns(self) -> None:
        column_ids = [col[0] for col in self.column_defs]
        self["columns"] = column_ids[1:]

        # Configure each column
        for index, (col_id, heading, width) in enumerate(self.column_defs):
            if index == 0:
                self.column(
                    "#0",
                    width=width,
                    minwidth=width,
                    stretch=False,
                    anchor="center")
                self.heading("#0", text=heading)
            else:
                self.column(col_id, width=width, anchor="w", stretch=True)
                self.heading(col_id, text=heading)

    def populate(self, items: list[tuple], checked: bool = False) -> None:
        self.delete(*self.get_children())
        item_checked = (self.checked_image
                        if checked else self.unchecked_image)
        for item in items:
            iid = self.insert(
                parent='',
                index='end',
                image=item_checked,
                values=item
            )
            if checked:
                self.item(iid, tags=("checked",))
            else:
                self.item(iid, tags=("unchecked"))

    def item_click(self, event) -> int:
        iid = self.identify_row(event.y)
        if not iid:
            return

        current_img = self.item(iid, "image")[0]
        if current_img == str(self.unchecked_image):
            self.item(iid, image=self.checked_image, tags=("checked",))
        else:
            self.item(iid, image=self.unchecked_image, tags=("unchecked"))

        return "break"

    def checked_items(self) -> list[tuple]:
        """
        Returns a list of the values (text columns) for all currently
        checked rows.

        Each returned tuple contains the values from the data columns only
        (excludes the checkbox image in the tree column).

        Example return value:
            [("docs", "report.pdf", "Read this file"),
            ("code", "main.py", "Fix bug")]
        """
        checked_items = []

        for iid in self.get_children(''):
            tags = self.item(iid, "tags")
            if "checked" in tags:
                values = self.item(iid, "values")
                checked_items.append(values)
        return checked_items
