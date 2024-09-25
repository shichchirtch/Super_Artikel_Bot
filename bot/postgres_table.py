import fake_useragent
from sqlalchemy import Integer, BigInteger, String, ARRAY
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=True)

session_marker = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

metadata = Base.metadata

class User(Base):

    __tablename__ = 'users'
    index: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    tg_us_id: Mapped[int] = mapped_column(BigInteger) # tg user id
    user_name: Mapped[str] = mapped_column(String(200), nullable=False)
    der: Mapped[str] = mapped_column(String, default='<b>DER</b>\n', nullable=True)
    die: Mapped[str] = mapped_column(String, default='<b>DIE</b>\n', nullable=True)
    das: Mapped[str] = mapped_column(String, default='<b>DAS</b>\n', nullable=True)
    verb: Mapped[str] = mapped_column(String, default='<b>VERB</b>\n', nullable=True)
    adj: Mapped[str] = mapped_column(String, default='<b>ADJ</b>\n', nullable=True)

class Admin(Base):

    __tablename__ = 'admin'
    index: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    tg_us_id: Mapped[int] = mapped_column(BigInteger) # tg user id
    spielers_list: Mapped[list] = mapped_column(ARRAY(BigInteger), default=[], nullable=True)
    spam_list: Mapped[list] = mapped_column(ARRAY(BigInteger), default=[], nullable=True)

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


user = fake_useragent.UserAgent().random

# site_url = 'https://der-artikel.de/'

site_url = 'https://www.woerter.ru/?w='

site_headers = {
    'Accept': '*/*',
    'User-Agent': user}