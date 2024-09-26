from aiogram import Router, F,  html
import asyncio
from bs4 import BeautifulSoup as bs
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import CommandStart, Command, StateFilter
import requests
from aiogram.fsm.context import FSMContext
from postgres_table import site_url, site_headers
from keyboards import *
from aiogram.enums import ParseMode
from filters import PRE_START, IS_LETTER, IS_ADMIN, WORD_ACCEPT, EXCLUDE_COMMAND
from lexicon import *
from postgres_functions import *
from bot_instance import FSM_ST, bot_storage_key, dp
from bot_base import users_db, user_dict, bot_server_base
from copy import deepcopy
from string import ascii_letters
from external_functions import translates, translates_in_english
from contextlib import suppress
from aiogram.exceptions import TelegramBadRequest
from note_class import User_Note

ch_router = Router()

@ch_router.message(~StateFilter(FSM_ST.add_note_2),~F.text)
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
                              {'lan': '',   # Язык по дефолту ничего
                              'pur':'',   # personal ubersetzung темповое значение своего перевода
                              'current_stunde':'',  # Для изучекния словарного запаса урока
                              'spam':''  #  Согласен или нет получать уведомления от бота
                               })
        await message.answer(text=f'{html.bold(html.quote(user_name))}, '
                                  f'{start}',
                             parse_mode=ParseMode.HTML,
                             reply_markup=ReplyKeyboardRemove())
        att = await message.answer(text='Wählen Sie die Sprache aus, die Sie sprechen',
                             reply_markup=lan_kb)
        users_db[user_id]['bot_ans'] = att
        bot_dict = await dp.storage.get_data(key=bot_storage_key)

        bot_dict[user_id]={}  #  Создаю словарь с ключом - tg_us_id
        await dp.storage.set_data(key=bot_storage_key, data=bot_dict)
        await asyncio.sleep(0.5)
        await add_in_list(user_id)  # Кто стартанул бота - добавляю в список админа
        bot_server_base[user_id]={}  # Создаю словарь юзера
    else:
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
    await asyncio.sleep(6)
    await att.delete()




@ch_router.message(StateFilter(FSM_ST.after_start), IS_LETTER())
async def artikle_geber(message: Message, state: FSMContext):
    user_id = message.from_user.id
    us_dict = await state.get_data()
    lan = us_dict['lan']
    suchend_word = message.text
    print(suchend_word.capitalize())
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
            sin_stroka = await translates(i_do_not_know, lan)  # Вывожу что не знаю этого слова
        else:
            trans_data = trans.find(class_='rBox rBoxWht').find_all(class_='wNrn')
            kirill_block = trans_data[1]
            fars_blok = trans_data[2]
            kit_lang = kirill_block.find_all('dd')
            fars_kit_lan = fars_blok.find_all('dd')
            us_dict = await state.get_data()
            us_lan = us_dict['lan']
            for perevod in (kit_lang + fars_kit_lan):
                data = perevod.get('lang')
                if data == us_lan:  # Определение языка
                    my_perevod = perevod.text
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
                # print('\n\n\neng_gleiche= ', eng_gleiche.text.strip("\n"))
                first_eng_analog = eng_gleiche.text.strip("\n")
                if '\n' in first_eng_analog:
                    first_eng_analog = first_eng_analog.replace('\n', ' ')

                first_step2 = SS_1[2]
                second_step2 = first_step2.find(class_='rAufZu')
                # print('test = ', second_step2)

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
                    # print('Test_2 =', test_2)
                    test_3 = test_2.find(class_='rCntr rClear')
                    # print('Test_3 =', test_3)
                    artikl = test_3.get_text(strip=True)
                    # print('artikl = ', artikl)
                    final_data = artikl.split(',')
                    if len(final_data) > 1:
                        data = final_data[1] + ' ' + final_data[0]
                        if final_data[1] == 'der':
                            await insert_neue_wort_in_der(user_id, data)
                        elif final_data[1] == 'die':
                            await insert_neue_wort_in_die(user_id, data)
                        else:
                            await insert_neue_wort_in_das(user_id, data)
                    # print(data)
                    else:
                        data = 'die ' + final_data[0]
                    suchend_word = data

                    ##### Часть со множественным числом

                    plur_1 = test_2.find(class_='r1Zeile rU3px rO0px')
                    # print('\n\n\nplur_1 = ', plur_1)
                    plur_2 = plur_1.find_all('q')
                    # print('plur2 = ', plur_2[-1].text)
                    fin_plural = f'<b>Plural Forme : {plur_2[-1].text}</b>\n\n'

                    eng_1 = test_2.find(class_='r1Zeile rU6px rO0px')
                    # print('eng_1 = ', eng_1.get_text(strip=True))
                    eng_2 = eng_1.get_text(strip=True)
                    if eng_2:
                        first_eng_analog = eng_2.split(',')[0].capitalize()
                ##### ADJ
                needed_cont = SS_1[0]
                # print('nedeed_count = ', needed_cont)
                eng_p1 = needed_cont.find(class_='rAuf rCntr')
                # print('eng_p1 = ', eng_p1)
                eng_p2 = eng_p1.find(class_='r1Zeile rU6px rO0px')
                # print('eng_p2 = ', eng_p2)
                eng_p3 = eng_p2.get_text(strip=True)
                if eng_p3:
                    first_eng_analog = eng_p3.split(',')[0]
                else:
                    first_eng_analog = ''
                await insert_neue_wort_in_adj(user_id, message.text)
                needed_cont = SS_1[2]
                # s1 = needed_cont.find(class_='rAufZu').find_all('span')

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

        # print(sin_stroka)
        await message.answer(text=sin_stroka)

    else:
        att = await message.answer(await translates(i_do_not_know, lan))  # Вывожу что не знаю этого слова)
        await asyncio.sleep(3)
        await att.delete()

    await message.delete()

