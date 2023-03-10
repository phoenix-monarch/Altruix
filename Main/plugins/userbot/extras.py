# Copyright (C) 2021-present by Altruix@Github, < https://github.com/Altruix >.
#
# This file is part of < https://github.com/Altruix/Altruix > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/Altriux/Altruix/blob/main/LICENSE >
#
# All rights reserved.

import os
import re
import uuid
import base64
import psutil
import socket
import platform
import contextlib
from Main import Altruix
from os import remove as rmv
from mimetypes import guess_type
from Main.utils.paste import Paste
from pyrogram.types import Message
from Main.utils.essentials import Essentials


# from telegraph import Telegraph, upload_file


# telegraph = Telegraph()
# res = telegraph.create_account(short_name="Altruix")
# auth_url = res["auth_url"]


def fileToBase64(file_path: str) -> str:
    """
    File to Base64
        takes a file as input and encodes it to base 64
    """
    with open(file_path, "rb") as file:
        return base64.b64encode(file.read())


@Altruix.run_in_exc
def get_info(value=False) -> tuple:
    """
    Get Info
        fetches information about your system
        hides MAC and IP until explicitly referenced
        incompatible with termux due to problem with ethtool.h file .so objects
    """
    splatform = platform.system()
    platform_release = platform.release()
    platform_version = platform.version()
    architecture = platform.machine()
    hostname = socket.gethostname()
    ip_address = "Unable to fetch"
    mac_address = "Unable to fetch"
    with contextlib.suppress(Exception):
        ip_address = socket.gethostbyname(socket.gethostname())
    with contextlib.suppress(Exception):
        mac_address = ":".join(re.findall("..", "%012x" % uuid.getnode()))
    processor = platform.processor()
    ram = Essentials.humanbytes(round(psutil.virtual_memory().total))
    cpu_freq = psutil.cpu_freq().current
    if cpu_freq >= 1000:
        cpu_freq = f"{round(cpu_freq / 1000, 2)}GHz"
    else:
        cpu_freq = f"{round(cpu_freq, 2)}MHz"
    du = psutil.disk_usage(os.getcwd())
    psutil.disk_io_counters()
    disk = (
        f"{Essentials.humanbytes(du.used)}/{Essentials.humanbytes(du.total)}"
        f"({du.percent}%)"
    )
    cpu_len = len(psutil.Process().cpu_affinity())
    return (
        splatform,
        platform_release,
        platform_version,
        architecture,
        hostname,
        ip_address if value else None,
        mac_address if value else None,
        processor,
        ram,
        cpu_len,
        cpu_freq,
        disk,
    )


@Altruix.register_on_cmd(
    ["ubstat", "stat"],
    cmd_help={
        "help": "Get info about your machine.",
        "example": "ubstat",
        "user_args": [
            {
                "arg": "a",
                "help": "Reveal all info - IP and MAC.",
                "requires_input": False,
            },
        ],
    },
)
async def sTATS(c: Altruix, m: Message):
    msg = await m.handle_message("PROCESSING")
    value = m.user_args and m.user_args.a
    ub_stat = await get_info(value)
    database_ = await Altruix.db._db_name.command("dbstats")
    s = tuple(ub_stat) + (
        Essentials.humanbytes(database_["dataSize"]),
        Essentials.humanbytes(database_.get("storageSize")),
    )
    await msg.edit_msg("UBSTAT", string_args=s)


# Unstable


@Altruix.register_on_cmd(
    ["base64", "b64"],
    cmd_help={
        "help": "Encodes given file to an url",
        "example": "base64 <reply_to_file>",
    },
    requires_reply=True,
)
async def file_to_b64(c: Altruix, m: Message):
    msg = await m.handle_message("PROCESSING")
    if not msg.reply_to_message.media:
        return msg.edit("Reply to media...")
    file = await msg.reply_to_message.download()
    base = fileToBase64(file)
    type = guess_type(file)[0]
    name, link = await Paste(f"data:{type};base64,{str(base)[2:][:-1]}").paste()
    await msg.edit(
        Altruix.get_string("PASTE_TEXT").format(link, name),
        disable_web_page_preview=True,
    )
    rmv(file)


# @Altruix.register_on_cmd(
#     ["telegraph", "tg"],
#     cmd_help={
#         "help": "upload files to telegraph",
#         "cmd_help": "telegraph <reply to media>",
#     },
#     requires_reply=True,
# )
# async def download_files_from_telegram(c, m):
#     msg = await m.handle_message("PROCESSING")
#     if not m.reply_to_message.media:
#         return await msg.edit_msg("REPLY_TO_FILE")
#     media = await m.reply_to_message.download()
#     media_url = upload_file(media)
#     await msg.edit(f"https://graph.org{media_url[0]}")
#     if os.path.exists(media):
#         os.remove(media)
