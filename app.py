import FTPP

print('\n\n===Aplicação para transferência de arquivos ===\n\n')

address = input('Informe o endereço IP: ')
port = input('Informe a porta: ')

while(True):
	print(' Menu: '+'\n')
	print(' 1 - Enviar arquivo: '+'\n')
	print(' 2 - Receber arquivo: '+'\n')
	option = input('Escolha uma opção: \n')

	if(option == '1'):
		files = input('Digite o nome do arquivo: \n')
		recv = FTPP.send(address, port, files, 'testerecv.jpg')
		if(recv == '0'):
			print('Arquivo enviado com sucesso!\n')
			input('\nPrecione Enter para continuar\n\n')
		else:
			print(recv)
			input('\nPrecione Enter para continuar\n\n')
	elif(option == '2'):
		recv = FTPP.receive(address, int(port))
		if(recv == '0'):
			print('Arquivo recebido com sucesso: \n')
			input('\nPrecione Enter para continuar\n\n')
		else:
			print(recv)
			input('\nPrecione Enter para continuar\n\n')
	else:
		print('Opção inválida!\n')
		input('\nPrecione Enter para continuar\n\n')
	
