# save as inspect_env.py and run: python inspect_env.py
from dotenv import load_dotenv
import os

# ensure load uses utf-8
load_dotenv('.env.test', encoding='utf-8')

keys = [
  'DATABASE_HOSTNAME','DATABASE_PORT','DATABASE_PASSWORD',
  'DATABASE_NAME','DATABASE_USERNAME','DATABASE_CLIENT_ENCODING'
]

for k in keys:
    v = os.getenv(k)
    print(f"{k}: {repr(v)}")
    if v is None:
        print(f"  -> {k} not set")
        continue
    # show any non-ascii chars and their positions
    nonascii = [(i, ch, hex(ord(ch))) for i,ch in enumerate(v) if ord(ch) > 127]
    if nonascii:
        print("  non-ascii characters found:", nonascii)
    # show bytes (utf-8) with replacement so you can spot � in output
    print("  bytes (utf-8):", v.encode('utf-8', errors='replace'))
    print()
# show constructed DSN repr
dsn = f"host={os.getenv('DATABASE_HOSTNAME')} dbname={os.getenv('DATABASE_NAME')} user={os.getenv('DATABASE_USERNAME')} password={os.getenv('DATABASE_PASSWORD')} port={os.getenv('DATABASE_PORT')}"
print("DSN repr:", repr(dsn))
print("DSN bytes:", dsn.encode('utf-8', errors='replace'))
