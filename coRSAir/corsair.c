#include "openssl/rsa.h"
#include "openssl/bn.h"
#include "openssl/bio.h"
#include "openssl/evp.h"
#include "openssl/err.h"
#include "openssl/x509.h"
#include "openssl/pem.h"
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <fcntl.h> 

#define CERT1 "./cert1.pem"
#define CERT2 "./cert2.pem"
#define ENCRYPTED "./passwd.enc"
#define BUFFER 1024


RSA *get_rsa(char *file)
{
	X509		*cert;
	EVP_PKEY	*pbkey;
	RSA			*rsa;
	BIO			*biocert;
	int			check;

	biocert = BIO_new(BIO_s_file());
	check = BIO_read_filename(biocert, file);
	if (check != 1)
	{
		printf("\n Error: Spected %s and %s. File not found \n", CERT1, CERT2);
		return(0);
	}
	cert = PEM_read_bio_X509(biocert, NULL, 0, NULL);
	pbkey = X509_get_pubkey(cert);
	rsa = EVP_PKEY_get1_RSA(pbkey);
	EVP_PKEY_free(pbkey);
	X509_free(cert);
	BIO_free(biocert);
	return(rsa);
}

int main(void)
{
	BN_CTX		*ctx;
	BIO			*bioprint;
	RSA			*rsa1;
	RSA			*rsa2;
	RSA			*pv_rsa;
	BIGNUM		*one;
	BIGNUM		*n1;
	BIGNUM		*n2;
	BIGNUM		*q1;
	BIGNUM		*q2;
	BIGNUM		*p;
	BIGNUM		*fi_total;
	BIGNUM		*fi_sub1;
	BIGNUM		*fi_sub2;
	BIGNUM		*e;
	BIGNUM		*d;
	unsigned char 		*buff;
	unsigned char		*sol;
	int			fd;
	int			len;

/* Inicializar variables */
	buff = malloc(sizeof(unsigned char)*BUFFER);
	sol = malloc(sizeof(unsigned char)*BUFFER);
	ctx = BN_CTX_new();
	bioprint = BIO_new_fp(stdout, BIO_NOCLOSE);
	rsa1 = get_rsa(CERT1);
	rsa2 = get_rsa(CERT2);
	if (!rsa1 || !rsa2)
		return(0);
	one = BN_new();
	q1 = BN_new();
	q2 = BN_new();
	p = BN_new();
	d = BN_new();
	fi_total = BN_new();
	fi_sub1 = BN_new();
	fi_sub2 = BN_new();
	pv_rsa = RSA_new();
/* Hacer la aritmetica para obtener los datos */
/*
		public-key rsa1(e, n1) ;  public-key rsa2(e, n2)
		n1 = p*q1 ; n2 = p*q2
		p = MCD(n1, n2)
		fi = (p-1)*(q-1)
		d*e mod fi = 1  |  d = inv(e,fi) 
		private-key (d, n)
*/
	n1 = (BIGNUM *)RSA_get0_n(rsa1);
	n2 = (BIGNUM *)RSA_get0_n(rsa2);
	e = (BIGNUM *)RSA_get0_e(rsa1);
	BN_gcd(p, n1, n2, ctx);
	BN_div(q1, NULL, n1, p, ctx);
	BN_div(q2, NULL, n2, p, ctx);
	BN_dec2bn(&one, "1");
	BN_sub(fi_sub1, q1, one);
	BN_sub(fi_sub2, p, one);
	BN_mul(fi_total, fi_sub1, fi_sub2, ctx);
	BN_mod_inverse(d, e, fi_total, ctx);
/* Usar datos para generar la clave privada y asociar los numeros primos a cada rsa*/
	RSA_set0_key(pv_rsa, n1, e, d);
	RSA_set0_factors(rsa1, p, q1);
	RSA_set0_factors(rsa2, p, q2);
/* Usar clave privada para descifrar mensaje */
	fd = open(ENCRYPTED, O_RDONLY);
	len = read(fd, buff, BUFFER);
	if (len < 1)
	{
		printf("\n Error: Spected encrypted file %s . File not found \n", ENCRYPTED);
		return (0);
	}
	RSA_private_decrypt(len, buff, sol, pv_rsa, RSA_PKCS1_PADDING);
/* Imprimir resultados */
	printf("\n\n ****   Public-Key1 from Cert1    **** \n ");
	RSA_print(bioprint, rsa1, 0);
	printf("\n\n ****   Public-Key2 from Cert2    **** \n ");
	RSA_print(bioprint, rsa2, 0);
	printf("\n\n ****   Private-Key from Public-Key1    **** \n ");
	RSA_print(bioprint, pv_rsa, 0);
	printf("\n\n\n ****   Encrypted Text    **** \n");
	printf("%s", buff);
	printf("\n\n ****    Decrypted Message!    **** \n");
	printf("%s", sol);
	printf("\n");
/* Liberar memoria a troche-moche */
	free(sol);
	free(buff);
	BIO_free(bioprint);
	BN_free(one);
	BN_free(n1);
	BN_free(n2);
	BN_free(q1);
	BN_free(q2);
	BN_free(p);
	BN_free(fi_total);
	BN_free(fi_sub1);
	BN_free(fi_sub2);
	BN_free(e);
	BN_free(d);
	BN_CTX_free(ctx);
	return (0);
}
