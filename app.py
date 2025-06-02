from flask import Flask, request, render_template, redirect, url_for, flash, session, send_file
import pandas as pd
import numpy as np
import os
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import io
import base64
from pptx import Presentation
from pptx.util import Inches, Pt
import pickle
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

app = Flask(__name__)
app.secret_key = 'stringsANDbytes234234'  

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

SCOPES = ['https://www.googleapis.com/auth/presentations', 'https://www.googleapis.com/auth/drive.file']

@app.route('/authorize')
def authorize():
    flow = Flow.from_client_secrets_file(
        'credentials.json',
        scopes=SCOPES,
        redirect_uri=url_for('oauth2callback', _external=True)
    )
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    session['state'] = state
    return redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    state = session['state']
    flow = Flow.from_client_secrets_file(
        'credentials.json',
        scopes=SCOPES,
        state=state,
        redirect_uri=url_for('oauth2callback', _external=True)
    )
    flow.fetch_token(authorization_response=request.url)

    credentials = flow.credentials
    session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    flash('Google authorization successful!')
    return redirect(url_for('upload_file'))




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
        
        # just display the processed data info
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
    chart_dir = os.path.join('analysis', 'charts')
    os.makedirs(chart_dir, exist_ok=True)

    # Remove old chart images before saving new ones
    for filename in os.listdir(chart_dir):
        file_path = os.path.join(chart_dir, filename)
        if os.path.isfile(file_path) and filename.endswith('.png'):
            os.remove(file_path)

    for single in selected_columns:
        data = df_filtered[single].value_counts()
        x = data.index.tolist()
        y = data.values.tolist()

        # Bar chart
        fig_bar, ax_bar = plt.subplots(figsize=(8, 8))
        ax_bar.bar(x, y, edgecolor='black', width=0.7, alpha=0.7, color=plt.cm.viridis(np.linspace(0, 1, len(x))))
        ax_bar.set_xlabel(single)
        ax_bar.set_ylabel('Count')
        ax_bar.set_title(f"Performance by {single}")
        plt.xticks(rotation=90)
        plt.tight_layout()
        img_bar = io.BytesIO()
        plt.savefig(img_bar, format='png')
        img_bar.seek(0)
        base64_bar = base64.b64encode(img_bar.getvalue()).decode()
        plt.close(fig_bar)

        # Save bar chart as file
        bar_path = os.path.join(chart_dir, f"{single}_bar.png")
        with open(bar_path, "wb") as f:
            f.write(img_bar.getvalue())

        # Pie chart
        fig_pie, ax_pie = plt.subplots(figsize=(8, 8))
        ax_pie.pie(y, labels=x, autopct='%1.1f%%')
        ax_pie.set_title(f'Performance by {single}')
        plt.tight_layout()
        img_pie = io.BytesIO()
        plt.savefig(img_pie, format='png')
        img_pie.seek(0)
        base64_pie = base64.b64encode(img_pie.getvalue()).decode()
        plt.close(fig_pie)

        # Save pie chart as file
        pie_path = os.path.join(chart_dir, f"{single}_pie.png")
        with open(pie_path, "wb") as f:
            f.write(img_pie.getvalue())

        charts.append({
            'column': single,
            'bar': base64_bar,
            'pie': base64_pie
        })

    return render_template('graphs.html', charts=charts)

@app.route('/generate_pptx', methods = ['GET'])
def generate_pptx():
    chart_dir = os.path.join('analysis', 'charts')
    if not os.path.exists(chart_dir):
        flash('Charts not found. Please generate graphs first.')
        return redirect(url_for('graphs'))

    charts = []
    for filename in os.listdir(chart_dir):
        if filename.endswith('.png'):
            column = os.path.splitext(filename)[0]
            img_path = os.path.join(chart_dir, filename)
            charts.append({'column': column, 'image_path': img_path})

    ppt = Presentation()
    for chart in charts:
        column = chart['column']
        img_path = chart['image_path']
        slide = ppt.slides.add_slide(ppt.slide_layouts[6])
        title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.5), Inches(8), Inches(1))
        title_frame = title_box.text_frame
        title_frame.text = f"Performance by {column}"
        title_frame.paragraphs[0].runs[0].font.size = Pt(32)
        title_frame.paragraphs[0].runs[0].bold = True
        left = Inches(1)
        top = Inches(1.5)
        height = Inches(4.5)
        slide.shapes.add_picture(img_path, left, top, height=height)

    pptx_path = os.path.abspath(os.path.join('analysis/results', 'test.pptx'))
    os.makedirs(os.path.dirname(pptx_path), exist_ok=True)
    ppt.save(pptx_path)

    return send_file(pptx_path, as_attachment=True)
    

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error_404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)