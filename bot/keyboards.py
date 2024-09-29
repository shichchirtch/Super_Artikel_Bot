from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

arab_button = InlineKeyboardButton(text='🇸🇦', callback_data='ar')
farsi_button = InlineKeyboardButton(text='🇮🇷', callback_data='fa' )
ukr_button = InlineKeyboardButton(text='🇺🇦', callback_data='uk' )
rus_button = InlineKeyboardButton(text='🇷🇺', callback_data='ru')
isp_button = InlineKeyboardButton(text='🇪🇸', callback_data='es' )
fra_button = InlineKeyboardButton(text='🇫🇷', callback_data='fr' )
turkei_button = InlineKeyboardButton(text='🇹🇷', callback_data='tr')
pol_button = InlineKeyboardButton(text='🇵🇱', callback_data='pl' )
gree_button = InlineKeyboardButton(text='🇬🇷', callback_data='el' )
serb_button = InlineKeyboardButton(text='🇷🇸', callback_data='sr-Cyrl' )
eng_button = InlineKeyboardButton(text='🇬🇧', callback_data='en' )

lan_kb = InlineKeyboardMarkup(
            inline_keyboard=[[arab_button], [farsi_button],[ukr_button],
                             [isp_button],[rus_button],[turkei_button],
                             [pol_button],[serb_button],[eng_button]])

pre_start_button = KeyboardButton(text='/start')

pre_start_clava = ReplyKeyboardMarkup(
    keyboard=[[pre_start_button]],
    resize_keyboard=True
)

pril_button = InlineKeyboardButton(text='Adlektive', url='https://telegra.ph/Der-Deklination-von-Artikeln-und-Adjektiven-09-20')
verb_button = InlineKeyboardButton(text='Verben', url='https://telegra.ph/Unregelmäßige-Verben-09-21')


gram_kb = InlineKeyboardMarkup(inline_keyboard=[[pril_button], [verb_button]])
###########################################

erste_button = InlineKeyboardButton(text='Stunde 1', callback_data='1')
zweite_button = InlineKeyboardButton(text='Stunde 2', callback_data='2')
dritte_button = InlineKeyboardButton(text='Stunde 3', callback_data='3')
vierte_button = InlineKeyboardButton(text='Stunde 4', callback_data='4')
funfte_button = InlineKeyboardButton(text='Stunde 5', callback_data='5')
sex_button = InlineKeyboardButton(text='Stunde 6', callback_data='6')
siben_button = InlineKeyboardButton(text='Stunde 7', callback_data='7')
eight_button = InlineKeyboardButton(text='Stunde 8', callback_data='8')
neun_button = InlineKeyboardButton(text='Stunde 9', callback_data='9')
zehn_button = InlineKeyboardButton(text='Stunde 10', callback_data='10')
elf_button = InlineKeyboardButton(text='Stunde 11', callback_data='11')
zwelfe_button = InlineKeyboardButton(text='Stunde 12', callback_data='12')
f13_button = InlineKeyboardButton(text='Stunde 13', callback_data='13')
f14_button = InlineKeyboardButton(text='Stunde 14', callback_data='14')
f15_button = InlineKeyboardButton(text='Stunde 15', callback_data='15')
f16_button = InlineKeyboardButton(text='Stunde 16', callback_data='16')


ws_kb = InlineKeyboardMarkup(inline_keyboard=[[erste_button], [zweite_button], [dritte_button],
                                              [vierte_button], [funfte_button], [sex_button]])


ja_button = InlineKeyboardButton(text='✅', callback_data='ja')
nein_button = InlineKeyboardButton(text='❌', callback_data='nein')
ja_nein_kb = InlineKeyboardMarkup(inline_keyboard=[[nein_button, ja_button]])

#################################################################################################

one_button = InlineKeyboardButton(text='Stunde 1', callback_data='one')
two_button = InlineKeyboardButton(text='Stunde 2', callback_data='two')
three_button = InlineKeyboardButton(text='Stunde 3', callback_data='three')
four_button = InlineKeyboardButton(text='Stunde 4', callback_data='four')
five_button = InlineKeyboardButton(text='Stunde 5', callback_data='five')
six_button = InlineKeyboardButton(text='Stunde 6', callback_data='six')
sevan_button = InlineKeyboardButton(text='Stunde 7', callback_data='sevan')
acht_button = InlineKeyboardButton(text='Stunde 8', callback_data='eight')
nine_button = InlineKeyboardButton(text='Stunde 9', callback_data='nine')
ten_button = InlineKeyboardButton(text='Stunde 10', callback_data='ten')
elevan_button = InlineKeyboardButton(text='Stunde 11', callback_data='elevan')
twelve_button = InlineKeyboardButton(text='Stunde 12', callback_data='twelve')
t13_button = InlineKeyboardButton(text='Stunde 13', callback_data='t13')
t14_button = InlineKeyboardButton(text='Stunde 14', callback_data='t14')
t15_button = InlineKeyboardButton(text='Stunde 15', callback_data='t15')
t16_button = InlineKeyboardButton(text='Stunde 16', callback_data='t16')

selber_button = InlineKeyboardButton(text='Mein Wortschatz', callback_data='Wortschatz')


lernen_kb = (
    InlineKeyboardMarkup(
        inline_keyboard=
        [[one_button], [two_button], [three_button],[four_button],[five_button],[sex_button],[selber_button]]))

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

weis_button = InlineKeyboardButton(text='😊', callback_data='weis')
nicht_weis_button = InlineKeyboardButton(text='🤷', callback_data='nicht')

weis_kb = InlineKeyboardMarkup(inline_keyboard=[[nicht_weis_button, weis_button]])

####################################################################################################

w_shatz_button = InlineKeyboardButton(text='Meine Wortschatz', callback_data='wh')
add_note_button = InlineKeyboardButton(text='Neue Notiz', callback_data='add_notiz')
show_note_button = InlineKeyboardButton(text='Zeigen meine Notiz', callback_data='zeigen_notiz')

zeigen_kb = InlineKeyboardMarkup(inline_keyboard=[[w_shatz_button],[add_note_button], [show_note_button]])

##################################################################################################

ns_button = InlineKeyboardButton(text='🤢', callback_data='no_spam')
sp_button = InlineKeyboardButton(text='🤓', callback_data='spam')

spam_kb = InlineKeyboardMarkup(inline_keyboard=[[ns_button, sp_button]])

####################################################################################################


it_a1_button = InlineKeyboardButton(text='A 1', callback_data='IT_A1')
it_a2_button = InlineKeyboardButton(text='A 2', callback_data='IT_A2')
it_b1_button = InlineKeyboardButton(text='B 1', callback_data='IT_B1')

it_buch_kb = InlineKeyboardMarkup(inline_keyboard=[[it_a1_button], [it_a2_button], [it_b1_button]])



































