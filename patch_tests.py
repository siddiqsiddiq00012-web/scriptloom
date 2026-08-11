import os, glob, re

test_files = glob.glob('tests/*.py')
for tf in test_files:
    with open(tf, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # regex to match: client.post( "/ or client.get( f"/ 
    # taking into account whitespace/newlines
    new_content = re.sub(
        r'(client\.(get|post|patch|put|delete)\(\s*(?:f)?\")(/)(?!api/v1/)',
        r'\1api/v1/',
        content
    )
    
    if new_content != content:
        with open(tf, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f'Updated {tf}')
