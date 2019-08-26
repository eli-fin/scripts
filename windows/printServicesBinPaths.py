'''
Print all service bin paths

Author: Eli Finkel - eyfinkel@gmail.com
'''

import os
serviceNames = \
    [l.strip()[len('SERVICE_NAME: '):] for l \
     in os.popen(f'sc query type= all state= all').readlines() if 'SERVICE_NAME: ' in l]

print(f'Found {len(serviceNames)} services')
for s in sorted(serviceNames):
    p = os.popen(f'sc qc {s}')
    lines = p.readlines()
    retCode = p.close()
    if retCode:
        print(f'<error calling \'sc qc {s}\' (code={retCode})')
    else:
        binPath = [line for line in lines if 'BINARY_PATH_NAME' in line][0]
        binPath = binPath.split(':', 1)[1].strip()
        print((s, binPath))
