import asyncio
from aiogram import Router
from filters import *
from aiogram.filters import StateFilter
from contextlib import suppress
from aiogram.types import CallbackQuery
from bot_base import users_db
from aiogram.exceptions import TelegramBadRequest
from lexicon import *
from aiogram.fsm.context import FSMContext
from bot_instance import FSM_ST
from keyboards import *
from random import choice
from external_functions import translates, create_note_collection_keyboard
from stunde import *
from postgres_functions import add_in_spam_list

lernen_dict = {'one':erste_stunde, 'two':zweite_stunde, 'three':dritte_stunde, }


cb_router = Router()

@cb_router.callback_query(LAN_FILTER())
async def set_lan_process(callback: CallbackQuery, state: FSMContext):
    print('set_lan_process works')
    user_id = callback.from_user.id
    lan = callback.data
    us_dict = await state.get_data()
    firts_mal = us_dict['lan']
    await state.update_data(lan=callback.data)
    temp_data = users_db[user_id]['bot_ans']
    if temp_data:
        with suppress(TelegramBadRequest):
            await temp_data.delete()
            users_db[user_id]['bot_ans'] = ''
    await callback.message.answer(f'{await translates(slovo=lan_trans, lan=lan)}  <b>{lan}</b>')
    if not firts_mal:
        att = await callback.message.answer(text=f'{await translates(slovo=spam_offer, lan=lan)}',
                                      reply_markup=spam_kb)
        users_db[user_id]['bot_ans'] = att
    await callback.answer()


@cb_router.callback_query(STUNDE_FILTER())
async def stunde_worschatz_process(callback: CallbackQuery, state: FSMContext):
    print('stunde_worschatz_process works')
    stunde_collection = {'1':erste_stunde}
    user_id = callback.from_user.id
    dict_lan = await state.get_data()
    lan = dict_lan['lan']
    current_stunde = stunde_collection[callback.data]
    temp_data = users_db[user_id]['bot_ans']
    if temp_data:
        with suppress(TelegramBadRequest):
            await temp_data.delete()
            users_db[user_id]['bot_ans'] = ''
    att = await callback.message.answer(await translates(watren_uber, lan))
    users_db[user_id]['bot_ans'] = att
    form_str = ''
    for k, v in current_stunde.items():
        try:
            perevod = await translates(v, lan)
            form_str+=f'<b>{k}</b>  {perevod}\n'
        except Exception:
            print(f'Exception for {k}')
        await asyncio.sleep(0.15)

    await callback.message.answer(form_str)
    temp_data = users_db[user_id]['bot_ans']
    if temp_data:
        with suppress(TelegramBadRequest):
            await temp_data.delete()
            users_db[user_id]['bot_ans'] = ''
    await callback.answer()


@cb_router.callback_query(JA_NEIN_FILTER())
async def ja_nein_process(callback: CallbackQuery, state: FSMContext):
    print('ja_nein_process works')
    user_id = callback.from_user.id
    dict_lan = await state.get_data()
    lan = dict_lan['lan']
    temp_data = users_db[user_id]['bot_ans']

    if callback.data == 'ja':

        if temp_data:
            with suppress(TelegramBadRequest):
                await temp_data.delete()
            users_db[user_id]['bot_ans'] = '' #
            otvet = await translates(erfolgreich_fugen, lan)
            uber_noch = await translates(noch, lan)
            print('JA IF  works')
            att = await callback.message.answer(f'{otvet}\n\n{uber_noch}', reply_markup=ja_nein_kb)
            users_db[user_id]['user_msg'] = att
            await state.update_data(pur='')
        else:  # Срабатывает, когда добавляется ещё одно слово
            print("JA ELSE works")
            att = await callback.message.answer(f'<b>{await translates(deine_wort, lan)}</b>')
            users_db[callback.from_user.id]['bot_ans'] = att

    else:
        us_pur_dict = await state.get_data()
        us_pur = us_pur_dict['pur']
        if us_pur:  # Сейчас юзер говорит что перевод не правильный и ему устанавляивается состоние для редактиврвоания перевода
            att = await callback.message.answer(ricgtig_trans)
            print('NO if works')
            await state.set_state(FSM_ST.personal_uber)
            users_db[callback.from_user.id]['bot_ans'] = att
        else:  # Если у юзера pur None, значит он уже только что записал юзерский перевод и отказывается продолжать добавлять слова
            await state.set_state(FSM_ST.after_start)
            print('NO else works')
            temp_data = users_db[user_id]['bot_ans']
            if temp_data:
                with suppress(TelegramBadRequest):
                    await temp_data.delete()
                    users_db[user_id]['bot_ans'] = ''

            temp_data = users_db[user_id]['user_msg']
            if temp_data:
                with suppress(TelegramBadRequest):
                    await temp_data.delete()
                    users_db[user_id]['user_msg'] = ''
            att = await callback.message.answer(await translates(weiter_arbeiten, lan))
            users_db[callback.from_user.id]['bot_ans'] = att
    await callback.answer()


