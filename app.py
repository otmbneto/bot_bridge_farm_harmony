import sys
import os
import traceback
import requests
from BD_utils import *

from dotenv import load_dotenv

load_dotenv()

def sendMessage(message, channel, server, attachment, headers={}):
    server_channel = server + "/" + channel
    print("MESSAGE: {0}".format(message))
    print("SERVER: {0}".format(server_channel))
    print("HEADERS: {0}".format(headers))
    if bool(attachment):
        headers["Filename"] = os.path.basename(attachment)
        headers["Message"] = message
        return requests.put(server_channel, data=open(attachment, "rb"), headers=headers)
    else:
        return requests.post(server_channel, data=message, headers=headers)


def parseCommand(command, args):
    output = None
    f = getRoute(command, script_path=os.path.abspath(os.path.dirname(__file__)))
    if f is not None:
        output = eval(f + "(" + str(args) + ")")

    return output


def messageReceived(request):

    if not "reply_to" in request.keys() or not "at_channel" in request.keys():
        print("Error: received request is incomplete")
        return None

    response = {"reply_to": request["reply_to"], "at_channel": request["at_channel"]}
    try:
        cmd = request["command"]
        args = request["args"] if "args" in request.keys() else []
        args += [os.getenv("QUEUE_CONFIG"), os.getenv("QUEUE_PATH")]  # adiciona a fila atual para os argumentos
        output = parseCommand(cmd, args)
        if output is None:
            output = "ERRO: Comando desconhecido: {0}".format(args[0])

        header = 'Hello <@{0}>'.format(request["user_id"]) if "user_id" in request.keys() else "Hello!"
        # test if output is a file path
        if os.path.isfile(output) and os.path.exists(output):
            msg = header
        else:
            msg = "{0}\n```{1}\n```".format(header, output)

        response["response"] = msg
        response["attach"] = output if os.path.isfile(output) and os.path.exists(output) else None
    except Exception as e:
        traceback.print_exc()
        response["response"] = str(e)

    return response


def whatisthis(s):
    if isinstance(s, str):
        print("ordinary string")
    elif isinstance(s, unicode):
        print("unicode string")
    else:
        print("not a string")


def tags_to_dict(tags):
    
    tags_dict = {}
    if tags is not None:
        for tag in tags.split(","):
            tag_split = tag.split(":")
            tags_dict[tag_split[0]] = tag_split[1]

    return tags_dict


def dict_to_tags(dict):
    tags = ""
    if tags is not None:
        tags = str(dict)[1:-1].replace(" ", "").replace("'", "")
    return tags


def main(args):

    request = tags_to_dict(os.getenv("NTFY_TAGS"))
    message = os.getenv("NTFY_MESSAGE").split("-") if os.getenv("NTFY_MESSAGE") is not None else []
    request["command"] = message[0] if len(message) > 0 else ""
    request["args"] = message[1:]
    output = messageReceived(request)
    server = args[0]

    msg = output.pop("response") if output is not None else "Error: message is incomplete"
    attach = output.pop("attach") if output is not None and "attach" in output.keys() else False
    tags_str = dict_to_tags(output)
    headers = {
        "charset": "UTF-8",
        "Tags": str(tags_str)
    }

    print(sendMessage(msg, "RESPOSTA", server, attach, headers=headers))


if __name__ == '__main__':
    args = sys.argv
    main(args[1:])
