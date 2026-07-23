#!/bin/bash
cd ~/cosmos-proj/15_phase1/track_b
# Wait for Track A (pid 356346) to release the GPU.
while ps -p 356346 >/dev/null 2>&1; do sleep 20; done
echo "TRACK_A_EXITED $(date)" > run_b.log
sleep 5
~/cosmos-proj/venv/bin/python run_track_b.py >> run_b.log 2>&1
echo "LAUNCHER_DONE $(date)" >> run_b.log
