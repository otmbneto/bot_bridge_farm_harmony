import os
import sys
import json
import traceback
import requests
from BD_utils import *

from dotenv import load_dotenv
load_dotenv()

def sendMessage(message,channel,server,headers = {}):

	return requests.post(server + "/" + channel,data=message,headers=headers)

def parseCommand(command,args):

	output = None
	f = getRoute(command,script_path=os.path.abspath(os.path.dirname(__file__)))
	if f is not None:
		output = eval(f + "("+ str(args) +")")

	return output

def messageReceived(args):

	print args[0].replace("'","\"")
	request = json.loads(args[0].replace("'","\""))
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

def main(args):

	output = messageReceived(os.getenv("NTFY_MESSAGE"))
	topic = os.getenv("NTFY_TOPIC")
	server = args[2]
	print output
	sendMessage(str(output),"RESPOSTA",server)

if __name__ == '__main__':
	main()