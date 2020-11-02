# html2vec
Algorithm that converts an HTML to a vectorized object suitable for neural networks.

![alt text](/wallpaper.jpeg)

## Instructions
Installing dependencies.
```bash
virtualenv -p python3 .env
source .env/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_md
```
Vectorizing HTML from the CLI
```bash
python3 html2vec.py "https://hippie-inheels.com/3-day-new-orleans-itinerary/"
```
Vectorizing HTML inside a Python script.
```python
from html2vec import Html2Vec

model: Html2Vec = Html2Vec()
model.relatives = 5
for node in model.fit(html):
    print(node)
    print(node.get_vector())
```
