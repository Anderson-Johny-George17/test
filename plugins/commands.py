import os
import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from info import START_MSG, CHANNELS, ADMINS, AUTH_CHANNEL, CUSTOM_FILE_CAPTION
from utils import Media, get_file_details
from pyrogram.errors import UserNotParticipant
logger = logging.getLogger(__name__)

WASIM ="https://t.me/wafikh"

@Client.on_message(filters.command("start"))
async def start(bot, cmd):
    usr_cmdall1 = cmd.text
    if usr_cmdall1.startswith("/start subinps"):
        if AUTH_CHANNEL:
            invite_link = await bot.create_chat_invite_link(int(AUTH_CHANNEL))
            try:
                user = await bot.get_chat_member(int(AUTH_CHANNEL), cmd.from_user.id)
                if user.status == "kicked":
                    await bot.send_message(
                        chat_id=cmd.from_user.id,
                        text="Sorry Sir, You are Banned to use me.",
                        parse_mode="markdown",
                        disable_web_page_preview=True
                    )
                    return
            except UserNotParticipant:
                ident, file_id = cmd.text.split("_-_-_-_")
                await bot.send_message(
                    chat_id=cmd.from_user.id,
                    text="""**🔊 Please Join Our Main Channel For Files 🔊
താഴെ കാണുന്ന ചാനലിൽ ജോയിൻ ചെയ്തതിനു ശേഷം 'try again' ക്ലിക്ക് ചെയ്താൽ നിങ്ങളുടെ ഫയൽ ലഭിക്കുന്നതാണ്!!**""",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton("🤖 Join Updates Channel", url=invite_link.invite_link)
                            ],
                            [
                                InlineKeyboardButton(" 🔄 Try Again", callback_data=f"checksub#{file_id}")
                            ]
                        ]
                    ),
                    parse_mode="markdown"
                )
                return
            except Exception:
                await bot.send_message(
                    chat_id=cmd.from_user.id,
                    text="Something went Wrong.",
                    parse_mode="markdown",
                    disable_web_page_preview=True
                )
                return
        try:
            ident, file_id = cmd.text.split("_-_-_-_")
            filedetails = await get_file_details(file_id)
            for files in filedetails:
                title = files.file_name
                size=files.file_size
                f_caption=files.caption
                if CUSTOM_FILE_CAPTION:
                    try:
                        f_caption=CUSTOM_FILE_CAPTION.format(file_name=title, file_size=size, file_caption=f_caption)
                    except Exception as e:
                        print(e)
                        f_caption=f_caption
                if f_caption is None:
                    f_caption = f"{files.file_name}"
                buttons = [
                    [
                        InlineKeyboardButton('Search again', switch_inline_query_current_chat=''),
                        InlineKeyboardButton('More Bots', url='https://t.me/subin_works/122')
                    ]
                    ]
                await bot.send_cached_media(
                    chat_id=cmd.from_user.id,
                    file_id=file_id,
                    caption=f_caption,
                    reply_markup=InlineKeyboardMarkup(buttons)
                    )
        except Exception as err:
            await cmd.reply_text(f"Something went wrong!\n\n**Error:** `{err}`")
    elif len(cmd.command) > 1 and cmd.command[1] == 'subscribe':
        invite_link = await bot.create_chat_invite_link(int(AUTH_CHANNEL))
        await bot.send_message(
            chat_id=cmd.from_user.id,
            text="**Please Join My Updates Channel to use this Bot!**",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🤖 Join Updates Channel", url=invite_link.invite_link)
                    ]
                ]
            )
        )
    else:
        await cmd.reply_photo(
            photo="https://telegra.ph/file/9e4771df0f2f210ba05df.jpg",
            caption=START_MSG,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(" 🔎  𝐬𝐞𝐚𝐫𝐜𝐡 𝐡𝐞𝐫𝐞", switch_inline_query_current_chat=''),
                        InlineKeyboardButton("⚠️  𝐣𝐨𝐢𝐧", url="https://t.me/no_ones_like_me")
                    ],
                    [
                        InlineKeyboardButton("🧑‍💻 𝐜𝐫𝐞𝐚𝐭𝐨𝐫", url="https://t.me/no_ones_like_me"),
                        InlineKeyboardButton("🤖 𝐚𝐛𝐨𝐮𝐭", callback_data="about"),
                      ]
                    ]
                 )
              )
