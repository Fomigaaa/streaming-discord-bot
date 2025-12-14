import discord
import requests
import json
import os

from config import DISCORD_TOKEN, CHANNELS, JUSTWATCH_LOCALE

intents = discord.Intents.default()
client = discord.Client(intents=intents)

JW_URL = f"https://apis.justwatch.com/content/titles/{JUSTWATCH_LOCALE}/new"

PROVIDERS = {
    "disney": {
        "id": "dnp",
        "name": "Disney+",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/3/3e/Disney%2B_logo.svg"
    },
    "netflix": {
        "id": "nfx",
        "name": "Netflix",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/0/08/Netflix_2015_logo.svg"
    },
    "prime": {
        "id": "prv",
        "name": "Prime Video",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/f/f1/Prime_Video.png"
    },
    "hbo": {
        "id": "hbm",
        "name": "HBO Max",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/1/17/HBO_Max_Logo.svg"
    }
}

def load_sent():
    if not os.path.exists("sent_ids.json"):
        return {k: [] for k in PROVIDERS}
    with open("sent_ids.json", "r") as f:
        return json.load(f)

def save_sent(data):
    with open("sent_ids.json", "w") as f:
        json.dump(data, f, indent=2)

def fetch_new(provider_id):
    payload = {
        "providers": [provider_id],
        "monetization_types": ["flatrate"],
        "page_size": 20
    }
    headers = {"Content-Type": "application/json"}
    r = requests.post(JW_URL, json=payload, headers=headers)
    return r.json().get("items", [])

@client.event
async def on_ready():
    print(f"🤖 Bot ligado como {client.user}")
    sent = load_sent()

    for key, provider in PROVIDERS.items():
        channel = client.get_channel(CHANNELS[key])
        if not channel:
            continue

        items = fetch_new(provider["id"])

        for item in items:
            jw_id = str(item["id"])
            if jw_id in sent[key]:
                continue

            title = item.get("title", "Sem título")
            year = item.get("original_release_year", "")
            item_type = "Série" if item.get("object_type") == "show" else "Filme"

            poster = None
            if item.get("poster"):
                poster = f"https://images.justwatch.com{item['poster'].replace('{profile}', 's332')}"

            embed = discord.Embed(
                title=f"{title} ({year})",
                description=f"🎬 **{item_type}** disponível agora na **{provider['name']}**",
                color=0x00FFFF
            )

            embed.set_author(
                name=provider["name"],
                icon_url=provider["logo"]
            )

            if poster:
                embed.set_thumbnail(url=poster)

            await channel.send(embed=embed)
            sent[key].append(jw_id)

    save_sent(sent)
    await client.close()

client.run(DISCORD_TOKEN)
