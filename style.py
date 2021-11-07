import io
from flask.helpers import send_file
from PIL import Image
import cloudscraper
from connection import redis_cache 

db = redis_cache()

def cache_bytes(bytes, image_url, image_size, name):
    if db.get(f'{image_url}_{image_size}_{name}') is None:
        db.set(f'{image_url}_{image_size}_{name}', bytes, 300)
        print(f'{image_url}_{image_size}_{name}\nimage is cached')
        return bytes
    else:
        return db.get(f'{image_url}_{image_size}_{name}')

class style:
    def __init__(self, image_url, image_size):
        self.image_url = image_url
        self.image_size = image_size

    def classic(self):
        image_url = self.image_url
        image_size = self.image_size
        if db.get(f'{image_url}_{image_size}_classic') is None:
            scraper = cloudscraper.create_scraper()
            scraper_out = scraper.get(image_url, stream=True)
            print(image_url, scraper_out.status_code)
            if scraper_out.status_code == 404 or scraper_out.status_code == 403:
                return
            with Image.open(scraper_out.raw) as im:
                background = im.crop((8, 8, 16, 16)).convert("RGBA")
                foreground = im.crop((40, 8, 48, 16)).convert("RGBA")
                head = Image.alpha_composite(background, foreground)
                result = head.resize((image_size, image_size), resample=0)
                result_byte = io.BytesIO()
                result.save(result_byte, format='PNG')
                result_byte.seek(0)
                cache_bytes(result_byte.getvalue(), image_url, image_size, 'classic')
                result_byte.seek(0)
                return send_file(result_byte , mimetype='image/png')
        else:
            print(f'{image_url}_{image_size}_class', '\nimage is in cache')
            byte_from_db = db.get(f'{image_url}_{image_size}_classic')
            return send_file(io.BytesIO(byte_from_db), mimetype='image/png')
