import random
import string
import asyncio

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import UserAlreadyParticipant, FloodWait

from bot import CHAT_DETAILS
from bot.bot import Bot 
from bot.database import Database 
from bot.plugins.auto_filter import recacher
from bot.plugins.utils import admin_list

db = Database()

@Client.on_message(filters.command(["add"]) & filters.group, group=1)
async def connect(bot: Bot, update: Message):
    """
    A Funtion To Handle Incoming /add Command TO COnnect A Chat With Group
    """
    chat_id = update.chat.id
    user_id = update.from_user.id if update.from_user else None
    target_chat = update.text.split(None, 1)
    global CHAT_DETAILS
    
    chat_dict = CHAT_DETAILS.get(str(chat_id))
    chat_admins = chat_dict.get("admins") if chat_dict != None else None

    if ( chat_dict or chat_admins ) == None: # Make Admin's ID List
        chat_admins = await admin_list(chat_id, bot, update)

    if user_id not in chat_admins:
        return
    
    try:
        if target_chat[1].startswith("@"):
            if len(target_chat[1]) < 5:
                await update.reply_text("Nom d'utilisateur invalide...!!!")
                return
            target = target_chat[1]
            
        elif not target_chat[1].startswith("@"):
            if len(target_chat[1]) < 14:
                await update.reply_text("Identifiant de discussion non valide...\nL'ID de chat devrait ressembler à ceci : <code>-100xxxxxxxxxx</code>")
                return
            target = int(target_chat[1])
                
    except Exception:
        await update.reply_text("Entrée invalide...\nVous devez Entrée des données valide <code>chat_id(-100xxxxxxxxxx)</code> or <code>@username</code>")
        return
    
    try:
        join_link = await bot.export_chat_invite_link(target)
    except Exception as e:
        print(e)
        await update.reply_text(f"Assurez-vous que je suis administrateur à <code>{target}</code> Et avoir la permission de '<i>Inviting Users via Link</i>' Et essayez à nouveau.....!!!")
        return
    
    userbot_info = await bot.USER.get_me()
    userbot_id = userbot_info.id
    userbot_name = userbot_info.first_name
    
    try:
        await bot.USER.join_chat(join_link)
        
    except UserAlreadyParticipant:
        pass
    
    except Exception:
        await update.reply_text(f"Mon Assistante [{userbot_name}](tg://user?id={userbot_id}) Impossible de rejoindre la chaîne `{target}` Assurez-vous que Katnice n'y est pas interdit ou ajoutez-le manuellement et réessayez....!!")
        return
    
    try:
        c_chat = await bot.get_chat(target)
        channel_id = c_chat.id
        channel_name = c_chat.title
        
    except Exception as e:
        await update.reply_text("A rencontré un problème..Veuillez vérifier les journaux..!!")
        raise e
        
        
    in_db = await db.in_db(chat_id, channel_id)
    
    if in_db:
        await update.reply_text("Canal déjà dans la DB...!!!")
        return
    
    wait_msg = await update.reply_text("Veuillez patienter jusqu'à ce que j'ajoute tous vos fichiers de la chaîne à la base de données\n\n<i>Cela peut prendre 2 ou 3 heures selon votre nombre de fichiers dans le canal.....</i>\n\nJusque-là, veuillez ne pas envoyer d'autre commande ou cette opération pourrait être interrompue....")
    
    try:
        type_list = ["video", "audio", "document"]
        data = []
        skipCT = 0
        
        for typ in type_list:

            async for msgs in bot.USER.search_messages(channel_id,filter=typ): #Thanks To @PrgOfficial For Suggesting
                
                # Using 'if elif' instead of 'or' to determine 'file_type'
                # Better Way? Make A PR
                try:
                    if msgs.video:
                        try:
                            file_id = await bot.get_messages(channel_id, message_ids=msgs.message_id)
                        except FloodWait as e:
                            asyncio.sleep(e.x)
                            file_id = await bot.get_messages(channel_id, message_ids=msgs.message_id)
                        except Exception as e:
                            print(e)
                            continue
                        file_id = file_id.video.file_id
                        file_name = msgs.video.file_name[0:-4]
                        file_size = msgs.video.file_size
                        file_caption  = msgs.caption if msgs.caption else ""
                        file_type = "video"
                    
                    elif msgs.audio:
                        try:
                            file_id = await bot.get_messages(channel_id, message_ids=msgs.message_id)
                        except FloodWait as e:
                            asyncio.sleep(e.x)
                            file_id = await bot.get_messages(channel_id, message_ids=msgs.message_id)
                        except Exception as e:
                            print(e)
                            continue
                        file_id = file_id.audio.file_id
                        file_name = msgs.audio.file_name[0:-4]
                        file_size = msgs.audio.file_size
                        file_caption  = msgs.caption if msgs.caption else ""
                        file_type = "audio"
                    
                    elif msgs.document:
                        try:
                            file_id = await bot.get_messages(channel_id, message_ids=msgs.message_id)
                        except FloodWait as e:
                            asyncio.sleep(e.x)
                            file_id = await bot.get_messages(channel_id, message_ids=msgs.message_id)
                        except Exception as e:
                            print(str(e))
                            continue
                        file_id = file_id.document.file_id
                        file_name = msgs.document.file_name[0:-4]
                        file_size = msgs.document.file_size
                        file_caption  = msgs.caption if msgs.caption else ""
                        file_type = "document"
                    
                    for i in ["_", "|", "-", "."]: # Work Around
                        try:
                            file_name = file_name.replace(i, " ")
                        except Exception:
                            pass
                    
                    file_link = msgs.link
                    group_id = chat_id
                    unique_id = ''.join(
                        random.choice(
                            string.ascii_lowercase + 
                            string.ascii_uppercase + 
                            string.digits
                        ) for _ in range(15)
                    )
                    
                    dicted = dict(
                        file_id=file_id, # Done
                        unique_id=unique_id,
                        file_name=file_name,
                        file_size=file_size,
                        file_caption=file_caption,
                        file_type=file_type,
                        file_link=file_link,
                        chat_id=channel_id,
                        group_id=group_id,
                    )
                    
                    data.append(dicted)
                except Exception as e:
                    if 'NoneType' in str(e): # For Some Unknown Reason Some File Names are NoneType
                        skipCT +=1
                        continue
                    print(e)

        print(f"{skipCT} Les fichiers ont été ignorés car le nom du fichier n'a pas été..... #BlameTG")
    except Exception as e:
        await wait_msg.edit_text("Impossible de récupérer les fichiers de la chaîne... Veuillez consulter les journaux pour plus de détails")
        raise e
    
    await db.add_filters(data)
    await db.add_chat(chat_id, channel_id, channel_name)
    await recacher(chat_id, True, True, bot, update)
    
    await wait_msg.edit_text(f"La chaîne a été ajoutée avec succès avec <code>{len(data)}</code> Files..")


