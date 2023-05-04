import os
import sys
import json
import traceback
import requests
from BD_utils import *

from dotenv import load_dotenv
load_dotenv()

def sendMessage(message,channel,server,headers = {}):

	print "MESSAGE: " + message
	print "SERVER:" + server + "/" + channel
	print "HEADERS:" + str(headers)
	return requests.post(server + "/" + channel,data=message,headers=headers)

def parseCommand(command,args):

	output = None
	print command 
	print args
	f = getRoute(command,script_path=os.path.abspath(os.path.dirname(__file__)))
	if f is not None:
		output = eval(f + "("+ str(args) +")")

	return output

def messageReceived(request):

	response = {"reply_to": request["reply_to"],"at_channel": request["at_channel"]}
	try:
		cmd = request["command"]
		print request["args"] 
		print [os.getenv("QUEUE_CONFIG"),os.getenv("QUEUE_PATH")]
		args = request["args"] + [os.getenv("QUEUE_CONFIG"),os.getenv("QUEUE_PATH")] #adiciona a fila atual para os argumentos
		output = parseCommand(cmd,args)
		if output is None:
			output = "ERRO: Comando desconhecido: {0}".format(args[0])

		header = 'Hello <@{0}>\n```'.format(request["user_id"]) if "user_id" in request.keys() else ""
		output = header + output
		output += "```"
		output = output.replace("\n","\\n")
		response["response"] = output
		print "Generating output"
		print output
	except Exception as e:
		traceback.print_exc()
		response["response"] = str(e)

	return response

def tags_to_dict(tags):

	tags_dict = {}
	for tag in tags.split(","):
		tag_split = tag.split(":")
		tags_dict[tag_split[0]] = tag_split[1]

	return tags_dict

def dict_to_tags(dict):

	tags = str(dict)[1:-1].replace(" ", "").replace("'", "")

	return tags

def main(args):

	output = messageReceived(tags_to_dict(os.getenv("NTFY_TAGS")))
	topic = os.getenv("NTFY_TOPIC")
	server = args[0]
	print output

	msg = output.pop("response")
	tags_str = dict_to_tags(output)
	headers = {
		"charset": "UTF-8",
		"Tags": str(tags_str)
	}
	
	sendMessage(msg,"RESPOSTA",server,headers=headers)

if __name__ == '__main__':
	args = sys.argv
	main(args[1:])