from app import create_app, db
from app.models.models import User, Garage, Service, Booking, Vehicle, Document, SOSAlert

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Garage=Garage, Service=Service,
                Booking=Booking, Vehicle=Vehicle, Document=Document, SOSAlert=SOSAlert)

@app.context_processor
def inject_now():
    from datetime import date
    return {'now': date.today().strftime('%Y-%m-%d')}

with app.app_context():
    db.create_all()
    print("✅ Database tables created.")