from flask import Flask, render_template, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import os
import xlwt
import io
from werkzeug.exceptions import NotFound

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jobdata.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mesin = db.Column(db.String(50), nullable=False)
    job_type = db.Column(db.String(20), nullable=False)  # current / next
    MODEL = db.Column(db.String(100), nullable=False)
    PART = db.Column(db.String(100), nullable=False)
    SIZE = db.Column(db.String(50), nullable=False)
    START = db.Column(db.String(20), nullable=True)  # DD/MM - HH:MM
    FINISH = db.Column(db.String(20), nullable=True)  # DD/MM - HH:MM
    ETC_H = db.Column(db.String(10), nullable=False)  # target jam kerja
    OPERATOR = db.Column(db.String(50), nullable=False)
    ACHIEVEMENT = db.Column(db.Float, default=0.0)
    REMARK = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'mesin': self.mesin,
            'job_type': self.job_type,
            'MODEL': self.MODEL,
            'PART': self.PART,
            'SIZE': self.SIZE,
            'START': self.START,
            'FINISH': self.FINISH,
            'ETC_H': self.ETC_H,
            'OPERATOR': self.OPERATOR,
            'ACHIEVEMENT': self.ACHIEVEMENT,
            'REMARK': self.REMARK
        }

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mesin = db.Column(db.String(50), nullable=False)
    job_type = db.Column(db.String(20), nullable=False)
    MODEL = db.Column(db.String(100), nullable=False)
    PART = db.Column(db.String(100), nullable=False)
    SIZE = db.Column(db.String(50), nullable=False)
    START = db.Column(db.String(20), nullable=True)
    FINISH = db.Column(db.String(20), nullable=True)
    ETC_H = db.Column(db.String(10), nullable=False)
    OPERATOR = db.Column(db.String(50), nullable=False)
    ACHIEVEMENT = db.Column(db.Float, default=0.0)
    REMARK = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'mesin': self.mesin,
            'job_type': self.job_type,
            'MODEL': self.MODEL,
            'PART': self.PART,
            'SIZE': self.SIZE,
            'START': self.START,
            'FINISH': self.FINISH,
            'ETC_H': self.ETC_H,
            'OPERATOR': self.OPERATOR,
            'ACHIEVEMENT': self.ACHIEVEMENT,
            'REMARK': self.REMARK
        }

def calculate_achievement(start_time, finish_time, etc_h):
    """Calculate achievement percentage based on actual vs target time"""
    if not start_time or not finish_time or not etc_h:
        return 0.0
    
    try:
        # Parse times (DD/MM - HH:MM format)
        start_dt = datetime.strptime(start_time, "%d/%m - %H:%M")
        finish_dt = datetime.strptime(finish_time, "%d/%m - %H:%M")
        
        # Calculate actual duration in hours
        duration = (finish_dt - start_dt).total_seconds() / 3600
        
        # Extract target hours from ETC_H (e.g., "4 H" -> 4)
        target_hours = float(etc_h.replace(' H', '').replace('H', ''))
        
        # Calculate achievement (reverse calculation)
        if duration <= target_hours:
            return 100.0
        else:
            return max(0.0, 100.0 - ((duration - target_hours) / target_hours * 100))
    except:
        return 0.0

# Routes
@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/add_job', methods=['POST'])
def add_job():
    """Add new job"""
    try:
        data = request.get_json()
        
        # Calculate achievement if both start and finish are provided
        achievement = 0.0
        if data.get('START') and data.get('FINISH'):
            achievement = calculate_achievement(data.get('START'), data.get('FINISH'), data.get('ETC_H'))
        
        new_job = Job(
            mesin=data['mesin'],
            job_type=data['job_type'],
            MODEL=data['MODEL'],
            PART=data['PART'],
            SIZE=data['SIZE'],
            START=data.get('START'),
            FINISH=data.get('FINISH'),
            ETC_H=data['ETC_H'],
            OPERATOR=data['OPERATOR'],
            ACHIEVEMENT=achievement,
            REMARK=data.get('REMARK', '')
        )
        
        db.session.add(new_job)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Job berhasil ditambahkan'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/job_data/<int:job_id>')
