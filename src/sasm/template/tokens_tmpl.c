/*
 * This file is generated from insnsa.xml, regs.xml and token.xml
 * by tokhash.py; do not edit.
 */

#include "compiler.h"
#include <string.h>
#include "nasm.h"
#include "hashtbl.h"
#include "insns.h"
#include "stdscan.h"


struct tokendata {
    const char *string;
    int32_t tokentype;
    int32_t aux;
    int64_t tokflag;
    int64_t num;
};

static int T1[] = { $S1 };

static int T2[] = { $S2 };

static int G[] = { $G };

static const struct tokendata K[] = { $K };

static int hash_g (const char *key, const int *T)
{
  int i, sum = 0;
  
  for (i = 0; key[i] != '\0'; i++) {
    sum += T[i] * key[i];
    sum %= $NG;
  }
  return G[sum];
}

static int perfect_hash (const char *key)
{
  return (hash_g (key, T1) + hash_g (key, T2)) % $NG;
}

int nasm_token_hash(const char *abbr, struct tokenval *tv)
{
  char c = 0;
  int ix = 0;
  int i = 0;
  char szBuf[256] = {0};
  const struct tokendata *data;
  tv->t_flag = 0;

  if (strlen (abbr) > $NS)
    return tv->t_type = TOKEN_ID;

  while ((c = *abbr++) != 0) {
	  szBuf[i++] = nasm_tolower(c);
  }

  ix = perfect_hash (szBuf);
  if (ix >= $NK)
    return tv->t_type = TOKEN_ID;
	
  data = &K[ix];
  if (strcmp(szBuf, data->string))
    return tv->t_type = TOKEN_ID;

  tv->t_integer = data->num;
  tv->t_inttwo  = data->aux;
  tv->t_flag    = data->tokflag;
  return tv->t_type = data->tokentype;
}
