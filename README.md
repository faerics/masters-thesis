# masters-thesis
This is a repository for my Masters Thesis called
'Cognitive technologies in traffic light control.'

The thesis is written in russian and is unpublished yet, I have some plans to turn it
into a publication (article) in English.

Howewer, I refer to some chapters of the thesis to help those who are familiar
with its contents match this with what they've read (or _are_ reading).

If you are interested in publication or have a question, open an issue
to get in touch.

### The main goals achieved are:

1. The SUMO/TraCI pair extended at application level to run simulations with buses.
This includes teleporting to next stop, running simulation until some bus stops, etc.
See Chapter 2 for details. 
1. Proposed an algorithm to biuld a traffic model according to buses stopping data 
(see dataset).
2. Gathered a geometry model of Nevskiy Prospect's part: bus stops, buses and
car routes, some trafic lights.
1. The proposed algoritm applied and produced a result (see results folder).
 
### This repository contains:

- The extension of TraCI to work with buses properly at `python_src/simulation` (described in Chapter 2)
- The modified version of NASH algorithm at `python_src/simulation` (described at Chapter 3
along with theoriginal algorithm to biuld a traffic flow)
- The dataset of buses tracks in raw and preprocessed form at `dataset/` folder.
The script `dataset/preprocessing.py` can do the preprocessing logic described at Chapter 3
- Nevskiy prospect model with bus stops and routes for buses and cars crafted manually at
`SUMO/`. This folder includes the original `.osm` file and a command
to NETCONVERT which were used to build the net for SUMO.
- `results` folder contains the results of originally proposed algorithm described 
in Chapter 3. Theese includes:
    - `opt_fight_2.log` is a full log of the launch including each iteration output, the incoming data, etc.
    - `result_fight_2.log`is a subset of that log containing information only about the
    NASH final results. The line of this file is of the form
    ```
        # SimResult: vid, route, stop_time, next_stop, #iterations, f(0), f_value
        SimResult: 7381, 3_a, 222, liteyny_1, 0, 4, 4
    ```
    - `fight_2_result.rou.xml` is a model obtained from the algorithm.
    - `fight_1_result.rou.xml` is another (legacy) model. Unfortunately, the logs for it 
    was lacking information about buses routes, and can not be used for plotting
    (thus not present). But the model can be used for demo.
    - plots from the article, Use `python_src/postprocessing.py` to produce them. It also
    runs a demo on the model, and uses its result to build some plots.
    
 ### Reqiurements
 
 - SUMO (tested on 1.1.0)
 - python3 (tested on 3.6.7)
 - the other requirements can be installed via `pip install -r requirements.txt` 
 in `python_src` folder.
