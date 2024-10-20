from aiogram import Router, F, html
import asyncio
import pickle
from bs4 import BeautifulSoup as bs
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import CommandStart, Command, StateFilter
import requests
from aiogram.fsm.context import FSMContext
from postgres_table import site_url, site_headers
from keyboards import *
from aiogram.enums import ParseMode
from filters import (PRE_START, IS_LETTER, IS_ADMIN, WORD_ACCEPT,
                     EXCLUDE_COMMAND, EXCLUDE_COMMAND_MIT_EXIT, STOP_EMODJI)
from lexicon import *
from postgres_functions import *
from bot_instance import FSM_ST, bot_storage_key, dp
from bot_base import *
from copy import deepcopy
from string import ascii_letters
from external_functions import translates, translates_in_english, regular_message, message_trasher, us_message_trasher
from note_class import User_Note
from random import choice
from stunde import *
from aiogram.exceptions import TelegramForbiddenError


ch_router = Router()

# @ch_router.message(F.video)
# async def video_id_geber_messages(message: Message):
#     data = message.video.file_id
#     print(data)


# @ch_router.message(F.photo)
# async def foto_id_geber_messages(message: Message):
#     data = message.photo[-1].file_id
#     print(data)

@ch_router.message(~StateFilter(FSM_ST.add_note_2), ~F.text)
async def delete_not_text_type_messages(message: Message):
    await message.delete()


@ch_router.message(CommandStart())
async def process_start_command(message: Message, state: FSMContext):
    user_name = message.from_user.first_name
    user_id = message.from_user.id
    data = await check_user_in_table(user_id)
    if not data:
        await insert_new_user_in_table(user_id, user_name)
        users_db[message.from_user.id] = deepcopy(user_dict)
        await insert_new_user_in_admin_table(user_id)
        await state.set_state(FSM_ST.after_start)
        await state.set_data(
            {'pur': '',  # personal ubersetzung темповое значение своего перевода
             'current_stunde': '',  # Для изучения словарного запаса урока
             'spam': ''  # Согласен или нет получать уведомления от бота
             })
        await message.answer(text=f'{html.bold(html.quote(user_name))}, '
                                  f'{start}',
                             parse_mode=ParseMode.HTML,
                             reply_markup=ReplyKeyboardRemove())
        att = await message.answer(text='Wählen Sie die Sprache aus, die Sie sprechen',
                                   reply_markup=lan_kb)
        users_db[user_id]['bot_ans'] = att
        bot_dict = await dp.storage.get_data(key=bot_storage_key)

        bot_dict[user_id] = {}  # Создаю словарь с ключом - tg_us_id
        await dp.storage.set_data(key=bot_storage_key, data=bot_dict)
        await asyncio.sleep(0.5)
        await add_in_list(user_id)  # Кто стартанул бота - добавляю в список админа
        bot_server_base[user_id] = {}  # Создаю словарь юзера
        test_state = await state.get_state()
        print('test state = ', test_state)
    else:
        await state.set_state(FSM_ST.after_start)
        await state.set_data(
            {'pur': '',  # personal ubersetzung темповое значение своего перевода
             'current_stunde': '',  # Для изучекния словарного запаса урока
             'spam': ''  # Согласен или нет получать уведомления от бота
             })
        users_db[message.from_user.id] = deepcopy(user_dict)
        lan = await return_lan(user_id)
        restart_msg = await regular_message(bot_was_restarted, lan)

        await message.answer(restart_msg)
        await message.delete()


@ch_router.message(PRE_START())
async def before_start(message: Message):
    prestart_ant = await message.answer(text='Klicken auf <b>start</b> !',
                                        reply_markup=pre_start_clava)
    await message.delete()
    await asyncio.sleep(3)
    await prestart_ant.delete()


@ch_router.message(Command('set_lan'), StateFilter(FSM_ST.after_start))
async def reselect_lan(message: Message):
    att = await message.answer(text='Wählen Sie die Sprache aus, die Sie sprechen',
                               reply_markup=lan_kb)
    await asyncio.sleep(2)
    await message.delete()
    await asyncio.sleep(9)
    await att.delete()


@ch_router.message(Command('presentation'), StateFilter(FSM_ST.after_start))
async def show_presentation(message: Message):
    print('show_presentation works')
    user_id = message.from_user.id
    temp_data = users_db[user_id]['bot_ans']
    await message_trasher(user_id, temp_data)
    lan = await return_lan(user_id)  # достаю язык
    referal_dict = {'tr':'https://youtu.be/OzeAUBBIJAk', 'ru':'https://www.youtube.com/watch?v=LUNjMktIszE',
                    'ar':'https://youtu.be/ecrMDlehMCs', 'de':'https://youtu.be/X9tOaR7rXcw',
                    'en':'https://youtu.be/UGITy9dYrTI', 'fa':'https://youtu.be/w8f62WhScek'}
    if lan in referal_dict:
        att = await message.answer(text=referal_dict[lan])
    else:
        att = await message.answer(text=referal_dict['de'])
    users_db[user_id]['bot_ans'] = att
    await asyncio.sleep(2)
    await message.delete()


