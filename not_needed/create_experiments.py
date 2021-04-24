tops = ["B4_000",
        "B4_001",
        "B4_002",
        "B4_003",
        "B4_004",
        "B4_005",
        "B4_006",
        "B4_007",
        "B4_008",
        "B4_009"]
dems = [i for i in range(100)]

cs = [0.001,0.00001]

x = 0
for d in dems:
    for t in tops:
        for c in cs:
            txt = f'''add_ducts = True
alpha = 0.99
demand_scale = 1.5
fiber_cost = 3600.0
gbps_cost = 30.0
n_fibers_per_fiberduct = 200.0
n_wavelengths_fiber = 64.0
path_selection = KSP-4
time_heuristic_fwd = True
timesteps = 1
transceiver_amortization_years = 3.0
wavelength_capacity = 400.0
cutoff = {c}
demand_no = {d}
topology = {t}
path = experiments/018/'''

            with open(f'experiments/018/config_{x:08d}.cfg', 'w') as fi:
                fi.write(txt)

            x += 1



