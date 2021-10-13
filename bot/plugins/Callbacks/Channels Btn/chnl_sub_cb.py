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


@Client.on_callback_query(filters.regex(r"^connect\((.+)\)"), group=2)
async def cb_connect(bot, update: CallbackQuery):
    """
    A Callback Funtion Helping The user To Make A Chat Active Chat Which Will
    Make The Bot To Fetch Results From This Channel Too
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

    channel_id, channel_name = re.findall(r"connect\((.+)\)", query_data)[0].split("|", 1)
    channel_id = int(channel_id)
    
    f_count = await db.cf_count(chat_id, channel_id)
    
    add_active = await db.update_active(chat_id, channel_id, channel_name)
    
    if not add_active:
        await update.answer(f"{channel_name} Est déjà en connexion active", show_alert=True)
        return

    text= f"<i>Connexion réussie à</i> <code>{channel_name}</code>\n"
    text+=f"\n<i>Informations sur <b>{channel_name}</b></i>\n"
    text+=f"\n<i>Nom du Canal:</i> <code>{channel_name}</code>\n"
    text+=f"\n<i>L'ID du Canal:</i> <code>{channel_id}</code>\n"
    text+=f"\n<i>Fichiers du Canal:</i> <code>{f_count}</code>\n"
    text+=f"\n<i>Statut actuel:</i> <code>Connected</code>\n"

    buttons = [
                [
                    InlineKeyboardButton
                        (
                            "🚨 Déconnecter 🚨", callback_data=f"warn({channel_id}|{channel_name}|disconnect)"
                        ),
                    
                    InlineKeyboardButton
                        (
                            "Supprimer ❌", callback_data=f"warn({channel_id}|{channel_name}|c_delete)"
                        )
                ]
    ]
    
    buttons.append(
            [
                InlineKeyboardButton
                    (
                        "Supprimer les filtres ⚠", callback_data=f"warn({channel_id}|{channel_name}|f_delete)"
                    )
            ]
    )
    
    buttons.append(
            [
                InlineKeyboardButton
                    (
                        "🔙 Retour", callback_data=f"channel_list({chat_id})"
                    )
            ]
    )
    await recacher(chat_id, False, True, bot, update)
    
    reply_markup = InlineKeyboardMarkup(buttons)
        
    await update.message.edit_text(
            text, reply_markup=reply_markup, parse_mode="html"
        )



@Client.on_callback_query(filters.regex(r"disconnect\((.+)\)"), group=2)
async def cb_disconnect(bot, update: CallbackQuery):
    """
    A Callback Funtion Helping The user To Make A Chat inactive Chat Which Will
    Make The Bot To Avoid Fetching Results From This Channel
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

    channel_id, channel_name = re.findall(r"connect\((.+)\)", query_data)[0].split("|", 1)
    
    f_count = await db.cf_count(chat_id, int(channel_id))
    
    remove_active = await db.del_active(chat_id, int(channel_id))
    
    if not remove_active:
        await update.answer("Impossible de répondre à votre demande...\n Référer vous à @Shar_Group avec le journal du bot", show_alert=True)
        return
    
    text= f"<i>Déconnecté avec succès de</i> <code>{channel_name}</code>\n"
    text+=f"\n<i>Informations sur <b>{channel_name}</b></i>\n"
    text+=f"\n<i>Nom du Canal:</i> <code>{channel_name}</code>\n"
    text+=f"\n<i>L'ID du Canal:</i> <code>{channel_id}</code>\n"
    text+=f"\n<i>Fichiers du Canal:</i> <code>{f_count}</code>\n"
    text+=f"\n<i>Statut actuel:</i> <code>Disconnected</code>\n"
    
    buttons = [ 
                [
                    InlineKeyboardButton
                        (
                            "💠 Connecter 💠", callback_data=f"warn({channel_id}|{channel_name}|connect)"
                        ),
                    
                    InlineKeyboardButton
                        (
                            "Supprimer ❌", callback_data=f"warn({channel_id}|{channel_name}|c_delete)"
                        )
                ]
    ]
    
    buttons.append(
            [
                InlineKeyboardButton
                    (
                        "Supprimer les filtres ⚠", callback_data=f"warn({channel_id}|{channel_name}|f_delete)"
                    )
            ]
    )
    
    buttons.append(
            [
                InlineKeyboardButton
                    (
                        "🔙 Retour", callback_data=f"channel_list({chat_id})"
                    )
            ]
    )
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await recacher(chat_id, False, True, bot, update)

    await update.message.edit_text(
            text, reply_markup=reply_markup, parse_mode="html"
        )



