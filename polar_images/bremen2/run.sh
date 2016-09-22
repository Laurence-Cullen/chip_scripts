module load dials/nightly

# start the server in the background
nohup dials.find_spots_server > dials.server.out 2> dials.server.err < /dev/null &

# give server time to start
sleep 5

files=/dls/i24/data/2016/nt14486-21/df/bremen2/bremen2_*.cbf

time dials.find_spots_client \
  d_min=1.7 d_max=40 \
  indexing.method=fft1d \
  refinement_protocol.n_macro_cycles=2 \
  basis_vector_combinations.max_try=10 \
  detector.fix=all beam.fix=all \
  json=find_spots.json \
  ${files} > dials.client.out 2> dials.client.err < /dev/null

# stop the server
dials.find_spots_client stop

