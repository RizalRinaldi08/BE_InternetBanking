import datetime
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column,relationship
from sqlalchemy import ForeignKey, MetaData, Column, Enum, String
from typing import Literal, get_args
import enum
from sqlalchemy.ext.declarative import declarative_base
from typing import List
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
#untuk ORM agar terbaca menjadi ORM

metadata = MetaData()
Base = declarative_base(metadata=metadata)

class TransactionStatus(str, enum.Enum):
    debit = "debit"
    credit = "credit"

class User(Base):
    __tablename__ = 'tb_user'

    id_user:Mapped[uuid4] = mapped_column(UUID(as_uuid=True),default=uuid4, primary_key=True)
    name:Mapped[str] = mapped_column(nullable=False)
    username:Mapped[str] = mapped_column(unique=True,nullable=False)
    password:Mapped[str] = mapped_column(nullable=False)
    address:Mapped[str] = mapped_column(nullable=False)
    phone_number:Mapped[str] = mapped_column( nullable=False)
    created_at:Mapped[datetime] = mapped_column(server_default=func.now())
    is_admin:Mapped[bool] = mapped_column(default=False, nullable=False)
    
    #relation to Account
    accounts:Mapped[List["Account"]]=relationship('Account', backref='user', lazy=True)

    # accounts:Mapped[List["Account"]] = relationship('Account',back_populates='user', lazy='select')

    def __repr__(self) -> str:
        return f'<User name={self.name}>'

class Branch(Base):
    __tablename__ ='tb_branch'

    id_branch:Mapped[uuid4] = mapped_column(UUID(as_uuid=True),primary_key=True, default=uuid4)
    city:Mapped[str] = mapped_column(nullable=False)
    branch_name:Mapped[str] = mapped_column(nullable=False)
    address:Mapped[str] = mapped_column(nullable=False)
    branch_code:Mapped[str] = mapped_column(String(4),nullable=False, unique=True)
    
    # user:Mapped["User"] = mapped_column(ForeignKey('tb_user.id_user'),nullable=False)
    # accounts:Mapped[List["Account"]] = relationship('Account', foreign_keys=[])
    accounts:Mapped[List["Account"]] = relationship('Account', backref='branchuser', lazy=True)
    created_at:Mapped[datetime] = mapped_column(server_default=func.now())


    def __repr__(self) -> str:
        return f'<Branch city={self.branch_name}>'

class Account(Base):
    __tablename__ = 'tb_account'

    id_account:Mapped[uuid4] = mapped_column(UUID(as_uuid=True), default=uuid4)
    #  id_transaction:Mapped[uuid4] = mapped_column(UUID(as_uuid=True),primary_key=True, default=uuid4)
    account_number:Mapped[str] = mapped_column(String(10),unique=True,nullable=False, primary_key=True)
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

    id_transaction:Mapped[uuid4] = mapped_column(UUID(as_uuid=True),primary_key=True, default=uuid4)
    #  id_user:Mapped[uuid4] = mapped_column(UUID(as_uuid=True),primary_key=True, autoincrement=True,default=uuid4)
    account_number:Mapped[str] = mapped_column(ForeignKey('tb_account.account_number'), nullable=True)
    # to_account_number:Mapped[str] = mapped_column(ForeignKey('tb_account.account_number'), nullable=True)
    type_transaction:Mapped[TransactionStatus] = mapped_column(Enum(
            TransactionStatus,
            create_constrain=True,
            validate_strings=True,
        ))
    amount:Mapped[float] = mapped_column(nullable=False)
    notes:Mapped[str] = mapped_column(nullable=True)
    created_at:Mapped[datetime] = mapped_column(server_default=func.now())
    # from_account:Mapped["Account"] = mapped_column(ForeignKey('tb_account.id_account'),
    # nullable=False)
    # to_account:Mapped["Account"] = mapped_column(ForeignKey('tb_account.id_account'),
    # nullable=False)

    def __repr__(self) -> str:
        return f'<Transaction id_transaction={self.id_transaction}>'