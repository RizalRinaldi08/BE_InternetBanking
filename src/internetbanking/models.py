import datetime
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column,relationship
from sqlalchemy import ForeignKey, MetaData, Column, Enum
from typing import Literal, get_args
import enum
from sqlalchemy.ext.declarative import declarative_base
from typing import List
from sqlalchemy.sql import func
#untuk ORM agar terbaca menjadi ORM

metadata = MetaData()
Base = declarative_base(metadata=metadata)


class TransactionStatus(str, enum.Enum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"
    TRANSFER = "TRANSFER"

class User(Base):
    __tablename__ = 'tb_user'

    id_user:Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nama:Mapped[str] = mapped_column(nullable=False)
    username:Mapped[str] = mapped_column(nullable=False)
    password:Mapped[str] = mapped_column(nullable=False)
    alamat:Mapped[str] = mapped_column(nullable=False)
    hp:Mapped[str] = mapped_column( nullable=False)
    created_at:Mapped[datetime] = mapped_column(server_default=func.now())
    isAdmin:Mapped[bool] = mapped_column(default=False, nullable=True)
    
    #relation to Account
    accounts:Mapped[List["Account"]]=relationship('Account', backref='user', lazy=True)

    # accounts:Mapped[List["Account"]] = relationship('Account',back_populates='user', lazy='select')

    def __repr__(self) -> str:
        return f'<User nama={self.nama}>'

class Branch(Base):
    __tablename__ ='tb_branch'

    id_branch:Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    city:Mapped[str] = mapped_column(nullable=False)
    address:Mapped[str] = mapped_column(nullable=False)
    # user:Mapped["User"] = mapped_column(ForeignKey('tb_user.id_user'),nullable=False)
    # accounts:Mapped[List["Account"]] = relationship('Account', foreign_keys=[])
    accounts:Mapped[List["Account"]] = relationship('Account', backref='branchuser', lazy=True)
    created_at:Mapped[datetime] = mapped_column(server_default=func.now())


    def __repr__(self) -> str:
        return f'<Branch city={self.city}>'

class Account(Base):
    __tablename__ = 'tb_account'

    id_account:Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    account_name:Mapped[str] = mapped_column(nullable=False)
    balance:Mapped[float] = mapped_column(nullable=False)
    is_active:Mapped[bool] = mapped_column(default=True)
    id_user:Mapped["User"] = mapped_column(ForeignKey('tb_user.id_user'), nullable=False)
    id_branch:Mapped["Branch"] = mapped_column(ForeignKey('tb_branch.id_branch'),nullable=False)
    created_at:Mapped[datetime] = mapped_column(server_default=func.now())
    
    # transactions:Mapped[List["Transaction"]] = relationship('Transaction', backref="account", lazy="select")
    def __repr__(self) -> str:
        return f'<Account username={self.account_name}>'
    

class Transaction(Base):
    __tablename__ = 'tb_transaction'

    id_transaction:Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    from_account_id:Mapped[int] = mapped_column(ForeignKey('tb_account.id_account'))
    to_account_id:Mapped[int] = mapped_column(ForeignKey('tb_account.id_account'))
    type_transaction:Mapped[TransactionStatus] = mapped_column(Enum(
            TransactionStatus,
            create_constrain=True,
            validate_strings=True,
        ))
    amount:Mapped[float] = mapped_column(nullable=False)
    created_at:Mapped[datetime] = mapped_column(server_default=func.now())
    # from_account:Mapped["Account"] = mapped_column(ForeignKey('tb_account.id_account'),
    # nullable=False)
    # to_account:Mapped["Account"] = mapped_column(ForeignKey('tb_account.id_account'),
    # nullable=False)

    def __repr__(self) -> str:
        return f'<Transaction id_transaction={self.id_transaction}>'