import datetime

from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.models.datasource import DataSource
from app.schemas.datasource import DataSourceItem, DataSourceCreate, DataSourceUpdate
from app.crud.base import CRUDBase


class CRUDDataSource(CRUDBase[DataSource, DataSourceCreate, DataSourceUpdate]):
    def create_with_owner(
        self, db_session: Session, *, obj_in: DataSourceCreate, created_by: int
    ) -> DataSourceItem:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data,
                            created_at=datetime.datetime.now(),
                            updated_at=datetime.datetime.now(),
                            created_by=created_by)
        db_session.add(db_obj)
        db_session.commit()
        db_session.refresh(db_obj)
        return db_obj

    def get_multi_by_owner(
        self, db_session: Session, *, create_by: int, skip=0, limit=100
    ) -> List[DataSourceItem]:
        return (
            db_session.query(self.model)
            .filter(DataSource.create_by == create_by)
            .offset(skip)
            .limit(limit)
            .all()
        )


data_source = CRUDDataSource(DataSource)
