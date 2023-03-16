import click
from flask.cli import with_appcontext
from .models import db
import csv
from .models import db, Participant
from datetime import date, datetime

@click.command(name="createdb")
@with_appcontext
def create_db():
    """Create database tables."""
    db.create_all()
    db.session.commit()
    print("Database tables created")

@click.command(name="load")
@click.option('--path', prompt='Path to csv file',
              help='File containing participants to load.')
@with_appcontext
def load_participants(path):
    """Load one or more already enrolled participants from CSV file."""
    from . import format_info
    cnt = 0
    with open(path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            row['dob'] = date.fromisoformat(row['dob'])
            info = format_info(first_initial=row['first_initial'],
                               last_initial=row['last_initial'],
                               dob=row['dob'],
                               sex=row['sex'])
            participant = Participant(info=info,
                                      recruitment_date=datetime.fromisoformat(row['recruitment_date']),
                                      recruited_by=row['recruited_by'])
            db.session.add(participant)
            cnt += 1

    db.session.commit()
    print(f'{cnt} records loaded')
