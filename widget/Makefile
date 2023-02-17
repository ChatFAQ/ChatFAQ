my_target:
	FILENAME=`npm pack | tail -n 1`
	ECHO $FILENAME
	curl -F package=@$(FILENAME) https://$(TOKEN)@push.fury.io/with/
