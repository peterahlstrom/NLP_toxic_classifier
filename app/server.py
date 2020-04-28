import aiohttp
import asyncio
import uvicorn
from fastai import *
from fastai.text import *
from io import BytesIO
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse, JSONResponse
from starlette.staticfiles import StaticFiles
from zipfile import ZipFile

# export_file_url = 'https://www.dropbox.com/s/6bgq8t6yextloqp/export.pkl?raw=1'
# export_file_url = 'https://drive.google.com/open?id=1qUGhD2f8YyVfOxhdyUOZJIktBWAgeomy'
# export_file_url = 'https://drive.google.com/uc?export=download&id=1-3vVyfmwXYFOYPCyLAaWwAbiaBHo1lee' #pkl-file
# export_file_url = 'https://drive.google.com/uc?export=download&id=1Iy8wD51J2ZMndDhxoOmDr5lZCWM4lkys' #pkl-file
export_file_url = 'http://kartor.malmo.se/test/ml/model.zip'
export_file_name = 'model.pkl'
# export_file_name = 'boris_vs_harry.pkl'



classes=['toxic', 'severe_toxic', 'obscene', 'threat', 'insult', 'identity_hate']
path = Path(__file__).parent

app = Starlette()
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_headers=['X-Requested-With', 'Content-Type'])
app.mount('/static', StaticFiles(directory='app/static'))


async def download_file(url, dest):
    if dest.exists(): return
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.read()
            with open(dest, 'wb') as f:
                f.write(data)


async def setup_learner():
    await download_file(export_file_url, path / 'model.zip')
    with ZipFile(path/'model.zip', 'r') as zip_obj:
        await zip_obj.extractall()
    try:
        learn = load_learner(path, export_file_name)
        return learn
    except RuntimeError as e:
        if len(e.args) > 0 and 'CPU-only machine' in e.args[0]:
            print(e)
            message = "\n\nThis model was trained with an old version of fastai and will not work in a CPU environment.\n\nPlease update the fastai library in your training environment and export your model again.\n\nSee instructions for 'Returning to work' at https://course.fast.ai."
            raise RuntimeError(message)
        else:
            raise


loop = asyncio.get_event_loop()
tasks = [asyncio.ensure_future(setup_learner())]
learn = loop.run_until_complete(asyncio.gather(*tasks))[0]
loop.close()


@app.route('/')
async def homepage(request):
    html_file = path / 'view' / 'index.html'
    return HTMLResponse(html_file.open().read())


@app.route('/analyze', methods=['POST'])
async def analyze(request):
    img_data = await request.form()
    text = await (img_data['text'])
    # img = open_image(BytesIO(img_bytes))
    prediction = learn.predict(text)
    # print(learn.predict(img))
    resp = JSONResponse({'result': str(prediction[0])})
    return resp

if __name__ == '__main__':
    if 'serve' in sys.argv:
        uvicorn.run(app=app, host='0.0.0.0', port=5000, log_level="info")
