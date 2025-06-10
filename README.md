# AI PCA Tool

A Flask-based web application for data preprocessing and visualization, designed to help users analyze Excel data through column selection, renaming, chart generation, and automated Google Slides presentation creation.

## Features

- **Excel File Upload**: Support for `.xls` and `.xlsx` files with drag-and-drop interface
- **Column Management**: Select specific columns and rename them for better analysis
- **Data Visualization**: Generate interactive bar charts and pie charts from your data
- **Chart Toggle**: Switch between bar and pie chart views for each column
- **Google Slides Integration**: Automatically generate presentation slides with your charts
- **Download Options**: Download individual charts or all charts at once
- **Modern UI**: Responsive design with smooth animations and intuitive navigation
- **Session Management**: Maintains user state throughout the workflow
- **Error Handling**: Comprehensive error handling with custom 404 page

## Project Structure

```
AI-pca-pase01/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
├── LICENSE                 # MIT License
├── .gitignore              # Git ignore rules
├── .gitattributes          # Git attributes
├── templates/              # HTML templates
│   ├── upload.html         # File upload page
│   ├── columns.html        # Column selection page
│   ├── rename_columns.html # Column renaming page
│   ├── results.html        # Data processing results
│   ├── graphs.html         # Chart visualization page
│   └── error_404.html      # Custom error page
├── static/                 # Static assets
│   ├── css/                # Stylesheets
│   │   ├── upload.css      # Upload page styles
│   │   ├── columns.css     # Column selection styles
│   │   ├── graphs.css      # Charts page styles
│   │   ├── results.css     # Results page styles
│   │   └── error_404.css   # Error page styles
│   └── images/
│       └── 404_error.svg   # Error page illustration
├── analysis/               # Generated content
│   ├── charts/             # Chart images (auto-generated)
│   └── results/            # Analysis results (auto-generated)
├── uploads/                # Uploaded files directory (auto-created)
└── credentials.json        # Google API credentials (not included)
```

## Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager
- Google Cloud Console account (for Slides integration)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yasithS/AI-pca-pase01.git
   cd AI-pca-pase01
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Google API credentials** (for Slides integration)
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Google Slides API and Google Drive API
   - Create credentials (OAuth 2.0 Client ID)
   - Download the credentials file and save as `credentials.json` in the project root

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   Open your web browser and navigate to `http://localhost:5000`

## Dependencies

- **Flask 2.3.3** - Web framework
- **pandas 2.0.3** - Data manipulation and analysis
- **numpy 1.24.3** - Numerical computing
- **openpyxl 3.1.2** - Excel file reading/writing
- **matplotlib 3.7.2** - Data visualization
- **seaborn 0.12.2** - Statistical data visualization
- **google-api-python-client** - Google APIs integration
- **google-auth-httplib2** - Google authentication
- **google-auth-oauthlib** - OAuth 2.0 for Google APIs
- **python-pptx 0.6.21** - PowerPoint file handling
- **scikit-learn 1.3.0** - Machine learning library
- **Werkzeug 2.3.7** - WSGI utilities

## Usage Guide

### Step 1: Upload Excel File
1. Navigate to the upload page
2. Drag and drop or click to select an `.xls` or `.xlsx` file
3. Click "Upload and Continue" to proceed

### Step 2: Select Columns
1. Review all available columns from your dataset
2. Check the boxes for columns you want to analyze
3. Use "Select All" to quickly select all columns
4. Click "Next: Rename Columns"

### Step 3: Rename Columns (Optional)
1. Modify column names as needed for better readability
2. Leave fields unchanged to keep original names
3. Click "Process & Continue"

### Step 4: View Results
1. Review the processing summary
2. Check data shape and column mappings
3. Preview the first 5 rows of processed data
4. Continue to chart generation

### Step 5: Generate and Interact with Charts
1. View automatically generated charts for each column
2. Toggle between bar charts and pie charts using the toggle button
3. Download individual charts or all charts at once
4. Charts are automatically saved to the `analysis/charts/` directory

### Step 6: Create Google Slides Presentation
1. Click "Generate the slides" to authorize Google integration
2. Complete OAuth authorization in your browser
3. The application automatically creates a presentation with your selected charts
4. Access your presentation through the provided Google Slides link

## Chart Types

- **Bar Charts**: Default visualization showing value counts for each column
- **Pie Charts**: Alternative visualization showing data distribution as percentages
- **Interactive Toggle**: Switch between chart types with a single click
- **High Quality**: All charts generated at high resolution for presentations

## Configuration

### Environment Variables
For production deployment, set the following environment variables:
```bash
export SECRET_KEY='your-secure-secret-key-here'
export FLASK_ENV='production'
```

### Google Slides Template
The application uses a predefined Google Slides template. Update the `PRESENTATION_ID` in `app.py`:
```python
PRESENTATION_ID = "your-google-slides-template-id"
```

### Upload Directory
Default upload directory is `uploads/`. Modify in `app.py` if needed:
```python
UPLOAD_FOLDER = 'your-custom-upload-path'
```

## Features Deep Dive

### Modern UI/UX
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Drag & Drop**: Intuitive file upload with visual feedback
- **Progress Indicators**: Real-time feedback during file processing
- **Smooth Animations**: Professional transitions and hover effects

### Data Processing
- **Robust Excel Parsing**: Handles various Excel formats and structures
- **Column Validation**: Ensures data integrity throughout the process
- **Session Management**: Secure handling of user data and preferences

### Google Integration
- **OAuth 2.0 Security**: Secure authentication with Google services
- **Automatic Uploads**: Charts uploaded to Google Drive with proper permissions
- **Template System**: Uses placeholder-based slide generation

## Security Features

- **Session Security**: Encrypted session management
- **File Validation**: Strict file type checking for uploads
- **Google OAuth**: Secure authentication for API access
- **Error Handling**: Graceful handling of errors without exposing sensitive data

## Future Enhancements

- **PCA Analysis**: Principal Component Analysis implementation (planned)
- **Advanced Visualizations**: More chart types and interactive plots
- **Data Export**: Export processed data in multiple formats
- **Batch Processing**: Handle multiple files simultaneously
- **User Authentication**: Multi-user support with individual accounts
- **Cloud Storage**: Integration with multiple cloud storage providers

## Troubleshooting

### Common Issues

**Upload Errors**
- Ensure file is in `.xls` or `.xlsx` format
- Check file size (large files may timeout)
- Verify file is not corrupted or password-protected

**Google Slides Integration**
- Ensure `credentials.json` is properly configured
- Check that Google Slides API and Drive API are enabled
- Verify OAuth consent screen is configured

**Chart Generation**
- Ensure matplotlib backend is properly configured
- Check that `analysis/charts/` directory has write permissions
- Verify data contains valid values for visualization

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for full details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

For questions, issues, or suggestions:
- Create an issue on GitHub
- Check the troubleshooting section above
- Review the configuration options

---

**Note**: This tool is currently focused on data visualization and Google Slides integration. The PCA analysis feature mentioned in the project name is planned for future releases.

## Quick Start

```bash
# Clone and setup
git clone https://github.com/yasithS/AI-pca-pase01.git
cd AI-pca-pase01
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Add Google credentials (credentials.json)
# Run the application
python app.py

# Open http://localhost:5000 in your browser
```

Ready to transform your Excel data into beautiful visualizations!


### in case of InsecureTransportError use this 
```
export OAUTHLIB_INSECURE_TRANSPORT=1
```
