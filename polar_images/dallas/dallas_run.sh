module load dials/nightly

# start the server in the background
nohup dials.find_spots_server > dials.server.out 2> dials.server.err < /dev/null &

# give server time to start
sleep 5

files=/dls/i24/data/2016/nt14493-21/mb/dallas/dallas*.cbf

time dials.find_spots_client \
  d_min=1.8 d_max=40 \
  json=find_spots.json \
  ${files} > dials.client.out 2> dials.client.err < /dev/null

# stop the server
dials.find_spots_client stop

