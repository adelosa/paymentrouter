from sqlalchemy import Column, Integer, Date

from paymentrouter.model import Base


class SystemControl(Base):
    __tablename__ = 'syscontrol'

    system_id = Column(Integer, primary_key=True)
    effective_date = Column(Date)
