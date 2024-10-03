import asyncio
import pickle
from aiogram import Router
from filters import *
from aiogram.filters import StateFilter
from contextlib import suppress
from aiogram.types import CallbackQuery
from bot_base import *
from aiogram.exceptions import TelegramBadRequest
from lexicon import *
from aiogram.fsm.context import FSMContext
from bot_instance import FSM_ST, dp, bot_storage_key
from keyboards import *
from random import choice
from external_functions import regular_message, form_WS_string, message_trasher, translates, create_note_collection_keyboard
from stunde import *
from postgres_functions import add_in_spam_list, insert_lan, return_zametki, return_lan


cb_router = Router()

@cb_router.callback_query(LAN_FILTER())
async def set_lan_process(callback: CallbackQuery, state: FSMContext):
    print('24 set_lan_process works')
    user_id = callback.from_user.id
    lan = callback.data
    firts_mal = await return_lan(callback.from_user.id)
    await state.update_data(lan=lan)  #  Добавляю язык в Redis
    await insert_lan(user_id, lan)  #  Добавляю язык в Postgres
    temp_data = users_db[user_id]['bot_ans']
    await message_trasher(user_id, temp_data)
    await callback.message.answer(f'{await regular_message(slovo=lan_trans, lan=lan)}  <b>{lan}</b>')
    if not firts_mal:
        att = await callback.message.answer(text=f'{await regular_message(slovo=spam_offer, lan=lan)}',
                                      reply_markup=spam_kb)
        users_db[user_id]['bot_ans'] = att
    await callback.answer()


@cb_router.callback_query(IT_FILTER())
async def intensive_trainer_auswahlen(callback: CallbackQuery, state:FSMContext):
    """Хэндлер отпраляет клавиатуры со списком уроков"""
    user_id = callback.from_user.id
    lan = await return_lan(user_id)
    a1a2b1 = {'IT_A1':A1, 'IT_A2':A2, 'IT_B1':B1}
    await state.update_data(spam=callback.data)  # Записываю ключ от нужной коллекции
    capture = await regular_message(worschatz_text, lan)
    current_foto_id = a1a2b1[callback.data]
    current_state = await state.get_state()
    if current_state == 'FSM_ST:after_start':
        att = await callback.message.answer_photo(photo=current_foto_id, caption=capture, reply_markup=ws_kb)
    else:
        att = await callback.message.answer_photo(photo=current_foto_id, caption=capture, reply_markup=lernen_kb)
    await asyncio.sleep(20)
    await att.delete()


@cb_router.callback_query(StateFilter(FSM_ST.after_start), STUNDE_FILTER())
async def stunde_worschatz_process(callback: CallbackQuery, state:FSMContext):
    """Хэндлер возвращет превод воршатца целую страницу со словарём урока"""
    print('stunde_worschatz_process works')
    stunde_kit_dict = {'IT_A1':'Intensivtrainer A1', 'IT_A2':'Intensivtrainer A2', 'IT_B1':'Intensivtrainer B1' }
    us_dict = await state.get_data()
    cb_key = us_dict['spam']   #  Получаю колбэк из предыдущего хэндлера
    stunde_collection = it_coll[cb_key]  #  получаю коллекцию уроков
    user_id = callback.from_user.id
    lan = await return_lan(callback.from_user.id)
    current_stunde = stunde_collection[callback.data]  # Вот актуальный урок
    combain_key = cb_key + '_' + callback.data + '_' + lan  # IT_A1_1_ru
    temp_data = users_db[user_id]['bot_ans']
    await message_trasher(user_id, temp_data)
    att = await callback.message.answer(await regular_message(watren_uber, lan))
    users_db[user_id]['bot_ans'] = att
    if lan == 'ru':
        if combain_key not in bot_rus_wortschatz:
            translated_string = await form_WS_string(current_stunde, lan)  # Формирую строку перевода
            bot_rus_wortschatz[combain_key]=translated_string
        else:
            translated_string =  bot_rus_wortschatz[combain_key]
    elif lan == 'uk':
        if combain_key not in bot_rus_wortschatz:
            translated_string = await form_WS_string(current_stunde, lan)
            bot_ukr_wortschatz[combain_key]=translated_string
        else:
            translated_string = bot_ukr_wortschatz[combain_key]

    elif lan == 'de':
        translated_string = await form_WS_string(current_stunde, lan)

    else:
        if combain_key not in bot_anders_wortschatz:
            translated_string = await form_WS_string(current_stunde, lan)
            bot_ukr_wortschatz[combain_key]=translated_string
        else:
            translated_string = bot_ukr_wortschatz[combain_key]

    await callback.message.answer(f'✅  <b>{stunde_kit_dict[cb_key]} Stunde # {callback.data}</b>\n\n{translated_string}\n🟣')  # Здесь выводится список слов
    temp_data = users_db[user_id]['bot_ans']
    await message_trasher(user_id, temp_data)
    await callback.answer()