@ch_router.message(Command('help'))
async def process_help_command(message: Message, state:FSMContext):
    us_dict = await state.get_data()
    lan = us_dict['lan']
    att = await message.answer(await translates(help_text, lan))
    await asyncio.sleep(20)
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


@ch_router.message(Command('settings'))
async def process_settings_command(message: Message, state:FSMContext):
    us_dict = await state.get_data()
    lan = us_dict['lan']
    att = await message.answer(await translates(settings_text, lan))
    await asyncio.sleep(20)
    await att.delete()
    await message.delete()

@ch_router.message(Command('grammatik'))
async def process_grammatik_command(message: Message):
    att = await message.answer(text=grammatik_text, reply_markup=gram_kb)
    await asyncio.sleep(20)
    await att.delete()
    await message.delete()

@ch_router.message(Command('wortschatz'), StateFilter(FSM_ST.after_start))
async def process_worschatz_command(message: Message, state:FSMContext):
    """Хэндлер  показывает инлайн клаву с доступными уроками словарный запас"""
    us_dict = await state.get_data()
    user_id = message.from_user.id
    lan = us_dict['lan']
    temp_data = users_db[user_id]['bot_ans']
    if temp_data:
        with suppress(TelegramBadRequest):
            await temp_data.delete()
            users_db[user_id]['bot_ans'] = ''
    att = await message.answer(text=await translates(worschatz_text, lan), reply_markup=ws_kb)
    users_db[user_id]['bot_ans'] = att
    await asyncio.sleep(20)
    await att.delete()
    await message.delete()

@ch_router.message(Command('add_wort'))
async def process_add_wort_command(message: Message, state:FSMContext):
    """Отправляет сообщение с предложением отправить ему слово на немецком языке"""
    user_id = message.from_user.id
    us_dict = await state.get_data()
    lan = us_dict['lan']
    await state.set_state(FSM_ST.add_wort)
    temp_data = users_db[user_id]['bot_ans']
    if temp_data:
        with suppress(TelegramBadRequest):
            await temp_data.delete()
            users_db[user_id]['bot_ans'] = ''
    att = await message.answer(f'<b>{await translates(deine_wort, lan)}</b>')
    users_db[message.from_user.id]['bot_ans'] = att
    await asyncio.sleep(3)
    await message.delete()

