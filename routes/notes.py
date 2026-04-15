from flask import Blueprint, g, jsonify, request

from extensions import db
from models import Note
from utils import auth_required

notes_bp = Blueprint("notes_bp", __name__)


def _paginate_notes(query):
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    pagination = query.order_by(Note.created_at.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False,
    )

    return {
        "items": [note.to_dict() for note in pagination.items],
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total": pagination.total,
        "pages": pagination.pages,
        "has_next": pagination.has_next,
        "has_prev": pagination.has_prev,
    }


def _get_owned_note_or_none(note_id):
    return Note.query.filter_by(id=note_id, user_id=g.current_user.id).first()


@notes_bp.get("/notes")
@auth_required
def get_notes():
    user = g.current_user
    data = _paginate_notes(Note.query.filter_by(user_id=user.id))
    return jsonify(data), 200


@notes_bp.post("/notes")
@auth_required
def create_note():
    user = g.current_user
    data = request.get_json(silent=True) or {}

    title = (data.get("title") or "").strip()
    content = data.get("content") or ""
    is_pinned = bool(data.get("is_pinned", False))

    if not title:
        return jsonify({"error": "title is required"}), 400

    note = Note(
        title=title,
        content=content,
        is_pinned=is_pinned,
        user_id=user.id,
    )

    db.session.add(note)
    db.session.commit()

    return jsonify(note.to_dict()), 201


@notes_bp.get("/notes/<int:note_id>")
@auth_required
def get_note(note_id):
    note = _get_owned_note_or_none(note_id)
    if not note:
        return jsonify({"error": "note not found"}), 404

    return jsonify(note.to_dict()), 200


@notes_bp.patch("/notes/<int:note_id>")
@auth_required
def update_note(note_id):
    note = _get_owned_note_or_none(note_id)
    if not note:
        return jsonify({"error": "note not found"}), 404

    data = request.get_json(silent=True) or {}
    allowed_keys = {"title", "content", "is_pinned"}

    if not any(key in data for key in allowed_keys):
        return jsonify({"error": "no valid fields provided"}), 400

    if "title" in data:
        title = data.get("title")
        if not isinstance(title, str) or not title.strip():
            return jsonify({"error": "title cannot be empty"}), 400
        note.title = title.strip()

    if "content" in data:
        content = data.get("content")
        note.content = "" if content is None else str(content)

    if "is_pinned" in data:
        note.is_pinned = bool(data.get("is_pinned"))

    db.session.commit()
    return jsonify(note.to_dict()), 200


@notes_bp.delete("/notes/<int:note_id>")
@auth_required
def delete_note(note_id):
    note = _get_owned_note_or_none(note_id)
    if not note:
        return jsonify({"error": "note not found"}), 404

    db.session.delete(note)
    db.session.commit()
    return jsonify({}), 200