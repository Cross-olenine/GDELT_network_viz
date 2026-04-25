import time
from datetime import datetime
from gdeltdoc import Filters, GdeltDoc

gd = GdeltDoc()

def fetch(keyword, delay=0):
    if delay:
        time.sleep(delay)
    try:
        f = Filters(keyword=keyword, start_date="2024-03-01", end_date="2024-03-02", num_records=5, language="English")
        df = gd.article_search(f)
        print(f"[delay={delay}s] OK — {len(df)} articles")
        return True
    except Exception as e:
        print(f"[delay={delay}s] ECHEC — {type(e).__name__}")
        return False

# Deux requêtes successives avec différents délais
fetch("bilateral agreement", delay=0)
fetch("diplomatic talks", delay=2)