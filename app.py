from flask import Flask, request, render_template, redirect, url_for, flash, session
import pandas as pd
import numpy as np
import os
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)
app.secret_key = 'stringsANDbytes234234'  

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files.get('excel_file')
        if not file or file.filename == '':
            return redirect(request.url)
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        try:
            df = pd.read_excel(file_path, engine='openpyxl')
        except Exception as e:
            print(f"Error reading the Excel file: {e}")
            return redirect(request.url)
        
        columns = list(df.columns)
        # Store file info in session
        session['file_name'] = file.filename
        session['file_path'] = file_path
        return render_template('columns.html', columns=columns, file_name=file.filename)
    
    return render_template('upload.html')

@app.route('/select_columns', methods=['POST'])
def select_columns():
    selected_columns = request.form.getlist('columns')
    if not selected_columns:
        flash('Please select at least one column')
        return redirect(url_for('upload_file'))
    
    # Store selected columns in session
    session['selected_columns'] = selected_columns
    return render_template('rename_columns.html', columns=selected_columns)

@app.route('/rename_columns', methods=['POST'])
def rename_columns():
    selected_columns = session.get('selected_columns', [])
    file_path = session.get('file_path', '')
    
    if not selected_columns or not file_path:
        flash('Session expired. Please start over.')
        return redirect(url_for('upload_file'))
    
    # Get the new column names from form
    column_mapping = {}
    for old_name in selected_columns:
        new_name = request.form.get(f'rename_{old_name}', old_name)
        if new_name.strip():  # Only rename if new name is not empty
            column_mapping[old_name] = new_name.strip()
    
    try:
        # Read the Excel file and process selected columns
        df = pd.read_excel(file_path, engine='openpyxl')
        
        # Filter to only selected columns
        df_filtered = df[selected_columns].copy()
        
        # Rename columns
        if column_mapping:
            df_filtered.rename(columns=column_mapping, inplace=True)
        
        # Here you can add your PCA processing logic
        # For now, just display the processed data info
        processed_info = {
            'original_columns': selected_columns,
            'renamed_columns': list(df_filtered.columns),
            'data_shape': df_filtered.shape,
            'column_mapping': column_mapping
        }

        temp_csv_path = os.path.join(app.config['UPLOAD_FOLDER'], 'processed.csv')
        df_filtered.to_csv(temp_csv_path, index=False)
        session['processed_csv_path'] = temp_csv_path
        
        return render_template('results.html', 
                             processed_info=processed_info,
                             data_preview=df_filtered.head().to_html(classes='table table-striped'))
    
    except Exception as e:
        flash(f'Error processing file: {str(e)}')
        return redirect(url_for('upload_file'))
    
    
@app.route('/create_graphs', methods=['GET'])
def graphs():
    csv_path = session.get('processed_csv_path')
    if not csv_path or not os.path.exists(csv_path):
        flash('Processed data not found. Please restart.')
        return redirect(url_for('upload_file'))

    df_filtered = pd.read_csv(csv_path)
    selected_columns = df_filtered.columns.tolist()

    charts = []

    for single in selected_columns:
        data = df_filtered[single].value_counts()
        x = data.index.tolist()
        y = data.values.tolist()

        fig, ax = plt.subplots(figsize=(12, 6))

        if single.lower() == 'country':
            ax.pie(y, labels=x, autopct='%1.1f%%')
            ax.set_title(f'Performance by {single}')
        else:
            ax.bar(x, y, edgecolor='black', width=0.7, alpha=0.7, color=plt.cm.viridis(np.linspace(0, 1, len(x)))) 
            ax.set_xlabel(single)
            ax.set_ylabel('Count')
            ax.set_title(f'Performance by {single}')
            plt.xticks(rotation=90)

        plt.tight_layout()

        # Convert to base64
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        base64_img = base64.b64encode(img.getvalue()).decode()

        charts.append({
            'column': single,
            'image': base64_img
        })

        plt.close(fig)

    return render_template('graphs.html', charts=charts)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error_404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)