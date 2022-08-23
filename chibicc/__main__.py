import sys

if len(sys.argv) != 2:
    print(f"{sys.argv[0]}: invalid number of arguments")
    exit(1)

try:
    retval = int(sys.argv[1])
except ValueError:
    print("ERROR: invalid argument")
    exit(1)

print("    .globl main")
print("main:")
print(f"    movl ${retval}, %rax")
print("    ret")
