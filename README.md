# Memory Management Policies Simulator

## Requirements
This simulation requires:
1. Python 2 or 3
2. sortedcontainers library of Python

sortedcontainers can be installed using **pip install sortedcontainers** or **pip install -r requirements.txt**

## How to run
Simulation can be run via command line providing some flags. Here is the man page of main.py:

```
usage: main.py [-h] -s N -w FILE -p N -o FILE

Memory Management Policy Simulator

optional arguments:
  -h, --help            show this help message and exit
  -s N, --size N        memory size in Kb
  -w FILE, --workload FILE
                        path of workload file
  -p N, --policy N      memory management policy 1- VSP 2- PAG 3- SEG
  -o FILE, --output FILE
                        path of output report file

```

Note that **-p** flag donates the policy to use from the given options <1,2,3>. If policy **1** or **3**
are chosen **-a** (**a**lgorithm) flag is must to provide from options of <1,2> where **1** and **2**
represent *first-fit* or *best-fit* algorithms respectively. Otherwise, if policy number **2** is chosen
**-f**(**f**rame) flag is must to provide to indicate the frame size.

Few example run commands are also provided below.

## Examples Commands to execute

###### VSP
python main.py -s 2000 -w ../inputs/VSP/input1.txt -p 1 -a 1 -o ../outputs/VSP/output1_vsp_first.txt

python main.py -s 2000 -w ../inputs/VSP/input1.txt -p 1 -a 2 -o ../outputs/VSP/output1_vsp_best.txt

python main.py -s 2000 -w ../inputs/VSP/input2.txt -p 1 -a 1 -o ../outputs/VSP/output2_vsp_first.txt

python main.py -s 2000 -w ../inputs/VSP/input2.txt -p 1 -a 2 -o ../outputs/VSP/output2_vsp_best.txt

###### SEG
python main.py -s 2000 -w ../inputs/SEG/input1.txt -p 3 -a 1 -o ../outputs/SEG/output1_seg_first.txt

python main.py -s 2000 -w ../inputs/SEG/input1.txt -p 3 -a 2 -o ../outputs/SEG/output1_seg_best.txt

python main.py -s 2000 -w ../inputs/SEG/input2.txt -p 3 -a 1 -o ../outputs/SEG/output2_seg_first.txt

python main.py -s 2000 -w ../inputs/SEG/input2.txt -p 3 -a 2 -o ../outputs/SEG/output2_seg_best.txt


###### PAG
python main.py -s 2000 -w ../inputs/PAG/input1.txt -p 2 -f 100 -o ../outputs/PAG/output1_pag_100.txt

python main.py -s 2000 -w ../inputs/PAG/input1.txt -p 2 -f 200 -o ../outputs/PAG/output1_pag_200.txt

python main.py -s 2000 -w ../inputs/PAG/input1.txt -p 2 -f 400 -o ../outputs/PAG/output1_pag_400.txt