@cb_router.callback_query(StateFilter(FSM_ST.lernen), LERNEN_FILTER())
async def lernen_process(callback: CallbackQuery, state: FSMContext):
    print('lernen_process works')
    user_id = callback.from_user.id
    using_dict = lernen_dict[callback.data]
    dict_user = await state.get_data()
    lan = dict_user['lan']
    temp_data = users_db[user_id]['bot_ans']
    if temp_data:
        with suppress(TelegramBadRequest):
            await temp_data.delete()
            users_db[user_id]['bot_ans'] = ''

    #  Начинаю выдвать пары ключ-занчение
    begin_tuple = choice(sorted(using_dict.items()))
    deutsch, engl = begin_tuple
    uber_eng = await translates(engl, lan)
    remodify_begin_tuple = (deutsch, uber_eng,)
    await state.update_data(pur=remodify_begin_tuple, current_stunde=using_dict)
    att = await callback.message.answer(f'Wissen Sie dieses Wort ?\n\n<b>{begin_tuple[0]}</b>',
                                  reply_markup=weis_kb)
    users_db[user_id]['bot_ans'] = att
    await callback.answer()


@cb_router.callback_query(StateFilter(FSM_ST.lernen), WEIS_NEIN_FILTER())
async def weis_nicht_process(callback: CallbackQuery, state: FSMContext):
    print('weis_nciht works')
    dict_user = await state.get_data()
    lan = dict_user['lan']
    using_dict = dict_user['current_stunde']
    previous_word = dict_user['pur']
    print('139  previous wort = ', previous_word)
    if previous_word[1] in using_dict.values():
        print('previous wort = ', previous_word)
        andere = previous_word[0]
    else:
        andere = await translates(previous_word[1], lan)

    working_tuple = choice(sorted(using_dict.items()))  # Выбираю случайную пару из словаря


    deutsch, engl = working_tuple
    uber_engl = await translates(engl, lan)

    random_de_en = choice((deutsch, uber_engl,))  #Выбираю либо немецкое слово - либо английский перевод


    if random_de_en == uber_engl:
        remodifyid_tuple = (deutsch, engl,)
    else:
        remodifyid_tuple = (deutsch, uber_engl,)
    await state.update_data(pur=remodifyid_tuple)

    if callback.data == 'nicht':
        try:
            await callback.message.edit_text(
                text=f"🔹          <b>Das ist</b> ➡️  "
                     f"<b>{andere}</b>\n\n\n"
                     f"Wissen Sie dieses Wort ?\n\n"
                     f"<b>{random_de_en}</b>",
                reply_markup=weis_kb
            )
        except TelegramBadRequest:
            print('weis_nicht into Exeption')

    else:
        try:
            await callback.message.edit_text(
                text=f"Wissen Sie dieses Wort ?\n\n"
                     f"<b>{random_de_en}</b>",
                reply_markup=weis_kb
            )
        except TelegramBadRequest:
            print('weis into Exeption, wenn Ich WEISS')

    await callback.answer()