@ch_router.message(StateFilter(FSM_ST.after_start), IS_LETTER())
async def artikle_geber(message: Message):
    user_id = message.from_user.id
    lan = await return_lan(user_id)  # достаю язык
    suchend_word = message.text
    # print("1111 suchend_word = ", suchend_word)
    if suchend_word.lower().startswith('die ') or suchend_word.lower().startswith('der ') or suchend_word.lower().startswith('das '):
        suchend_word = suchend_word[4:]
        # print("suchend_word = ", suchend_word)
    zapros = f'{site_url}{suchend_word}'
    print(zapros)
    req = requests.get(url=zapros, headers=site_headers)
    if req.status_code == 200:
        fin_plural = ''
        first_eng_analog = ' Keine'
        my_perevod = ' Keine'
        verb_formen = ''
        soup = bs(req.text, 'lxml')
        trans = soup.find(class_='rInfo')
        if not trans:
            sin_stroka = await regular_message(i_do_not_know, lan)  # Вывожу что не знаю этого слова
        else:
            trans_data = trans.find(class_='rBox rBoxWht').find_all(class_='wNrn')
            if trans_data:  # Добавлено условие, проверяющее получение страницы
                en_block = trans_data[0]
                kirill_block = trans_data[1]
                fars_blok = trans_data[2]

                kit_lang = kirill_block.find_all('dd')
                fars_kit_lan = fars_blok.find_all('dd')
                en_structure = en_block.find_all('dd')
                if lan != 'de':
                    for perevod in (kit_lang + fars_kit_lan + en_structure):
                        data = perevod.get('lang')
                        if data == lan:  #  us_lan:  # Определение языка
                            my_perevod = perevod.text
                else:
                    my_perevod = '🤷  Es ist unmöglich in der Grleiche Sprache zu übersetzen'
            ######################################################################################
            SS_2 = soup.find('h1')
            chast_rechi = SS_2.text.split()[1]
            SS_2 = soup.find(class_='rAbschnitt')
            SS_1 = SS_2.find_all(class_='rBox rBoxWht')

            if chast_rechi == suchend_word:
                f_data = ' '

            elif chast_rechi == 'глагола':
                #### Formen
                await insert_neue_wort_in_verb(user_id, message.text)
                verb_cont = SS_1[0].find(class_='rAufZu')  # .find(class_='wNrn')
                v2 = verb_cont.find(class_='rAuf rCntr')
                v3 = v2.find(class_='r1Zeile rU3px rO0px')
                verb_formen = v3.text.split('\n')
                ss = ''
                for x in verb_formen:
                    ss += x
                verb_formen = f'<b>Verb Formen :</b> {ss}\n\n'

                ### Синоноимы
                verb_cont = SS_1[3].find(class_='rAufZu').find(class_='wNrn')
                a_cont = verb_cont.find_all('span')[1]
                finish_data = a_cont.text.replace(' ≡', ',')
                if finish_data[-1] not in ascii_letters:
                    f_data = finish_data[2:-1]
                else:
                    f_data = finish_data[2:]

                verb_needed_cont = SS_1[0]
                ### English analog
                test = verb_needed_cont.find(class_='rAufZu')
                test_2 = test.find(class_="rAuf rCntr")
                eng_1 = test_2.find(class_='r1Zeile rU6px rO0px')
                eng_2 = eng_1.get_text(strip=True)
                if eng_2:
                    first_eng_analog = eng_2.split(',')[0]
                else:
                    first_eng_analog = ''

            elif chast_rechi not in (
                    'прилагательного', 'существительного', 'глагола'):  # для наречий и всего остального
                first_step = SS_1[0]
                second_step = first_step.find(class_='rAufZu')
                # print('test = ', second_step)
                eng_gleiche = second_step.find(class_='r1Zeile rU6px rO0px')

                first_eng_analog = eng_gleiche.text.strip("\n")
                if '\n' in first_eng_analog:
                    first_eng_analog = first_eng_analog.replace('\n', ' ')

                first_step2 = SS_1[2]
                second_step2 = first_step2.find(class_='rAufZu')

                third_step = second_step2.find(class_='wNrn')
                # print('third step', third_step.text)
                sin_data = third_step.text
                if 'a.' in sin_data:
                    syn_data = sin_data.split('a.')[1]
                    finish_data = syn_data.replace(' ≡', ',')
                    if finish_data[-1] not in ascii_letters:
                        f_data = finish_data[2:-1]
                    else:
                        f_data = finish_data[2:]

                else:
                    syn_data = sin_data
                if '\n' in syn_data:
                    syn_data = syn_data.replace('\n', ', ').replace('.', '').replace('≡', '')
                    n = syn_data.split()
                    s = ''
                    for x in n:
                        if len(x) > 1:
                            s += x + ' '
                    f_data = s[:-2]
                    if f_data[-1] not in ascii_letters:
                        f_data = f_data[:-1]
                    if ' ' in f_data:
                        f_data = f_data.replace(' ', ', ')
                    if ',,' in f_data:
                        f_data = f_data.replace(',,', ',')

            elif chast_rechi in ('прилагательного', 'существительного'):
                if chast_rechi == 'существительного':
                    art_needed_cont = SS_1[0]
                    test = art_needed_cont.find(class_='rAufZu')
                    ### Часть с артиклем
                    test_2 = test.find(class_="rAuf rCntr")
                    test_3 = test_2.find(class_='rCntr rClear')
                    artikl = test_3.get_text(strip=True)

                    final_data = artikl.split(',')
                    if len(final_data) > 1:
                        data = final_data[1] + ' ' + final_data[0]
                        if final_data[1] == 'der':
                            await insert_neue_wort_in_der(user_id, data)
                        elif final_data[1] == 'die':
                            await insert_neue_wort_in_die(user_id, data)
                        else:
                            await insert_neue_wort_in_das(user_id, data)

                    else:
                        data = 'die ' + final_data[0]
                    suchend_word = data

                    ##### Часть со множественным числом

                    plur_1 = test_2.find(class_='r1Zeile rU3px rO0px')
                    plur_2 = plur_1.find_all('q')
                    fin_plural = f'<b>Plural Forme : {plur_2[-1].text}</b>\n\n'

                    eng_1 = test_2.find(class_='r1Zeile rU6px rO0px')
                    # print('eng_1 = ', eng_1.get_text(strip=True))
                    eng_2 = eng_1.get_text(strip=True)
                    if eng_2:
                        first_eng_analog = eng_2.split(',')[0].capitalize()
                ##### ADJ
                needed_cont = SS_1[0]
                eng_p1 = needed_cont.find(class_='rAuf rCntr')
                eng_p2 = eng_p1.find(class_='r1Zeile rU6px rO0px')
                eng_p3 = eng_p2.get_text(strip=True)
                if eng_p3:
                    first_eng_analog = eng_p3.split(',')[0]
                else:
                    first_eng_analog = ''
                if chast_rechi == 'прилагательного':
                    await insert_neue_wort_in_adj(user_id, message.text)
                needed_cont = SS_1[2]

                test_2 = needed_cont.find(class_='rAufZu')
                # print('test_2 = ', test_2)
                s1 = test_2.find_all('span')

                if len(s1):
                    if len(s1) == 1:
                        a_cont = s1[0]
                        finish_data = a_cont.text.replace(' ≡', ',')
                    elif len(s1) > 1:
                        a_cont = s1[1]
                        finish_data = a_cont.text.replace(' ≡', ',')
                    if finish_data[-1] not in ascii_letters:
                        f_data = finish_data[2:-1]
                    else:
                        f_data = finish_data[2:]
                else:
                    f_data = 'Keine Synonyme'
            else:
                f_data = ' 🤷 '

            # Формирую конечное сообщение
            if first_eng_analog:
                eng_str = f'<b>English : {first_eng_analog}</b>'
            else:
                eng_str = ''
            sin_stroka = (f'\n\n<b>{suchend_word}</b> ➡️ <b>Übersetzung :</b> {my_perevod}\n\n'
                          f'{fin_plural}{verb_formen}'
                          f'{eng_str}\n\n'
                          f'<b>Synonyme :</b>  {f_data}')

        await message.answer(text=sin_stroka)

    else:
        att = await message.answer(await translates(i_do_not_know, lan))  # Вывожу что не знаю этого слова)
        await asyncio.sleep(3)
        await att.delete()

    await message.delete()