@Client.on_message(filters.command(["del"]) & filters.group, group=1)
async def disconnect(bot: Bot, update):
    """
    A Funtion To Handle Incoming /del Command TO Disconnect A Chat With A Group
    """
    chat_id = update.chat.id
    user_id = update.from_user.id if update.from_user else None
    target_chat = update.text.split(None, 1)
    global CHAT_DETAILS
    
    chat_dict = CHAT_DETAILS.get(str(chat_id))
    chat_admins = chat_dict.get("admins") if chat_dict != None else None

    if ( chat_dict or chat_admins ) == None: # Make Admin's ID List
        chat_admins = await admin_list(chat_id, bot, update)

    if user_id not in chat_admins:
        return
    
    try:
        if target_chat[1].startswith("@"):
            if len(target_chat[1]) < 5:
                await update.reply_text("Nom d'utilisateur invalide...!!!")
                return
            target = target_chat[1]
            
        elif not target_chat.startswith("@"):
            if len(target_chat[1]) < 14:
                await update.reply_text("ID non valide...\nL'ID de chat devrait être quelque chose comme ça: <code>-100xxxxxxxxxx</code>")
                return
            target = int(target_chat[1])
                
    except Exception:
        await update.reply_text("Entrée invalide...\nVous devez spécifier un chat_id(-100xxxxxxxxxx) or @username")
        return
    
    userbot = await bot.USER.get_me()
    userbot_name = userbot.first_name
    userbot_id = userbot.id
    
    try:
        channel_info = await bot.USER.get_chat(target)
        channel_id = channel_info.id
    except Exception:
        await update.reply_text(f"Mon Assistante [{userbot_name}](tg://user?id={userbot_id}) Impossible de récupérer les détails de `{target}` Assurez-vous que Katnice n'y est pas interdit ou ajoutez-le manuellement et réessayez....!!")
        return
    
    in_db = await db.in_db(chat_id, channel_id)
    
    if not in_db:
        await update.reply_text("Cette chaîne n'est pas connectée au groupe...")
        return
    
    wait_msg = await update.reply_text("Suppression de tous les fichiers de ce canal de la base de données....!!!\n\nS'il vous plaît soyez patient... N'envoyez pas d'autre commande jusqu'à ce que ce processus se termine..")
    
    await db.del_filters(chat_id, channel_id)
    await db.del_active(chat_id, channel_id)
    await db.del_chat(chat_id, channel_id)
    await recacher(chat_id, True, True, bot, update)
    
    await wait_msg.edit_text("Suppression réussie de tous les fichiers de la base de données....")


