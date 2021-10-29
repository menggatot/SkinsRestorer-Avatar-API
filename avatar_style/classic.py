import io
from flask.helpers import send_file
from PIL import Image
import cloudscraper

def classic(image_url, image_size):
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
        return send_file(result_byte, mimetype='image/png')