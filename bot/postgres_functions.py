from postgres_table import session_marker, User, Admin
from sqlalchemy import select

async def insert_new_user_in_table(user_tg_id: int, name: str):
    async with session_marker() as session:
        query = await session.execute(select(User).filter(User.tg_us_id == user_tg_id))
        needed_data = query.scalar()
        if not needed_data:
            print('Now we are into first function')
            new_us = User(tg_us_id=user_tg_id, user_name=name)
            session.add(new_us)
            await session.commit()

async def insert_new_user_in_admin_table(user_tg_id):
    async with session_marker() as session:
        query = await session.execute(select(Admin).filter(Admin.tg_us_id == user_tg_id))
        needed_data = query.scalar()
        if not needed_data:
            print('Now we are into first function admin table')
            new_us = Admin(tg_us_id=user_tg_id)
            session.add(new_us)
            await session.commit()

async def check_user_in_table(user_tg_id:int):
    """Функция проверяет есть ли юзер в БД"""
    async with session_marker() as session:
        print("Work check_user Function")
        query = await session.execute(select(User).filter(User.tg_us_id == user_tg_id))
        data = query.one_or_none()
        return data

async def insert_lan(user_id:int, lan:str):
    async with session_marker() as session:
        query = await session.execute(select(User).filter(User.tg_us_id == user_id))
        needed_data = query.scalar()
        needed_data.lan = lan
        await session.commit()


async def insert_neue_wort_in_der(user_id:int, neue_wort):
    async with session_marker() as session:
        query = await session.execute(select(User).filter(User.tg_us_id == user_id))
        needed_data = query.scalar()
        previous = needed_data.der
        updated_str = previous+'\n'+ neue_wort
        needed_data.der = updated_str
        await session.commit()

async def insert_neue_wort_in_die(user_id:int, neue_wort):
    async with session_marker() as session:
        query = await session.execute(select(User).filter(User.tg_us_id == user_id))
        needed_data = query.scalar()
        previous = needed_data.die
        updated_str = previous+'\n'+ neue_wort
        needed_data.die = updated_str
        await session.commit()

async def insert_neue_wort_in_das(user_id:int, neue_wort):
    async with session_marker() as session:
        query = await session.execute(select(User).filter(User.tg_us_id == user_id))
        needed_data = query.scalar()
        previous = needed_data.das
        updated_str = previous+'\n'+ neue_wort
        needed_data.das = updated_str
        await session.commit()

async def insert_neue_wort_in_verb(user_id:int, neue_wort):
    async with session_marker() as session:
        print('insert_neue_wort_in_verb\n\n')
        query = await session.execute(select(User).filter(User.tg_us_id == user_id))
        needed_data = query.scalar()
        previous = needed_data.verb
        updated_str = previous+'\n'+ neue_wort
        needed_data.verb = updated_str
        await session.commit()

async def insert_neue_wort_in_adj(user_id:int, neue_wort):
    async with session_marker() as session:
        print('insert_neue_wort_in_adj\n\n')
        query = await session.execute(select(User).filter(User.tg_us_id == user_id))
        needed_data = query.scalar()
        previous = needed_data.adj
        updated_str = previous+'\n'+ neue_wort
        needed_data.adj = updated_str
        await session.commit()

async def insert_serialised_note(user_id:int, zametka):
    async with session_marker() as session:
        print('insert_serialised_note\n\n')
        query = await session.execute(select(User).filter(User.tg_us_id == user_id))
        needed_data = query.scalar()
        needed_data.zametki = zametka
        await session.commit()

async def return_lan(user_id:int):
    async with session_marker() as session:
        query = await session.execute(select(User).filter(User.tg_us_id == user_id))
        needed_data = query.scalar()
        return needed_data.lan

async def return_der_string(user_id:int):
    async with session_marker() as session:
        query = await session.execute(select(User).filter(User.tg_us_id == user_id))
        needed_data = query.scalar()
        return needed_data.der


async def return_die_string(user_id:int):
    async with session_marker() as session:
        query = await session.execute(select(User).filter(User.tg_us_id == user_id))
        needed_data = query.scalar()
        return needed_data.die

async def return_das_string(user_id:int):
    async with session_marker() as session:
        query = await session.execute(select(User).filter(User.tg_us_id == user_id))
        needed_data = query.scalar()
        return needed_data.das

async def return_verb_string(user_id:int):
    async with session_marker() as session:
        query = await session.execute(select(User).filter(User.tg_us_id == user_id))
        needed_data = query.scalar()
        return needed_data.verb

async def return_adj_string(user_id:int):
    async with session_marker() as session:
        query = await session.execute(select(User).filter(User.tg_us_id == user_id))
        needed_data = query.scalar()
        return needed_data.adj

async def return_zametki(user_id:int):
    async with session_marker() as session:
        query = await session.execute(select(User).filter(User.tg_us_id == user_id))
        needed_data = query.scalar()
        return needed_data.zametki


async def add_in_list(user_tg_id: int):
    async with session_marker() as session:
        query = await session.execute(select(Admin).filter(Admin.tg_us_id == 6685637602))
        needed_data = query.scalar()
        print('Add new spieler in admin list')
        admin_list = needed_data.spielers_list
        print('admin_list = ', admin_list)
        updated_list = admin_list+[user_tg_id]
        needed_data.spielers_list = updated_list
        await session.commit()

async def add_in_spam_list(user_tg_id: int):
    async with session_marker() as session:
        query = await session.execute(select(Admin).filter(Admin.tg_us_id == 6685637602))
        needed_data = query.scalar()
        print('Add new spieler in spam list')
        admin_list = needed_data.spam_list
        updated_list = admin_list+[user_tg_id]
        needed_data.spam_list = updated_list
        await session.commit()

async def return_quantity_users():
    async with session_marker() as session:
        query = await session.execute(select(Admin).filter(Admin.tg_us_id == 6685637602))
        needed_data = query.scalar()
        return needed_data.spielers_list

async def return_spam_users():
    async with session_marker() as session:
        query = await session.execute(select(Admin).filter(Admin.tg_us_id == 6685637602))
        needed_data = query.scalar()
        return needed_data.spam_list