from flask import Flask, request, render_template, redirect, url_for, flash, session, send_file, jsonify
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
import logging
from flask import Flask, request, render_template, redirect, url_for, session, flash
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'stringsANDbytes234234'

# folders
UPLOAD_FOLDER = 'uploads'
CHART_FOLDER = os.path.join('analysis', 'charts')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CHART_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# OAuth scopes (added readonly scopes)
SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/drive.metadata.readonly',
    'https://www.googleapis.com/auth/presentations',
    'https://www.googleapis.com/auth/drive.file'
]

# Presentation ID
PRESENTATION_ID = "1nP1VA5rNflyb3IgxhI7hv3-2K6WHufM4qLOaZg2qUDI"

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


@app.route('/authorize')
def authorize():
    flow = Flow.from_client_secrets_file(
        'credentials.json',
        scopes=SCOPES,
        redirect_uri=url_for('oauth2callback', _external=True)
    )
    auth_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    session['state'] = state
    return redirect(auth_url)


@app.route('/oauth2callback')
def oauth2callback():
    state = session.get('state')
    flow = Flow.from_client_secrets_file(
        'credentials.json',
        scopes=SCOPES,
        state=state,
        redirect_uri=url_for('oauth2callback', _external=True)
    )
    flow.fetch_token(authorization_response=request.url)
    creds = flow.credentials

    session['credentials'] = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes
    }
    logging.info("Google authorization successful!")
    return redirect(url_for('upload_file'))

@app.route('/need_login')
def need_login():
    return render_template('need_login.html')

@app.route('/reset')
def reset():
    # remove everything related to the last upload
    for key in ['file_path', 'file_name', 'processed_csv_path', 
                'selected_columns', 'selected_graph_types']:
        session.pop(key, None)
    return redirect(url_for('upload_file'))


@app.route('/picker_token')
def picker_token():
    if 'credentials' not in session:
        return redirect(url_for('need_login'))
        # return jsonify({}), 401
    creds = Credentials(**session['credentials'])
    return jsonify(token=creds.token)

@app.route('/drive_browser', methods=['GET'])
def drive_browser():
    if 'credentials' not in session:
        return redirect(url_for('need_login'))

    creds = Credentials(**session['credentials'])
    drive = build('drive', 'v3', credentials=creds)

    # allow folder_id via ?folder_id=… so you can drill down
    folder_id = request.args.get(
        'folder_id',
        '1z72ZZSiSTGyXH_BmbaO6IB2jkvkpSkEJ'
    )

    # 1) sub-folders
    folder_q = (
        f"'{folder_id}' in parents and "
        "mimeType='application/vnd.google-apps.folder' and trashed=false"
    )
    folders = drive.files().list(
        q=folder_q,
        fields='files(id,name)',
        includeItemsFromAllDrives=True,
        supportsAllDrives=True
    ).execute().get('files', [])

    # 2) .xlsx files
    file_q = (
        f"'{folder_id}' in parents and "
        "mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' and trashed=false"
    )
    files = drive.files().list(
        q=file_q,
        fields='files(id,name)',
        includeItemsFromAllDrives=True,
        supportsAllDrives=True
    ).execute().get('files', [])

    return render_template(
        'drive_browser.html',
        folders=folders,
        files=files,
        folder_id=folder_id
    )


@app.route('/select_drive_file', methods=['POST'])
def select_drive_file():
    if 'credentials' not in session:
        return redirect(url_for('need_login'))

    # 1) grab the file_id, not the folder_id
    file_id = request.form.get('file_id')
    if not file_id:
        flash('No file selected.')
        return redirect(url_for('drive_browser'))

    creds = Credentials(**session['credentials'])
    drive_svc = build('drive', 'v3', credentials=creds)

    # 2) download the file bytes (include supportsAllDrives if it's a shared folder)
    request_media = drive_svc.files().get_media(
        fileId=file_id,
        supportsAllDrives=True
    )
    fh = BytesIO()
    downloader = MediaIoBaseDownload(fh, request_media)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    fh.seek(0)

    # 3) fetch the real filename
    meta = drive_svc.files().get(
        fileId=file_id,
        fields='name',
        supportsAllDrives=True
    ).execute()
    filename = meta.get('name', f"{file_id}.xlsx")

    # 4) save locally and push into your existing flow
    local_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    with open(local_path, 'wb') as f:
        f.write(fh.read())

    session['file_path'] = local_path
    session['file_name'] = filename

    return redirect(url_for('upload_file'))



