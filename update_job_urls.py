#!/usr/bin/env python3
"""Update demo jobs with real WTTJ URLs"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from shared.database import SessionLocal
from shared.models import Job

# Real WTTJ job URLs (example format - these may not be active jobs)
job_urls = {
    'job-wttj-001': 'https://www.welcometothejungle.com/fr/companies/spendesk/jobs/developpeur-full-stack-react-node-js_paris',
    'job-wttj-002': 'https://www.welcometothejungle.com/fr/companies/datadog/jobs/senior-devops-engineer_paris',
    'job-wttj-003': 'https://www.welcometothejungle.com/fr/companies/blablacar/jobs/data-scientist-machine-learning_paris',
    'job-wttj-004': 'https://www.welcometothejungle.com/fr/companies/doctolib/jobs/chef-de-projet-digital_paris',
    'job-wttj-005': 'https://www.welcometothejungle.com/fr/companies/alan/jobs/senior-product-designer_paris',
    'job-wttj-006': 'https://www.welcometothejungle.com/fr/companies/contentsquare/jobs/backend-engineer-python_paris',
    'job-wttj-007': 'https://www.welcometothejungle.com/fr/companies/owkin/jobs/machine-learning-engineer_paris',
    'job-wttj-008': 'https://www.welcometothejungle.com/fr/companies/luko/jobs/growth-marketing-manager_paris'
}

def update_urls():
    db = SessionLocal()
    try:
        updated = 0
        for job_id, url in job_urls.items():
            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                job.externalUrl = url
                updated += 1
                print(f"✅ Updated {job_id}: {job.title} -> {url[:60]}...")
        
        db.commit()
        print(f"\n✅ Successfully updated {updated} jobs with WTTJ URLs")
        
        # Verify
        print("\n📊 Verification:")
        jobs = db.query(Job).limit(3).all()
        for job in jobs:
            print(f"  {job.id}: {job.externalUrl[:80] if job.externalUrl else 'NO URL'}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_urls()
