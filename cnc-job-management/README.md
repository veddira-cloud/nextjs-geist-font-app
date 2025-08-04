# 🏭 CNC Job Management System

A futuristic web-based CNC Job Management application built with Flask, featuring a modern dashboard with real-time monitoring, job tracking, and history management.

![CNC Job Management Dashboard](https://placehold.co/1200x600?text=Futuristic+CNC+dashboard+with+glowing+neon+effects+and+machine+status+cards)

## ✨ Features

### 🎯 Dashboard
- **Real-time Digital Clock** - Always shows current time
- **Machine Grid Layout** - Responsive grid showing all CNC machines (CNC1-CNC5)
- **Current & Next Job Display** - Clear visualization of job queue per machine
- **Progress Tracking** - Achievement percentage with color-coded progress bars
- **Job Navigation** - Prev/Next buttons for multiple queued jobs
- **Job Count Display** - Total jobs per machine in corner badges

### 📊 Job Management
- **Add New Jobs** - Modal form with all required fields
- **Edit Existing Jobs** - Pre-filled forms for easy updates
- **Finish Jobs** - Move completed jobs to history with validation
- **Achievement Calculation** - Automatic calculation based on actual vs target time
- **Job Types** - Support for "current" and "next" job classifications

### 📚 History Management
- **Completed Jobs Archive** - Table view of all finished jobs
- **Achievement Tracking** - Visual progress bars showing job performance
- **Data Export** - Excel export functionality for reporting
- **Clear History** - Bulk delete with confirmation dialog

### 🎨 Futuristic UI Design
- **Dark Theme** - Professional dark blue (#0f172a) background
- **Glowing Effects** - Cyan (#38bdf8) accents with glow animations
- **Responsive Layout** - Works on desktop, tablet, and mobile
- **Smooth Animations** - Slide-in effects and hover transitions
- **Modern Typography** - Orbitron and Exo 2 fonts for futuristic feel

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- pip (Python package manager)

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd cnc-job-management
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Generate dummy data (optional):**
   ```bash
   python generate_dummy.py
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```

5. **Open your browser and visit:**
   ```
   http://localhost:5000
   ```

## 📁 Project Structure

```
cnc-job-management/
├── app.py                 # Main Flask application
├── generate_dummy.py      # Dummy data generator
├── requirements.txt       # Python dependencies
├── jobdata.db            # SQLite database (auto-created)
├── templates/
│   ├── index.html        # Dashboard page
│   └── history.html      # History page
└── static/
    └── js/
        └── main.js       # Frontend JavaScript
```

## 🗄️ Database Schema

### Job Table
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key (auto-increment) |
| mesin | String(50) | Machine name (CNC1-CNC5) |
| job_type | String(20) | Job type (current/next) |
| MODEL | String(100) | Product model |
| PART | String(100) | Part name |
| SIZE | String(50) | Part dimensions |
| START | String(20) | Start time (DD/MM - HH:MM) |
| FINISH | String(20) | Finish time (DD/MM - HH:MM) |
| ETC_H | String(10) | Target hours (e.g., "4 H") |
| OPERATOR | String(50) | Operator name |
| ACHIEVEMENT | Float | Achievement percentage |
| REMARK | Text | Additional notes |

### History Table
Same structure as Job table for archiving completed jobs.

## 🔧 API Endpoints

### Dashboard Routes
- `GET /` - Main dashboard page
- `GET /dashboard_data` - Get all dashboard data (JSON)
- `POST /add_job` - Add new job
- `GET /job_data/<id>` - Get job data for editing
- `POST /edit_job/<id>` - Update existing job
- `POST /finish_job/<id>` - Mark job as finished
- `GET /navigate_job/<mesin>/<direction>` - Navigate job queue

### History Routes
- `GET /history` - History page
- `GET /history_data` - Get history data (JSON)
- `DELETE /clear_history` - Clear all history

### Export Routes
- `GET /export_excel/jobs` - Export current jobs to Excel
- `GET /export_excel/history` - Export history to Excel

## 🎮 Usage Guide

### Adding a New Job
1. Click **"+ Tambah Job"** button
2. Fill in the form:
   - Select machine (CNC1-CNC5)
   - Choose job type (Current/Next)
   - Enter MODEL, PART, SIZE
   - Set START/FINISH times (optional)
   - Specify target hours (ETC_H)
   - Enter operator name
   - Add remarks if needed
3. Click **"Simpan"** to save

### Editing a Job
1. Click the **✏️** button on any job card
2. Modify the pre-filled form
3. Click **"Simpan"** to update

### Finishing a Job
1. Click the **✓** button on current jobs
2. Ensure FINISH time is set (required)
3. Job moves to history automatically
4. Next job becomes current if available

### Viewing History
1. Click **"📊 History"** button
2. View completed jobs in table format
3. Export to Excel or clear history as needed

## 🎨 Customization

### Colors
- Primary Background: `#0f172a` (Dark Blue)
- Secondary Background: `#1e293b` (Slate)
- Accent Color: `#38bdf8` (Cyan)
- Success Color: `#22c55e` (Green)
- Warning Color: `#f59e0b` (Yellow)
- Error Color: `#ef4444` (Red)

### Fonts
- Headers: **Orbitron** (Futuristic monospace)
- Body: **Exo 2** (Modern sans-serif)

### Machine Configuration
To add/modify machines, update the `MACHINES` list in:
- `generate_dummy.py` (line 8)
- `app.py` (dashboard_data function)
- `templates/index.html` (machine dropdown)

## 🔧 Development

### Adding New Features
1. **Backend**: Add routes in `app.py`
2. **Frontend**: Update templates and `main.js`
3. **Database**: Modify models if needed
4. **Testing**: Use `generate_dummy.py` for test data

### Database Management
```python
# Reset database
from app import app, db
with app.app_context():
    db.drop_all()
    db.create_all()
```

## 📊 Achievement Calculation

Achievement percentage is calculated as:
- **100%** if actual time ≤ target time
- **Decreasing %** if actual time > target time
- Formula: `100 - ((actual - target) / target * 100)`

## 🛠️ Troubleshooting

### Common Issues