@ch_router.message(StateFilter(FSM_ST.add_wort),F.text, WORD_ACCEPT())
async def process_add_wort(message: Message, state:FSMContext):
    us_dict = await state.get_data()
    lan = us_dict['lan']
    user_id = message.from_user.id
    undersatz_in_eng = await translates_in_english(message.text)
    heimat_lan = await translates(undersatz_in_eng, lan)
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
    att = await message.answer(f'{message.text} =  {heimat_lan} ❓',
                               reply_markup=ja_nein_kb)
    users_db[user_id]['bot_ans'] = att

    bot_dict = await dp.storage.get_data(key=bot_storage_key)
    user_bot_stor = bot_dict[str(user_id)]
    user_bot_stor[message.text]=heimat_lan
    bot_dict[user_id]=user_bot_stor
    await dp.storage.update_data(key=bot_storage_key, data=bot_dict)
    await state.update_data(pur=message.text)  #  worschatz=us_dict)




@ch_router.message(StateFilter(FSM_ST.personal_uber),F.text)
async def process_add_personal_ubersetzen_command(message: Message, state:FSMContext):
    print('pesonal uber works\n\n')
    us_dict = await state.get_data()
    lan = us_dict['lan']
    user_id = message.from_user.id
    isk_slovo = us_dict['pur']

    bot_dict = await dp.storage.get_data(key=bot_storage_key)
    user_bot_stor = bot_dict[str(user_id)]  # Получаю доступ по tg_id
    user_bot_stor[message.text] = isk_slovo
    bot_dict[user_id] = user_bot_stor
    await dp.storage.update_data(key=bot_storage_key, data=bot_dict)

    await state.update_data(pur='')
    await state.set_state(FSM_ST.add_wort)
    temp_data = users_db[user_id]['bot_ans']
    if temp_data:
        with suppress(TelegramBadRequest):
            await temp_data.delete()
            users_db[user_id]['bot_ans'] = ''
    otvet = await translates(erfolgreich_fugen, lan)
    uber_noch = await translates(noch, lan)
    att = await message.answer(f'{otvet}\n\n{uber_noch}', reply_markup=ja_nein_kb)
    users_db[user_id]['bot_ans'] = att


@ch_router.message(Command('lernen'), StateFilter(FSM_ST.after_start))
async def process_lernen_command(message: Message, state:FSMContext):
    us_dict = await state.get_data()
    lan = us_dict['lan']
    user_id = message.from_user.id
    await state.set_state(FSM_ST.lernen)
    temp_data = users_db[user_id]['bot_ans']
    if temp_data:
        with suppress(TelegramBadRequest):
            await temp_data.delete()
            users_db[user_id]['bot_ans'] = ''
    att = await message.answer(text=await translates(lernen_msg, lan),
                         reply_markup=lernen_kb)
    users_db[user_id]['bot_ans'] = att
    await message.delete()


@ch_router.message(Command('exit'), ~StateFilter(FSM_ST.after_start))
async def process_exit_command(message: Message, state:FSMContext):
    us_dict = await state.get_data()
    lan = us_dict['lan']
    user_id = message.from_user.id
    await state.set_state(FSM_ST.after_start)
    await state.update_data(pur='', current_stunde='')  # reset user data
    temp_data = users_db[user_id]['bot_ans']
    if temp_data:
        with suppress(TelegramBadRequest):
            await temp_data.delete()
            users_db[user_id]['bot_ans'] = ''
    att = await message.answer(text=await translates(exit_msg, lan))
    users_db[user_id]['bot_ans'] = att
    await message.delete()

@ch_router.message(Command('review'), StateFilter(FSM_ST.after_start))
async def process_review_command(message: Message, state:FSMContext):
    us_dict = await state.get_data()
    lan = us_dict['lan']
    text = await translates(review_text, lan)
    fin_text = f'{text} \n\n\n @Smart_Imperium_bot'
    att = await message.answer(text=fin_text)
    await asyncio.sleep(20)
    await att.delete()
    await message.delete()

@ch_router.message(Command('zeigen'), StateFilter(FSM_ST.after_start))
async def process_notiz_command(message: Message, state:FSMContext):
    """Хэндлер отправлят сообщение с инлайн клавой - где можно посмотреть свои заметки и слова"""
    us_dict = await state.get_data()
    lan = us_dict['lan']
    us_text = await translates(zeigen_start, lan)
    att = await message.answer(us_text, reply_markup=zeigen_kb)
    temp_data = users_db[message.from_user.id]['bot_ans']
    if temp_data:
        with suppress(TelegramBadRequest):
            await temp_data.delete()
            users_db[message.from_user.id]['bot_ans'] = ''
    users_db[message.from_user.id]['bot_ans'] = att
    await asyncio.sleep(3)
    await message.delete()



