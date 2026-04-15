from app import create_app
from extensions import db
from models import Note, User

app = create_app()

with app.app_context():
    db.create_all()

    Note.query.delete()
    User.query.delete()
    db.session.commit()

    user1 = User(username="alice")
    user1.set_password("password123")

    user2 = User(username="bob")
    user2.set_password("password123")

    db.session.add_all([user1, user2])
    db.session.commit()

    seed_notes = [
        Note(
            title="Welcome",
            content="This is a starter note for Alice.",
            is_pinned=True,
            user_id=user1.id,
        ),
        Note(
            title="Tasks",
            content="Buy groceries and finish homework.",
            is_pinned=False,
            user_id=user1.id,
        ),
        Note(
            title="Bob Note",
            content="Bob's first starter note.",
            is_pinned=False,
            user_id=user2.id,
        ),
    ]

    db.session.add_all(seed_notes)
    db.session.commit()

    print("Seeded database successfully.")