@app.route('/', methods=['GET', 'POST'])
def upload_file():
    # 1) Handle new upload
    if request.method == 'POST':
        file = request.files.get('excel_file')
        if not file or not file.filename:
            return redirect(request.url)

        path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(path)

        try:
            df = pd.read_excel(path, engine='openpyxl')
        except Exception as e:
            flash(f"Error reading Excel: {e}")
            return redirect(request.url)

        session['file_path'] = path
        session['file_name'] = file.filename
        # redirect to GET so browser’s refresh won’t re-POST
        return redirect(url_for('upload_file'))

    # 2) If we already have a file in session, show the column picker
    elif session.get('file_path'):
        df = pd.read_excel(session['file_path'], engine='openpyxl')
        return render_template(
            'columns.html',
            columns=list(df.columns),
            file_name=session.get('file_name')
        )
    

    # 3) Otherwise show the upload form
    return render_template('upload.html')



@app.route('/select_columns', methods=['POST'])
def select_columns():
    cols = request.form.getlist('columns')
    if not cols:
        flash('Select at least one column.')
        return redirect(url_for('upload_file'))
    session['selected_columns'] = cols
    return render_template('rename_columns.html', columns=cols)


@app.route('/rename_columns', methods=['POST'])
def rename_columns():
    cols = session.get('selected_columns')
    path = session.get('file_path')
    if not cols or not path:
        flash('Session expired. Start over.')
        return redirect(url_for('upload_file'))

    mapping = {}
    for old in cols:
        new = request.form.get(f'rename_{old}', old).strip()
        if new:
            mapping[old] = new

    try:
        df = pd.read_excel(path, engine='openpyxl')
        df_filtered = df[cols].copy()
        if mapping:
            df_filtered.rename(columns=mapping, inplace=True)

        info = {
            'original_columns': cols,
            'renamed_columns': list(df_filtered.columns),
            'data_shape': df_filtered.shape,
            'column_mapping': mapping
        }

        temp_csv = os.path.join(app.config['UPLOAD_FOLDER'], 'processed.csv')
        df_filtered.to_csv(temp_csv, index=False)
        session['processed_csv_path'] = temp_csv

        return render_template(
            'results.html',
            processed_info=info,
            data_preview=df_filtered.head().to_html(classes='table table-striped')
        )
    except Exception as e:
        flash(f"Error processing file: {e}")
        return redirect(url_for('upload_file'))


@app.route('/create_graphs', methods=['GET'])
def create_graphs():
    csv_path = session.get('processed_csv_path')
    if not csv_path or not os.path.exists(csv_path):
        flash('Processed data not found.')
        return redirect(url_for('upload_file'))

    df = pd.read_csv(csv_path)
    cols = df.columns.tolist()

    # clear old charts
    for f in os.listdir(CHART_FOLDER):
        if f.endswith('.png'):
            os.remove(os.path.join(CHART_FOLDER, f))

    charts = []
    for col in cols:
        counts = df[col].value_counts()
        labels = counts.index.tolist()
        values = counts.values.tolist()

        # bar
        fig, ax = plt.subplots(figsize=(5,5))
        ax.bar(labels, values, edgecolor='black', width=0.7, alpha=0.7)
        ax.set_xlabel(col)
        ax.set_ylabel('Count')
        plt.xticks(rotation=90)
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        b64 = base64.b64encode(buf.getvalue()).decode()
        plt.close(fig)
        with open(os.path.join(CHART_FOLDER, f"{col}_bar.png"), 'wb') as imgf:
            imgf.write(buf.getvalue())

        # pie
        fig2, ax2 = plt.subplots(figsize=(5,5))
        ax2.pie(values, labels=labels, autopct='%1.1f%%')
        plt.tight_layout()
        buf2 = io.BytesIO()
        plt.savefig(buf2, format='png')
        buf2.seek(0)
        b64_pie = base64.b64encode(buf2.getvalue()).decode()
        plt.close(fig2)
        with open(os.path.join(CHART_FOLDER, f"{col}_pie.png"), 'wb') as imgf:
            imgf.write(buf2.getvalue())

        charts.append({'column': col, 'bar': b64, 'pie': b64_pie})

    return render_template('graphs.html', charts=charts)