@ch_router.message(StateFilter(FSM_ST.add_note_1), F.text, EXCLUDE_COMMAND())
async def add_notiz_1(message: Message, state:FSMContext):
    """Хэндлер выводит просбу добавить саму заметку"""
    print('add_notiz_1 works')
    us_dict = await state.get_data()
    lan = us_dict['lan']
    await state.update_data(pur=message.text)
    otvet = await translates(your_name_is, lan)
    otvet_2 = await translates(step_2, lan)
    stroka = f"{otvet} {message.text}\n\n{otvet_2}"
    att = await message.answer(stroka)
    temp_data = users_db[message.from_user.id]['bot_ans']
    if temp_data:
        with suppress(TelegramBadRequest):
            await temp_data.delete()
            users_db[message.from_user.id]['bot_ans'] = ''
    users_db[message.from_user.id]['bot_ans'] = att
    await state.set_state(FSM_ST.add_note_2)
    await message.delete()

@ch_router.message(StateFilter(FSM_ST.add_note_2),  F.content_type.in_({'photo', 'text'}), EXCLUDE_COMMAND())
async def add_notiz_2(message: Message, state:FSMContext):
    """Принимает текст или фото и отвечает, что заметка успешно добавлена"""
    print('add_notiz_2 works')
    us_dict = await state.get_data()
    user_id = message.from_user.id
    lan = us_dict['lan']
    note_name = us_dict['pur']
    temp_data = users_db[message.from_user.id]['bot_ans']
    if temp_data:
        with suppress(TelegramBadRequest):
            await temp_data.delete()
            users_db[message.from_user.id]['bot_ans'] = ''

    if message.text:
        new_note = User_Note(name=note_name, foto='', descripion=message.text)

    else:
        foto_id = message.photo[-1].file_id
        capcha = message.caption
        new_note = User_Note(name=note_name, foto=foto_id, descripion=capcha)
    bot_server_base[user_id][note_name] = new_note

    stroka = await translates(successfully_add, lan)
    att = await message.answer(stroka)
    await state.set_state(FSM_ST.after_start)
    await asyncio.sleep(5)
    await att.delete()
    await message.delete()


@ch_router.message(StateFilter(FSM_ST.add_note_2))
async def something_goes_wrong(message: Message, state: FSMContext):
    print('something_goes_wrong')
    user_id = message.from_user.id
    us_dict = await state.get_data()
    lan = us_dict['lan']
    await state.update_data(pur='')
    temp_data = users_db[message.from_user.id]['bot_ans']
    if temp_data:
        with suppress(TelegramBadRequest):
            await temp_data.delete()
            users_db[message.from_user.id]['bot_ans'] = ''
    await state.set_state(FSM_ST.after_start)
    stroka = await translates(wrong_add_new_note, lan)
    att = await message.answer(stroka)
    await asyncio.sleep(4)
    await message.delete()
    await att.delete()

 ###########################################ADMIN PART#######################################
@ch_router.message(Command('admin'), IS_ADMIN())
async def admin_enter(message: Message):
    print('admin_enter works')
    await message.answer(admin_eintritt)


@ch_router.message(Command('skolko'), IS_ADMIN())
async def get_quantyty_users(message: Message):
    qu = await return_quantity_users()
    await message.answer(f'Бота запустили {len(qu)} юзеров')

@ch_router.message(Command('send_msg'), IS_ADMIN())
async def send_message(message: Message, state: FSMContext ):
    await state.set_state(FSM_ST.admin)
    await message.answer('Schreib ihre Nachrichten')

@ch_router.message(StateFilter(FSM_ST.admin))
async def send_message(message: Message, state: FSMContext):
    us_list = await return_spam_users()
    us_list.remove(6685637602)
    for chat_id in us_list:
        await message.send_copy(chat_id=chat_id)
        await asyncio.sleep(0.2)

    await state.set_state(FSM_ST.after_start)
    await message.answer('Mailing abgeschlossen')


@ch_router.message()
async def trasher(message: Message):
    print('TRASHER')
    if message.text in ('/zeigen', '/help'):
        att = await message.answer('TRASHER WORKS')
        await asyncio.sleep(5)
        await att.delete()
    await asyncio.sleep(1)
    await message.delete()










