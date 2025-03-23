

from fastapi import HTTPException
from database import SessionLocal
from note.domain.note import Note as NoteVO
from note.infra.db_models.note import Note, Tag
from note.domain.repository.note_repo import INoteRepository
from sqlalchemy.orm import joinedload

from utils.db_utils import row_to_dict


class NoteRepository(INoteRepository):
    def get_notes(self, user_id: str, page: int, items_per_page: int) -> tuple[int, list[NoteVO]]:
        with SessionLocal() as session:
           query = session.query(Note).options(joinedload(Note.tags)).filter(Note.user_id == user_id)
           total_count = query.count()
           notes = query.offset((page - 1) * items_per_page).limit(items_per_page).all()
        note_vos = [NoteVO(**row_to_dict(note)) for note in notes]
        return total_count, note_vos

    def find_by_id(self, user_id: str, id: str) -> NoteVO:
        with SessionLocal() as session:
            note = session.query(Note).options(joinedload(Note.tags)).filter(Note.user_id == user_id, Note.id == id).first()
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        return NoteVO(**row_to_dict(note))

    def save(self, user_id: str, note_vo: NoteVO):
        with SessionLocal() as session:
            tags: list[Tag] = []
            for tag in note_vo.tags:
                existing_tag = session.query(Tag).filter(Tag.name == tag).first()
                if existing_tag:
                    tags.append(existing_tag)
                else:
                    tags.append(Tag(id=tag.id, name=tag.name, created_at=tag.created_at, updated_at=tag.updated_at))
            new_note = Note(
                id=note_vo.id,
                user_id=user_id,
                title=note_vo.title,
                content=note_vo.content,
                memo_date=note_vo.memo_date,
                created_at=note_vo.created_at,
                updated_at=note_vo.updated_at,
                tags=tags
            )
            session.add(new_note)
            session.commit()
                

    def update(self, user_id: str, note_vo: NoteVO) -> NoteVO:
        with SessionLocal() as session:
            self.delete_tags(user_id, note_vo.id)
            note = session.query(Note).filter(Note.user_id == user_id, Note.id == note_vo.id).first()
            if not note:
                raise HTTPException(status_code=404, detail="Note not found")
            note.title = note_vo.title # type: ignore
            note.content = note_vo.content # type: ignore
            note.memo_date = note_vo.memo_date # type: ignore
            tags: list[Tag] = []
            for tag in note_vo.tags:
                existing_tag = session.query(Tag).filter(Tag.name == tag).first()
                if existing_tag:
                    tags.append(existing_tag)
                else:
                    tags.append(Tag(id=tag.id, name=tag.name, created_at=tag.created_at, updated_at=tag.updated_at))
            note.tags = tags
            session.add(note)
            session.commit()

        return NoteVO(**row_to_dict(note))


    def delete(self, user_id: str, id: str):
        with SessionLocal() as session:
            note = session.query(Note).filter(Note.user_id == user_id, Note.id == id).first()
            if not note:
                raise HTTPException(status_code=404, detail="Note not found")
            session.delete(note)
            session.commit()


    def delete_tags(self, user_id: str, id: str):
        with SessionLocal() as session:
            note = session.query(Note).filter(Note.user_id == user_id, Note.id == id).first()
            if not note:
                raise HTTPException(status_code=404, detail="Note not found")
            note.tags = []
            session.add(note)
            session.commit()

            unused_tags = session.query(Tag).filter(~Tag.notes.any()).all()
            for tag in unused_tags:
                session.delete(tag)
            session.commit()


    def get_notes_by_tag_name(
        self, user_id: str, tag_name: str, page: int, items_per_page: int
    ) -> tuple[int, list[NoteVO]]:
        with SessionLocal() as session:
            tag = session.query(Tag).filter_by(name=tag_name).first()
            if not tag:
                return 0, []
            query = session.query(Note).options(joinedload(Note.tags)).filter(Note.user_id == user_id, Note.tags.any(id=tag.id))
            total_count = query.count()
            notes = query.offset((page - 1) * items_per_page).limit(items_per_page).all()
        note_vos = [NoteVO(**row_to_dict(note)) for note in notes]
        return total_count, note_vos
