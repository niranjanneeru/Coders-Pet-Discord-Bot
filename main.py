import io
import os

import discord
import numpy as np
import requests
from PIL import Image
from PIL import ImageDraw

import utils

intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)

whitelist = [782330876389883975, ]


@client.event
async def on_message(message):
    if message.channel.id not in whitelist:
        if not message.author.guild_permissions.administrator:
            for i in message.content.split(" "):
                if (utils._match_url(i)):
                    await message.channel.send(f'<@{message.author.id}> URIs are not allowed -> <#782330876389883975>')
                    await message.delete()


@client.event
async def on_member_join(member):
    r = requests.get(member.avatar_url, stream=True,
                     headers={'User-agent': 'Mozilla/5.0'})
    print("Downloading Image")
    try:
        if r.status_code == 200:
            img = Image.open(io.BytesIO(r.content))
            img = img.resize((130, 130))
            img = img.convert("RGBA")
            img.save('raw.png')
            img = Image.open('raw.png').convert("RGB")
            h, w = 130, 130  # img.shape

            # Open the input image as numpy array, convert to RGB
            npImage = np.array(img)
            h, w = img.size

            # Create same size alpha layer with circle
            alpha = Image.new('L', img.size, 0)
            draw = ImageDraw.Draw(alpha)
            draw.pieslice([0, 0, h, w], 0, 360, fill=255)

            # Convert alpha Image to numpy array
            npAlpha = np.array(alpha)

            # Add alpha layer to RGB
            npImage = np.dstack((npImage, npAlpha))

            # Save with alpha
            img = Image.fromarray(npImage)

            # load background image as grayscale

            back = Image.open('background.png')
            hh, ww = 480, 720  # back.shape
            back = back.resize((ww, hh))

            # compute xoff and yoff for placement of upper left corner of resized image
            yoff = round((hh - h - 140) / 2)
            xoff = round((ww - w) / 2)

            # use numpy indexing to place the resized image in the center of background image
            result = back.copy()
            result.paste(img, box=(xoff, yoff, xoff + w, yoff + h), mask=img)
            # result[yoff:yoff + h, xoff:xoff + w] = img

            # save resulting centered image
            filename = 'welcome.png'
            result.convert(back.mode).save(filename)
            print("Image Created")
    except Exception as e:
        print(e)
        filename = None

    if filename:
        channel = client.get_channel(782348945744723978)
        print("Sending Image...")
        await channel.send(file=discord.File(filename))
        await channel.send(f'Hi, <@{member.id}> Read the rules - <#780100772842045450>')
        print("Flush Files")
        try:
            os.remove('raw.png')
            os.remove('welcome.png')
        except:
            print("Flush Failed")


client.run("")