#!/bin/bash
TOPOLOGY="leaf_spine_128_100G_OS2"
RUNTIME="0.02"
NETLOAD="80"

echo "=== Running fecmp (1/3) ==="
python3 run.py --lb fecmp --pfc 1 --irn 0 --simul_time ${RUNTIME} --netload ${NETLOAD} --topo ${TOPOLOGY}
echo "=== Running letflow (2/3) ==="
python3 run.py --lb letflow --pfc 1 --irn 0 --simul_time ${RUNTIME} --netload ${NETLOAD} --topo ${TOPOLOGY}
echo "=== Running conweave (3/3) ==="
python3 run.py --lb conweave --pfc 1 --irn 0 --simul_time ${RUNTIME} --netload ${NETLOAD} --topo ${TOPOLOGY}
echo "=== All done! ==="
