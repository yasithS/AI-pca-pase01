from flask import Flask, request, render_template, redirect, url_for, flash
import pandas as pd
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files.get('excel_file')
        if not file and file.filename == '':
            print("NO FILE UPLOADED")
            return redirect(request.url)
        
        file_path = os.path.join(app.config['UPLOAD_FOLEDR'], file.filename)
        file.save(file_path)

        try:
            df = pd.read_excel(file_path, engine='openpyxl')
        except Exception as e:
            print(f"Error reading the Excel file: {e}")
            return redirect(request.url)
        
        columns = list(df.columns)
        return render_template('columns.html', columns=columns, file_name=file.filename)
    
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)