@Client.on_message(filters.command(["delall"]) & filters.group, group=1)
async def delall(bot: Bot, update):
    """
    A Funtion To Handle Incoming /delall Command TO Disconnect All Chats From A Group
    """
    chat_id=update.chat.id
    user_id = update.from_user.id if update.from_user else None
    global CHAT_DETAILS
    
    chat_dict = CHAT_DETAILS.get(str(chat_id))
    chat_admins = chat_dict.get("admins") if chat_dict != None else None

    if ( chat_dict or chat_admins ) == None: # Make Admin's ID List
        chat_admins = await admin_list(chat_id, bot, update)

    if user_id not in chat_admins:
        return
    
    await db.delete_all(chat_id)
    await recacher(chat_id, True, True, bot, update)
    
    await update.reply_text("Tous les chats connectés de ce groupe ont été supprimés avec succès....")


@Client.on_message(filters.channel & (filters.video | filters.audio | filters.document) & ~filters.edited, group=0)
async def new_files(bot: Bot, update):
    """
    A Funtion To Handle Incoming New Files In A Channel ANd Add Them To Respective Channels..
    """
    channel_id = update.chat.id
    
    # Using 'if elif' instead of 'or' to determine 'file_type'
    # Better Way? Make A PR
    
    try:
        if update.video: 
            file_type = "video" 
            file_id = update.video.file_id
            file_name = update.video.file_name[0:-4]
            file_size = update.video.file_size
            file_caption  = update.caption if update.caption else ""

        elif update.audio:
            file_type = "audio"
            file_id = update.audio.file_id
            file_name = update.audio.file_name[0:-4]
            file_size = update.audio.file_size
            file_caption  = update.caption if update.caption else ""

        elif update.document:
            file_type = "document"
            file_id = update.document.file_id
            file_name = update.document.file_name[0:-4]
            file_size = update.document.file_size
            file_caption  = update.caption if update.caption else ""
        
        for i in ["_", "|", "-", "."]: # Work Around
            try:
                file_name = file_name.replace(i, " ")
            except Exception:
                pass
    except Exception as e:
        print(e)
        return
        
    
    file_link = update.link
    group_ids = await db.find_group_id(channel_id)
    unique_id = ''.join(
        random.choice(
            string.ascii_lowercase + 
            string.ascii_uppercase + 
            string.digits
        ) for _ in range(15)
    )
    
    data = []
    
    if group_ids:
        for group_id in group_ids:
            data_packets = dict(
                    file_id=file_id, # File Id For Future Updates Maybe...
                    unique_id=unique_id,
                    file_name=file_name,
                    file_size=file_size,
                    file_caption=file_caption,
                    file_type=file_type,
                    file_link=file_link,
                    chat_id=channel_id,
                    group_id=group_id,
                )
            
            data.append(data_packets)
        await db.add_filters(data)
    return

