from typing import Generic, TypeVar, Type, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.inspection import inspect
from dal.models.base import BaseModel

T = TypeVar('T', bound=BaseModel)

class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T], db: Session):
        self.model = model
        self.db = db

    def get_primary_key(self) -> str:
        """动态获取模型的主键字段名称"""
        primary_keys = inspect(self.model).primary_key
        if primary_keys:
            return primary_keys[0].name
        raise Exception("No primary key found for model")

    def get_by_id(self, id_value: int) -> Optional[T]:
        pk = self.get_primary_key()
        return self.db.query(self.model).filter(getattr(self.model, pk) == id_value).first()

    def get_all(self) -> List[T]:
        return self.db.query(self.model).all()

    def create(self, obj_in: dict) -> T:
        obj = self.model(**obj_in)
        self.db.add(obj)
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e
        self.db.refresh(obj)
        return obj

    def update(self, id_value: int, obj_in: dict) -> Optional[T]:
        obj = self.get_by_id(id_value)
        if obj:
            for key, value in obj_in.items():
                setattr(obj, key, value)
            try:
                self.db.commit()
            except Exception as e:
                self.db.rollback()
                raise e
            self.db.refresh(obj)
        return obj

    def delete(self, id_value: int) -> bool:
        obj = self.get_by_id(id_value)
        if obj:
            self.db.delete(obj)
            try:
                self.db.commit()
            except Exception as e:
                self.db.rollback()
                raise e
            return True
        return False
