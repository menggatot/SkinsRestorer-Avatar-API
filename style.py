import io, logging, os, cloudscraper
from flask.helpers import send_file
from PIL import Image
from connection import redis_cache 
from dotenv import load_dotenv

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, '.env'))

CACHE_IMAGE_TIME = int(os.getenv('CACHE_IMAGE_TIME', 300))
JPEG_QUALITY = int(os.getenv('JPEG_QUALITY', 80))

db = redis_cache()

def cache_bytes(bytes, image_url, image_size, name):
    if db.get(f'{image_url}_{image_size}_{name}') is None:
        db.set(f'{image_url}_{image_size}_{name}', bytes, CACHE_IMAGE_TIME)
        logging.info('%s_%s_%s image is cached', str(image_url), str(image_size), str(name))
        return bytes
    else:
        return db.get(f'{image_url}_{image_size}_{name}')

class style:
    def __init__(self, image_url, image_size):
        self.image_url = image_url
        self.image_size = image_size

    def classic_png(self):
        image_url = self.image_url
        image_size = self.image_size
        if db.get(f'{image_url}_{image_size}_classic_png') is None:
            scraper = cloudscraper.create_scraper()
            scraper_out = scraper.get(image_url, stream=True)
            logging.info('%s %s', str(image_url), str(scraper_out.status_code))
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
                cache_bytes(result_byte.getvalue(), image_url, image_size, 'classic_png')
                result_byte.seek(0)
                return send_file(result_byte , mimetype='image/png')
        else:
            logging.info('%s_%s_classic_png image is in cache', str(image_url), str(image_size))
            byte_from_db = db.get(f'{image_url}_{image_size}_classic_png')
            return send_file(io.BytesIO(byte_from_db), mimetype='image/png')

    def classic_jpeg(self):
        image_url = self.image_url
        image_size = self.image_size
        if db.get(f'{image_url}_{image_size}_classic_jpeg') is None:
            scraper = cloudscraper.create_scraper()
            scraper_out = scraper.get(image_url, stream=True)
            logging.info('%s %s', str(image_url), str(scraper_out.status_code))
            if scraper_out.status_code == 404 or scraper_out.status_code == 403:
                return
            with Image.open(scraper_out.raw) as im:
                background = im.crop((8, 8, 16, 16)).convert("RGBA")
                foreground = im.crop((40, 8, 48, 16)).convert("RGBA")
                head = Image.alpha_composite(background, foreground)
                result = head.resize((image_size, image_size), resample=0).convert("RGB")
                result_byte = io.BytesIO()
                result.save(result_byte, format='JPEG', quality=JPEG_QUALITY)
                result_byte.seek(0)
                cache_bytes(result_byte.getvalue(),
                            image_url, image_size, 'classic_jpeg')
                result_byte.seek(0)
                return send_file(result_byte, mimetype='image/jpeg')
        else:
            logging.info('%s_%s_classic_jpeg image is in cache',
                str(image_url), str(image_size))
            byte_from_db = db.get(f'{image_url}_{image_size}_classic_jpeg')
            return send_file(io.BytesIO(byte_from_db), mimetype='image/jpeg')