@Client.on_message(filters.command('channel') & filters.user(ADMINS))
async def channel_info(bot, message):
    """Send basic information of channel"""
    if isinstance(CHANNELS, (int, str)):
        channels = [CHANNELS]
    elif isinstance(CHANNELS, list):
        channels = CHANNELS
    else:
        raise ValueError("Unexpected type of CHANNELS")

    text = '📑 **Indexed channels/groups**\n'
    for channel in channels:
        chat = await bot.get_chat(channel)
        if chat.username:
            text += '\n@' + chat.username
        else:
            text += '\n' + chat.title or chat.first_name

    text += f'\n\n**Total:** {len(CHANNELS)}'

    if len(text) < 4096:
        await message.reply(text)
    else:
        file = 'Indexed channels.txt'
        with open(file, 'w') as f:
            f.write(text)
        await message.reply_document(file)
        os.remove(file)


@Client.on_message(filters.command('total') & filters.user(ADMINS))
async def total(bot, message):
    """Show total files in database"""
    msg = await message.reply("Processing...⏳", quote=True)
    try:
        total = await Media.count_documents()
        await msg.edit(f'📁 Saved files: {total}')
    except Exception as e:
        logger.exception('Failed to check total files')
        await msg.edit(f'Error: {e}')


@Client.on_message(filters.command('logger') & filters.user(ADMINS))
async def log_file(bot, message):
    """Send log file"""
    try:
        await message.reply_document('TelegramBot.log')
    except Exception as e:
        await message.reply(str(e))


@Client.on_message(filters.command('delete') & filters.user(ADMINS))
async def delete(bot, message):
    """Delete file from database"""
    reply = message.reply_to_message
    if reply and reply.media:
        msg = await message.reply("Processing...⏳", quote=True)
    else:
        await message.reply('Reply to file with /delete which you want to delete', quote=True)
        return

    for file_type in ("document", "video", "audio"):
        media = getattr(reply, file_type, None)
        if media is not None:
            break
    else:
        await msg.edit('This is not supported file format')
        return

    result = await Media.collection.delete_one({
        'file_name': media.file_name,
        'file_size': media.file_size,
        'mime_type': media.mime_type
    })
    if result.deleted_count:
        await msg.edit('File is successfully deleted from database')
    else:
        await msg.edit('File not found in database')
@Client.on_message(filters.command('about'))
async def bot_info(bot, message):
    buttons = [
        [
            InlineKeyboardButton('Movie Channel', url='https://t.me/joinchat/0NL8yWMlB2AxZGVl'),
            InlineKeyboardButton('Source Code', url='https://t.me/angotmaariiri')
        ]
        ]
    await message.reply(text="""<b>○ ᴍʏ ɴᴀᴍᴇ :  ᴘʀᴏғᴇssᴏʀ
    
○ ʟᴀɴɢᴜᴀɢᴇ : ᴘʏᴛʜᴏɴ

○ ғʀᴀᴍᴇᴡᴏʀᴋ : ᴘʏʀᴏɢʀᴀᴍ

○ sᴇʀᴠᴇʀ : ʜᴇʀᴏᴋᴜ

○ ᴠᴇʀsɪᴏɴ : 1.0.0

○ ᴄʀᴇᴀᴛᴏʀ : <a href="https://t.me/xxxtentacion_TG">xxxᴛᴇɴᴛᴀᴄɪᴏɴ</a>

○ sᴏᴜʀᴄᴇ ᴄᴏᴅᴇ : 🔐

ᴜᴘᴅᴀᴛᴇ ᴏɴ 22-08-21 ɪɴᴅɪᴀɴ ᴛɪᴍᴇ 1:19 ᴘᴍ </b>""", reply_markup=InlineKeyboardMarkup(buttons), disable_web_page_preview=True)

