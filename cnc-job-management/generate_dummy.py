import random
from datetime import datetime, timedelta
from app import app, db, Job, History

# Sample data
MACHINES = ['CNC1', 'CNC2', 'CNC3', 'CNC4', 'CNC5']
OPERATORS = ['JONI', 'DONI', 'NANI', 'SARI', 'BUDI', 'ANDI', 'RINI', 'TONO']
MODELS = ['MODEL-A1', 'MODEL-B2', 'MODEL-C3', 'MODEL-D4', 'MODEL-E5', 'MODEL-F6']
PARTS = ['SHAFT', 'GEAR', 'HOUSING', 'BRACKET', 'PLATE', 'COVER', 'BASE', 'FLANGE']
SIZES = ['10x20', '15x30', '20x40', '25x50', '30x60', '35x70', '40x80', '50x100']
ETC_H_OPTIONS = ['2 H', '3 H', '4 H', '5 H', '6 H', '8 H']
REMARKS = [
    'Normal operation',
    'Check tool wear',
    'Material shortage',
    'Quality check required',
    'Rush order',
    'Special handling',
    'Customer priority',
    ''
]

def generate_random_datetime(days_offset=0, hour_range=(6, 22)):
    """Generate random datetime within specified range"""
    base_date = datetime.now() + timedelta(days=days_offset)
    random_hour = random.randint(hour_range[0], hour_range[1])
    random_minute = random.randint(0, 59)
    
    return base_date.replace(hour=random_hour, minute=random_minute, second=0, microsecond=0)

def format_datetime(dt):
    """Format datetime to DD/MM - HH:MM"""
    return dt.strftime("%d/%m - %H:%M")

def calculate_achievement(start_dt, finish_dt, etc_h):
    """Calculate achievement percentage"""
    if not start_dt or not finish_dt:
        return 0.0
    
    duration_hours = (finish_dt - start_dt).total_seconds() / 3600
    target_hours = float(etc_h.replace(' H', ''))
    
    if duration_hours <= target_hours:
        return 100.0
    else:
        return max(0.0, 100.0 - ((duration_hours - target_hours) / target_hours * 100))

def generate_dummy_jobs():
    """Generate dummy job data"""
    print("🔄 Generating dummy job data...")
    
    with app.app_context():
        # Clear existing data
        print("🗑️  Clearing existing data...")
        Job.query.delete()
        History.query.delete()
        db.session.commit()
        
        jobs_created = 0
        history_created = 0
        
        # Generate jobs for each machine
        for machine in MACHINES:
            # Generate 1 current job (50% chance)
            if random.choice([True, False]):
                start_dt = generate_random_datetime(days_offset=-1)
                
                # 70% chance to have finish time for current jobs
                finish_dt = None
                if random.random() < 0.7:
                    finish_dt = start_dt + timedelta(hours=random.randint(2, 8))
                
                etc_h = random.choice(ETC_H_OPTIONS)
                achievement = calculate_achievement(start_dt, finish_dt, etc_h) if finish_dt else 0.0
                
                current_job = Job(
                    mesin=machine,
                    job_type='current',
                    MODEL=random.choice(MODELS),
                    PART=random.choice(PARTS),
                    SIZE=random.choice(SIZES),
                    START=format_datetime(start_dt),
                    FINISH=format_datetime(finish_dt) if finish_dt else None,
                    ETC_H=etc_h,
                    OPERATOR=random.choice(OPERATORS),
                    ACHIEVEMENT=achievement,
                    REMARK=random.choice(REMARKS)
                )
                
                db.session.add(current_job)
                jobs_created += 1
                print(f"✅ Created current job for {machine}")
            
            # Generate 1-3 next jobs
            next_job_count = random.randint(1, 3)
            for i in range(next_job_count):
                # Next jobs usually don't have start/finish times yet
                start_dt = None
                finish_dt = None
                
                # 20% chance to have scheduled start time
                if random.random() < 0.2:
                    start_dt = generate_random_datetime(days_offset=random.randint(0, 2))
                
                etc_h = random.choice(ETC_H_OPTIONS)
                
                next_job = Job(
                    mesin=machine,
                    job_type='next',
                    MODEL=random.choice(MODELS),
                    PART=random.choice(PARTS),
                    SIZE=random.choice(SIZES),
                    START=format_datetime(start_dt) if start_dt else None,
                    FINISH=format_datetime(finish_dt) if finish_dt else None,
                    ETC_H=etc_h,
                    OPERATOR=random.choice(OPERATORS),
                    ACHIEVEMENT=0.0,
                    REMARK=random.choice(REMARKS)
                )
                
                db.session.add(next_job)
                jobs_created += 1
                print(f"✅ Created next job {i+1} for {machine}")
        
        # Generate some history data (completed jobs)
        print("📚 Generating history data...")
        for _ in range(random.randint(10, 20)):
            start_dt = generate_random_datetime(days_offset=random.randint(-7, -1))
            duration_hours = random.randint(2, 10)
            finish_dt = start_dt + timedelta(hours=duration_hours)
            etc_h = random.choice(ETC_H_OPTIONS)
            achievement = calculate_achievement(start_dt, finish_dt, etc_h)
            
            history_job = History(
                mesin=random.choice(MACHINES),
                job_type=random.choice(['current', 'next']),
                MODEL=random.choice(MODELS),
                PART=random.choice(PARTS),
                SIZE=random.choice(SIZES),
                START=format_datetime(start_dt),
                FINISH=format_datetime(finish_dt),
                ETC_H=etc_h,
                OPERATOR=random.choice(OPERATORS),
                ACHIEVEMENT=achievement,
                REMARK=random.choice(REMARKS)
            )
            
            db.session.add(history_job)
            history_created += 1
        
        # Commit all changes
        try:
            db.session.commit()
            print(f"✅ Successfully created {jobs_created} jobs and {history_created} history records")
            print("🎉 Dummy data generation completed!")
            
            # Print summary
            print("\n📊 SUMMARY:")
            print(f"   • Active Jobs: {jobs_created}")
            print(f"   • History Records: {history_created}")
            print(f"   • Total Records: {jobs_created + history_created}")
            
            # Print machine status
            print("\n🏭 MACHINE STATUS:")
            for machine in MACHINES:
                current_count = Job.query.filter_by(mesin=machine, job_type='current').count()
                next_count = Job.query.filter_by(mesin=machine, job_type='next').count()
                total = current_count + next_count
                print(f"   • {machine}: {total} jobs (Current: {current_count}, Next: {next_count})")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating dummy data: {str(e)}")
            raise

def main():
    """Main function"""
    print("🚀 CNC Job Management - Dummy Data Generator")
    print("=" * 50)
    
    try:
        generate_dummy_jobs()
        print("\n✨ Ready to test the application!")
        print("   Run: python app.py")
        print("   Then visit: http://localhost:5000")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("Make sure the Flask app is properly configured.")

if __name__ == '__main__':
    main()
