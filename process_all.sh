poetry shell
python main.py --skip_worldmap --batch_start 0 &
python main.py --skip_worldmap --batch_start 100 &
python main.py --skip_worldmap --batch_start 200 &
python main.py --skip_worldmap --batch_start 300 &
python main.py --skip_worldmap --batch_start 400 &
python main.py --skip_worldmap --batch_start 500 &
python main.py --skip_worldmap --batch_start 600 &
python main.py --skip_worldmap --batch_start 700 &
python main.py --skip_worldmap --batch_start 800
wait
