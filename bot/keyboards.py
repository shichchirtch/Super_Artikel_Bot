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


ws_kb = InlineKeyboardMarkup(inline_keyboard=[[erste_button], [zweite_button], [dritte_button]])


ja_button = InlineKeyboardButton(text='✅', callback_data='ja')
nein_button = InlineKeyboardButton(text='❌', callback_data='nein')
ja_nein_kb = InlineKeyboardMarkup(inline_keyboard=[[nein_button, ja_button]])

#################################################################################################

one_button = InlineKeyboardButton(text='Stunde 1', callback_data='one')
two_button = InlineKeyboardButton(text='Stunde 2', callback_data='two')
three_button = InlineKeyboardButton(text='Stunde 3', callback_data='three')
selber_button = InlineKeyboardButton(text='Mein Wortschatz', callback_data='Wortschatz')


lernen_kb = InlineKeyboardMarkup(inline_keyboard=[[one_button], [two_button],
                                                  [three_button],[selber_button]])

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




































