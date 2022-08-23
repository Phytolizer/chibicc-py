import sys

from chibicc.chibicc import chibicc

ret = chibicc(sys.argv, sys.stdout)
exit(ret)