@cb_router.callback_query(JA_NEIN_FILTER())
async def ja_nein_process(callback: CallbackQuery, state: FSMContext):
    """Хэнделер отправляет клаву ✅ ❌"""
    print('ja_nein_process works ')
    user_id = callback.from_user.id
    lan = await return_lan(user_id)
    temp_data = users_db[user_id]['bot_ans']

    if callback.data == 'ja':
        if temp_data:
            with suppress(TelegramBadRequest):
                await temp_data.delete()
            users_db[user_id]['bot_ans'] = ''
            otvet = await regular_message(erfolgreich_fugen, lan)
            uber_noch = await regular_message(noch, lan)
            # print('JA IF  works')
            att = await callback.message.answer(f'{otvet}\n\n{uber_noch}', reply_markup=ja_nein_kb)
            users_db[user_id]['user_msg'] = att
            await state.update_data(pur='')
        else:  # Срабатывает, когда добавляется ещё одно слово
            # print("JA ELSE works")
            att = await callback.message.answer(f'<b>{await regular_message(deine_wort, lan)}</b>')
            users_db[callback.from_user.id]['bot_ans'] = att

    else:
        us_pur_dict = await state.get_data()
        us_pur = us_pur_dict['pur']
        if us_pur:  # Сейчас юзер говорит что перевод не правильный и ему устанавляивается состоние для редактиврвоания перевода
            att = await callback.message.answer(await regular_message(ricgtig_trans, lan))
            # print('NO if works')
            await state.set_state(FSM_ST.personal_uber)
            users_db[callback.from_user.id]['bot_ans'] = att
        else:  # Если у юзера pur None, значит он уже только что записал юзерский перевод и отказывается продолжать добавлять слова
            await state.set_state(FSM_ST.after_start)
            # print('NO else works')
            temp_data = users_db[user_id]['bot_ans']
            await message_trasher(user_id, temp_data)

            temp_data = users_db[user_id]['user_msg']
            if temp_data:
                with suppress(TelegramBadRequest):
                    await temp_data.delete()
                    users_db[user_id]['user_msg'] = ''
            att = await callback.message.answer(await regular_message(weiter_arbeiten, lan))
            users_db[callback.from_user.id]['bot_ans'] = att
    await callback.answer()


@cb_router.callback_query(StateFilter(FSM_ST.lernen), LERNEN_FILTER())
async def lernen_process(callback: CallbackQuery, state: FSMContext):
    """Хэндлер работает со словарём с вортшатцем урока
    отправляет первое слово и эмоджи клаву 🤷 😊"""
    print('lernen_process works')
    user_id = callback.from_user.id
    us_dict = await state.get_data()
    cb_key = us_dict['spam']  # Это callback от intensive_trainer_auswahlen IT_A1', 'IT_A2' или 'IT_B1'
    if callback.data == 'Wortschatz':
        bot_dict = await dp.storage.get_data(key=bot_storage_key)  # Получаю словарь бота
        using_dict = bot_dict[str(user_id)]  # Получаю словарь юзера
    else:
        lernen_dict = lern_coll[cb_key]  # Получаю один из трёх наборов словарей
        using_dict = lernen_dict[callback.data]  # По ключу получаю словарь
    # lernen_dict = lern_coll[cb_key]  # Получаю словарь вида IT_A1:{}
    # using_dict = lernen_dict[callback.data]  # Получаю словарь deutsch:english
    lan = await return_lan(callback.from_user.id)
    temp_data = users_db[user_id]['bot_ans']
    await message_trasher(user_id, temp_data)

    #  Начинаю выдвать пары ключ-занчение
    begin_tuple = choice(sorted(using_dict.items()))
    deutsch, engl = begin_tuple
    combined_key = lan + '_' + engl  # ru_thing
    if lan == 'ru':
        if combined_key not in bot_rus_collection:
            uber_eng = await translates(engl, lan)
            bot_rus_collection[combined_key]=uber_eng # Перевод на язык юзера
        else:
            uber_eng = bot_rus_collection[combined_key]
    elif lan == 'uk':
        if combined_key not in bot_ukr_collection:
            uber_eng = await translates(engl, lan)
            bot_ukr_collection[combined_key] = uber_eng
        else:
            uber_eng = bot_ukr_collection[combined_key]
    elif lan == 'de':
        uber_eng = deutsch
    else:
        if combined_key not in bot_word_collection:
            uber_eng = await translates(engl, lan)
            bot_word_collection[combined_key] = uber_eng
        else:
            uber_eng = bot_word_collection[combined_key]

    await state.update_data(pur=uber_eng, current_stunde=using_dict)  # Здесь в редис записывается
    att = await callback.message.answer(f'Wissen Sie dieses Wort ?\n\n<b>{begin_tuple[0]}</b>',
                                  reply_markup=weis_kb)
    users_db[user_id]['bot_ans'] = att
    await callback.answer()


