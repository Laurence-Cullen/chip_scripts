module load dials/nightly

# start the server in the background
nohup dials.find_spots_server > dials.server.out 2> dials.server.err < /dev/null &

# give server time to start
sleep 5

files=/dls/i24/data/2016/nt14493-21/mb/dallas/dallas*.cbf

time dials.find_spots_client \
  index=True\
  d_min=1.8 d_max=40 \
  indexing.method=real_space_grid_search \
  known_symmetry.space_group=P212121 \
  known_symmetry.unit_cell=38,46.9,84.6,90,90,90 \
  refinement_protocol.n_macro_cycles=2 \
  basis_vector_combinations.max_try=10 \
  detector.fix=all beam.fix=all \
  json=find_spots.json \
  ${files} > dials.client.out 2> dials.client.err < /dev/null

# stop the server
dials.find_spots_client stop