@Client.on_callback_query(filters.regex(r"c_delete\((.+)\)"), group=2)
async def cb_channel_delete(bot, update: CallbackQuery):
    """
    A Callback Funtion For Delete A Channel Connection From A Group Chat History
    Along With All Its Filter Files
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

    channel_id, channel_name = re.findall(r"c_delete\((.+)\)", query_data)[0].split("|", 1)
    channel_id = int(channel_id)
    
    c_delete = await db.del_chat(chat_id, channel_id)
    a_delete = await db.del_active(chat_id, channel_id) # pylint: disable=unused-variable
    f_delete = await db.del_filters(chat_id, channel_id)

    if (c_delete and f_delete ):
        text=f"<code>{channel_name} [ {channel_id} ]</code> A été supprimé avec succès et tous ses fichiers ont été effacés de la base de données...."

    else:
        text=f"<i>Impossible de supprimer le canal et tous ses fichiers de la base de données avec succès....</i>\n<i>Veuillez réessayer après...Assurez-vous également de vérifier les journaux..!!</i>"
        await update.answer(text=text, show_alert=True)

    buttons = [
        [
            InlineKeyboardButton
                (
                    "🔙 Retour", callback_data=f"channel_list({chat_id})"
                ),
                
            InlineKeyboardButton
                (
                    "Fermer 🔐", callback_data="close"
                )
        ]
    ]

    await recacher(chat_id, True, True, bot, update)
    
    reply_markup=InlineKeyboardMarkup(buttons)

    await update.message.edit_text(
        text, reply_markup=reply_markup, parse_mode="html"
    )



@Client.on_callback_query(filters.regex(r"f_delete\((.+)\)"), group=2)
async def cb_filters_delete(bot, update: CallbackQuery):
    """
    A Callback Funtion For Delete A Specific Channel's Filters Connected To A Group
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

    channel_id, channel_name = re.findall(r"f_delete\((.+)\)", query_data)[0].split("|", 1)

    f_delete = await db.del_filters(chat_id, int(channel_id))

    if not f_delete:
        text="<b><i>Oops..!!</i></b>\n\nA rencontré une erreur lors de la suppression des filtres....\nVeuillez vérifier les journaux...."
        await update.answer(text=text, show_alert=True)
        return

    text =f"Tous les Filtres de <code>{channel_id}[{channel_name}]</code> A été supprimé avec succès de ma base de données.."

    buttons=[
        [
            InlineKeyboardButton
                (
                    "Retour", callback_data="settings"
                ),
            
            InlineKeyboardButton
                (
                    "Fermer", callback_data="close"
                )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(buttons)

    await update.message.edit_text(
        text, reply_markup=reply_markup, parse_mode="html"
    )
    

#
    # @Client.on_callback_query(filters.regex(r"^gcmds\((.)\)"), group=2)
    # async def cb_gcmds(bot, update: CallbackQuery):
    #     """
    #     A Callback Funtion to Connect, Disconnect, Delete, Delete Filters of, 
    #     All Connected Chat in 1 GO
    #     """
    #     global CHAT_DETAILS
    #     query_data = update.data
    #     chat_id = update.message.chat.id
    #     chat_name = update.message.chat.title
    #     user_id = update.from_user.id
        
    #     print(user_id)
            
    #     chat_dict = CHAT_DETAILS.get(str(chat_id))
    #     chat_admins = chat_dict.get("admins") if chat_dict != None else None

    #     if ( chat_dict or chat_admins ) == None: # Make Admin's ID List
    #         chat_admins = await admin_list(chat_id, bot, update)

    #     if user_id not in chat_admins:
    #         print(user_id)
    #         print(chat_admins)
    #         return
        
    #     chat_id, action = re.findall(r"gcmds\((.)\)", query_data)[0].split("|", 1)
        
    #     if action == "conn":
    #         await db.add_all_chat_as_active(chat_id)
    #         await update.answer("Sucessfully Made All Chat Connection Active.....")
        
    #     elif action == "disconn":
    #         await db.delall_active(chat_id)
    #         await update.answer("Sucessfully Disabled All Active Chats.....")

    #     elif action == "c_delete":
    #         await db.delete_all(chat_id)
    #         await update.answer("Sucessfully Deleted All Data About This Group From DB")
        
    #     elif action == "f_delete":
    #         await db.delall_filters(chat_id)
    #         await update.answer("Sucessfully Deleted All Files Connected With This Chat...")
        

        
    #     f_count = await db.tf_count(chat_id) 
    #     connected_chats = await db.find_chat(chat_id)
    #     active_chats = await db.find_active(chat_id)
        
    #     db_cids = None
    #     db_cnames = None
    #     total_chats = 0
        
    #     if connected_chats: # Checks for active chats connected to a chat
    #         dicts = connected_chats["chat_ids"]
    #         adicts = active_chats["chats"]
    #         adb_cids = [ int(x["chat_id"]) for x in adicts ]
    #         db_cids = []
    #         db_cnames = []
    #         for x in dicts:
    #             cid = x["chat_id"]
    #             cname = x["chat_name"]
                
    #             db_cids.append(cid)
    #             if cid in adb_cids:
    #                 cname + " (A)"
    #             db_cnames.append(db_cnames)
        
    #         total_chats = len(db_cids)

    #     text=f"<i>Infos sur tous connectés de <b>{chat_name}</b></i>\n"
    #     text+=f"\n<i>Nombre total de Chats connectés:</i> {total_chats}"
        
    #     text+=f"\n<i>Noms des chaînes:</i>\n"
        
    #     for ch in db_cnames:
    #         text+=f"                   <code>{ch}</code>\n"
            
    #     text+=f"\n<i>ID de chaîne:</i>\n"
        
    #     for ch in db_cnames:
    #         text+=f"\n                 <code>{ch}</code>\n"
        
    #     text+=f"\n<i>Nombre total de fichiers dans la BD:</i> <code>{f_count}</code>\n"



    #     buttons = [ 
    #                 [
    #                     InlineKeyboardButton
    #                         (
    #                             "💠 Tout connecté 💠", callback_data=f"warn({chat_id}|conn|gcmds)"
    #                         ),
                        
    #                     InlineKeyboardButton
    #                         (
    #                             "🚨 Tout Déconnecté 🚨", callback_data=f"warn({chat_id}|disconn|gcmds)"
    #                         )
    #                 ]
    #     ]


    #     buttons.append(
    #             [                    
    #                 InlineKeyboardButton
    #                     (
    #                         "Supprimer toutes les discussions ❌", callback_data=f"warn({chat_id}|c_delete|gcmds)"
    #                     )
    #             ]
    #     )


    #     buttons.append(
    #             [
    #                 InlineKeyboardButton
    #                     (
    #                         "Supprimer tous les filtres ⚠", callback_data=f"warn({chat_id}|f_delete|gcmds)"
    #                     )
    #             ]
    #     )
        
    #     buttons.append(
    #             [
    #                 InlineKeyboardButton
    #                     (
    #                         "🔙 Retour", callback_data=f"channel_list({chat_id})"
    #                     )
    #             ]
    #     )

    #     reply_markup = InlineKeyboardMarkup(buttons)
            
    #     await update.message.edit_text(
    #             text, reply_markup=reply_markup, parse_mode="html"
    #         )