@cb_router.callback_query(StateFilter(FSM_ST.schreiben), LERNEN_FILTER())
async def schreiben_process(callback: CallbackQuery, state: FSMContext):
    print('\n\nschreiben_process works\n\n')
    user_id = callback.from_user.id
    us_dict = await state.get_data()
    cb_key = us_dict['spam']
    if callback.data == 'Wortschatz':
        bot_dict = await dp.storage.get_data(key=bot_storage_key)  # Получаю словарь бота
        using_dict = bot_dict[str(user_id)]  # Получаю словарь юзера
    else:
        lernen_dict = lern_coll[cb_key]  # Получаю один из трёх наборов словарей
        using_dict = lernen_dict[callback.data]  # По ключу получаю словарь
    lan = await return_lan(callback.from_user.id)
    temp_data = users_db[user_id]['bot_ans']
    await message_trasher(user_id, temp_data)

    #  Начинаю выдвать пары ключ-занчение
    begin_tuple = choice(sorted(using_dict.items()))
    deutsch, engl = begin_tuple
    combined_key = lan + '_' + engl  # ru_thing
    if lan == 'ru':
        if combined_key not in bot_rus_collection:
            uber_eng = await translates(engl, lan)
            bot_rus_collection[combined_key] = uber_eng  # Перевод на язык юзера
        else:
            uber_eng = bot_rus_collection[combined_key]
    elif lan == 'uk':
        if combined_key not in bot_ukr_collection:
            uber_eng = await translates(engl, lan)
            bot_ukr_collection[combined_key] = uber_eng
        else:
            uber_eng = bot_ukr_collection[combined_key]
    elif lan == 'de':
        pass
    else:
        if combined_key not in bot_word_collection:
            uber_eng = await translates(engl, lan)
            bot_word_collection[combined_key] = uber_eng
        else:
            uber_eng = bot_word_collection[combined_key]
    # uber_eng = await translates(engl, lan)
    # await state.update_data(pur=deutsch, current_stunde=using_dict)
    if lan != 'de' and lan != 'en':
        att = await callback.message.answer(f'Schreiben Sie bitte die Übersetzung des Worts !\n\n<b>{uber_eng}</b>\n\n'
                                            f'<i>English</i> = <b>{engl}</b>',
                                      reply_markup=exit_clava)
        await state.update_data(pur=deutsch, current_stunde=using_dict)
    elif lan == 'en':
        att = await callback.message.answer(f'Schreiben Sie bitte die Übersetzung des Worts !\n\n<b>{uber_eng}</b>\n\n',
                                            reply_markup=exit_clava)
        await state.update_data(pur=deutsch, current_stunde=using_dict)

    else:
        att = await callback.message.answer(f'Schreiben Sie bitte die Übersetzung vom Englisch des Worts !\n\n<b>{engl}</b>\n\n',
                                            reply_markup=exit_clava)
        await state.update_data(pur=(deutsch, engl,), current_stunde=using_dict)
    users_db[user_id]['bot_ans'] = att
    await callback.answer()


