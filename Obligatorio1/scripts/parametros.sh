#! /bin/bash
pregunta="100"
comandos="--absolute-names"
comprimir=0
while [ $pregunta -ne 0 ]
do
	while [ $comprimir -ne 1 ] && [ $comprimir -ne 2 ] && [ $comprimir -ne 3 ];
	do
		echo "¿Cómo quiere comprimir el archivo? (1. tar, 2. gzip, 3. bzip2) "
		read comprimir
		case $comprimir in
			1) comandos="$comandos -c";;
			2) comandos="$comandos -cz";;
			3) comandos="$comandos -cj";;
			*) echo "Número inválido";;
		esac
	done
	echo "¿Quiere mostrar los detalles de la ejecuciòn? (-1. No)"
	read verbose
	if [ $verbose -ne -1 ]
	then
		comandos="$comandos -v"
	fi
	echo "Ingrese el archivo o carpeta que quiere comprimir."
	read nombre
	echo "¿Cuál va a ser el nombre del archivo comprimido?"
	read guardado
	case $comprimir in
		1) guardado="$guardado.tar";;
		2) guardado="$guardado.gz";;
		3) guardado="$guardado.bz2";;
		*) echo "Imposible llegar.";;
	esac
	comandos="$comandos -f /backup/$guardado"
	echo ""
	echo "Comando generado: tar $comandos $nombre"
	echo ""
	while [ $pregunta -ne 0 ]
	do
		echo "¿Está satisfecho con este backup? (1. Para ejecutar, 0. Para rechazar y salir)"
		read pregunta
		case $pregunta in
			1) echo "EJECUTANDO EL COMANDO..."
			tar $comandos $nombre
			echo "Backup Realizado."
			pregunta="0";;
			0) echo "Backup cancelado.";;
			*) echo "Numero invalido.";;
		esac
	done
done

