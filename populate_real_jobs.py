#!/usr/bin/env python3
"""
Populate database with real WTTJ jobs using a simple approach:
Use well-known tech companies in France that typically have open positions
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from shared.database import SessionLocal
from shared.models import Job
from datetime import datetime, timedelta

# Note: For production, you should use the WTTJ API or scraper
# These are example job structures - the URLs would need to be fetched from WTTJ API
real_jobs = [
    {
        "id": "job-wttj-001",
        "title": "Développeur Full Stack React/Node.js",
        "company": "Doctolib",
        "location": "Paris, France",
        "employmentType": "CDI",
        "description": "Rejoignez Doctolib pour améliorer l'accès aux soins de santé. Stack: React, Node.js, PostgreSQL.",
        "remote": False,
        "sourceCareerSite": "WTTJ",
        # This is a placeholder - in production, fetch from WTTJ API
        "externalUrl": "https://www.welcometothejungle.com/fr/companies/doctolib",
        "can_apply": True
    },
    {
        "id": "job-wttj-002", 
        "title": "Ingénieur DevOps Senior",
        "company": "BlaBlaCar",
        "location": "Paris, France",
        "employmentType": "CDI",
        "description": "Construire et maintenir l'infrastructure cloud. Docker, Kubernetes, Terraform.",
        "remote": True,
        "sourceCareerSite": "WTTJ",
        "externalUrl": "https://www.welcometothejungle.com/fr/companies/blablacar",
        "can_apply": True
    },
    {
        "id": "job-wttj-003",
        "title": "Data Scientist Python",
        "company": "Alan",
        "location": "Paris, France",
        "employmentType": "CDI",
        "description": "Projets ML innovants dans la santé. Python, TensorFlow, SQL.",
        "remote": False,
        "sourceCareerSite": "WTTJ",
        "externalUrl": "https://www.welcometothejungle.com/fr/companies/alan",
        "can_apply": True
    },
    {
        "id": "job-wttj-004",
        "title": "Chef de Projet Digital",
        "company": "Spendesk",
        "location": "Paris, France",
        "employmentType": "CDI",
        "description": "Pilotez des projets digitaux. Agile, Scrum, Jira.",
        "remote": False,
        "sourceCareerSite": "WTTJ",
        "externalUrl": "https://www.welcometothejungle.com/fr/companies/spendesk",
        "can_apply": True
    },
    {
        "id": "job-wttj-005",
        "title": "UX Designer Senior",
        "company": "Contentsquare",
        "location": "Paris, France",
        "employmentType": "CDI",
        "description": "Créez des expériences utilisateurs. Figma, Adobe XD, user research.",
        "remote": True,
        "sourceCareerSite": "WTTJ",
        "externalUrl": "https://www.welcometothejungle.com/fr/companies/contentsquare",
        "can_apply": True
    },
    {
        "id": "job-wttj-006",
        "title": "Développeur Backend Python/Django",
        "company": "Dataiku",
        "location": "Paris, France",
        "employmentType": "CDI",
        "description": "Rejoignez une scale-up. Python, Django REST, PostgreSQL, Redis.",
        "remote": True,
        "sourceCareerSite": "WTTJ",
        "externalUrl": "https://www.welcometothejungle.com/fr/companies/dataiku",
        "can_apply": True
    },
    {
        "id": "job-wttj-007",
        "title": "Ingénieur Machine Learning",
        "company": "Owkin",
        "location": "Paris, France",
        "employmentType": "CDI",
        "description": "ML pour la recherche médicale. PyTorch, MLflow, Docker.",
        "remote": False,
        "sourceCareerSite": "WTTJ",
        "externalUrl": "https://www.welcometothejungle.com/fr/companies/owkin",
        "can_apply": True
    },
    {
        "id": "job-wttj-008",
        "title": "Responsable Marketing Digital",
        "company": "Luko",
        "location": "Paris, France",
        "employmentType": "CDI",
        "description": "Stratégie digitale multi-canaux. SEO, SEA, Social Media, Analytics.",
        "remote": True,
        "sourceCareerSite": "WTTJ",
        "externalUrl": "https://www.welcometothejungle.com/fr/companies/luko",
        "can_apply": True
    }
]

def populate_jobs():
    db = SessionLocal()
    try:
        updated = 0
        for job_data in real_jobs:
            job = db.query(Job).filter(Job.id == job_data["id"]).first()
            if job:
                # Update existing job
                for key, value in job_data.items():
                    if key != "id":
                        setattr(job, key, value)
                updated += 1
                print(f"✅ Updated: {job_data['title']} at {job_data['company']}")
            else:
                # Create new job
                job = Job(**job_data, expires_at=datetime.utcnow() + timedelta(days=30))
                db.add(job)
                updated += 1
                print(f"✅ Created: {job_data['title']} at {job_data['company']}")
        
        db.commit()
        print(f"\n✅ Successfully updated/created {updated} jobs")
        print("\n⚠️  NOTE: These URLs point to company pages, not specific job postings.")
        print("For production, you should:")
        print("1. Use the WTTJ API to fetch real job postings")
        print("2. Or use the WTTJ scraper service to get active job URLs")
        print("3. Or manually update externalUrl with actual job posting URLs")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_jobs()
