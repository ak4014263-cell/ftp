#!/usr/bin/env python3
"""
Update demo jobs with generic WTTJ search URLs that will work
These URLs will take users to job search pages where they can apply
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from shared.database import SessionLocal
from shared.models import Job

# Generic WTTJ job search URLs by role - these always work
job_search_urls = {
    'job-wttj-001': 'https://www.welcometothejungle.com/fr/jobs?query=developpeur%20full%20stack%20react&page=1',
    'job-wttj-002': 'https://www.welcometothejungle.com/fr/jobs?query=devops%20engineer&page=1',
    'job-wttj-003': 'https://www.welcometothejungle.com/fr/jobs?query=data%20scientist%20python&page=1',
    'job-wttj-004': 'https://www.welcometothejungle.com/fr/jobs?query=chef%20de%20projet%20digital&page=1',
    'job-wttj-005': 'https://www.welcometothejungle.com/fr/jobs?query=ux%20designer&page=1',
    'job-wttj-006': 'https://www.welcometothejungle.com/fr/jobs?query=backend%20python%20django&page=1',
    'job-wttj-007': 'https://www.welcometothejungle.com/fr/jobs?query=machine%20learning%20engineer&page=1',
    'job-wttj-008': 'https://www.welcometothejungle.com/fr/jobs?query=marketing%20digital&page=1'
}

def update_urls():
    db = SessionLocal()
    try:
        updated = 0
        for job_id, url in job_search_urls.items():
            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                job.externalUrl = url
                updated += 1
                print(f"✅ Updated {job_id}: {job.title}")
                print(f"   URL: {url}")
        
        db.commit()
        print(f"\n✅ Successfully updated {updated} jobs with generic WTTJ search URLs")
        print("\n⚠️  NOTE: These are search page URLs, not specific job postings.")
        print("Users will be taken to relevant job search results where they can browse and apply.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_urls()
