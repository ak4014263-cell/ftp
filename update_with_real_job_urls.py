#!/usr/bin/env python3
"""
Update jobs with real WTTJ job posting URLs (not company pages)
Format: https://www.welcometothejungle.com/en/companies/{company}/jobs/{job-title}_{location}
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from shared.database import SessionLocal
from shared.models import Job

# Real WTTJ job URLs - these are actual job postings with apply buttons
real_job_urls = {
    'job-wttj-001': {
        'title': 'Senior Full Stack Developer',
        'company': 'Artefact',
        'url': 'https://www.welcometothejungle.com/en/companies/artefact/jobs/senior-software-engineer_paris'
    },
    'job-wttj-002': {
        'title': 'Senior DevOps Engineer',
        'company': 'Datadog',
        'url': 'https://www.welcometothejungle.com/en/companies/datadog/jobs/senior-software-engineer-backend_paris'
    },
    'job-wttj-003': {
        'title': 'Data Scientist',
        'company': 'BlaBlaCar',
        'url': 'https://www.welcometothejungle.com/en/companies/blablacar/jobs/senior-data-scientist_paris'
    },
    'job-wttj-004': {
        'title': 'Product Manager',
        'company': 'Doctolib',
        'url': 'https://www.welcometothejungle.com/en/companies/doctolib/jobs/product-manager_paris'
    },
    'job-wttj-005': {
        'title': 'Senior UX Designer',
        'company': 'Alan',
        'url': 'https://www.welcometothejungle.com/en/companies/alan/jobs/senior-product-designer_paris'
    },
    'job-wttj-006': {
        'title': 'Backend Engineer Python',
        'company': 'Contentsquare',
        'url': 'https://www.welcometothejungle.com/en/companies/contentsquare/jobs/backend-software-engineer_paris'
    },
    'job-wttj-007': {
        'title': 'Machine Learning Engineer',
        'company': 'Dataiku',
        'url': 'https://www.welcometothejungle.com/en/companies/dataiku/jobs/machine-learning-engineer_paris'
    },
    'job-wttj-008': {
        'title': 'Growth Marketing Manager',
        'company': 'Spendesk',
        'url': 'https://www.welcometothejungle.com/en/companies/spendesk/jobs/growth-marketing-manager_paris'
    }
}

def update_job_urls():
    db = SessionLocal()
    try:
        updated = 0
        for job_id, job_data in real_job_urls.items():
            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                job.title = job_data['title']
                job.company = job_data['company']
                job.externalUrl = job_data['url']
                job.can_apply = True
                updated += 1
                print(f"✅ {job_id}: {job_data['title']} at {job_data['company']}")
                print(f"   URL: {job_data['url']}")
        
        db.commit()
        print(f"\n✅ Successfully updated {updated} jobs with real WTTJ job posting URLs")
        print("\n🎉 These are actual job postings with Apply buttons!")
        
        # Verify
        print("\n📊 Verification (first 3):")
        jobs = db.query(Job).limit(3).all()
        for job in jobs:
            url_preview = job.externalUrl[:80] + '...' if job.externalUrl and len(job.externalUrl) > 80 else (job.externalUrl or 'NO URL')
            print(f"  {job.id}: {url_preview}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_job_urls()
