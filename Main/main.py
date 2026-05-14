import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from PIL import Image, ImageTk
import sys
import threading
import os

# Import our custom modules
from kaggle_loader import download_from_kaggle
from Quality_Assessment import run_assessment
from Cleaning_Data import clean_data
from Split_data import split_data
from Train_RandomForest import train_random_forest
from Train_LinearRegression import train_linear_regression
from Evaluate_Model import evaluate_model
from Make_Prediction import make_prediction

class TextRedirector(object):
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, str):
        self.widget.configure(state="normal")
        self.widget.insert("end", str, (self.tag,))
        self.widget.see("end")
        self.widget.configure(state="disabled")

    def flush(self):
        pass

class DataPipelineApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kaggle Data Pipeline")
        self.root.geometry("1300x800")

        # Main scrollable container
        self.main_canvas = tk.Canvas(self.root)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.main_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.main_canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(
                scrollregion=self.main_canvas.bbox("all")
            )
        )

        self.canvas_frame = self.main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        def configure_canvas(event):
            self.main_canvas.itemconfig(self.canvas_frame, width=event.width)
            
        self.main_canvas.bind('<Configure>', configure_canvas)
        self.main_canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Enable Mac two-finger / scroll wheel scrolling
        def _on_mousewheel(event):
            # macOS delta is usually +/- 1 or higher. We use a small multiplier if needed, 
            # but usually just passing the delta works best for trackpads.
            self.main_canvas.yview_scroll(int(-1 * event.delta), "units")
            
        self.main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        self.main_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.create_widgets()

        # Redirect stdout
        sys.stdout = TextRedirector(self.terminal)
        
    def create_widgets(self):
        # --- INPUT FRAME ---
        input_frame = ttk.LabelFrame(self.scrollable_frame, text="Configuration", padding="10")
        input_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(input_frame, text="Kaggle Username:").grid(row=0, column=0, sticky="w", pady=2)
        self.entry_username = ttk.Entry(input_frame, width=30)
        self.entry_username.grid(row=0, column=1, sticky="w", pady=2, padx=5)
        self.entry_username.insert(0, "bingfox123456789")

        ttk.Label(input_frame, text="Kaggle Token:").grid(row=0, column=2, sticky="w", pady=2, padx=(10,0))
        self.entry_token = ttk.Entry(input_frame, width=40, show="*")
        self.entry_token.grid(row=0, column=3, sticky="w", pady=2, padx=5)
        self.entry_token.insert(0, "KGAT_e6626d5b5022062b41e7f9e19e6e4706")

        ttk.Label(input_frame, text="Dataset URL:").grid(row=1, column=0, sticky="w", pady=2)
        self.entry_url = ttk.Entry(input_frame, width=80)
        self.entry_url.grid(row=1, column=1, columnspan=3, sticky="w", pady=2, padx=5)
        self.entry_url.insert(0, "https://www.kaggle.com/datasets/juhibhojani/house-price")

        # --- BUTTON FRAME ---
        btn_frame = ttk.Frame(self.scrollable_frame, padding="10")
        btn_frame.pack(fill="x", padx=10)

        self.btn_download = ttk.Button(btn_frame, text="1. Download Dataset", command=self.run_download)
        self.btn_download.pack(side="left", padx=5)

        self.btn_clean = ttk.Button(btn_frame, text="2. Assess & Clean Data", command=self.run_clean)
        self.btn_clean.pack(side="left", padx=5)

        self.btn_split = ttk.Button(btn_frame, text="3. Split Data", command=self.run_split)
        self.btn_split.pack(side="left", padx=5)

        # --- ML BUTTON FRAME ---
        btn_frame_ml = ttk.Frame(self.scrollable_frame, padding="10")
        btn_frame_ml.pack(fill="x", padx=10)

        self.btn_train_rf = ttk.Button(btn_frame_ml, text="4a. Train RF", command=self.run_train_rf)
        self.btn_train_rf.pack(side="left", padx=5)

        self.btn_train_lr = ttk.Button(btn_frame_ml, text="4b. Train LR", command=self.run_train_lr)
        self.btn_train_lr.pack(side="left", padx=5)

        self.btn_eval = ttk.Button(btn_frame_ml, text="5. Evaluate", command=self.run_eval)
        self.btn_eval.pack(side="left", padx=5)

        self.btn_predict = ttk.Button(btn_frame_ml, text="6. Predict", command=self.run_predict)
        self.btn_predict.pack(side="left", padx=5)

        # --- TERMINAL FRAME ---
        term_frame = ttk.LabelFrame(self.scrollable_frame, text="Live Output", padding="10")
        term_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.terminal = scrolledtext.ScrolledText(term_frame, wrap=tk.WORD, height=15, bg="black", fg="white", font=("Courier", 12))
        self.terminal.pack(fill="both", expand=True)
        self.terminal.configure(state="disabled")

        # --- SUMMARY DASHBOARD ---
        self.summary_frame = ttk.LabelFrame(self.scrollable_frame, text="Data Quality & Cleaning Summary", padding="10")
        self.summary_frame.pack(fill="x", padx=10, pady=5)
        
        self.summary_tree = ttk.Treeview(self.summary_frame, columns=("Section", "Metric", "Value"), show='headings', height=5)
        self.summary_tree.heading("Section", text="Section")
        self.summary_tree.heading("Metric", text="Metric")
        self.summary_tree.heading("Value", text="Value")
        self.summary_tree.column("Section", width=200)
        self.summary_tree.column("Metric", width=300)
        self.summary_tree.column("Value", width=150)
        self.summary_tree.pack(fill="x")

        # --- PLOT FRAME ---
        self.plot_frame = ttk.LabelFrame(self.scrollable_frame, text="Visualizations", padding="10")
        self.plot_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.lbl_plot1 = ttk.Label(self.plot_frame, text="Plot 1 will appear here")
        self.lbl_plot1.pack(side="left", expand=True)
        
        self.lbl_plot2 = ttk.Label(self.plot_frame, text="Plot 2 will appear here")
        self.lbl_plot2.pack(side="left", expand=True)
        
        self.lbl_plot3 = ttk.Label(self.plot_frame, text="Plot 3 will appear here")
        self.lbl_plot3.pack(side="left", expand=True)

        # --- EVALUATION DASHBOARD ---
        self.eval_frame = ttk.LabelFrame(self.scrollable_frame, text="Model Evaluation Results", padding="10")
        self.eval_frame.pack(fill="x", padx=10, pady=5)
        
        self.eval_tree = ttk.Treeview(self.eval_frame, columns=("Metric", "Value"), show='headings', height=3)
        self.eval_tree.heading("Metric", text="Metric")
        self.eval_tree.heading("Value", text="Value")
        self.eval_tree.column("Metric", width=300)
        self.eval_tree.column("Value", width=300)
        self.eval_tree.pack(fill="x")

    def run_thread(self, target_func, on_success=None):
        # Disable buttons while running
        self.btn_download.config(state="disabled")
        self.btn_clean.config(state="disabled")
        self.btn_split.config(state="disabled")
        self.btn_train_rf.config(state="disabled")
        self.btn_train_lr.config(state="disabled")
        self.btn_eval.config(state="disabled")
        self.btn_predict.config(state="disabled")
        
        def wrapper():
            result = None
            try:
                result = target_func()
            except Exception as e:
                print(f"Error in background task: {e}")
            finally:
                # Re-enable buttons
                self.root.after(0, lambda: self.btn_download.config(state="normal"))
                self.root.after(0, lambda: self.btn_clean.config(state="normal"))
                self.root.after(0, lambda: self.btn_split.config(state="normal"))
                self.root.after(0, lambda: self.btn_train_rf.config(state="normal"))
                self.root.after(0, lambda: self.btn_train_lr.config(state="normal"))
                self.root.after(0, lambda: self.btn_eval.config(state="normal"))
                self.root.after(0, lambda: self.btn_predict.config(state="normal"))
                
                # Update UI with results
                if on_success and result is not None:
                    self.root.after(0, lambda: on_success(result))
                
                # Always try to load plots after assessment/cleaning
                self.root.after(500, self.load_plots)
        
        thread = threading.Thread(target=wrapper)
        thread.daemon = True
        thread.start()

    def update_dashboard(self, stats_list):
        # Clear old entries
        for item in self.summary_tree.get_children():
            self.summary_tree.delete(item)
            
        for section, stats in stats_list:
            if stats:
                for metric, value in stats.items():
                    # Format float nicely
                    val_str = f"{value:,.2f}" if isinstance(value, float) else str(value)
                    self.summary_tree.insert("", "end", values=(section, metric, val_str))

    def run_download(self):
        username = self.entry_username.get().strip()
        url = self.entry_url.get().strip()
        token = self.entry_token.get().strip()
        
        if not url or not token:
            messagebox.showwarning("Input Error", "Please provide both URL and Token.")
            return
            
        print(f"\n[{'-'*20} STARTING DOWNLOAD {'-'*20}]")
        self.run_thread(lambda: download_from_kaggle(url, username, token))

    def run_clean(self):
        def assess_and_clean():
            all_stats = []
            print(f"\n[{'-'*20} STARTING ASSESSMENT {'-'*20}]")
            a_stats = run_assessment()
            all_stats.append(("Assessment", a_stats))
            
            print(f"\n[{'-'*20} STARTING CLEANING {'-'*20}]")
            c_stats = clean_data()
            all_stats.append(("Cleaning", c_stats))
            
            print(f"[{'-'*20} PIPELINE COMPLETE {'-'*20}]")
            return all_stats
            
        self.run_thread(assess_and_clean, on_success=self.update_dashboard)

    def run_split(self):
        print(f"\n[{'-'*20} STARTING DATA SPLIT {'-'*20}]")
        self.run_thread(split_data)

    def run_train_rf(self):
        print(f"\n[{'-'*20} STARTING RF TRAINING {'-'*20}]")
        def train_and_update():
            stats = train_random_forest()
            if stats: return [("Training (RF)", stats)]
        self.run_thread(train_and_update, on_success=self.update_dashboard)

    def run_train_lr(self):
        print(f"\n[{'-'*20} STARTING LR TRAINING {'-'*20}]")
        def train_and_update():
            stats = train_linear_regression()
            if stats: return [("Training (LR)", stats)]
        self.run_thread(train_and_update, on_success=self.update_dashboard)

    def update_eval_dashboard(self, stats_list):
        for item in self.eval_tree.get_children():
            self.eval_tree.delete(item)
            
        for section, stats in stats_list:
            if stats:
                for metric, value in stats.items():
                    val_str = f"{value:,.4f}" if isinstance(value, float) else str(value)
                    self.eval_tree.insert("", "end", values=(metric, val_str))

    def run_eval(self):
        print(f"\n[{'-'*20} STARTING EVALUATION {'-'*20}]")
        def eval_and_update():
            stats = evaluate_model()
            if stats: return [("Evaluation", stats)]
        self.run_thread(eval_and_update, on_success=self.update_eval_dashboard)

    def run_predict(self):
        print(f"\n[{'-'*20} STARTING PREDICTION {'-'*20}]")
        self.run_thread(make_prediction)

    def load_plots(self):
        try:
            plot1_path = "plots/missing_values_heatmap.png"
            plot2_path = "plots/target_distribution.png"

            if os.path.exists(plot1_path):
                img1 = Image.open(plot1_path)
                img1 = img1.resize((400, 250), Image.Resampling.LANCZOS)
                self.img1_tk = ImageTk.PhotoImage(img1)
                self.lbl_plot1.config(image=self.img1_tk, text="")
                
            if os.path.exists(plot2_path):
                img2 = Image.open(plot2_path)
                img2 = img2.resize((400, 250), Image.Resampling.LANCZOS)
                self.img2_tk = ImageTk.PhotoImage(img2)
                self.lbl_plot2.config(image=self.img2_tk, text="")
                
            plot3_path = "plots/model_evaluation.png"
            if os.path.exists(plot3_path):
                img3 = Image.open(plot3_path)
                img3 = img3.resize((400, 250), Image.Resampling.LANCZOS)
                self.img3_tk = ImageTk.PhotoImage(img3)
                self.lbl_plot3.config(image=self.img3_tk, text="")
        except Exception as e:
            print(f"Failed to load plots: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DataPipelineApp(root)
    root.mainloop()
