import requests
import os
import asyncio
import json
import websockets
import base64

BASE = "https://discord.com/api/v10"
GATEWAYURL = 'wss://gateway.discord.gg/?v=10&encoding=json'
spacing = ' '*8
stop_event = asyncio.Event()

#ws
async def heartbeat(ws, interval):
    while True:
        await asyncio.sleep(interval / 1000)
        await ws.send(json.dumps({"op": 1, "d": None}))
async def recv_json(ws):
    msg = await ws.recv()
    if msg:
        return json.loads(msg)
async def send_json(ws, data):
    await ws.send(json.dumps(data))
async def identify(ws, token):
    identify_payload = {
        "op": 2,
        "d": {
            "token": token,
            "intents": 513,
            "properties": {
                "$os": "windows",
                "$browser": "disco",
                "$device": "disco"
            }
        }
    }
    await send_json(ws, identify_payload)
async def waitForCommandUse(token):
    async with websockets.connect(GATEWAYURL) as ws:
        hello_data = await recv_json(ws)
        heartbeat_interval = hello_data['d']['heartbeat_interval']
        asyncio.create_task(heartbeat(ws, heartbeat_interval))
        await identify(ws, token)
        while not stop_event.is_set():
            message = await recv_json(ws)
            eventName = message['t']
            if eventName == 'READY':
                print(f"{spacing}[+] Logged in as {message['d']['user']['username']}")
            elif eventName == 'INTERACTION_CREATE':
                print(f"{spacing}[+] Command used by {message['d']['member']['user']['username']}!")
                response_payload = {
                    'type': 4,  # ACKNOWLEDGE
                    'data': {
                        'embeds': [
                            {
                                'title': 'Success!',
                                'description': 'Great! You can collect it in 24h here: [Active Developer](https://discord.com/developers/active-developer)'
                            }
                        ]
                    }
                }
                requests.post(BASE+f'/interactions/{message['d']['id']}/{message['d']['token']}/callback', json=response_payload)
                stop_event.set()




def clear():
    os.system('cls')
    print(f"""\033[94m\n\n{spacing}██╗  ██╗██╗██╗    ██╗██╗██████╗ ███████╗██╗   ██╗\n{spacing}██║ ██╔╝██║██║    ██║██║██╔══██╗██╔════╝██║   ██║\n{spacing}█████╔╝ ██║██║ █╗ ██║██║██║  ██║█████╗  ██║   ██║\n{spacing}██╔═██╗ ██║██║███╗██║██║██║  ██║██╔══╝  ╚██╗ ██╔╝\n{spacing}██║  ██╗██║╚███╔███╔╝██║██████╔╝███████╗ ╚████╔╝\n{spacing}╚═╝  ╚═╝╚═╝ ╚══╝╚══╝ ╚═╝╚═════╝ ╚══════╝  ╚═══╝ 
                                        By NexusKiwi ඞ\n\033[0m""")
    
def cIn(quest):
    return input(f'{spacing}{quest}\n{spacing}  -> ')


def getHeader(token):
    return {'Authorization': 'Bot '+token, 'Content-Type': 'application/json'}

def validateToken(token):
    res = requests.get(BASE+'/users/@me', headers=getHeader(token))
    if res.status_code == 200:
        return True, res.json()['username'], res.json()['id']
    else:
        return False, None
def getToken():
    tFileName = 'token.txt'
    if os.path.exists(tFileName):
        with open(tFileName, 'r') as f:
            tFc = f.read()
            if tFc != '' and len(tFc) == 72:
                valid, name, bId = validateToken(tFc)
                if valid:
                    return tFc, name, bId
            print(f"{spacing}[-] Token in token file invalid. Please enter a new one")
            open(tFileName, 'w').write('')

    while True:
        print(f"{spacing}[-] When you have to create a new bot click \033]8;;https://discord.dev\033\\here\033]8;;\033\\ (Ctrl + Click)")
        tIn = cIn('Enter bot token')
        valid, name, bId = validateToken(tIn)
        if valid:
            if cIn('Do you want to save the token for the next time? (y/n)').lower() == 'y':
                open(tFileName, 'w').write(tIn)
                print(f"{spacing}[+] Token saved!")
            return tIn, name, bId


