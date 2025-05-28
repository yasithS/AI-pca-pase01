# AI PCA Tool

A Flask-based web application for data preprocessing and visualization, designed to help users analyze Excel data through column selection, renaming, and chart generation.

## Features

- **Excel File Upload**: Upload `.xls` and `.xlsx` files
- **Column Selection**: Choose specific columns from your dataset
- **Column Renaming**: Rename selected columns for better analysis
- **Data Visualization**: Generate charts and graphs from your processed data
- **Session Management**: Maintains user state throughout the workflow
- **Error Handling**: Custom 404 page and comprehensive error handling

## Project Structure

```
AI-pca-pase01/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
├── LICENSE                 # GNU GPL v3 License
├── .gitignore              # Git ignore rules
├── .gitattributes          # Git attributes
├── templates/              # HTML templates
│   ├── upload.html         # File upload page
│   ├── columns.html        # Column selection page
│   ├── rename_columns.html # Column renaming page
│   ├── results.html        # Data processing results
│   ├── graphs.html         # Chart visualization page
│   └── 404.html            # Custom error page
├── static/                 # Static assets
│   └── images/
│       └── 404_error.svg   # Error page illustration
├── Research/               # Foledr with i-python notebooks
└── uploads/                # Uploaded files directory (auto-created)
```

## Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager

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

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   Open your web browser and navigate to `http://localhost:5000/upload`

## Dependencies

- **Flask 2.3.3** - Web framework
- **pandas 2.0.3** - Data manipulation and analysis
- **numpy 1.24.3** - Numerical computing
- **openpyxl 3.1.2** - Excel file reading/writing
- **Werkzeug 2.3.7** - WSGI utilities
- **scikit-learn 1.3.0** - Machine learning library
- **matplotlib 3.7.2** - Data visualization
- **seaborn 0.12.2** - Statistical data visualization
- **pptx 0.6.21** - PowerPoint file handling

## Usage

### Step 1: Upload Excel File
1. Navigate to the upload page
2. Select an `.xls` or `.xlsx` file
3. Click "Upload" to proceed

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
4. Continue to graph generation

### Step 5: Generate Charts
1. View automatically generated charts for each column
2. Charts include bar plots and pie charts (for country data)
3. All visualizations are displayed on a single page

## Chart Types

- **Bar Charts**: Default visualization for most data types
- **Pie Charts**: Automatically generated for columns named "country"
- **Value Distribution**: Shows count of unique values in each column

## File Management

- Uploaded files are stored in the `uploads/` directory
- Processed data is temporarily saved as CSV files
- Files are managed through Flask sessions
- Clean up uploaded files periodically to save disk space

## Error Handling

- **404 Errors**: Custom error page with navigation options
- **File Upload Errors**: Validation for file types and upload issues
- **Session Management**: Handles expired or invalid sessions
- **Data Processing Errors**: Comprehensive error messages for debugging

## Development Features

- **Debug Mode**: Enabled by default for development
- **Session Security**: Secret key for secure session management
- **Automatic Directory Creation**: Upload folder created automatically
- **Git Integration**: Configured with `.gitignore` and `.gitattributes`

## Configuration

### Environment Variables
The application uses a hardcoded secret key. For production, set:
```python
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')
```

### Upload Directory
Default upload directory is `uploads/`. Modify in `app.py`:
```python
UPLOAD_FOLDER = 'your-custom-upload-path'
```

## Future Enhancements

Based on the project name and structure, planned features may include:

- **PCA Analysis**: Principal Component Analysis implementation
- **Advanced Visualizations**: More chart types and interactive plots
- **Data Export**: Export processed data and charts
- **Batch Processing**: Handle multiple files simultaneously
- **User Authentication**: Multi-user support with accounts

## License

This project is licensed under the GNU General Public License v3.0. See the [LICENSE](LICENSE) file for full details.

## Changelog

### Current Version
- Excel file upload and processing
- Column selection and renaming
- Basic chart generation
- Session management
- Error handling and custom 404 page

---

**Note**: This tool is currently in development phase. The PCA analysis feature mentioned in the project name is planned for future releases.
