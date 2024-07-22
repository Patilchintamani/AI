from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file and allowed_file(file.filename):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        return redirect(url_for('display_data', filename=file.filename))
    return redirect(request.url)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv', 'xlsx'}

@app.route('/display/<filename>')
def display_data(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    df = read_file(file_path)
    data_info = df.describe().to_html()
    return render_template('data_info.html', data_info=data_info, filename=filename)

@app.route('/plot/<filename>')
def plot(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    df = read_file(file_path)
    
    # Plotting histograms
    plt.figure()
    df.hist(figsize=(10, 8))
    img_hist = io.BytesIO()
    plt.savefig(img_hist, format='png')
    img_hist.seek(0)
    plot_hist_url = base64.b64encode(img_hist.getvalue()).decode()
    
    # Plotting pie chart (example with first column)
    plt.figure()
    df.iloc[:, 0].value_counts().plot.pie(autopct='%1.1f%%', figsize=(8, 8))
    img_pie = io.BytesIO()
    plt.savefig(img_pie, format='png')
    img_pie.seek(0)
    plot_pie_url = base64.b64encode(img_pie.getvalue()).decode()
    
    # Plotting line chart (example with first two columns)
    plt.figure()
    df.plot(kind='line', x=df.columns[0], y=df.columns[1:], figsize=(10, 8))
    img_line = io.BytesIO()
    plt.savefig(img_line, format='png')
    img_line.seek(0)
    plot_line_url = base64.b64encode(img_line.getvalue()).decode()
    
    return render_template('plot1.html', plot_hist_url=plot_hist_url, plot_pie_url=plot_pie_url, plot_line_url=plot_line_url)

def read_file(file_path):
    if file_path.endswith('.csv'):
        return pd.read_csv(file_path)
    elif file_path.endswith('.xlsx'):
        return pd.read_excel(file_path)
    else:
        raise ValueError("Unsupported file format")

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
