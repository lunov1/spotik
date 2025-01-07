# spotik
`spotik` is here to translate your tracks right now in your telegram profile

### installation for *linux*:
```
git clone https://github.com/lunov1/spotik.git
cd spotik
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env # fill in all fields with variables
nano .env
python3 __main__.py
```

### installation for *windows*:
```
git clone https://github.com/lunov1/spotik.git
cd spotik
python -m venv venv
venv/scripts/activate
pip install -r requirements.txt
copy .env.example .env
# fill in all fields with variables in file .env
python __main__.py
```

### some problems?:
1. check if you have put a picture for the state when the music is not playing.
2. Make sure that you have filled in the relevant information in the .env file.
3. If you are from Russia try to use VPN.
