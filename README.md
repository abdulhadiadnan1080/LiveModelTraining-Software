# Kaggle House Price Prediction Pipeline

An end-to-end Machine Learning pipeline for house price prediction, featuring a custom GUI for seamless data processing, model training, and evaluation.

---

## Features
- **Integrated Data Ingestion**: Automated downloading of datasets directly from Kaggle using API credentials.
- **Automated Data Cleaning**: Intelligent handling of missing values, outlier detection, and feature engineering.
- **Model Training**: Support for multiple algorithms:
    - **Random Forest Regressor** (Robust non-linear model)
    - **Linear Regression** (Interpretable baseline model)
- **Real-time Evaluation**: In-app metrics display (MSE, R², etc.) and visualization of model performance.
- **Interactive GUI**: A user-friendly Tkinter-based dashboard to manage every stage of the pipeline with live terminal output.
- **Dynamic Visualizations**: Automatically generates heatmaps, distribution plots, and prediction error graphs.

---

## Tech Stack
- **Languages**: Python 3.10+
- **Machine Learning**: Scikit-Learn
- **Data Manipulation**: Pandas, NumPy
- **Visualization**: Matplotlib, Seaborn
- **GUI Framework**: Tkinter
- **Image Handling**: Pillow (PIL)

---

## Getting Started

### 1. Prerequisites
Ensure you have Python installed. You will also need a **Kaggle API Token** (`kaggle.json`) to download the dataset automatically.

### 2. Installation
1. Clone the repository or navigate to the project folder.
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install the required dependencies:
   ```bash
   pip install -r "Main/requirements.txt"
   ```

### 3. How to Run
Launch the interactive dashboard:
```bash
python3 "Main/main.py"
```

---

## Pipeline Workflow

The GUI is designed to guide you through the standard ML workflow sequentially:

1. **Download Dataset**: Connects to Kaggle and fetches the specified house pricing data.
2. **Assess & Clean**: Runs `Quality_Assessment.py` and `Cleaning_Data.py` to prepare the features.
3. **Split Data**: Divides the data into Training and Testing sets.
4. **Train Model**: Choose between Random Forest or Linear Regression training.
5. **Evaluate**: Compares predictions against true values and displays accuracy metrics.
6. **Predict**: Uses the trained model to perform inference on new samples.

---

## Project Structure
- `Main/`: Core source code and automation scripts.
- `data/`: Local storage for raw and processed datasets.
- `The Models/`: Persistent storage for trained `.pkl` or `.joblib` model files.
- `OutPuts_of_DataSets/`: Automatically generated visualizations and performance charts.
- `requirements.txt`: List of Python packages required.

---

## 📊 Visualizations
The system automatically generates and displays:
- **Missing Value Heatmaps**: To identify data gaps.
- **Target Distribution Plots**: To understand the spread of house prices.
- **Model Evaluation Graphs**: Predicted vs. Actual value comparisons.

---

*Built with for Data Science enthusiasts.*
