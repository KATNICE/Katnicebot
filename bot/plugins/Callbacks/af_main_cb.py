import re
import time
import asyncio

from pyrogram import Client, filters
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
 
from . import (
    FIND,
    Database,
    admin_list,
    ACTIVE_CHATS,
    CHAT_DETAILS,
    INVITE_LINK, 
    remove_emoji,
    gen_invite_links,
)
from bot import Translation

db = Database()



@Client.on_callback_query(filters.regex(r"navigate\((.+)\)"), group=2)
async def cb_navg(bot, update: CallbackQuery):
    """
    A Callback Funtion For The Next Button Appearing In Results
    """
    global CHAT_DETAILS
    query_data = update.data
    chat_id = update.message.chat.id
    user_id = update.from_user.id
    
    index_val, btn, query = re.findall(r"navigate\((.+)\)", query_data)[0].split("|", 2)
    try:
        ruser_id = update.message.reply_to_message.from_user.id
    except Exception as e:
        print(e)
        ruser_id = None
    
    chat_dict = CHAT_DETAILS.get(str(chat_id))
    chat_admins = chat_dict.get("admins") if chat_dict != None else None

    # Make Admin's ID List
    if ( chat_dict or chat_admins ) == None: 
        chat_admins = await admin_list(chat_id, bot, update)
    
    # Checks if user is same as requested user or is admin
    if not ((user_id == ruser_id) or (user_id in chat_admins)):
        await update.answer("Nice Try ;)",show_alert=True)
        return


    if btn == "next":
        index_val = int(index_val) + 1
    elif btn == "back":
        index_val = int(index_val) - 1
    
    achats = ACTIVE_CHATS[str(chat_id)]
    configs = await db.find_chat(chat_id)
    pm_file_chat = configs["configs"]["pm_fchat"]
    show_invite = configs["configs"]["show_invite_link"]
    
    # show_invite = (False if pm_file_chat == True else show_invite) # turn show_invite to False if pm_file_chat is True

    results = FIND.get(query).get("results")
    leng = FIND.get(query).get("total_len")
    max_pages = FIND.get(query).get("max_pages")
    
    try:
        temp_results = results[index_val].copy()
    except IndexError:
        return # Quick Fix🏃🏃
    except Exception as e:
        print(e)
        return

    if ((index_val + 1 )== max_pages) or ((index_val + 1) == len(results)): # Max Pages
        temp_results.append([
            InlineKeyboardButton("⏪ Précédente", callback_data=f"navigate({index_val}|back|{query})")
        ])

    elif int(index_val) == 0:
        pass

    else:
        temp_results.append([
            InlineKeyboardButton("⏪ Précédente", callback_data=f"navigate({index_val}|back|{query})"),
            InlineKeyboardButton("Suivante ⏩", callback_data=f"navigate({index_val}|next|{query})")
        ])

    if not int(index_val) == 0:    
        temp_results.append([
            InlineKeyboardButton(f"⭕️ Page {index_val + 1}/{len(results) if len(results) < max_pages else max_pages} ⭕️", callback_data="ignore")
        ])
    
    if show_invite and int(index_val) !=0 :
        
        ibuttons = []
        achatId = []
        await gen_invite_links(configs, chat_id, bot, update)
        
        for x in achats["chats"] if isinstance(achats, dict) else achats:
            achatId.append(int(x["chat_id"])) if isinstance(x, dict) else achatId.append(x)
        
        for y in INVITE_LINK.get(str(chat_id)):
            
            chat_id = int(y["chat_id"])
            
            if chat_id not in achatId:
                continue
            
            chat_name = y["chat_name"]
            invite_link = y["invite_link"]
            
            if ((len(ibuttons)%2) == 0):
                ibuttons.append(
                    [
                        InlineKeyboardButton
                            (
                                f"⚜ {chat_name} ⚜", url=invite_link
                            )
                    ]
                )

            else:
                ibuttons[-1].append(
                    InlineKeyboardButton
                        (
                            f"⚜ {chat_name} ⚜", url=invite_link
                        )
                )
            
        for x in ibuttons:
            temp_results.insert(0, x)
        ibuttons = None
        achatId = None
    
    reply_markup = InlineKeyboardMarkup(temp_results)
    
    text=f"<i>Trouver</i> <code>{leng}</code> <i>Résultats de votre requête:</i> <code>{query}</code>"
        
    try:
        await update.message.edit(
                text,
                reply_markup=reply_markup,
                parse_mode="html"
        )
        
    except FloodWait as f: # Flood Wait Caused By Spamming Next/Back Buttons
        await asyncio.sleep(f.x)
        await update.message.edit(
                text,
                reply_markup=reply_markup,
                parse_mode="html"
        )