@Client.on_message(filters.command('help'))
async def bot_info(bot, message):
    buttons = [
        [
            InlineKeyboardButton('☃️ 𝐠𝐫𝐨𝐮𝐩', url='https://t.me/cinemazilla'),
            InlineKeyboardButton('🌨 𝐜𝐡𝐚𝐧𝐧𝐞𝐥', url='https://t.me/joinchat/CXRICR1ok3ViZjk9')
        ]
        ]
    await message.reply(text="""<b>○ 𝐢𝐭'𝐬 𝐍𝐨𝐭𝐞 𝐂𝐨𝐦𝐩𝐥𝐢𝐜𝐚𝐭𝐞𝐝...🤓

○  𝐒𝐞𝐚𝐫𝐜𝐡 𝐮𝐬𝐢𝐧𝐠 𝐢𝐧𝐥𝐢𝐧𝐞 𝐦𝐨𝐝𝐞
𝐓𝐡𝐢𝐬 𝐦𝐞𝐭𝐡𝐨𝐫𝐝 𝐰𝐨𝐫𝐤𝐬 𝐨𝐧 𝐚𝐧𝐲 𝐜𝐡𝐚𝐭, 𝐉𝐮𝐬𝐭 𝐭𝐲𝐩𝐞 @𝐂𝐙_𝐕1_𝐁𝐎𝐓 𝐚𝐧𝐝 𝐭𝐡𝐞𝐧 𝐥𝐞𝐚𝐯𝐞 𝐚 𝐬𝐩𝐚𝐜𝐞 𝐚𝐧𝐝 𝐬𝐞𝐚𝐫𝐜𝐡 𝐚𝐧𝐲 𝐦𝐨𝐯𝐢𝐞 𝐲𝐨𝐮 𝐰𝐚𝐧𝐭.

○ 𝐈𝐧 𝐏𝐌
𝐓𝐡𝐢𝐬 𝐢𝐬 𝐭𝐡𝐞 𝐞𝐚𝐬𝐢𝐞𝐬𝐭 𝐦𝐞𝐭𝐡𝐨𝐫𝐝 𝐟𝐨𝐫 𝐭𝐡𝐨𝐬𝐞 𝐰𝐡𝐨 𝐝𝐨 𝐧𝐨𝐭 𝐤𝐧𝐨𝐰 𝐡𝐨𝐰 𝐭𝐨 𝐮𝐬𝐞 𝐢𝐧𝐥𝐢𝐧𝐞 𝐦𝐨𝐝𝐞. 𝐉𝐮𝐬𝐭 𝐬𝐞𝐧𝐝 𝐭𝐡𝐞 𝐧𝐚𝐦𝐞 𝐨𝐟 𝐦𝐨𝐯𝐢𝐞 𝐭𝐨 𝐛𝐨𝐭. 
𝐁𝐨𝐭 𝐰𝐢𝐥𝐥 𝐫𝐞𝐩𝐥𝐲 𝐰𝐢𝐭𝐡 𝐚 𝐥𝐢𝐬𝐭 𝐨𝐟 𝐦𝐨𝐯𝐢𝐞𝐬 𝐚𝐯𝐚𝐢𝐥𝐚𝐛𝐥𝐞 𝐚𝐬 𝐛𝐮𝐭𝐭𝐨𝐧𝐬.
𝐂𝐥𝐢𝐜𝐤 𝐨𝐧 𝐭𝐡𝐞 𝐛𝐮𝐭𝐭𝐨𝐧𝐬 𝐭𝐨 𝐠𝐞𝐭 𝐭𝐡𝐞 𝐦𝐨𝐯𝐢𝐞.

○ 𝐍𝐁:-📗

○𝐓𝐡𝐢𝐬 𝐢𝐬 𝐚 𝐛𝐨𝐭, 𝐧𝐨𝐭 𝐚 𝐡𝐮𝐦𝐚𝐧, 𝐨𝐧𝐥𝐲 𝐬𝐞𝐧𝐝 𝐰𝐢𝐭𝐡 𝐭𝐡𝐞 𝐜𝐨𝐫𝐫𝐞𝐜𝐭 𝐈𝐌𝐃𝐛 𝐧𝐚𝐦𝐞

𝐌𝐚𝐢𝐧𝐭𝐚𝐢𝐧𝐞𝐝 𝐛𝐲 <a href="https://t.me/no_ones_like_me">𝐩𝐞𝐚𝐤𝐲 𝐛𝐥𝐢𝐧𝐝𝐞𝐫</a></b>""", reply_markup=InlineKeyboardMarkup(buttons), disable_web_page_preview=True)
