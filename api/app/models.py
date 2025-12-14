from sqlalchemy import Table, Column, Integer, String, Text, MetaData

metadata = MetaData()

items = Table(
    "items",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(200), nullable=False),
    Column("description", Text, nullable=True),
)