@ch_router.message(Command('help'))
async def process_help_command(message: Message):
    lan = await return_lan(message.from_user.id)
    if not lan:
        await insert_lan(message.from_user.id, 'ru')
        lan = 'ru'
    erste = await regular_message('This bot can define ', lan)
    stroka = await regular_message(help_text, lan)
    # print('stroka = ', stroka)
    st_present = f'{erste} {artikel}\n\n{stroka} {presentation}'
    att = await message.answer(text=st_present)  # Почему не проверяется наличие этого слова в лексиконе bot_lexicon = {} ? -
    # ответ - потому что уже сформированы в erste и stroka
    await asyncio.sleep(30)
    await message.delete()
    await att.delete()


@ch_router.message(Command('liefern'))
async def process_show_command(message: Message):
    print('INTO LIFERN')
    user_id = message.from_user.id
    der = await return_der_string(user_id)
    await asyncio.sleep(0.2)
    die = await return_die_string(user_id)
    await asyncio.sleep(0.2)
    das = await return_das_string(user_id)
    await asyncio.sleep(0.2)
    verb = await return_verb_string(user_id)
    await asyncio.sleep(0.2)
    adj = await return_adj_string(user_id)
    await asyncio.sleep(0.2)

    DER = await message.answer(der)
    await asyncio.sleep(0.2)
    DIE = await message.answer(die)
    await asyncio.sleep(0.2)
    DAS = await message.answer(das)
    await asyncio.sleep(0.2)
    VER = await message.answer(verb)
    await asyncio.sleep(0.2)
    ADJ = await message.answer(adj)
    await message.delete()


