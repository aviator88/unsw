from datetime import datetime

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Column, Integer, Text, Boolean


class Base(DeclarativeBase):
    pass

class Wallet(Base):
    __tablename__ = 'wallet'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    private_key: Mapped[str] = mapped_column(unique=True, index=True)
    address: Mapped[str] = mapped_column(unique=True)
    proxy_pk: Mapped[str]
    proxy_address: Mapped[str]
    google_acc: Mapped[str]
    google_pass: Mapped[str]
    next_farming_time: Mapped[datetime | None]
    next_unichain_time: Mapped[datetime | None]
    proxy: Mapped[str]
    useragent: Mapped[str]
   

    def __str__(self):
        return f'{self.name}: {self.address}'

    def __repr__(self):
        return f'{self.name}: {self.address}'