@Client.on_callback_query(filters.regex(r"settings"), group=2)
async def cb_settings(bot, update: CallbackQuery):
    """
    A Callback Funtion For Back Button in /settings Command
    """
    global CHAT_DETAILS
    chat_id = update.message.chat.id
    user_id = update.from_user.id

    chat_dict = CHAT_DETAILS.get(str(chat_id))
    chat_admins = chat_dict.get("admins") if chat_dict != None else None

    if ( chat_dict or chat_admins ) == None: # Make Admin's ID List
        chat_admins = await admin_list(chat_id, bot, update)

    if user_id not in chat_admins: # Check If User Is Admin
        return

    bot_status = await bot.get_me()
    bot_fname= bot_status.first_name
    
    text =f"<i>{bot_fname}'s</i> Panneau de configuration de Katnice.....\n"
    text+=f"\n<i>Vous pouvez utiliser ce menu pour modifier la connectivité et connaître l'état de chaque canal connecté, modifier les types de filtre, configurer les résultats du filtre et connaître l'état de votre groupe...</i>"
    
    buttons = [
        [
            InlineKeyboardButton
                (
                    "Canaux", callback_data=f"channel_list({chat_id})"
                ), 
            
            InlineKeyboardButton
                (
                    "Types de Filtres", callback_data=f"types({chat_id})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "Configurer 🛠", callback_data=f"config({chat_id})"
                )
        ], 
        [
            InlineKeyboardButton
                (
                    "Status", callback_data=f"status({chat_id})"
                ),
            
            InlineKeyboardButton
                (
                    "À propos", callback_data=f"about({chat_id})"
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
        text, 
        reply_markup=reply_markup, 
        parse_mode="html"
        )



@Client.on_callback_query(filters.regex(r"warn\((.+)\)"), group=2)
async def cb_warn(bot, update: CallbackQuery):
    """
    A Callback Funtion For Acknowledging User's About What Are They Upto
    """
    global CHAT_DETAILS
    query_data = update.data
    chat_id = update.message.chat.id
    chat_name = remove_emoji(update.message.chat.title)
    chat_name = chat_name.encode('ascii', 'ignore').decode('ascii')[:35]
    user_id = update.from_user.id

    chat_dict = CHAT_DETAILS.get(str(chat_id))
    chat_admins = chat_dict.get("admins") if chat_dict != None else None

    if ( chat_dict or chat_admins ) == None: # Make Admin's ID List
        chat_admins = await admin_list(chat_id, bot, update)

    if user_id not in chat_admins:
        return
    
    channel_id, channel_name, action = re.findall(r"warn\((.+)\)", query_data)[0].split("|", 2)
    
    if action == "connect":
        text=f"<i>Êtes-vous sûr de vouloir activer la connexion avec</i> <code>{channel_name}</code><i>..???</i>\n"
        text+=f"\n<i>Cela affichera les liens de fichiers de</i> <code>{channel_name}</code> <i>Tout en affichant les résultats</i>..."


    elif action == "disconnect":
        text=f"<i>Êtes-vous sûr de vouloir désactiver</i> <code>{channel_name}</code> <i>Connexion avec le groupe???....</i>\n"
        text+=f"\n<i>Les fichiers DB seront toujours là et vous pourrez vous reconnecter à ce canal à tout moment à partir du menu Paramètres sans ajouter à nouveau de fichiers à la base de données....</i>\n"
        text+=f"\n<i>Cette désactivation ne fait que masquer les résultats des résultats du filtre...</i>"


    elif action == "c_delete":
        text=f"<i>Êtes-vous sûr de vouloir vous déconnecter</i> <code>{channel_name}</code> <i>De ce groupe??</i>\n"
        text+=f"\n<i><b>Cela supprimera également la chaîne et tous ses fichiers de la base de données....!!</b></i>\n"
        text+=f"\nYou Need To Add Channel Again If You Need To Shows It Result..."
        text+=f"\n<s>ProTip: Make Use Of Disconnect Button To Disable <code>{channel_name}</code> Results Temporarily....</s>"


    elif action=="f_delete":
        text=f"<i>Êtes-vous sûr de vouloir effacer tous les filtres de ce chat</i> <code>{channel_name}</code><i>???</i>\n"
        text+=f"\n<i>Cela effacera tous les fichiers de la base de données..</i>"


    elif action == "gcmds" and channel_name == "conn":
        text=f"<i>Êtes-vous sûr de vouloir activer toutes les connexions de</i> <code>{chat_name}</code><i>..???</i>\n"
        text+=f"\n<i>Cela affichera le fichier dans les résultats de toutes les connexions de discussion de</i> <code>{chat_name}</code>..."


    elif action == "gcmds" and channel_name == "disconn":
        text=f"<i>Êtes-vous sûr de vouloir désactiver toutes les connexions Of</i> <code>{chat_name}</code><i>....???</i>\n"
        text+=f"\n<i>Les fichiers DB seront toujours là et vous pourrez vous reconnecter à tous les canaux à tout moment à partir du menu Paramètres sans ajouter à nouveau de fichiers à la base de données...</i>\n"
        text+=f"\n<i>Cette désactivation n'affichera plus les résultats d'aucune requête à moins que vous ne les activiez en arrière...</i>"
    
    
    elif action == "gcmds" and channel_name == "c_delete":
        text=f"<i>Êtes-vous sûr de vouloir déconnecter TOUS les chats connectés de </i> <code>{chat_name}</code> <i>....???</i>\n"
        text+=f"\n<i><b>Cela supprimera également tous les canaux connectés et tous ses fichiers de la base de données....!!</b></i>\n"
        text+=f"\nVous devez à nouveau ajouter une chaîne si vous devez afficher à nouveau ses résultats.....\n"
        text+=f"\n<s>Conseil de pro : utilisez le bouton de déconnexion pour désactiver temporairement tous les résultats de discussion....</s>"


    elif action == "gcmds" and channel_name == "f_delete":
        text=f"<i>Êtes-vous sûr de vouloir effacer tous les filtres de</i> <code>{chat_name}</code><i>....???</i>\n"
        text+=f"\n<i>Cela effacera tous les fichiers de <code>{chat_name}</code> De la BD....</i>"
    
    
    buttons = [
        [
            InlineKeyboardButton
                (
                    "Oui", callback_data=f"{action}({channel_id}|{channel_name})"
                ), 
            
            InlineKeyboardButton
                (
                    "Non", callback_data="close"
                )
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await update.message.edit_text(
        text,
        reply_markup=reply_markup,
        parse_mode="html"
    )



@Client.on_callback_query(filters.regex(r"set\((.+)\)"), group=2)
async def cb_set(bot, update: CallbackQuery):
    """
    A Callback Funtion Support For config()
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


    action, val, chat_id, curr_val = re.findall(r"set\((.+)\)", query_data)[0].split("|", 3)

    try:
        val, chat_id, curr_val = float(val), int(chat_id), float(curr_val)
    except:
        chat_id = int(chat_id)
    
    if val == curr_val:
        await update.answer("La nouvelle valeur ne peut pas être une ancienne valeur... Veuillez choisir une valeur différente...!!!", show_alert=True)
        return
    
    prev = await db.find_chat(chat_id)

    accuracy = float(prev["configs"].get("accuracy", 0.80))
    max_pages = int(prev["configs"].get("max_pages"))
    max_results = int(prev["configs"].get("max_results"))
    max_per_page = int(prev["configs"].get("max_per_page"))
    pm_file_chat = True if prev["configs"].get("pm_fchat") == (True or "True") else False
    show_invite_link = True if prev["configs"].get("show_invite_link") == (True or "True") else False
    
    if action == "accuracy": # Scophisticated way 😂🤣
        accuracy = val
    
    elif action == "pages":
        max_pages = int(val)
        
    elif action == "results":
        max_results = int(val)
        
    elif action == "per_page":
        max_per_page = int(val)

    elif action =="showInv":
        show_invite_link = True if val=="True" else False

    elif action == "inPM":
        pm_file_chat = True if val=="True" else False
        

    new = dict(
        accuracy=accuracy,
        max_pages=max_pages,
        max_results=max_results,
        max_per_page=max_per_page,
        pm_fchat=pm_file_chat,
        show_invite_link=show_invite_link
    )
    
    append_db = await db.update_configs(chat_id, new)
    
    if not append_db:
        text="Something Wrong Please Check Bot Log For More Information...."
        await update.answer(text=text, show_alert=True)
        return
    
    text=f"Votre demande a été mise à jour avec succès....\nMaintenant, tous les résultats à venir s'afficheront en fonction de ces paramètres..."
        
    buttons = [
        [
            InlineKeyboardButton
                (
                    "Retour 🔙", callback_data=f"config({chat_id})"
                ),
            
            InlineKeyboardButton
                (
                    "Fermer 🔐", callback_data="close"
                )
        ]
    ]
    
    reply_markup=InlineKeyboardMarkup(buttons)
    
    await update.message.edit_text(
        text, reply_markup=reply_markup, parse_mode="html"
    )



@Client.on_callback_query(filters.regex(r"^(start|help|about|close)$"), group=2)
async def callback_data(bot, update: CallbackQuery):

    query_data = update.data

    if query_data == "start":
        buttons = [[
            InlineKeyboardButton('My Dev 👨‍🔬', url='https://t.me/Philantrpe'),
            InlineKeyboardButton('Source Code 🧾', url ='https://t.me/Sharing_Club')
        ],[
            InlineKeyboardButton('Support 🛠', url='https://t.me/Shar_Group')
        ],[
            InlineKeyboardButton('Aides ⚙', callback_data="help")
        ]]
    
        reply_markup = InlineKeyboardMarkup(buttons)
        
        await update.message.edit_text(
            Translation.START_TEXT.format(update.from_user.mention),
            reply_markup=reply_markup,
            parse_mode="html",
            disable_web_page_preview=True
        )


    elif query_data == "help":
        buttons = [[
            InlineKeyboardButton('Home ⚡', callback_data='start'),
            InlineKeyboardButton('À propos 🚩', callback_data='about')
        ],[
            InlineKeyboardButton('Fermer 🔐', callback_data='close')
        ]]
    
        reply_markup = InlineKeyboardMarkup(buttons)
        
        await update.message.edit_text(
            Translation.HELP_TEXT,
            reply_markup=reply_markup,
            parse_mode="html",
            disable_web_page_preview=True
        )


    elif query_data == "about": 
        buttons = [[
            InlineKeyboardButton('Home ⚡', callback_data='start'),
            InlineKeyboardButton('Fermer 🔐', callback_data='close')
        ]]
        
        reply_markup = InlineKeyboardMarkup(buttons)
        
        await update.message.edit_text(
            Translation.ABOUT_TEXT,
            reply_markup=reply_markup,
            parse_mode="html"
        )


    elif query_data == "close":
        await update.message.delete()
        
