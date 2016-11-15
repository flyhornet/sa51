
#include <string.h>

#include "directiv.h"
#include "nasm.h"

static int T1[] = { $S1 };

static int T2[] = { $S2 };

static int G[] = { $G };

static char *K[] = { $K };

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

int find_directive (const char *abbr)
{

  char c = 0;
  int i = 0;
  int hash_value = 0;
  char szBuf[256] = {0};
  if (strlen (abbr) > $NS)
    return D_UNKNOWN;

  while ((c = *abbr++) != 0) {
	  szBuf[i++] = nasm_tolower(c);
  }

  hash_value = perfect_hash (szBuf);
  
  if (hash_value < $NK && strcmp(szBuf, K[hash_value]) == 0)
    return hash_value;
  
  return D_UNKNOWN;
}
