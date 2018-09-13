# Cartman

control your CARTMAN(R) cartesian robot from python.

## Installation

```bash
git clone https://github.com/ctmakro/cartman
pip install -e cartman # "-e" means "edit mode"
```

## Update (In case newer versions came out)

```bash
cd cartman
git pull
```

## Usage

```python
from cartman import bot

bot.home()
bot.goto(x=0,y=0,z=20)
```
