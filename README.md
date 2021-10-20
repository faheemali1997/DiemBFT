# DiemBFT
The project includes implementation of DiemBFT v4: State Machine Replication approach in the Diem Blockchain. DiemBFT
is responsible for forming agreement on ordering and finalizing transactions among distributed nodes. The main 
guarantee provided by the approach is resilience against Byzantine failures and Transaction Finality. DiemBFT uses
novel leader election mechanism to achieve leader utilization. Validators form agreement on sequence of transactions
and apply them in sequence order to replicate database. We define 3 types of validators - Byzantine, Compromised and 
Honest where there are atmost f < n/3 Byzantine Validators. DiemBFT assumes Partial Synchrony which has Δ 
transmission bound after GST(Global Stabilized Time). In diemBFT, leader role is to populate network with unique proposal 
for the round. DiemBFT is inspired by linear three phase Hotstuff, it extends it by preserving the communication linearity 
but allows quadratic cost during view-change protocol. Each round executes all the phases - Prepare, Pre-Commit, Commit.
Reference to DistAlgo Library : https://github.com/DistAlgo/distalgo


PLATFORM
--------
DistAlgo - pyDistAlgo 1.0.14 - DistAlgo is a high-level language for expressing distributed algorithms. DistAlgo requires 
			       Python version 3.5, 3.6, or 3.7. DistAlgo has been tested on GNU/Linux and Microsoft Windows.
			       It abstracts the underlying implementation and processes of network.

Python - version 3.6.7	     - Python is an interpreted high-level general-purpose programming language.

Setup and Run
-------

Steps for running the DiemBft Project:

A.)	 Setup

Step 1: Install pyDistAlgo 

	Command: pyDistAlgo : pip install pyDistAlgo

Step 2: Install treelib

	Command: pip install treelib

Step 3: Install pyNaCl

	Command: pip install pyNaC

Step 4: cd to the diembft root folder

	Command: cd ~/diembft


B.)	Running the project

Step 5: Run the distalgo code which takes config from configuration file.

	Command: python3 -m da --message-buffer-size 65353 diembft/driver.da
 

TIMEOUTS
--------
We have use DistAlgo Timeout Await which waits for 4 * Δ time period, after which it sends out timeout message.

BUGS AND LIMITATIONS
--------------------
1. The code continously processes NooP messages.
2. We are not pruning the in memory block tree to limit it to the window size


MAIN FILES
----------
diembft/driver.da - main driver file , creates replica and client nodes

CODE SIZE
---------
3000 Lines of code in the DiemBFT Repo