@cb_router.callback_query(StateFilter(FSM_ST.lernen), WEIS_NEIN_FILTER())
async def weis_nicht_process(callback: CallbackQuery, state: FSMContext):
    """Хэндрер срабатывает на нажатие эмоджи кнопок 😊 🤷"""
    print('weis_nciht works')
    dict_user = await state.get_data()
    lan = await return_lan(callback.from_user.id)
    using_dict = dict_user['current_stunde']
    previous_word = dict_user['pur']

    ############################# Новое сообщение ###############################################################
    working_tuple = choice(sorted(using_dict.items()))  # Выбираю случайную пару из словаря

    deutsch, engl = working_tuple
    combined_key = lan + '_' + engl
    if lan == 'ru':
        if combined_key not in bot_rus_collection:
            uber_eng = await translates(engl, lan)
            bot_rus_collection[combined_key] = uber_eng
        else:
            uber_eng = bot_rus_collection[combined_key]
    elif lan == 'uk':
        if combined_key not in bot_ukr_collection:
            uber_eng = await translates(engl, lan)
            bot_ukr_collection[combined_key] = uber_eng
        else:
            uber_eng = bot_ukr_collection[combined_key]
    elif lan == 'de':
        uber_eng = engl
    else:
        if combined_key not in bot_word_collection:
            uber_eng = await translates(engl, lan)
            bot_word_collection[combined_key] = uber_eng
        else:
            uber_eng = bot_word_collection[combined_key]
    random_de_en = choice((deutsch, uber_eng,))  # Выбираю либо немецкое слово - либо английский перевод
    if random_de_en == uber_eng:
        gegen_data = deutsch
    else:
        gegen_data = uber_eng
    await state.update_data(pur=gegen_data)   # Записываю на будущий ход следующую пару

    if callback.data == 'nicht':
        if lan != 'de':
            try:
                await callback.message.edit_text(
                    text=f"🔹          <b>Das ist</b> ➡️  "
                         f"<b>{previous_word}</b>\n\n\n"
                         f"Wissen Sie dieses Wort ?\n\n"
                         f"<b>{random_de_en}</b>",
                    reply_markup=weis_kb
                )
            except TelegramBadRequest:
                print('weis_nicht into Exeption')
        else:
            try:
                await callback.message.edit_text(
                    text=f"🔹          <b>Dieses Wort in Deutsch oder in English</b> ➡️  "
                         f"<b>{previous_word}</b>\n\n\n"
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
    user_id = callback.from_user.id
    lan = await return_lan(callback.from_user.id)
    temp_data = users_db[callback.from_user.id]['bot_ans']
    await message_trasher(user_id, temp_data)
    bot_dict = await dp.storage.get_data(key=bot_storage_key)
    using_dict = bot_dict[str(user_id)]
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
    """Хэндлер выводит инлайн кнопки с заметками, если они есть"""
    print('show_note_list works')
    user_id = callback.from_user.id

    # using_dict = bot_server_base[user_id]  # Здесь сохранение заметок происходит в оперативной памяти

    lan = await return_lan(user_id)
    serialised_note_dict = await return_zametki(user_id)
    # print('\n\n\nserialised_note_dict = ',serialised_note_dict)
    if serialised_note_dict:
        note_dict = pickle.loads(serialised_note_dict)  # строковый объект превращаю в питоновский
        s = await regular_message(meine_note, lan)
        att = await callback.message.answer(s,
                                            reply_markup=create_note_collection_keyboard(*note_dict.keys()))
    else:
        s = await regular_message(keine_note, lan)
        att = await callback.message.answer(s)

    temp_data = users_db[callback.from_user.id]['bot_ans']
    await message_trasher(user_id, temp_data)

    users_db[callback.from_user.id]['bot_ans'] = att
    await callback.answer()


@cb_router.callback_query(StateFilter(FSM_ST.after_start), ADD_NEW_NOTE_FILTER())
async def add_new_note(callback: CallbackQuery, state: FSMContext):
    """Хэндлер выводит сообщение с просьбой написать название личной заметки"""
    print('add_new_note works')
    lan = await return_lan(callback.from_user.id)
    s = await regular_message(add_note, lan)
    att = await callback.message.answer(s)
    temp_data = users_db[callback.from_user.id]['bot_ans']
    await message_trasher(callback.from_user.id, temp_data)
    users_db[callback.from_user.id]['bot_ans'] = att
    await state.set_state(FSM_ST.add_note_1)
    await callback.answer()


@cb_router.callback_query(StateFilter(FSM_ST.after_start), SPAM_FILTER())
async def spam_approve(callback: CallbackQuery, state: FSMContext):
    print('spam_approve works')
    lan = await return_lan(callback.from_user.id)
    if callback.data == 'spam':
        await state.update_data(spam='yes')
        await add_in_spam_list(callback.from_user.id)
        stroka = await regular_message(danke, lan)
        await callback.message.answer(stroka)
    temp_data = users_db[callback.from_user.id]['bot_ans']
    await message_trasher(callback.from_user.id, temp_data)
    await callback.answer()


@cb_router.callback_query(StateFilter(FSM_ST.after_start))
async def show_note(callback: CallbackQuery):
    print('show_note works')
    user_id = callback.from_user.id
    serialised_note_dict = await return_zametki(user_id)
    note_dict = pickle.loads(serialised_note_dict)
    # print('note_dict = ', note_dict)
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
    await message_trasher(user_id, temp_data)
    await callback.answer()