def get_job_data(job_id):
    """Get job data for editing"""
    try:
        job = Job.query.get_or_404(job_id)
        return jsonify(job.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/edit_job/<int:job_id>', methods=['POST'])
def edit_job(job_id):
    """Edit existing job"""
    try:
        job = Job.query.get_or_404(job_id)
        data = request.get_json()
        
        job.mesin = data['mesin']
        job.job_type = data['job_type']
        job.MODEL = data['MODEL']
        job.PART = data['PART']
        job.SIZE = data['SIZE']
        job.START = data.get('START')
        job.FINISH = data.get('FINISH')
        job.ETC_H = data['ETC_H']
        job.OPERATOR = data['OPERATOR']
        job.REMARK = data.get('REMARK', '')
        
        # Recalculate achievement
        if job.START and job.FINISH:
            job.ACHIEVEMENT = calculate_achievement(job.START, job.FINISH, job.ETC_H)
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Job berhasil diupdate'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/finish_job/<int:job_id>', methods=['POST'])
def finish_job(job_id):
    """Finish job and move to history"""
    try:
        job = Job.query.get_or_404(job_id)
        
        # Check if FINISH is provided
        if not job.FINISH:
            return jsonify({'success': False, 'message': 'FINISH time harus diisi sebelum menyelesaikan job'})
        
        # Calculate final achievement
        achievement = calculate_achievement(job.START, job.FINISH, job.ETC_H)
        
        # Move to history
        history_job = History(
            mesin=job.mesin,
            job_type=job.job_type,
            MODEL=job.MODEL,
            PART=job.PART,
            SIZE=job.SIZE,
            START=job.START,
            FINISH=job.FINISH,
            ETC_H=job.ETC_H,
            OPERATOR=job.OPERATOR,
            ACHIEVEMENT=achievement,
            REMARK=job.REMARK
        )
        
        db.session.add(history_job)
        db.session.delete(job)
        
        # If this was a current job, promote next job to current
        if job.job_type == 'current':
            next_job = Job.query.filter_by(mesin=job.mesin, job_type='next').first()
            if next_job:
                next_job.job_type = 'current'
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Job berhasil diselesaikan dan dipindah ke history'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/navigate_job/<mesin>/<direction>')
def navigate_job(mesin, direction):
    """Navigate through next jobs for a machine with current job id"""
    try:
        current_job_id = request.args.get('current_job_id', type=int)
        next_jobs = Job.query.filter_by(mesin=mesin, job_type='next').order_by(Job.id).all()
        
        if not next_jobs:
            return jsonify({'job': None})
        
        # Find current index
        current_index = 0
        if current_job_id:
            for idx, job in enumerate(next_jobs):
                if job.id == current_job_id:
                    current_index = idx
                    break
        
        if direction == 'next':
            new_index = current_index + 1
            if new_index >= len(next_jobs):
                new_index = 0  # loop back to first
        elif direction == 'prev':
            new_index = current_index - 1
            if new_index < 0:
                new_index = len(next_jobs) - 1  # loop back to last
        else:
            new_index = current_index
        
        job = next_jobs[new_index]
        return jsonify({'job': job.to_dict()})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/dashboard_data')
def get_dashboard_data():
    """Get all dashboard data"""
    try:
        machines = ['CNC1', 'CNC2', 'CNC3', 'CNC4', 'CNC5']
        dashboard_data = {}
        
        for machine in machines:
            current_job = Job.query.filter_by(mesin=machine, job_type='current').first()
            next_jobs = Job.query.filter_by(mesin=machine, job_type='next').all()
            
            dashboard_data[machine] = {
                'current': current_job.to_dict() if current_job else None,
                'next_jobs': [job.to_dict() for job in next_jobs],
                'total_jobs': len(next_jobs) + (1 if current_job else 0)
            }
        
        return jsonify(dashboard_data)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/history')
def history_page():
    """History page"""
    return render_template('history.html')

@app.route('/history_data')
def get_history_data():
    """Get all history data"""
    try:
        history_jobs = History.query.all()
        return jsonify([job.to_dict() for job in history_jobs])
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/clear_history', methods=['DELETE'])
def clear_history():
    """Clear all history"""
    try:
        History.query.delete()
        db.session.commit()
        return jsonify({'success': True, 'message': 'History berhasil dihapus'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/export_excel/jobs')
def export_jobs_excel():
    """Export jobs to Excel"""
    try:
        jobs = Job.query.all()
        
        # Create workbook
        wb = xlwt.Workbook()
        ws = wb.add_sheet('Jobs')
        
        # Headers
        headers = ['ID', 'Mesin', 'Job Type', 'MODEL', 'PART', 'SIZE', 'START', 'FINISH', 'ETC_H', 'OPERATOR', 'ACHIEVEMENT', 'REMARK']
        for col, header in enumerate(headers):
            ws.write(0, col, header)
        
        # Data
        for row, job in enumerate(jobs, 1):
            ws.write(row, 0, job.id)
            ws.write(row, 1, job.mesin)
            ws.write(row, 2, job.job_type)
            ws.write(row, 3, job.MODEL)
            ws.write(row, 4, job.PART)
            ws.write(row, 5, job.SIZE)
            ws.write(row, 6, job.START or '')
            ws.write(row, 7, job.FINISH or '')
            ws.write(row, 8, job.ETC_H)
            ws.write(row, 9, job.OPERATOR)
            ws.write(row, 10, job.ACHIEVEMENT)
            ws.write(row, 11, job.REMARK or '')
        
        # Save to memory
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.ms-excel',
            as_attachment=True,
            download_name='cnc_jobs.xls'
        )
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/export_excel/history')
def export_history_excel():
    """Export history to Excel"""
    try:
        history_jobs = History.query.all()
        
        # Create workbook
        wb = xlwt.Workbook()
        ws = wb.add_sheet('History')
        
        # Headers
        headers = ['ID', 'Mesin', 'Job Type', 'MODEL', 'PART', 'SIZE', 'START', 'FINISH', 'ETC_H', 'OPERATOR', 'ACHIEVEMENT', 'REMARK']
        for col, header in enumerate(headers):
            ws.write(0, col, header)
        
        # Data
        for row, job in enumerate(history_jobs, 1):
            ws.write(row, 0, job.id)
            ws.write(row, 1, job.mesin)
            ws.write(row, 2, job.job_type)
            ws.write(row, 3, job.MODEL)
            ws.write(row, 4, job.PART)
            ws.write(row, 5, job.SIZE)
            ws.write(row, 6, job.START or '')
            ws.write(row, 7, job.FINISH or '')
            ws.write(row, 8, job.ETC_H)
            ws.write(row, 9, job.OPERATOR)
            ws.write(row, 10, job.ACHIEVEMENT)
            ws.write(row, 11, job.REMARK or '')
        
        # Save to memory
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.ms-excel',
            as_attachment=True,
            download_name='cnc_history.xls'
        )
    except Exception as e:
        return jsonify({'error': str(e)})

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# Initialize database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