@cb_router.callback_query(StateFilter(FSM_ST.after_start), PRIVAT_WORTSCHATZ_FILTER())
async def show_private_wortschatz(callback: CallbackQuery, state: FSMContext):
    print('show_private works')
    dict_user = await state.get_data()
    using_dict = dict_user['wortschatz']
    lan = dict_user['lan']
    temp_data = users_db[callback.from_user.id]['bot_ans']
    if temp_data:
        with suppress(TelegramBadRequest):
            await temp_data.delete()
            users_db[callback.from_user.id]['bot_ans'] = ''
    if using_dict:
        s = ''
        for k, v in using_dict.items():
            s+=f'<b>{k}</b>  -  {v}\n'
        stroka = f'📕  <b>Meine Wortschatz</b>\n\n{s}\n\n🟢'
        await callback.message.answer(stroka)
    else:
        s = await translates(keine_wortschatz, lan)
        att = await callback.message.answer(s)
        await asyncio.sleep(3)
        await att.delete()
    await callback.answer()


@cb_router.callback_query(StateFilter(FSM_ST.after_start), SHOW_NOTE_FILTER())
async def show_note_list_wortschatz(callback: CallbackQuery, state: FSMContext):
    print('show_note_list works')
    dict_user = await state.get_data()
    using_dict = dict_user['note']
    lan = dict_user['lan']
    if using_dict:
        s = await translates(meine_note, lan)
        att = await callback.message.answer(s,
                                            reply_markup=create_note_collection_keyboard(*using_dict.keys()))
    else:
        s = await translates(keine_note, lan)
        att = await callback.message.answer(s)

    temp_data = users_db[callback.from_user.id]['bot_ans']
    if temp_data:
        with suppress(TelegramBadRequest):
            await temp_data.delete()
            users_db[callback.from_user.id]['bot_ans'] = ''

    users_db[callback.from_user.id]['bot_ans'] = att
    await callback.answer()



@cb_router.callback_query(StateFilter(FSM_ST.after_start), ADD_NEW_NOTE_FILTER())
async def add_new_note(callback: CallbackQuery, state: FSMContext):
    print('add_new_note works')
    dict_user = await state.get_data()
    lan = dict_user['lan']
    s = await translates(add_note, lan)
    att = await callback.message.answer(s)
    temp_data = users_db[callback.from_user.id]['bot_ans']
    if temp_data:
        with suppress(TelegramBadRequest):
            await temp_data.delete()
            users_db[callback.from_user.id]['bot_ans'] = ''
    users_db[callback.from_user.id]['bot_ans'] = att
    await state.set_state(FSM_ST.add_note_1)
    await callback.answer()


@cb_router.callback_query(StateFilter(FSM_ST.after_start), SPAM_FILTER())
async def spam_approve(callback: CallbackQuery, state: FSMContext):
    print('spam_approve works')
    dict_user = await state.get_data()
    lan = dict_user['lan']
    if callback.data == 'spam':
        await state.update_data(spam='yes')
        await add_in_spam_list(callback.from_user.id)
        stroka = await translates(danke, lan)
        await callback.message.answer(stroka)
    temp_data = users_db[callback.from_user.id]['bot_ans']
    if temp_data:
        with suppress(TelegramBadRequest):
            await temp_data.delete()
            users_db[callback.from_user.id]['bot_ans'] = ''
    await callback.answer()


@cb_router.callback_query(StateFilter(FSM_ST.after_start))
async def show_note(callback: CallbackQuery, state: FSMContext):
    print('show_note works')
    dict_user = await state.get_data()
    note_dict = dict_user['note']
    note_key = callback.data   # получаю ключ - названием заметки
    needed_note = note_dict[note_key]  # получаю ЭК Note
    foto_note = needed_note.foto   # Получаю фото
    description = needed_note.description   #  Получаю описание
    if foto_note:
        await callback.message.answer_photo(
            photo=foto_note, caption=description,
            reply_markup=None)
    else:
        await callback.message.answer(text=description,
            reply_markup=None)
    temp_data = users_db[callback.from_user.id]['bot_ans']
    if temp_data:
        with suppress(TelegramBadRequest):
            await temp_data.delete()
            users_db[callback.from_user.id]['bot_ans'] = ''
    await callback.answer()