@ch_router.message(Command('settings'), StateFilter(FSM_ST.after_start))
async def process_settings_command(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lan = await return_lan(user_id)
    if not lan:
        await insert_lan(message.from_user.id, 'ru')
        lan = 'ru'
    att = await message.answer(await regular_message(settings_text, lan))
    await asyncio.sleep(20)
    await att.delete()
    await message.delete()


@ch_router.message(Command('grammatik'), StateFilter(FSM_ST.after_start))
async def process_grammatik_command(message: Message):
    user_id = message.from_user.id
    lan = await return_lan(user_id)
    if not lan:
        await insert_lan(message.from_user.id, 'ru')
        lan = 'ru'
    att = await message.answer(text=await regular_message(grammatik_text, lan), reply_markup=gram_kb)
    await asyncio.sleep(20)
    await att.delete()
    await message.delete()


@ch_router.message(Command('wortschatz'), StateFilter(FSM_ST.after_start))
async def process_worschatz_command(message: Message):
    """Хэндлер  показывает инлайн клаву с 3 учебниками"""
    user_id = message.from_user.id
    lan = await return_lan(user_id)
    if not lan:
        await insert_lan(message.from_user.id, 'ru')
        lan = 'ru'
    temp_data = users_db[user_id]['bot_ans']
    await message_trasher(user_id, temp_data)
    carture = await regular_message(it_auswahlen, lan)
    att = await message.answer_photo(photo=ABC, caption=carture, reply_markup=it_buch_kb)
    users_db[user_id]['bot_ans'] = att
    await asyncio.sleep(8)
    try:
        await att.delete()
    except Exception:
        pass
    await message.delete()


@ch_router.message(Command('add_wort'), StateFilter(FSM_ST.after_start))
async def process_add_wort_command(message: Message, state: FSMContext):
    """Отправляет сообщение с предложением отправить ему слово на немецком языке"""
    user_id = message.from_user.id
    lan = await return_lan(user_id)
    if not lan:
        await insert_lan(message.from_user.id, 'ru')
        lan = 'ru'
    await state.set_state(FSM_ST.add_wort)

    temp_data = users_db[user_id]['bot_ans']
    await message_trasher(user_id, temp_data)

    att = await message.answer(f'<b>{await regular_message(deine_wort, lan)}</b>')
    users_db[message.from_user.id]['bot_ans'] = att
    await asyncio.sleep(3)
    await message.delete()


@ch_router.message(StateFilter(FSM_ST.add_wort), F.text, WORD_ACCEPT())
async def process_add_wort(message: Message, state: FSMContext):
    """Хэндлер получает слово на немецком и добавляет это слово с переводом в хранилище бота, что очень круто !"""
    lan = await return_lan(message.from_user.id)
    user_id = message.from_user.id
    ubersatz_in_eng = await translates_in_english(message.text)  # Перевожу немецкое слов на английский
    print('ubersatz_in_eng = ', ubersatz_in_eng)
    if lan != 'de':
        heimat_lan = await translates(ubersatz_in_eng, lan)  # Перевожу английское слово на язык юзера
    else:
        heimat_lan = message.text
    temp_data = users_db[user_id]['bot_ans']
    await message_trasher(user_id, temp_data)

    temp_data = users_db[user_id]['user_msg']
    await message_trasher(user_id, temp_data)
    if lan not in  ('de', 'en'):
        if ubersatz_in_eng in gleiche_words or ubersatz_in_eng.lower() != heimat_lan.lower() and len(
                message.text.lower()) != len(heimat_lan):
            att = await message.answer(f'{message.text} =  {heimat_lan.lower()} ❓',
                                       reply_markup=ja_nein_kb)
            users_db[user_id]['bot_ans'] = att

            bot_dict = await dp.storage.get_data(key=bot_storage_key)  # Получаю словарь бота
            user_bot_stor = bot_dict[str(user_id)]  # Получаю словарь юзера
            user_bot_stor[message.text] = heimat_lan.lower()  # по ключу - немецкому слову присваиваю значение
            bot_dict[user_id] = user_bot_stor  # Перезаписываю словарь юзера
            await dp.storage.update_data(key=bot_storage_key, data=bot_dict)  # перезаписываю словарь бота
            await state.update_data(pur=message.text)  # обновляю словарь юзера, записываю туда слово на немецком
        else:
            att = await message.answer(await translates('I do not know this word', lan))
            users_db[user_id]['bot_ans'] = att
    elif lan == 'en':
        att = await message.answer(f'{message.text} =  {heimat_lan.lower()} ❓',
                                   reply_markup=ja_nein_kb)
        users_db[user_id]['bot_ans'] = att

        bot_dict = await dp.storage.get_data(key=bot_storage_key)  # Получаю словарь бота
        user_bot_stor = bot_dict[str(user_id)]  # Получаю словарь юзера
        user_bot_stor[message.text] = heimat_lan.lower()  # по ключу - немецкому слову присваиваю значение
        bot_dict[user_id] = user_bot_stor  # Перезаписываю словарь юзера
        await dp.storage.update_data(key=bot_storage_key, data=bot_dict)  # перезаписываю словарь бота
        await state.update_data(pur=message.text)  # обновляю словарь юзера, записываю туда слово на немецком

    else:
        att = await message.answer(f'{message.text} =  {message.text} ❓',
                                   reply_markup=ja_nein_kb)
        users_db[user_id]['bot_ans'] = att
        bot_dict = await dp.storage.get_data(key=bot_storage_key)  # Получаю словарь бота
        user_bot_stor = bot_dict[str(user_id)]  # Получаю словарь юзера
        user_bot_stor[heimat_lan] = heimat_lan  # по ключу - немецкому слову присваиваю значение
        bot_dict[user_id] = user_bot_stor  # Перезаписываю словарь юзера
        await dp.storage.update_data(key=bot_storage_key, data=bot_dict)  # перезаписываю словарь бота
        await state.update_data(pur=message.text)  # обновляю словарь юзера, записываю туда слово на немецком


@ch_router.message(StateFilter(FSM_ST.personal_uber), F.text)
async def process_add_personal_ubersetzen_command(message: Message, state: FSMContext):
    """Хэндлер принимает верный перевод немецкого слова на язык юзера, который он ему сам посылает"""
    print('pesonal uber works\n\n')
    us_dict = await state.get_data()
    lan = await return_lan(message.from_user.id)
    user_id = message.from_user.id
    isk_slovo = us_dict['pur']  # Получаю немецкое слово

    bot_dict = await dp.storage.get_data(key=bot_storage_key)
    user_bot_stor = bot_dict[str(user_id)]  # Получаю доступ по tg_id
    user_bot_stor[isk_slovo] = message.text  # Судя по всему здесь получается конструкция вида {"немецкое слово":"перевод юзера"}
    bot_dict[user_id] = user_bot_stor
    await dp.storage.update_data(key=bot_storage_key, data=bot_dict)

    await state.update_data(pur='')
    await state.set_state(FSM_ST.add_wort)

    temp_data = users_db[user_id]['bot_ans']
    await message_trasher(user_id, temp_data)

    otvet = await regular_message(erfolgreich_fugen, lan)
    uber_noch = await regular_message(noch, lan)
    att = await message.answer(f'{otvet}\n\n{uber_noch}', reply_markup=ja_nein_kb)
    users_db[user_id]['user_msg'] = att


@ch_router.message(Command('lernen'), StateFilter(FSM_ST.after_start))
async def process_lernen_command(message: Message, state: FSMContext):
    """Хэндлер отпраляет текст с клваой из трёх учебников"""
    user_id = message.from_user.id
    await state.set_state(FSM_ST.lernen)
    temp_data = users_db[user_id]['bot_ans']
    await message_trasher(user_id, temp_data)
    att = await message.answer_photo(photo=ABC, caption=aus_welche_buch,
                                     reply_markup=it_buch_kb)
    users_db[user_id]['bot_ans'] = att
    await message.delete()


@ch_router.message(Command('schreiben'), StateFilter(FSM_ST.after_start))
async def process_schreiben_command(message: Message, state: FSMContext):
    """Хэндлер отпраляет текст с клваой из трёх учебников"""
    user_id = message.from_user.id
    await state.set_state(FSM_ST.schreiben)
    temp_data = users_db[user_id]['bot_ans']
    await message_trasher(user_id, temp_data)
    att = await message.answer_photo(photo= ABC, caption=aus_welche_buch,
                               reply_markup=it_buch_kb)
    users_db[user_id]['bot_ans'] = att
    await message.delete()


@ch_router.message(StateFilter(FSM_ST.schreiben), EXCLUDE_COMMAND_MIT_EXIT(), F.text, STOP_EMODJI())
async def check_writing_process(message: Message, state: FSMContext):
    print('check_writing works')
    dict_user = await state.get_data()
    lan = await return_lan(message.from_user.id)
    using_dict = dict_user['current_stunde']
    # print('bot_rus_collection = ', bot_rus_collection)
    previous_word = dict_user['pur']  # Получаю  немецкое слово
    # print('previous_word = ', previous_word)
    if lan != 'de':
        if ',' in previous_word:
            previous_word_1 = previous_word.split(',')[0]
        elif ('(') in previous_word:
            previous_word_1 = previous_word.split('(')[0]
        else:
            previous_word_1 = previous_word

        if previous_word_1.lower() == message.text.lower() or previous_word_1.lower == message.text.lower():

            await message.answer(f'<b>Richtig !</b>    🥳\n\nDas ist <b>{previous_word}</b>')
            await message.delete()
            # print('\n\n\nuser_dict = ', user_dict)
            del using_dict[previous_word] # удаляю пару ключ-занчение из копии словаря
        else:
            await message.answer(f'Sie haben geantwortet <b>{message.text}</b>\n\n'
                                 f'Richtige Antwort  ist <b>{previous_word}</b>')
            await message.delete()
        working_tuple = choice(sorted(using_dict.items()))  # Выбираю случайную пару из словаря
        deutsch, engl = working_tuple
        combined_key = lan + '_' + engl
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
        else:
            if combined_key not in bot_word_collection:
                uber_eng = await translates(engl, lan)
                bot_word_collection[combined_key] = uber_eng
            else:
                uber_eng = bot_word_collection[combined_key]

        await state.update_data(pur=deutsch)
        if len(using_dict)>1:
            if lan != 'en':
                await message.answer(text=f'Schreiben Sie bitte die Übersetzung des Worts !\n\n<b>{uber_eng}</b>'
                                          f'\n\n<i>English</i> = <b>{engl}</b>',
                                     reply_markup=exit_clava)
            else:
                await message.answer(text=f'Schreiben Sie bitte die Übersetzung des Worts !\n\n<b>{uber_eng}</b>',
                                     reply_markup=exit_clava)
        else:
            exit_command = ' /exit'
            ans = await regular_message(alles, lan)
            combo_str = ans + ' ' + exit_command
            att = await message.answer(text=combo_str)
            users_db[message.from_user.id]['user_msg'] = att


        ######### Часть с где у юзера у самого немецкий язык ####################################
    else:
        if len(previous_word)==2:
            previous_word = previous_word[0]
        if ',' in previous_word:
            previous_word_1 = previous_word.split(',')[0]
        elif ('(') in previous_word:
            previous_word_1 = previous_word.split('(')[0]
        else:
            previous_word_1 = previous_word
        if previous_word_1.lower() != message.text.lower():
            await message.answer(f'Sie haben geantwortet <b>{message.text}</b>\n\n'
                                 f'Richtige Antwort  ist <b>{previous_word_1}</b>')
            await message.delete()
        else:
            await message.answer(f'<b>Richtig !</b>    🥳\n\nDas ist <b>{previous_word}</b>')
            await message.delete()
            del using_dict[previous_word]

        if using_dict:
            working_tuple = choice(sorted(using_dict.items()))  # Выбираю случайную пару из словаря
            deutsch, engl = working_tuple
            await state.update_data(pur=deutsch)
            await message.answer(text=f'Schreiben Sie bitte die Übersetzung des Worts !\n\n<b>{engl}</b>', reply_markup=exit_clava)
        else:
            exit_command = ' /exit'
            ans = await regular_message(alles, lan)
            combo_str = ans + ' ' + exit_command
            att = await message.answer(text=combo_str)
            users_db[message.from_user.id]['user_msg'] = att



@ch_router.message(Command('exit'))
async def process_exit_command(message: Message, state: FSMContext):
    lan = await return_lan(message.from_user.id)
    if not lan:
        await insert_lan(message.from_user.id, 'ru')
        lan = 'ru'
    user_id = message.from_user.id
    current_state = await state.get_state()
    if current_state != 'FSM_ST:after_start':
        await state.set_state(FSM_ST.after_start)
        await state.update_data(pur='', current_stunde='')  # reset user data
        temp_data = users_db[user_id]['bot_ans']
        await message_trasher(user_id, temp_data)
        temp_data = users_db[user_id]['user_msg']
        await us_message_trasher(user_id, temp_data)
        att = await message.answer(text=await regular_message(exit_msg, lan), reply_markup=ReplyKeyboardRemove())
        users_db[user_id]['bot_ans'] = att
        await message.delete()
    else:
        temp_data = users_db[user_id]['bot_ans']
        await message_trasher(user_id, temp_data)
        att = await message.answer(text=await regular_message(exit_after_start, lan), reply_markup=ReplyKeyboardRemove())
        users_db[user_id]['bot_ans'] = att
        await message.delete()



@ch_router.message(Command('review'), StateFilter(FSM_ST.after_start))
async def process_review_command(message: Message):
    lan = await return_lan(message.from_user.id)
    text = await regular_message(review_text, lan)
    fin_text = f'{text} \n\n\n @Smart_Imperium_bot'
    att = await message.answer(text=fin_text)
    await asyncio.sleep(20)
    await att.delete()
    await message.delete()


@ch_router.message(Command('zeigen'), StateFilter(FSM_ST.after_start))
async def process_notiz_command(message: Message, state: FSMContext):
    """Хэндлер отправлят сообщение с инлайн клавой - где можно посмотреть свои заметки и слова"""
    lan = await return_lan(message.from_user.id)
    us_text = await regular_message(zeigen_start, lan)
    att = await message.answer(us_text, reply_markup=zeigen_kb)
    temp_data = users_db[message.from_user.id]['bot_ans']
    await message_trasher(message.from_user.id, temp_data)
    users_db[message.from_user.id]['bot_ans'] = att
    await asyncio.sleep(3)
    await message.delete()


@ch_router.message(StateFilter(FSM_ST.add_note_1), F.text, EXCLUDE_COMMAND())
async def add_notiz_1(message: Message, state: FSMContext):
    """Хэндлер принимает название заметки и выводит просьбу добавить саму заметку"""
    print('add_notiz_1 works')
    lan = await return_lan(message.from_user.id)
    await state.update_data(pur=message.text)
    otvet = await regular_message(your_name_is, lan)
    otvet_2 = await regular_message(step_2, lan)
    stroka = f"{otvet} {message.text}\n\n{otvet_2}"
    att = await message.answer(stroka)
    temp_data = users_db[message.from_user.id]['bot_ans']
    await message_trasher(message.from_user.id, temp_data)
    users_db[message.from_user.id]['bot_ans'] = att
    await state.set_state(FSM_ST.add_note_2)
    await message.delete()


@ch_router.message(StateFilter(FSM_ST.add_note_2), F.content_type.in_({'photo', 'text'}), EXCLUDE_COMMAND())
async def add_notiz_2(message: Message, state: FSMContext):
    """Принимает текст или фото и отвечает, что заметка успешно добавлена"""
    print('add_notiz_2 works')
    us_dict = await state.get_data()
    user_id = message.from_user.id
    lan = await return_lan(message.from_user.id)
    note_name = us_dict['pur']
    temp_data = users_db[message.from_user.id]['bot_ans']
    await message_trasher(user_id, temp_data)

    if message.text:
        new_note = User_Note(name=note_name, foto='', description=message.text)
    else:
        foto_id = message.photo[-1].file_id
        capcha = message.caption
        new_note = User_Note(name=note_name, foto=foto_id, description=capcha)

    us_zam = await return_zametki(user_id)
    if not us_zam:
        zam_dict = {note_name: new_note}  # Создаю словарь - название заметки : текст заметки
        serialized_data = pickle.dumps(zam_dict)  # Сериализую объект
        await insert_serialised_note(user_id, serialized_data)  # Вставляю его в Postgress

    else:
        zam_dict = pickle.loads(us_zam)
        zam_dict[note_name] = new_note
        serialized_data = pickle.dumps(zam_dict)  # Сериализую объект
        await insert_serialised_note(user_id, serialized_data)  # Вставляю его в Postgress

    stroka = await regular_message(successfully_add, lan)
    att = await message.answer(stroka)
    await state.set_state(FSM_ST.after_start)
    await asyncio.sleep(5)
    await att.delete()
    await message.delete()


@ch_router.message(StateFilter(FSM_ST.add_note_2))
async def something_goes_wrong(message: Message, state: FSMContext):
    print('something_goes_wrong')
    lan = await return_lan(message.from_user.id)
    await state.update_data(pur='')
    temp_data = users_db[message.from_user.id]['bot_ans']
    await message_trasher(message.from_user.id, temp_data)
    await state.set_state(FSM_ST.after_start)
    stroka = await regular_message(wrong_add_new_note, lan)
    att = await message.answer(stroka)
    await asyncio.sleep(4)
    await message.delete()
    await att.delete()

@ch_router.message(Command('maerchen'), StateFilter(FSM_ST.after_start))
async def maerchen_command(message: Message, state: FSMContext):
    """Хэндлер отправлят сообщение с инлайн клавой - skazki"""
    lan = await return_lan(message.from_user.id)
    us_text = await regular_message(maerchen_text, lan)
    att = await message.answer(us_text, reply_markup=maerchen_kb)
    temp_data = users_db[message.from_user.id]['bot_ans']
    await message_trasher(message.from_user.id, temp_data)
    users_db[message.from_user.id]['bot_ans'] = att
    await asyncio.sleep(3)
    await message.delete()


###########################################ADMIN PART#######################################
@ch_router.message(Command('admin'), IS_ADMIN())
async def admin_enter(message: Message):
    print('admin_enter works')
    att = await message.answer(admin_eintritt)
    await asyncio.sleep(12)
    await att.delete()


@ch_router.message(Command('skolko'), IS_ADMIN())
async def get_quantyty_users(message: Message):
    qu = await return_quantity_users()
    str_qu = str(len(qu))
    last_number = str_qu[-1]
    if last_number in ('2', '3', '4'):
        await message.answer(f'Бота запустили <b>{len(qu)}</b> юзера')
    elif last_number == '1':
        await message.answer(f'Бота запустили <b>{len(qu)}</b> юзер')
    else:
        await message.answer(f'Бота запустили <b>{len(qu)}</b> юзеров')





@ch_router.message(Command('send_msg'), IS_ADMIN())
async def send_message(message: Message, state: FSMContext):
    await state.set_state(FSM_ST.admin)
    await message.answer('Schreib ihre Nachrichten')


@ch_router.message(StateFilter(FSM_ST.admin))
async def send_message(message: Message, state: FSMContext):
    us_list = await return_spam_users()
    print('us_list = ', *us_list, sep='\n')
    # text in English
    us_list.remove(6685637602)
    for chat_id in us_list:
        lan = await return_lan(chat_id)  # Запрашиваю язык из постгреса
        spam = await translates(message.text, lan)
        try:
            await message.bot.send_message(chat_id=chat_id, text=spam)
        except TelegramForbiddenError:
            pass
        await asyncio.sleep(0.2)

    await state.set_state(FSM_ST.after_start)
    await message.answer('Mailing abgeschlossen')


@ch_router.message(IS_ADMIN(), Command('dump'))
async def dump_db(message: Message, state: FSMContext):
    bot_dict = await dp.storage.get_data(key=bot_storage_key)  # Получаю словарь бота
    with open('save_db.pkl', 'wb') as file:
        pickle.dump(bot_dict, file)
    with open('bot_rus_wortschatz_db.pkl', 'wb') as file:
        pickle.dump(bot_rus_wortschatz, file)

    with open('bot_ukr_wortschatz_db.pkl', 'wb') as file:
        pickle.dump(bot_ukr_wortschatz, file)

    with open('bot_anders_wortschatz_db.pkl', 'wb') as file:
        pickle.dump(bot_anders_wortschatz, file)

    with open('bot_rus_collection_db.pkl', 'wb') as file:
        pickle.dump(bot_rus_collection, file)

    with open('bot_ukr_collection_db.pkl', 'wb') as file:
        pickle.dump(bot_ukr_collection, file)

    with open('bot_word_collection_db.pkl', 'wb') as file:
        pickle.dump(bot_word_collection, file)

    with open('bot_lexicon_db.pkl', 'wb') as file:
        pickle.dump(bot_lexicon, file)
    await message.answer('Базы данных успешно записана !')
    await state.set_state(FSM_ST.after_start)

@ch_router.message(IS_ADMIN(), Command('load'))
async def load_db(message: Message, state: FSMContext):
    with open('save_db.pkl', 'rb') as file:
        recover_base = pickle.load(file)
        await dp.storage.set_data(key=bot_storage_key, data=recover_base)  # Обновляю словарь бота

    with open('bot_rus_wortschatz_db.pkl', 'rb') as file:
        recover_bot_rus_wortschatz = pickle.load(file)
        bot_rus_wortschatz.update(recover_bot_rus_wortschatz)

    with open('bot_ukr_wortschatz_db.pkl', 'rb') as file:
        recover_bot_ukr_wortschatz = pickle.load(file)
        bot_ukr_wortschatz.update(recover_bot_ukr_wortschatz)

    with open('bot_anders_wortschatz_db.pkl', 'rb') as file:
        recover_bot_anders_wortschatz = pickle.load(file)
        bot_anders_wortschatz.update(recover_bot_anders_wortschatz)

    with open('bot_rus_collection_db.pkl', 'rb') as file:
        recover_bot_rus_coll = pickle.load(file)
        bot_rus_collection.update(recover_bot_rus_coll)

    with open('bot_ukr_collection_db.pkl', 'rb') as file:
        recover_bot_ukr_coll = pickle.load(file)
        bot_ukr_collection.update(recover_bot_ukr_coll)

    with open('bot_word_collection_db.pkl', 'rb') as file:
        recover_bot_word_coll = pickle.load(file)
        bot_rus_collection.update(recover_bot_word_coll)

    with open('bot_lexicon_db.pkl', 'rb') as file:
        recover_bot_lexicon = pickle.load(file)
        bot_lexicon.update(recover_bot_lexicon)

    await message.answer('Базы данных успешно загружены !')
    await state.set_state(FSM_ST.after_start)


@ch_router.message()
async def trasher(message: Message):
    print('TRASHER')
    if message.text in ('/zeigen', '/help'):
        att = await message.answer('TRASHER WORKS')
        await asyncio.sleep(5)
        await att.delete()
    await asyncio.sleep(1)
    await message.delete()
