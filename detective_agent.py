"""
detective_gui.py
-----------------
DATA DETECTIVE AGENT - GUI Edition

A desktop app (built with CustomTkinter) that you point at any CSV
spreadsheet. It can:
    - Load and preview the data in a table
    - Answer questions: row count, average, max/min, top record, filter,
      group-by average
    - Draw charts: bar, line, histogram - shown right inside the window
    - Save any chart as a PNG image

Ships with world_data.csv - a small real-world dataset of country
population, GDP, area, and life expectancy (approximate figures, for
demo purposes) - instead of made-up sample data.

Run with:
    python detective_gui.py

Install dependencies first (only once per computer):
    pip install customtkinter pandas matplotlib numpy
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import customtkinter as ctk
import pandas as pd

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

APP_BG = "#0d1117"
PANEL_BG = "#161b22"
ACCENT = "#58a6ff"
TEXT_DIM = "#8b949e"

DEFAULT_FILE = "world_data.csv"


def make_font(size, weight="normal"):
    return ctk.CTkFont(family="Segoe UI", size=size, weight=weight)


class DataDetectiveApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Data Detective Agent")
        self.geometry("1150x720")
        self.minsize(950, 600)
        self.configure(fg_color=APP_BG)

        self.data = None          # the loaded pandas DataFrame
        self.current_filename = None
        self.current_figure = None  # last matplotlib Figure, for saving

        self._build_topbar()
        self._build_tabs()

        # Try to auto-load the sample dataset shipped alongside this script.
        if os.path.exists(DEFAULT_FILE):
            self._load_dataframe(DEFAULT_FILE)

    # ------------------------------------------------------------
    # Top bar: open file + status
    # ------------------------------------------------------------
    def _build_topbar(self):
        bar = ctk.CTkFrame(self, fg_color=PANEL_BG, height=64, corner_radius=0)
        bar.pack(fill="x", side="top")

        title_lbl = ctk.CTkLabel(bar, text="🔎 Data Detective Agent",
                                  font=make_font(20, "bold"))
        title_lbl.pack(side="left", padx=20, pady=14)

        open_btn = ctk.CTkButton(bar, text="Open CSV...", command=self.open_file,
                                  width=130, height=36, font=make_font(13, "bold"))
        open_btn.pack(side="right", padx=20, pady=14)

        self.status_lbl = ctk.CTkLabel(bar, text="No file loaded yet.",
                                        font=make_font(12), text_color=TEXT_DIM)
        self.status_lbl.pack(side="right", padx=10)

    # ------------------------------------------------------------
    # Tabs
    # ------------------------------------------------------------
    def _build_tabs(self):
        self.tabview = ctk.CTkTabview(self, fg_color=APP_BG,
                                       segmented_button_selected_color=ACCENT)
        self.tabview.pack(fill="both", expand=True, padx=16, pady=16)

        self.tab_preview = self.tabview.add("Preview")
        self.tab_ask = self.tabview.add("Ask a Question")
        self.tab_chart = self.tabview.add("Charts")

        self._build_preview_tab()
        self._build_ask_tab()
        self._build_chart_tab()

    # ==============================================================
    # PREVIEW TAB
    # ==============================================================
    def _build_preview_tab(self):
        info_frame = ctk.CTkFrame(self.tab_preview, fg_color=PANEL_BG)
        info_frame.pack(fill="x", pady=(0, 10))

        self.shape_lbl = ctk.CTkLabel(info_frame, text="Rows: -   Columns: -",
                                       font=make_font(13, "bold"))
        self.shape_lbl.pack(side="left", padx=16, pady=10)

        self.columns_lbl = ctk.CTkLabel(info_frame, text="Columns: -",
                                         font=make_font(12), text_color=TEXT_DIM,
                                         wraplength=900, justify="left")
        self.columns_lbl.pack(side="left", padx=16, pady=10)

        # A ttk.Treeview gives us a proper spreadsheet-style table.
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#0d1117", fieldbackground="#0d1117",
                         foreground="#e6edf3", rowheight=26, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background="#161b22", foreground="#58a6ff",
                         font=("Segoe UI", 10, "bold"))
        style.map("Treeview", background=[("selected", "#1f6feb")])

        table_frame = ctk.CTkFrame(self.tab_preview, fg_color=PANEL_BG)
        table_frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(table_frame, show="headings")
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

    def _refresh_preview(self):
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = list(self.data.columns)
        for col in self.data.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="w")

        # Show up to the first 200 rows so huge files don't freeze the UI.
        preview_rows = self.data.head(200)
        for _, row in preview_rows.iterrows():
            self.tree.insert("", "end", values=list(row))

        self.shape_lbl.configure(
            text=f"Rows: {self.data.shape[0]}   Columns: {self.data.shape[1]}"
        )
        self.columns_lbl.configure(text="Columns: " + ", ".join(self.data.columns))

    # ==============================================================
    # ASK A QUESTION TAB
    # ==============================================================
    def _build_ask_tab(self):
        self.tab_ask.grid_columnconfigure(0, weight=1)

        control_frame = ctk.CTkFrame(self.tab_ask, fg_color=PANEL_BG)
        control_frame.pack(fill="x", pady=(0, 12))

        op_lbl = ctk.CTkLabel(control_frame, text="What do you want to know?",
                               font=make_font(13, "bold"))
        op_lbl.grid(row=0, column=0, sticky="w", padx=16, pady=(14, 4), columnspan=4)

        self.operations = [
            "Row count",
            "Average of a column",
            "Highest & lowest of a column",
            "Find the row with the top value",
            "Filter rows by a condition",
            "Average grouped by a category",
        ]
        self.operation_var = ctk.StringVar(value=self.operations[0])
        op_menu = ctk.CTkOptionMenu(control_frame, values=self.operations,
                                     variable=self.operation_var,
                                     command=self._on_operation_change, width=280)
        op_menu.grid(row=1, column=0, padx=16, pady=(0, 14), sticky="w")

        # Dynamic inputs live in this sub-frame; rebuilt per operation.
        self.dynamic_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        self.dynamic_frame.grid(row=1, column=1, columnspan=3, sticky="w")

        run_btn = ctk.CTkButton(control_frame, text="Run", width=100,
                                 command=self.run_question, fg_color=ACCENT)
        run_btn.grid(row=2, column=0, padx=16, pady=(0, 14), sticky="w")

        result_lbl = ctk.CTkLabel(self.tab_ask, text="Answer",
                                   font=make_font(13, "bold"))
        result_lbl.pack(anchor="w", pady=(4, 4))

        self.result_box = ctk.CTkTextbox(self.tab_ask, fg_color=PANEL_BG,
                                          font=("Consolas", 12), wrap="none")
        self.result_box.pack(fill="both", expand=True)

        self._on_operation_change(self.operations[0])

    def _numeric_columns(self):
        if self.data is None:
            return []
        return self.data.select_dtypes(include="number").columns.tolist()

    def _category_columns(self):
        if self.data is None:
            return []
        numeric = set(self._numeric_columns())
        return [c for c in self.data.columns if c not in numeric]

    def _clear_dynamic_frame(self):
        for widget in self.dynamic_frame.winfo_children():
            widget.destroy()

    def _on_operation_change(self, operation):
        self._clear_dynamic_frame()
        numeric_cols = self._numeric_columns() or ["(load data first)"]
        category_cols = self._category_columns() or ["(load data first)"]

        if operation == "Row count":
            pass  # no extra inputs needed

        elif operation in ("Average of a column", "Highest & lowest of a column",
                            "Find the row with the top value"):
            self.col_var = ctk.StringVar(value=numeric_cols[0])
            menu = ctk.CTkOptionMenu(self.dynamic_frame, values=numeric_cols,
                                      variable=self.col_var, width=200)
            menu.pack(side="left", padx=8)

        elif operation == "Filter rows by a condition":
            self.col_var = ctk.StringVar(value=numeric_cols[0])
            ctk.CTkOptionMenu(self.dynamic_frame, values=numeric_cols,
                               variable=self.col_var, width=170).pack(side="left", padx=6)

            self.comparison_var = ctk.StringVar(value=">")
            ctk.CTkOptionMenu(self.dynamic_frame, values=[">", "<", "=="],
                               variable=self.comparison_var, width=70).pack(side="left", padx=6)

            self.value_entry = ctk.CTkEntry(self.dynamic_frame, width=120,
                                             placeholder_text="value")
            self.value_entry.pack(side="left", padx=6)

        elif operation == "Average grouped by a category":
            self.group_var = ctk.StringVar(value=category_cols[0])
            ctk.CTkOptionMenu(self.dynamic_frame, values=category_cols,
                               variable=self.group_var, width=170).pack(side="left", padx=6)

            self.col_var = ctk.StringVar(value=numeric_cols[0])
            ctk.CTkOptionMenu(self.dynamic_frame, values=numeric_cols,
                               variable=self.col_var, width=170).pack(side="left", padx=6)

    def run_question(self):
        if self.data is None:
            messagebox.showwarning("No data", "Please open a CSV file first.")
            return

        operation = self.operation_var.get()
        try:
            if operation == "Row count":
                answer = f"There are {len(self.data)} rows in this dataset."

            elif operation == "Average of a column":
                col = self.col_var.get()
                answer = f"The average {col} is {self.data[col].mean():.2f}."

            elif operation == "Highest & lowest of a column":
                col = self.col_var.get()
                answer = (f"Highest {col}: {self.data[col].max()}\n"
                          f"Lowest {col}: {self.data[col].min()}")

            elif operation == "Find the row with the top value":
                col = self.col_var.get()
                top_index = self.data[col].idxmax()
                top_row = self.data.loc[top_index]
                answer = f"Row with the highest {col}:\n\n{top_row.to_string()}"

            elif operation == "Filter rows by a condition":
                col = self.col_var.get()
                comparison = self.comparison_var.get()
                value_text = self.value_entry.get().strip()
                value = float(value_text)

                if comparison == ">":
                    result = self.data[self.data[col] > value]
                elif comparison == "<":
                    result = self.data[self.data[col] < value]
                else:
                    result = self.data[self.data[col] == value]

                answer = (f"Found {len(result)} row(s) where {col} {comparison} {value}:\n\n"
                          f"{result.to_string(index=False)}")

            elif operation == "Average grouped by a category":
                group_col = self.group_var.get()
                value_col = self.col_var.get()
                grouped = self.data.groupby(group_col)[value_col].mean()
                answer = f"Average {value_col} by {group_col}:\n\n{grouped.to_string()}"

            else:
                answer = "Unknown operation."

        except ValueError:
            answer = "That value isn't a valid number. Please check your input."
        except Exception as error:
            answer = f"Something went wrong: {error}"

        self.result_box.delete("1.0", "end")
        self.result_box.insert("1.0", answer)

    # ==============================================================
    # CHARTS TAB
    # ==============================================================
    def _build_chart_tab(self):
        control_frame = ctk.CTkFrame(self.tab_chart, fg_color=PANEL_BG)
        control_frame.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(control_frame, text="Chart type:", font=make_font(13, "bold")).grid(
            row=0, column=0, padx=(16, 6), pady=14, sticky="w")

        self.chart_type_var = ctk.StringVar(value="Bar chart")
        chart_menu = ctk.CTkOptionMenu(
            control_frame, values=["Bar chart", "Line chart", "Histogram"],
            variable=self.chart_type_var, command=self._on_chart_type_change, width=150,
        )
        chart_menu.grid(row=0, column=1, padx=6, pady=14, sticky="w")

        ctk.CTkLabel(control_frame, text="X / category column:", font=make_font(12)).grid(
            row=0, column=2, padx=(16, 6), pady=14, sticky="w")
        self.chart_x_var = ctk.StringVar()
        self.chart_x_menu = ctk.CTkOptionMenu(control_frame, values=["-"],
                                               variable=self.chart_x_var, width=160)
        self.chart_x_menu.grid(row=0, column=3, padx=6, pady=14, sticky="w")

        self.y_label = ctk.CTkLabel(control_frame, text="Y / value column:", font=make_font(12))
        self.y_label.grid(row=0, column=4, padx=(16, 6), pady=14, sticky="w")
        self.chart_y_var = ctk.StringVar()
        self.chart_y_menu = ctk.CTkOptionMenu(control_frame, values=["-"],
                                               variable=self.chart_y_var, width=160)
        self.chart_y_menu.grid(row=0, column=5, padx=6, pady=14, sticky="w")

        gen_btn = ctk.CTkButton(control_frame, text="Generate", width=100,
                                 command=self.generate_chart, fg_color=ACCENT)
        gen_btn.grid(row=0, column=6, padx=(16, 6), pady=14)

        save_btn = ctk.CTkButton(control_frame, text="Save PNG...", width=110,
                                  command=self.save_chart)
        save_btn.grid(row=0, column=7, padx=6, pady=14)

        self.chart_holder = ctk.CTkFrame(self.tab_chart, fg_color=PANEL_BG)
        self.chart_holder.pack(fill="both", expand=True)

        self.canvas_widget = None
        self._on_chart_type_change("Bar chart")

    def _on_chart_type_change(self, chart_type):
        # Histograms only need one numeric column; bar/line need X and Y.
        if chart_type == "Histogram":
            self.y_label.grid_remove()
            self.chart_y_menu.grid_remove()
        else:
            self.y_label.grid()
            self.chart_y_menu.grid()

    def _refresh_chart_columns(self):
        all_cols = list(self.data.columns) if self.data is not None else ["-"]
        numeric_cols = self._numeric_columns() or ["-"]

        self.chart_x_menu.configure(values=all_cols)
        self.chart_x_var.set(all_cols[0])

        self.chart_y_menu.configure(values=numeric_cols)
        self.chart_y_var.set(numeric_cols[0])

    def generate_chart(self):
        if self.data is None:
            messagebox.showwarning("No data", "Please open a CSV file first.")
            return

        chart_type = self.chart_type_var.get()
        x_col = self.chart_x_var.get()
        y_col = self.chart_y_var.get()

        fig = Figure(figsize=(8, 5), dpi=100, facecolor=PANEL_BG)
        ax = fig.add_subplot(111)
        ax.set_facecolor(PANEL_BG)
        ax.tick_params(colors="#e6edf3")
        for spine in ax.spines.values():
            spine.set_color("#30363d")
        ax.title.set_color("#e6edf3")
        ax.xaxis.label.set_color("#e6edf3")
        ax.yaxis.label.set_color("#e6edf3")

        try:
            if chart_type == "Bar chart":
                ax.bar(self.data[x_col].astype(str), self.data[y_col], color=ACCENT)
                ax.set_title(f"{y_col} by {x_col}")
                ax.set_xlabel(x_col)
                ax.set_ylabel(y_col)
                fig.autofmt_xdate(rotation=45)

            elif chart_type == "Line chart":
                ax.plot(self.data[x_col].astype(str), self.data[y_col], marker="o", color=ACCENT)
                ax.set_title(f"{y_col} over {x_col}")
                ax.set_xlabel(x_col)
                ax.set_ylabel(y_col)
                fig.autofmt_xdate(rotation=45)

            elif chart_type == "Histogram":
                ax.hist(self.data[x_col], color=ACCENT, bins=10)
                ax.set_title(f"Distribution of {x_col}")
                ax.set_xlabel(x_col)
                ax.set_ylabel("Count")

        except Exception as error:
            messagebox.showerror("Chart error", f"Couldn't build that chart:\n{error}")
            return

        # Remove any previous chart canvas before drawing the new one.
        if self.canvas_widget is not None:
            self.canvas_widget.get_tk_widget().destroy()

        canvas = FigureCanvasTkAgg(fig, master=self.chart_holder)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        self.canvas_widget = canvas
        self.current_figure = fig

    def save_chart(self):
        if self.current_figure is None:
            messagebox.showwarning("No chart yet", "Generate a chart first, then save it.")
            return
        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG image", "*.png")],
            initialfile="chart.png",
        )
        if filepath:
            self.current_figure.savefig(filepath, facecolor=self.current_figure.get_facecolor())
            messagebox.showinfo("Saved", f"Chart saved to:\n{filepath}")

    # ==============================================================
    # FILE LOADING
    # ==============================================================
    def open_file(self):
        filepath = filedialog.askopenfilename(
            title="Open a CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if filepath:
            self._load_dataframe(filepath)

    def _load_dataframe(self, filepath):
        try:
            data = pd.read_csv(filepath)
        except Exception as error:
            messagebox.showerror("Couldn't load file", f"Error reading '{filepath}':\n{error}")
            return

        self.data = data
        self.current_filename = filepath
        self.status_lbl.configure(text=f"Loaded: {os.path.basename(filepath)}")

        self._refresh_preview()
        self._on_operation_change(self.operation_var.get())
        self._refresh_chart_columns()


def main():
    app = DataDetectiveApp()
    app.mainloop()


if __name__ == "__main__":
    main()