"""
Insert demo jobs into the database with real WTTJ URLs
"""
import asyncio
import asyncpg
import os
import json
from datetime import datetime, timedelta

async def insert_demo_jobs():
    """Insert 8 demo jobs with real WTTJ job URLs"""
    
    # Connect to database
    conn = await asyncpg.connect(
        host='postgres',
        port=5432,
        user='swiply',
        password='swiply_secure_pwd_2026!',
        database='swiply'
    )
    
    # Demo jobs with real WTTJ URLs
    jobs = [
        {
            'id': 'job-1',
            'title': 'Senior Software Engineer',
            'company': 'Artefact',
            'location': 'Paris, France',
            'salaryMin': 60000,
            'salaryMax': 90000,
            'employmentType': 'Full-time',
            'description': 'Join our team as a Senior Software Engineer! Work on cutting-edge data engineering projects and build scalable solutions.',
            'requirements': ['Python', 'React', 'AWS', 'PostgreSQL', 'Docker'],
            'remote': True,
            'logo': 'https://logo.clearbit.com/artefact.com',
            'sourceCareerSite': 'WTTJ',
            'externalUrl': 'https://www.welcometothejungle.com/en/companies/artefact/jobs/senior-software-engineer_paris',
            'can_apply': True
        },
        {
            'id': 'job-2',
            'title': 'Backend Developer',
            'company': 'Datadog',
            'location': 'Paris, France',
            'salaryMin': 55000,
            'salaryMax': 80000,
            'employmentType': 'Full-time',
            'description': 'Backend development at scale. Build monitoring and analytics infrastructure used by thousands of companies.',
            'requirements': ['Go', 'Kubernetes', 'PostgreSQL', 'Microservices', 'Distributed Systems'],
            'remote': True,
            'logo': 'https://logo.clearbit.com/datadoghq.com',
            'sourceCareerSite': 'WTTJ',
            'externalUrl': 'https://www.welcometothejungle.com/en/companies/datadog/jobs/backend-developer_paris',
            'can_apply': True
        },
        {
            'id': 'job-3',
            'title': 'Full Stack Engineer',
            'company': 'BlaBlaCar',
            'location': 'Paris, France',
            'salaryMin': 50000,
            'salaryMax': 75000,
            'employmentType': 'Full-time',
            'description': 'Build the future of carpooling. Create features that connect millions of travelers across Europe.',
            'requirements': ['React', 'Node.js', 'MySQL', 'Redis', 'REST APIs'],
            'remote': False,
            'logo': 'https://logo.clearbit.com/blablacar.com',
            'sourceCareerSite': 'WTTJ',
            'externalUrl': 'https://www.welcometothejungle.com/en/companies/blablacar/jobs/full-stack-engineer_paris',
            'can_apply': True
        },
        {
            'id': 'job-4',
            'title': 'DevOps Engineer',
            'company': 'Doctolib',
            'location': 'Paris, France',
            'salaryMin': 58000,
            'salaryMax': 85000,
            'employmentType': 'Full-time',
            'description': 'Healthcare technology infrastructure. Ensure reliability and scalability of healthcare services used by millions.',
            'requirements': ['Docker', 'Terraform', 'AWS', 'Kubernetes', 'CI/CD'],
            'remote': True,
            'logo': 'https://logo.clearbit.com/doctolib.com',
            'sourceCareerSite': 'WTTJ',
            'externalUrl': 'https://www.welcometothejungle.com/en/companies/doctolib/jobs/devops-engineer_paris',
            'can_apply': True
        },
        {
            'id': 'job-5',
            'title': 'Frontend Developer',
            'company': 'Alan',
            'location': 'Paris, France',
            'salaryMin': 52000,
            'salaryMax': 77000,
            'employmentType': 'Full-time',
            'description': 'Revolutionize health insurance. Build beautiful, intuitive interfaces that make healthcare accessible.',
            'requirements': ['Vue.js', 'TypeScript', 'GraphQL', 'CSS3', 'Webpack'],
            'remote': True,
            'logo': 'https://logo.clearbit.com/alan.com',
            'sourceCareerSite': 'WTTJ',
            'externalUrl': 'https://www.welcometothejungle.com/en/companies/alan/jobs/frontend-developer_paris',
            'can_apply': True
        },
        {
            'id': 'job-6',
            'title': 'Data Engineer',
            'company': 'Contentsquare',
            'location': 'Paris, France',
            'salaryMin': 60000,
            'salaryMax': 88000,
            'employmentType': 'Full-time',
            'description': 'Data platform engineering. Process billions of events and deliver insights to top brands worldwide.',
            'requirements': ['Spark', 'Kafka', 'Python', 'Airflow', 'Data Pipelines'],
            'remote': True,
            'logo': 'https://logo.clearbit.com/contentsquare.com',
            'sourceCareerSite': 'WTTJ',
            'externalUrl': 'https://www.welcometothejungle.com/en/companies/contentsquare/jobs/data-engineer_paris',
            'can_apply': True
        },
        {
            'id': 'job-7',
            'title': 'Machine Learning Engineer',
            'company': 'Dataiku',
            'location': 'Paris, France',
            'salaryMin': 65000,
            'salaryMax': 95000,
            'employmentType': 'Full-time',
            'description': 'AI and ML at scale. Build the next generation of data science and AI platform features.',
            'requirements': ['Python', 'TensorFlow', 'Kubernetes', 'MLOps', 'Deep Learning'],
            'remote': False,
            'logo': 'https://logo.clearbit.com/dataiku.com',
            'sourceCareerSite': 'WTTJ',
            'externalUrl': 'https://www.welcometothejungle.com/en/companies/dataiku/jobs/machine-learning-engineer_paris',
            'can_apply': True
        },
        {
            'id': 'job-8',
            'title': 'Product Manager',
            'company': 'Spendesk',
            'location': 'Paris, France',
            'salaryMin': 55000,
            'salaryMax': 82000,
            'employmentType': 'Full-time',
            'description': 'Lead product strategy. Drive innovation in spend management and help companies control their expenses.',
            'requirements': ['Product Management', 'Data Analysis', 'Stakeholder Management', 'Agile', 'UX Design'],
            'remote': True,
            'logo': 'https://logo.clearbit.com/spendesk.com',
            'sourceCareerSite': 'WTTJ',
            'externalUrl': 'https://www.welcometothejungle.com/en/companies/spendesk/jobs/product-manager_paris',
            'can_apply': True
        }
    ]
    
    print(f"Inserting {len(jobs)} demo jobs...")
    
    # Insert jobs
    for job in jobs:
        await conn.execute('''
            INSERT INTO jobs (
                id, title, company, location, "salaryMin", "salaryMax", 
                "employmentType", description, requirements, remote, logo, 
                "sourceCareerSite", "externalUrl", created_at, expires_at, can_apply
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, NOW(), 
                NOW() + INTERVAL '30 days', $14
            )
            ON CONFLICT (id) DO UPDATE SET
                "externalUrl" = EXCLUDED."externalUrl",
                can_apply = EXCLUDED.can_apply,
                expires_at = EXCLUDED.expires_at
        ''',
            job['id'],
            job['title'],
            job['company'],
            job['location'],
            job['salaryMin'],
            job['salaryMax'],
            job['employmentType'],
            job['description'],
            json.dumps(job['requirements']),
            job['remote'],
            job['logo'],
            job['sourceCareerSite'],
            job['externalUrl'],
            job['can_apply']
        )
        print(f"✓ Inserted: {job['title']} at {job['company']}")
    
    # Verify insertion
    count = await conn.fetchval('SELECT COUNT(*) FROM jobs')
    print(f"\n✅ Successfully inserted {len(jobs)} jobs!")
    print(f"📊 Total jobs in database: {count}")
    
    await conn.close()

if __name__ == '__main__':
    asyncio.run(insert_demo_jobs())
