from pydantic import BaseModel


# Shared properties
class DataSourceBase(BaseModel):
    name: str
    description: str
    create_by: int


class DataSourceCreate(DataSourceBase):
    host: str
    port: str
    source_type: int
    user: str
    password: str
    kwargs: dict = None


class DataSourceUpdate(DataSourceCreate):
    pass


class DataSourceItem(DataSourceBase):
    id: int
    host: str
    port: int
    source_type: int

    class Config:
        orm_mode = True


if __name__ == '__main__':
    print(DataSourceBase.Config)
    print(DataSourceItem.Config)