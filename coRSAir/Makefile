INC		=	/System/Volumes/Data/sgoinfre/goinfre/Perso/fdiaz-ca/homebrew/opt/openssl@1.1/include
LIB		=	/System/Volumes/Data/sgoinfre/goinfre/Perso/fdiaz-ca/homebrew/opt/openssl@1.1/lib
CFLAGS	=	-Werror -Wall -Wextra

all:
	@clear
	@gcc corsair.c $(CFLAGS) -I$(INC) -L$(LIB) -lssl -lcrypto -o coRSAir
	@./coRSAir