def addCommand(token, bId):
    cmdPayload = {
        "name": "devbadge",
        "type": 1,
        "description": "Use this command to get the active developer badge!",
        "options": []
    }
    cmdRes = requests.post(BASE+f'/applications/{bId}/commands', headers=getHeader(token), json=cmdPayload)
    if cmdRes.status_code == 200:
        print(f"{spacing}[+] Command successfully added!")
    else:
        print(f"{spacing}[-] Error while adding Command:")
        print(cmdRes.content)
        print(f"\n\n{spacing}[-] Please rerun the application. This should fix the problem! When you saved the token it will be way faster😉")


def enableCommunity(token, gId):
    res = requests.get(f'https://discord.com/api/v10/guilds/{gId}', headers=getHeader(token))
    if res.status_code == 200:
        features = res.json()['features']
        if 'COMMUNITY' not in features:
            payload = {
                'system_channel_flags': 3,
                'verification_level': 2, 
                'public_updates_channel_id': 1,
                'explicit_content_filter': 2,
                'rules_channel_id': 1,
                'features': ['COMMUNITY']
            }
            res = requests.patch(f'https://discord.com/api/v10/guilds/{gId}', headers=getHeader(token), json=payload)
            if res.status_code == 200:
                print(f"{spacing}[+] Successfully enable community! This is the last key to be able to collect it!")
            else:
                print(res.content)
        else:
            print(f"{spacing}[+] Community already enabled!")
    else:
        print(res.content)
def main():
    clear()
    token, name, bId = getToken()
    print(f"{spacing}[+] Valid token for {name}")
    guilds = requests.get(BASE+'/users/@me/guilds', headers=getHeader(token))
    if guilds.status_code == 200:
        while len(guilds.json()) == 0:
            botId = base64.urlsafe_b64decode(token.split('.')[0] + '==').decode('utf-8')
            input(f"{spacing}[-] Please create a guild first.\n{spacing}    If you did click \033]8;;https://discord.com/oauth2/authorize?client_id={botId}&permissions=8&integration_type=0&scope=applications.commands+bot\033\\here\033]8;;\033\\ (Ctrl + Click) to add the bot.\n{spacing}    When you did it press Enter")
            guilds = requests.get(BASE+'/users/@me/guilds', headers=getHeader(token))

        guild_names = [guild['name'] for guild in guilds.json()] 
        print(spacing+'[>] Bot Guilds: '+', '.join(guild_names))  
        print(f"{spacing}[>] Adding command")
        addCommand(token, bId)
        print(f"{spacing}[+] Use /devbadge in the guild to collect it!")
        asyncio.run(waitForCommandUse(token))
        print(f"{spacing}[+] Thank you! You can collect it in ~24h \033]8;;https://discord.com/developers/active-developer\033\\here\033]8;;\033\\ (Ctrl + Click)")
        if len(guilds.json()) > 1:
            gId = cIn(f"You have more than one server the bot is on. Please enter the ID of one of them so i can activate community on it! That guild is later being used to collect the badge!")
            enableCommunity(token, gId)
        else:
            enableCommunity(token, guilds.json()[0]['id'])

        print(f"\n\n\n{spacing}That's all! You have to run this script every 30 days to keep it. Before the time is over you should receive a E-Mail from discord to warn you.\n{spacing}When you wanna be safe, just run it every 25 days or so.\n{spacing}When you saved your token it will be even faster.")
        input(f"{spacing}Press Enter to close the program.")

if __name__ == '__main__':
    print('\033]0;KiwiDev | Discord Dev Badge\007')
    print('\033[?25l')
    main()
