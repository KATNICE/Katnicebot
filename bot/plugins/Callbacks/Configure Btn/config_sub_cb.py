import re
import time
import asyncio

from pyrogram import Client, filters
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from . import (
    FIND, 
    recacher,
    Database,
    admin_list,
    ACTIVE_CHATS,
    CHAT_DETAILS,
    INVITE_LINK, 
    remove_emoji,
    gen_invite_links,
)

db = Database()


@Client.on_callback_query(filters.regex(r"mr_count\((.+)\)"), group=2)
async def cb_max_buttons(bot, update: CallbackQuery):
    """
    A Callback Funtion For Changing The Count Of Result To Be Shown Per Page
    """
    global CHAT_DETAILS
    query_data = update.data
    chat_id = update.message.chat.id
    chat_name = remove_emoji(update.message.chat.title)
    user_id = update.from_user.id
    
    chat_dict = CHAT_DETAILS.get(str(chat_id))
    chat_admins = chat_dict.get("admins") if chat_dict != None else None

    if ( chat_dict or chat_admins ) == None: # Make Admin's ID List
        chat_admins = await admin_list(chat_id, bot, update)

    if user_id not in chat_admins:
        return

    count, chat_id = re.findall(r"mr_count\((.+)\)", query_data)[0].split("|", 1)

    text = f"<i>Choisissez le 'nombre maximal de filtres par page' que vous souhaitez pour chaque résultat de filtre affiché dans</i> <code>{chat_name}</code>"

    buttons = [
        [
            InlineKeyboardButton
                (
                    "5 filtres", callback_data=f"set(per_page|5|{chat_id}|{count})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "10 filtres", callback_data=f"set(per_page|10|{chat_id}|{count})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "15 filtres", callback_data=f"set(per_page|15|{chat_id}|{count})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "20 filtres", callback_data=f"set(per_page|20|{chat_id}|{count})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "25 filtres", callback_data=f"set(per_page|25|{chat_id}|{count})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "30 filtres", callback_data=f"set(per_page|30|{chat_id}|{count})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "🔙 Retour", callback_data=f"config({chat_id})"
                )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(buttons)

    await update.message.edit_text(
        text, reply_markup=reply_markup, parse_mode="html"
    )



@Client.on_callback_query(filters.regex(r"mp_count\((.+)\)"), group=2)
async def cb_max_page(bot, update: CallbackQuery):
    """
    A Callback Funtion For Changing The Count Of Maximum Result Pages To Be Shown
    """
    global CHAT_DETAILS
    query_data = update.data
    chat_id = update.message.chat.id
    chat_name = remove_emoji(update.message.chat.title)
    user_id = update.from_user.id
    
    chat_dict = CHAT_DETAILS.get(str(chat_id))
    chat_admins = chat_dict.get("admins") if chat_dict != None else None

    if ( chat_dict or chat_admins ) == None: # Make Admin's ID List
        chat_admins = await admin_list(chat_id, bot, update)

    if user_id not in chat_admins:
        return

    count, chat_id = re.findall(r"mp_count\((.+)\)", query_data)[0].split("|", 1)
    
    text = f"<i>Choisissez le 'nombre maximal de pages de filtre' que vous souhaitez pour chaque résultat de filtre affiché dans</i> <code>{chat_name}</code>"
    
    buttons = [

        [
            InlineKeyboardButton
                (
                    "2 Pages", callback_data=f"set(pages|2|{chat_id}|{count})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "4 Pages", callback_data=f"set(pages|4|{chat_id}|{count})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "6 Pages", callback_data=f"set(pages|6|{chat_id}|{count})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "8 Pages", callback_data=f"set(pages|8|{chat_id}|{count})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "10 Pages", callback_data=f"set(pages|10|{chat_id}|{count})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "🔙 Retour", callback_data=f"config({chat_id})"
                )
        ]

    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await update.message.edit_text(
        text, reply_markup=reply_markup, parse_mode="html"
    )



@Client.on_callback_query(filters.regex(r"mf_count\((.+)\)"), group=2)
async def cb_max_results(bot, update: CallbackQuery):
    """
    A Callback Funtion For Changing The Count Of Maximum Files TO Be Fetched From Database
    """
    global CHAT_DETAILS
    query_data = update.data
    chat_id = update.message.chat.id
    chat_name = remove_emoji(update.message.chat.title)
    user_id = update.from_user.id
    
    chat_dict = CHAT_DETAILS.get(str(chat_id))
    chat_admins = chat_dict.get("admins") if chat_dict != None else None

    if ( chat_dict or chat_admins ) == None: # Make Admin's ID List
        chat_admins = await admin_list(chat_id, bot, update)

    if user_id not in chat_admins:
        return

    count, chat_id = re.findall(r"mf_count\((.+)\)", query_data)[0].split("|", 1)

    text = f"<i>Choisissez le 'filtre maximal' que vous souhaitez récupérer à partir de la base de données pour chaque résultat de filtre affiché dans</i> <code>{chat_name}</code>"

    buttons = [

        [
            InlineKeyboardButton
                (
                    "50 Résultats", callback_data=f"set(results|50|{chat_id}|{count})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "100 Résultats", callback_data=f"set(results|100|{chat_id}|{count})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "150 Résultats", callback_data=f"set(results|150|{chat_id}|{count})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "200 Résultats", callback_data=f"set(results|200|{chat_id}|{count})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "250 Results", callback_data=f"set(results|250|{chat_id}|{count})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "300 Results", callback_data=f"set(results|300|{chat_id}|{count})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "🔙 Retour", callback_data=f"config({chat_id})"
                )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(buttons)

    await update.message.edit_text(
        text, reply_markup=reply_markup, parse_mode="html"
    )



@Client.on_callback_query(filters.regex(r"show_invites\((.+)\)"), group=2)
async def cb_show_invites(bot, update: CallbackQuery):
    """
    A Callback Funtion For Enabling Or Diabling Invite Link Buttons
    """
    global CHAT_DETAILS
    query_data = update.data
    chat_id = update.message.chat.id
    user_id = update.from_user.id
    
    chat_dict = CHAT_DETAILS.get(str(chat_id))
    chat_admins = chat_dict.get("admins") if chat_dict != None else None

    if ( chat_dict or chat_admins ) == None: # Make Admin's ID List
        chat_admins = await admin_list(chat_id, bot, update)

    if user_id not in chat_admins:
        return

    value, chat_id = re.findall(r"show_invites\((.+)\)", query_data)[0].split("|", 1)
    
    value = True if value=="True" else False
    
    if value:
        buttons= [
            [
                InlineKeyboardButton
                    (
                        "Désactiver ❌", callback_data=f"set(showInv|False|{chat_id}|{value})"
                    )
            ],
            [
                InlineKeyboardButton
                    (
                        "Retour 🔙", callback_data=f"config({chat_id})"
                    )
            ]
        ]
    
    else:
        buttons =[
            [
                InlineKeyboardButton
                    (
                        "Activé ✔", callback_data=f"set(showInv|True|{chat_id}|{value})"
                    )
            ],
            [
                InlineKeyboardButton
                    (
                        "Retour 🔙", callback_data=f"config({chat_id})"
                    )
            ]
        ]
    
    text=f"<i>Cette configuration vous aidera à afficher le lien d'invitation de toutes les discussions actives ainsi que les résultats du filtre pour les utilisateurs qui ont rejoints.....</i>"
    
    reply_markup=InlineKeyboardMarkup(buttons)
    
    await update.message.edit_text(
        text,
        reply_markup=reply_markup,
        parse_mode="html"
    )



@Client.on_callback_query(filters.regex(r"inPM\((.+)\)"), group=2)
async def cb_pm_file(bot, update: CallbackQuery):
    """
    A Callback Funtion For Enabling Or Diabling File Transfer Through Bot PM
    """
    global CHAT_DETAILS
    query_data = update.data
    chat_id = update.message.chat.id
    user_id = update.from_user.id
    
    chat_dict = CHAT_DETAILS.get(str(chat_id))
    chat_admins = chat_dict.get("admins") if chat_dict != None else None

    if ( chat_dict or chat_admins ) == None: # Make Admin's ID List
        chat_admins = await admin_list(chat_id, bot, update)

    if user_id not in chat_admins:
        return

    value, chat_id = re.findall(r"inPM\((.+)\)", query_data)[0].split("|", 1)

    value = True if value=="True" else False
    
    if value:
        buttons= [
            [
                InlineKeyboardButton
                    (
                        "Désactiver ❎", callback_data=f"set(inPM|False|{chat_id}|{value})"
                    )
            ],
            [
                InlineKeyboardButton
                    (
                        "Retour 🔙", callback_data=f"config({chat_id})"
                    )
            ]
        ]
    
    else:
        buttons =[
            [
                InlineKeyboardButton
                    (
                        "Activé ✅", callback_data=f"set(inPM|True|{chat_id}|{value})"
                    )
            ],
            [
                InlineKeyboardButton
                    (
                        "Retour 🔙", callback_data=f"config({chat_id})"
                    )
            ]
        ]
    
    text=f"<i>Cette configuration vous aidera à activer/désactiver le transfert de fichiers via Katnice en Privée sans les rediriger vers le canal....</i>"
    
    reply_markup=InlineKeyboardMarkup(buttons)
    
    await update.message.edit_text(
        text,
        reply_markup=reply_markup,
        parse_mode="html"
    )



@Client.on_callback_query(filters.regex(r"accuracy\((.+)\)"), group=2)
async def cb_accuracy(bot, update: CallbackQuery):
    """
    A Callaback Funtion to control the accuracy of matching results
    that the bot should return for a query....
    """
    global CHAT_DETAILS
    chat_id = update.message.chat.id
    chat_name = update.message.chat.title
    user_id = update.from_user.id
    query_data = update.data
    
    chat_dict = CHAT_DETAILS.get(str(chat_id))
    chat_admins = chat_dict.get("admins") if chat_dict != None else None

    if ( chat_dict or chat_admins ) == None: # Make Admin's ID List
        chat_admins = await admin_list(chat_id, bot, update)
    
    if user_id not in chat_admins:
        return

    val, chat_id = re.findall(r"accuracy\((.+)\)", query_data)[0].split("|", 1)
    
    text = f"<i>Choisissez votre 'pourcentage de précision' souhaité pour chaque résultat de filtre affiché dans</i> <code>{chat_name}</code>\n\n"
    text+= f"<i>NB : Plus la valeur est élevée, de meilleurs résultats correspondants seront fournis... Et si la valeur est inférieure, cela affichera plus de résultats \
        Ce qui est similaire à la recherche par requête (ne sera pas précis)....</i>"

    buttons = [
        [
            InlineKeyboardButton
                (
                    "100 %", callback_data=f"set(accuracy|1.00|{chat_id}|{val})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "80 %", callback_data=f"set(accuracy|0.80|{chat_id}|{val})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "65 %", callback_data=f"set(accuracy|0.65|{chat_id}|{val})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "60 %", callback_data=f"set(accuracy|0.60|{chat_id}|{val})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "55 %", callback_data=f"set(accuracy|0.55|{chat_id}|{val})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "50 %", callback_data=f"set(accuracy|0.50|{chat_id}|{val})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "🔙 Retour", callback_data=f"config({chat_id})"
                )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(buttons)

    await update.message.edit_text(
        text, reply_markup=reply_markup, parse_mode="html"
    )