@app.route('/update_selected_graph_type', methods=['POST'])
def update_selected_graph_type():
    data = request.get_json()
    col = data.get('column')
    gt = data.get('graphType')
    if not col or not gt:
        return jsonify(error='Invalid data'), 400
    session.setdefault('selected_graph_types', {})[col] = gt
    session.modified = True
    return jsonify(success=True)


@app.route('/slides', methods=['GET'])
def slides():
    if 'credentials' not in session:
        return redirect(url_for('need_login'))

    creds = Credentials(**session['credentials'])
    drive_svc = build('drive', 'v3', credentials=creds)
    slides_svc = build('slides', 'v1', credentials=creds)

    # ensure charts exist
    if not os.path.isdir(CHART_FOLDER):
        flash('Generate graphs first.')
        return redirect(url_for('create_graphs'))

    sel = session.get('selected_graph_types', {})
    if not sel:
        flash('Select graphs first.')
        return redirect(url_for('create_graphs'))

    uploaded = []
    for col, gt in sel.items():
        fname = f"{col}_{gt}.png"
        path = os.path.join(CHART_FOLDER, fname)
        if not os.path.exists(path):
            logging.error(f"{fname} missing")
            flash(f"{fname} not found")
            continue

        res = drive_svc.files().create(
            body={'name': fname, 'mimeType': 'image/png'},
            media_body=MediaFileUpload(path, mimetype='image/png'),
            fields='id'
        ).execute()
        fid = res['id']
        drive_svc.permissions().create(
            fileId=fid,
            body={'role': 'reader', 'type': 'anyone'}
        ).execute()
        url = f"https://drive.google.com/uc?export=view&id={fid}"
        uploaded.append({'column': col, 'url': url})

    pres = slides_svc.presentations().get(presentationId=PRESENTATION_ID).execute()
    requests = []
    for idx, up in enumerate(uploaded, start=1):
        placeholder = f"{{{{DSCHART{idx}}}}}"
        # find slide with placeholder
        slide_id = None
        for s in pres['slides']:
            for el in s.get('pageElements', []):
                txt = el.get('shape', {}).get('text', {}).get('textElements', [])
                if any(placeholder in (t.get('textRun', {}).get('content','')) for t in txt):
                    slide_id = s['objectId']
                    break
            if slide_id:
                break

        if slide_id:
            # clear placeholder
            requests.append({
                'replaceAllText': {
                    'containsText': {'text': placeholder, 'matchCase': True},
                    'replaceText': ''
                }
            })
            # insert image
            requests.append({
                'createImage': {
                    'url': up['url'],
                    'elementProperties': {
                        'pageObjectId': slide_id,
                        'size': {'height': {'magnitude':3000000,'unit':'EMU'},
                                 'width':  {'magnitude':4000000,'unit':'EMU'}},
                        'transform': {'scaleX':1,'scaleY':1,'translateX':1000000,'translateY':1000000,'unit':'EMU'}
                    }
                }
            })

    slides_svc.presentations().batchUpdate(
        presentationId=PRESENTATION_ID,
        body={'requests': requests}
    ).execute()

    flash('Slides updated!')
    return redirect(f"https://docs.google.com/presentation/d/{PRESENTATION_ID}")


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error_404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
