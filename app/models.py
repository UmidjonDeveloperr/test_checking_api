from sqlalchemy import Column, Integer, String, Float, Table, MetaData, DateTime, func
from .database import Base, engine


# Standard tables
class Test(Base):
    __tablename__ = "tests"

    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(String, unique=True, index=True)
    subject1 = Column(String)
    subject2 = Column(String)
    status = Column(String(10), default='inactive', nullable=False)
    answers = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


# Function to create dynamic tables
async def create_dynamic_table(test_id: str):
    table_name = f"{test_id}_answers"
    metadata = MetaData()

    Table(
        table_name,
        metadata,
        Column("id", Integer, primary_key=True),
        Column("telegram_id", String, nullable=False),
        Column("first_name", String),
        Column("last_name", String),
        Column("middle_name", String),
        Column("region", String),
        Column("answers", String),
        Column("score", Float)
    )

    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

    return table_name