import re
import time

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from . import (
    CHAT_DETAILS,
    admin_list,
    time_formatter,
    start_uptime
)

@Client.on_callback_query(filters.regex(r"about\((.+)\)"), group=2)
async def cb_about(bot, update: CallbackQuery):
    """
    A Callback Funtion For Showing About Section In Bot Setting Menu
    """
    global CHAT_DETAILS
    chat_id = update.message.chat.id
    user_id = update.from_user.id
    
    chat_dict = CHAT_DETAILS.get(str(chat_id))
    chat_admins = chat_dict.get("admins") if chat_dict != None else None

    if ( chat_dict or chat_admins ) == None: # Make Admin's ID List
        chat_admins = await admin_list(chat_id, bot, update)

    if user_id not in chat_admins:
        return

    text=f"<i><u>Statut du bot</u></i>\n"
    text+=f"\n<b><i>Temps de disponibilité du bot:</i></b> <code>{time_formatter(time.time() - start_uptime)}</code>\n"
    text+=f"\n<b><i>Fonction de Katnice:</i></b> <i>Filtrer automatiquement les fichiers</i>\n"
    text+=f"""\n<b><i>Bot Support:</i></b> <a href="https://t.me/Sharing_Club">@Shar_Group</a>\n"""
    text+="""\n<b><i>Source Code:</i></b> <a href="https://t.me/Shar_Group">Source</a>"""

    buttons = [
        [
            InlineKeyboardButton
                (
                    "My Dev ⚡", url="https://t.me/Philanthrpe"
                ),
                
            InlineKeyboardButton
                (
                    "🔙 Retour", callback_data="settings"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "Fermer 🔐", callback_data="close"
                )
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await update.message.edit_text(
        text, reply_markup=reply_markup, parse_mode="html"
    )
