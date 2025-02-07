from sqlalchemy import String, DECIMAL
from sqlalchemy.orm import Mapped
from sqlalchemy.testing.schema import mapped_column

from db import Base
from db.utils import CreatedModel


# ctrl + space*2
class Product(CreatedModel):
    __tablename__= "products"
    name : Mapped[str] = mapped_column(String(55), nullable=True)
    price : Mapped[float] = mapped_column(DECIMAL(9,2))



metadata = Base.metadata