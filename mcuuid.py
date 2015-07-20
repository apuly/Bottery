import json
import urllib.request

_apiLink = 'https://api.mojang.com/users/profiles/minecraft/'

def _getUuid(nickName, postFix = ''):
    f = urllib.request.urlopen('{}{}{}'.format(_apiLink, nickName, postFix))
    data = f.read(100).decode()
    return json.loads(data)

def getUuidByCurrentName(playerName):
        try:
            playerProp = _getUuid(playerName)
            return playerProp['id']
        except ValueError:
            return None

def getUuidByOldName(playerName, timeStamp = 0):
    postFix = '?at={}'.format(timeStamp)
    try:
        playerProp = _getUuid(playerName, postFix)
        return playerProp['id']
    except ValueError:
        return None
